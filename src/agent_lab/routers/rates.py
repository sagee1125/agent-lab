import httpx
from fastapi import APIRouter

router = APIRouter(tags=["rates"])

RATE_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=CNY"


@router.get("/rate")
async def rate() -> dict[str, float | None]:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(RATE_URL, timeout=8)
            r.raise_for_status()
            return {"usd_cny": r.json()["rates"]["CNY"]}
        except httpx.HTTPError as e:
            print("⚠️", type(e).__name__, e)
            return {"usd_cny": None}
