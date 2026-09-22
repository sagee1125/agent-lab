from agent_lab.llm import MODEL, client
from agent_lab.tools import get_schemas
from agent_lab.tools.executor import execute_tool

SYSTEM_PROMPT = (
    "你是一個助理。需要即時資訊或操作時，請使用提供的工具，不要憑空猜測。"
    "如果工具回報錯誤，請根據錯誤訊息修正參數或改用其他工具，不要重複同樣的錯誤呼叫。"
)


async def run_agent(user_text: str, max_steps: int = 5) -> str:
    messages: list = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    for _ in range(max_steps):
        resp = await client.chat.completions.create(
            model=MODEL, messages=messages, tools=get_schemas()
        )
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content or ""

        for call in msg.tool_calls:
            result = await execute_tool(call.function.name, call.function.arguments)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result.content}
            )

    return "（已達最大步數，未完成）"
