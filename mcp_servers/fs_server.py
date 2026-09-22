import os
from pathlib import Path

from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".txt", ".json", ".yaml", ".yml", ".cfg", ".ini"}
DENY_NAMES = {".env", ".env.local", "credentials.json", "id_rsa", "id_ed25519"}
DENY_SUFFIXES = {".key", ".pem", ".pfx", ".p12"}
MAX_HITS = 50

mcp = FastMCP("agent-lab filesystem")


def _is_denied(p: Path) -> bool:
    return p.name in DENY_NAMES or p.suffix in DENY_SUFFIXES


def _resolve(path: str) -> Path:
    """把相對路徑解析成 ROOT 底下的絕對路徑；越界或敏感檔案一律拒絕。"""
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"拒絕存取工作區以外的路徑：{path}")
    if _is_denied(target):
        raise ValueError(f"拒絕存取敏感檔案：{path}")
    return target


@mcp.tool
def read_file(path: str) -> str:
    """讀取工作區內的文字檔。path 相對於工作區根目錄，例如 'pyproject.toml'。"""
    target = _resolve(path)
    if not target.is_file():
        return f"錯誤：找不到檔案 {path}"
    return target.read_text(encoding="utf-8")


@mcp.tool
def write_file(path: str, content: str) -> str:
    """把文字寫入工作區內的檔案，會覆蓋原有內容，必要時自動建立上層目錄。"""
    target = _resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"已寫入 {path}（{len(content)} 個字元）"


@mcp.tool
def list_dir(path: str = ".") -> str:
    """列出工作區內某個目錄的內容。path 預設為工作區根目錄。"""
    target = _resolve(path)
    if not target.is_dir():
        return f"錯誤：{path} 不是目錄"
    entries = [
        f"{'DIR ' if child.is_dir() else 'FILE'}  {child.name}"
        for child in sorted(target.iterdir())
        if child.name not in SKIP_DIRS
    ]
    return "\n".join(entries) if entries else "（空目錄）"


@mcp.tool
def search_content(keyword: str, path: str = ".") -> str:
    """在工作區內的文字檔中搜尋關鍵字，回傳「檔案:行號: 該行內容」，最多 50 筆。"""
    start = _resolve(path)
    needle = keyword.lower()
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(start):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if len(hits) >= MAX_HITS:
                break
            f = Path(dirpath) / name
            if f.suffix not in TEXT_SUFFIXES or _is_denied(f):
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if needle in line.lower():
                    hits.append(f"{f.relative_to(ROOT)}:{lineno}: {line.strip()[:120]}")
                    if len(hits) >= MAX_HITS:
                        break
    return "\n".join(hits) if hits else f"沒有找到「{keyword}」"


if __name__ == "__main__":
    mcp.run()
