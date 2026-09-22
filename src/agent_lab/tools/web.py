import httpx
from pydantic import BaseModel, Field

from agent_lab.tools.base import Tool

TIMEOUT = 10.0
USER_AGENT = "agent-lab/0.1 (learning project; contact: 1324300391@qq.com)"


# async def _get_json(url: str, params: dict | None = None) -> dict:
#     async with httpx.AsyncClient(timeout=TIMEOUT) as client:
#         r = await client.get(url, params=params) # 交給 httpx 自動做 URL 編碼 —— 比手動拼字串安全（中文、空格都不會出錯）。
#         r.raise_for_status() # 讓 4xx/5xx 變成異常，這樣才進得了 except
#         return r.json()

async def _get_json(url: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}
    ) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

class WeatherInput(BaseModel):
    city: str = Field(min_length=1, description="城市名稱，例如 Tokyo / 東京 / Hong Kong")


async def get_weather(inp: WeatherInput) -> str:
    geo = await _get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": inp.city, "count": 1, "language": "zh"},
    )
    results = geo.get("results") or []
    if not results:
        return f"找不到城市：{inp.city}"

    loc = results[0]
    fc = await _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        },
    )
    cur = fc["current"]
    return (
        f"{loc['name']}({loc.get('country', '')})現在："
        f"氣溫 {cur['temperature_2m']}°C、"
        f"濕度 {cur['relative_humidity_2m']}%、"
        f"風速 {cur['wind_speed_10m']} km/h"
    )


class FxInput(BaseModel):
    base: str = Field(default="USD", description="來源幣別，例如 USD / CNY / HKD")
    quote: str = Field(default="CNY", description="目標幣別，例如 CNY / HKD / JPY")


async def get_exchange_rate(inp: FxInput) -> str:
    data = await _get_json(
        "https://api.frankfurter.dev/v1/latest",
        {"base": inp.base.upper(), "symbols": inp.quote.upper()},
    )
    rate = data["rates"].get(inp.quote.upper())
    if rate is None:
        return f"不支援的幣別組合：{inp.base} → {inp.quote}"
    return f"1 {inp.base.upper()} = {rate} {inp.quote.upper()}（資料日 {data['date']}）"


class SearchInput(BaseModel):
    query: str = Field(min_length=1, description="搜尋關鍵字")


async def web_search(inp: SearchInput) -> str:
    data = await _get_json(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": inp.query,
            "srlimit": 3,
            "format": "json",
            "utf8": 1,
        },
    )
    hits = data["query"]["search"]
    if not hits:
        return f"找不到與「{inp.query}」相關的結果。"
    lines = []
    for h in hits:
        snippet = h["snippet"].replace('<span class="searchmatch">', "").replace("</span>", "")
        lines.append(f"- {h['title']}：{snippet}")
    return "\n".join(lines)


WEB_TOOLS = [
    Tool("get_weather", "查詢某個城市目前的天氣（氣溫、濕度、風速）。", WeatherInput, get_weather),
    Tool("get_exchange_rate", "查詢兩種貨幣之間的即時匯率。", FxInput, get_exchange_rate),
    Tool("web_search", "搜尋維基百科，取得某個主題的摘要資訊。", SearchInput, web_search),
]
