import asyncio
import time

import httpx
import truststore

truststore.inject_into_ssl()

async def task(name: str, sec: float) -> str:
    await asyncio.sleep(sec)
    return f"{name} done"


async def blocking_task(name: str, sec: float) -> str:
    time.sleep(sec)  # ❌ 同步阻塞，卡住整個事件循環
    return f"{name} done"


async def fetch_cny_rate(client: httpx.AsyncClient) -> float | None:
    url = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=CNY"
    try:
        r = await client.get(url, timeout=8)
        r.raise_for_status()
        return r.json()["rates"]["CNY"]
    except httpx.HTTPError as e:
        print("⚠️ 匯率查詢失敗:", type(e).__name__, e)
        return None

# async def fetch_rate(client: httpx.AsyncClient) -> float:
#     r = await client.get("https://open.er-api.com/v6/latest/USD")
#     r.raise_for_status()
#     return r.json()["rates"]["CNY"]


async def main() -> None:
    t0 = time.perf_counter()
    await task("A", 1)
    await task("B", 1)
    await task("C", 1)
    print("循序 sequential :", round(time.perf_counter() - t0, 2), "s")

    t0 = time.perf_counter()
    await asyncio.gather(task("A", 1), task("B", 1), task("C", 1))
    print("並發 gather     :", round(time.perf_counter() - t0, 2), "s")

    t0 = time.perf_counter()
    await asyncio.gather(blocking_task("A", 2), blocking_task("B", 2))
    print("❌ 直接 time.sleep:", round(time.perf_counter() - t0, 2), "s")

    t0 = time.perf_counter()
    await asyncio.gather(asyncio.to_thread(time.sleep, 2), asyncio.to_thread(time.sleep, 2))
    print("✅ to_thread 包裝 :", round(time.perf_counter() - t0, 2), "s")

    async with httpx.AsyncClient() as client:
        rate = await fetch_cny_rate(client)
        print("1 USD =", rate, "CNY")


if __name__ == "__main__":
    asyncio.run(main())
