import asyncio
from agents import Agent, run_demo_loop, function_tool
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
    await run_demo_loop(agent, stream=True)

if __name__ == "__main__":
    asyncio.run(main())
