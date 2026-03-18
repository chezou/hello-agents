import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, TResponseInputItem, Runner, trace, RawResponsesStreamEvent
import uuid

thors_agent = Agent(
    name="thors_agent",
    instructions="あなたはヴィンランド・サガのトールズ・エリクソンです。ヴィンランド・サガの世界観を踏まえた上で、質問に答えてください。",
)

thorfinn_agent = Agent(
    name="thorfinn_agent",
    instructions="あなたはヴィンランド・サガのトルフィン・エリクソンです。ヴィンランド・サガの世界観を踏まえた上で、質問に答えてください。",
)

thorkell_agent = Agent(
    name="thorkell_agent",
    instructions="あなたはヴィンランド・サガのトルケル・ハールダールです。ヴィンランド・サガの世界観を踏まえた上で、質問に答えてください。",
)

triage_instructions="""
ユーザーがどのキャラクターとしいて話したいかに基づいて、適切なエージェントに引き継ぐこと。
自分で回答せずに必ずいずれかのエージェントに引き継いでください。
なお、キャラクター同士の比較も想定されるため、その場合はエージェントへの引継ぎを行わずに、ユーザーの質問に対してその時点でのキャラクターの視点で回答してください。
"""
triage_agent=Agent(
    name="triage_agent",
    instructions=triage_instructions,
    handoffs=[thors_agent, thorfinn_agent, thorkell_agent],
)


async def main():
    conversation_id = str(uuid.uuid7().hex[:16])

    msg = input("こんにちは！ヴィンランド・サガの世界へようこそ。どのキャラクターと話したいですか？（トールズ、トルフィン、トルケル）\n>> ")
    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        with trace("Handoffs", group_id=conversation_id):
            result = Runner.run_streamed(
                agent,
                input=inputs,
            )
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        text = event.data.delta.encode('utf-8', errors='replace').decode('utf-8')
                        print(text, end="", flush=True)
                else:
                    pass
        
        inputs = result.to_input_list()
        print("\n")
        print(f"[current_agent: {result.current_agent.name}]")

        try:
            msg = input("あなた: ")
            inputs.append({"content": msg, "role": "user"})
            # agent = result.current_agent
        except (EOFError, KeyboardInterrupt):
            print()
            break

if __name__ == "__main__":
    asyncio.run(main())