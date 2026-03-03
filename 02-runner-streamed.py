import asyncio
from agents import (
    Agent,
    run_demo_loop,
    function_tool,
    Runner,
    RunResultStreaming,
    TResponseInputItem,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    AgentUpdatedStreamEvent,
)
from openai.types.responses import ResponseTextDeltaEvent
import subprocess


@function_tool
def run_man_command(command: str) -> str:
    """Run a man command and return the output."""
    if subprocess.run(["which", command], capture_output=True).returncode == 1:
        return f"Command '{command}' not found."
    result = subprocess.run(["man", command], capture_output=True)
    if not result.stdout:
        return f"No manual entry for '{command}'."
    return result.stdout.decode("utf-8", errors="replace")


INSTRUCTIONS = """
あなたはLinuxコマンドラインインターフェースの専門家です。Linuxコマンドの使い方を教えることができます。
ユーザーからLinuxコマンドの使い方について質問されたら、`run_man_command`ツールを使ってmanページを参照し、適切な回答を提供してください。

以下の制約条件を守ってください：
- 回答は日本語で行ってください。
- コマンド例を示してください。
- markdown形式ではなく、プレーンテキストで回答してください。
- 回答は簡潔にまとめてください。
- ツールの用途外のことを聞かれた場合は答えないでください。
"""


async def main() -> None:
    agent = Agent(
        name="LinuxCommandHelper",
        instructions=INSTRUCTIONS,
        model="gpt-5-nano",
        tools=[run_man_command],
    )
    try:
        user_input = input(">> Linuxコマンドについて質問してください\n")
    except EOFError, KeyboardInterrupt:
        print()
        return

    input_items: list[TResponseInputItem] = [{"role": "user", "content": user_input}]

    result: RunResultStreaming = Runner.run_streamed(agent, input=input_items)
    async for event in result.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            if isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
        elif isinstance(event, RunItemStreamEvent):
            if event.item.type == "tool_call_item":
                print(f"\n[ツール呼び出し: {event.item.raw_item.name}]", flush=True)
            elif event.item.type == "tool_call_output_item":
                print("\n[ツール出力を受け取りました]", flush=True)
            else:
                pass
        elif isinstance(event, AgentUpdatedStreamEvent):
            print(
                f"\n[エージェントが更新されました] {event.new_agent.name}", flush=True
            )

    print()


if __name__ == "__main__":
    asyncio.run(main())
