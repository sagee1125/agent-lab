"""送一句話給本機的 /chat API。

為什麼不用 curl？
    Windows 內建的 curl.exe（C:\\WINDOWS\\system32\\curl.exe）是 MSVC 編譯的，
    它用 CRT 的 char** argv 取命令列參數，非 ASCII 會被轉成 Windows ANSI 代碼頁
    （這台機器是 1252），中文就變成「?」。
    Python 在 Windows 上用 GetCommandLineW 取得命令列，中文原樣保留 ——
    所以中文交給 Python 走就沒事。

用法：
    uv run python chat_cli.py "東京現在天氣如何？"
    uv run python chat_cli.py "那濕度呢？" --thread cli-1
    uv run python chat_cli.py --thread cli-1 < req.txt      # 從 stdin 讀，完全不經命令列
"""

import argparse
import sys

import httpx

DEFAULT_URL = "http://127.0.0.1:8000/chat"


def main() -> int:
    parser = argparse.ArgumentParser(description="送一句話給本機的 /chat API")
    parser.add_argument("message", nargs="?", help="要送出的訊息；省略時從 stdin 讀")
    parser.add_argument("--thread", default="cli-1", help="thread_id（預設 cli-1）")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"API 位址（預設 {DEFAULT_URL}）")
    args = parser.parse_args()

    message = args.message if args.message is not None else sys.stdin.read()
    message = message.strip()
    if not message:
        print('沒有訊息可以送出。用法：uv run python chat_cli.py "你的問題"', file=sys.stderr)
        return 2

    payload = {"thread_id": args.thread, "message": message}
    try:
        resp = httpx.post(args.url, json=payload, timeout=120)
        resp.raise_for_status()
    except httpx.ConnectError:
        print(
            f"連不上 {args.url} —— 伺服器有在跑嗎？\n"
            "啟動：uv run uvicorn agent_lab.main:app --reload",
            file=sys.stderr,
        )
        return 1
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code}：{e.response.text}", file=sys.stderr)
        return 1

    data = resp.json()
    print(data["reply"])
    print(f"\n[thread={data['thread_id']}　累積訊息 {data['message_count']} 則]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
