import httpx
import truststore
from fastmcp import FastMCP

truststore.inject_into_ssl()

TIMEOUT = 10.0
USER_AGENT = "agent-lab/0.1 (learning project; contact: 1324300391@qq.com)"

mcp = FastMCP("agent-lab web tools")


async def _get_json(url: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}
    ) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool
async def get_weather(city: str) -> str:
    """查詢某個城市目前的天氣（氣溫、濕度、風速）。city 例如 Tokyo / 東京 / Hong Kong。"""
    try:
        geo = await _get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": city, "count": 1, "language": "zh"},
        )
        results = geo.get("results") or []
        if not results:
            return f"找不到城市：{city}"
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
    except httpx.HTTPError as e:
        return f"天氣查詢失敗（{type(e).__name__}）：{e}"


@mcp.tool
async def get_exchange_rate(base: str = "USD", quote: str = "CNY") -> str:
    """查詢兩種貨幣之間的即時匯率。base 是來源幣別，quote 是目標幣別。"""
    try:
        data = await _get_json(
            "https://api.frankfurter.dev/v1/latest",
            {"base": base.upper(), "symbols": quote.upper()},
        )
        rate = data["rates"].get(quote.upper())
        if rate is None:
            return f"不支援的幣別組合：{base} → {quote}"
        return f"1 {base.upper()} = {rate} {quote.upper()}（資料日 {data['date']}）"
    except httpx.HTTPError as e:
        return f"匯率查詢失敗（{type(e).__name__}）：{e}"


@mcp.tool
async def web_search(query: str) -> str:
    """搜尋維基百科，取得某個主題的摘要資訊。"""
    try:
        data = await _get_json(
            "https://en.wikipedia.org/w/api.php",
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "format": "json",
                "utf8": 1,
            },
        )
        hits = data["query"]["search"]
        if not hits:
            return f"找不到與「{query}」相關的結果。"
        lines = []
        for h in hits:
            snippet = (
                h["snippet"]
                .replace('<span class="searchmatch">', "")
                .replace("</span>", "")
            )
            lines.append(f"- {h['title']}：{snippet}")
        return "\n".join(lines)
    except httpx.HTTPError as e:
        return f"搜尋失敗（{type(e).__name__}）：{e}"


if __name__ == "__main__":
    mcp.run(transport="http", port=8001)
