import asyncio
from openai.types.responses import ResponseTextDeltaEvent
import uuid
from agents.items import T
from agents import (
    Agent,
    TResponseInputItem,
    trace,
    Runner,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    ToolCallItem,
    AgentUpdatedStreamEvent,
)

thors_agent = Agent(
    name="thors_agent",
    instructions="あなたはヴィンランド・サガのトールズ・エリクソンです。ヴィンランド・サガの世界観を踏まえた上で、振る舞ってください。",
)

thorfinn_agent = Agent(
    name="thorfinn_agent",
    instructions="あなたはヴィンランド・サガのトルフィン・エリクソンです。ヴィンランド・サガの世界観を踏まえた上で、振る舞ってください。",
)

thorkell_agent = Agent(
    name="thorkell_agent",
    instructions="あなたはヴィンランド・サガのトルケル・ハールダールです。ヴィンランド・サガの世界観を踏まえた上で、振る舞ってください。",
)

instructions = """
各ツールはそれぞれ特定のキャラクターとして振る舞うエージェントである。
ユーザーがどのキャラクターとして話したいかに基づいて、適切なツールを選択すること。
自分で回答せずに必ず一つ以上のツールを使うこと。
複数のツールを使う場合は、各ツールの回答を組み合わせずに、順番に出力すること。
"""

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=instructions,
    tools=[
        thors_agent.as_tool(
            tool_name="thors_tool",
            tool_description="ユーザーがトールズと話したいときに使用する",
        ),
        thorfinn_agent.as_tool(
            tool_name="thorfinn_tool",
            tool_description="ユーザーがトルフィンと話したいときに使用する",
        ),
        thorkell_agent.as_tool(
            tool_name="thorkell_tool",
            tool_description="ユーザーがトルケルと話したいときに使用する",
        ),
    ],
)


async def main():
    conversation_id = str(uuid.uuid7().hex[:16])
    msg = input(
        "こんにちは！ヴィンランド・サガの世界へようこそ。どのキャラクターと話したいですか？（トールズ、トルフィン、トルケル）\n>> "
    )
    agent = orchestrator_agent
    inputs: list[TResponseInputItem] = [{"content": msg.encode("utf-8", errors="ignore").decode("utf-8"), "role": "user"}]

    while True:
        with trace("Agent as tools", group_id=conversation_id):
            result = Runner.run_streamed(
                agent,
                input=inputs,
            )
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        print(event.data.delta, end="", flush=True)
                elif isinstance(event, RunItemStreamEvent):
                    if isinstance(event.item, ToolCallItem):
                        print(f"\n[Tool called: {event.item.raw_item}]\n")
                elif isinstance(event, AgentUpdatedStreamEvent):
                    pass

        inputs = result.to_input_list()
        print("\n")
        print(f"[current_agent: {result.current_agent.name}]")

        try:
            user_msg = input("あなた: ")
            user_msg = user_msg.encode("utf-8", errors="ignore").decode("utf-8")
            inputs.append({"content": user_msg, "role": "user"})
        except EOFError, KeyboardInterrupt:
            print()
            break


if __name__ == "__main__":
    asyncio.run(main())
