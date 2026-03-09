import asyncio
from agents import Agent, Runner, RunResult, SQLiteSession


async def main() -> None:
    agent = Agent(
        name="My Agent",
        instructions="日本語で簡潔におちゃめに答えてください。",
        model="gpt-5-nano",
    )
    session = SQLiteSession(session_id="conversation-1", db_path="agent_memory.db")

    while True:
        try:
            user_input = input(">> ")
            user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input.strip():
            continue

        result: RunResult = await Runner.run(agent, input=user_input, session=session)
        if result.final_output:
            print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
