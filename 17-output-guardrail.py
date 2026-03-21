from agents import (
    Agent,
    output_guardrail,
    RunContextWrapper,
    GuardrailFunctionOutput,
    TResponseInputItem,
    Runner,
    OutputGuardrailTripwireTriggered,
)
from operator import is_
from pydantic import BaseModel
import asyncio


class SpoilerOutput(BaseModel):
    is_spoiler: bool  # tripwrireを発動させるかどうか
    reasoning: str  # 判断の根拠


spoiler_guardrail_agent = Agent(
    name="spoiler_guardrail_agent",
    instructions="アシスタントの回答が「ヴィンランド・サガ」の勝敗や生死に関するネタバレを含むかを判断してください。",
    model="gpt-4.1-mini",
    output_type=SpoilerOutput,
)


@output_guardrail
async def spoiler_guardrail(
    context: RunContextWrapper, agent: Agent, assistant_output: str
) -> GuardrailFunctionOutput:
    input: list[TResponseInputItem] = [
        {"content": assistant_output, "role": "assistant"}
    ]
    result = await Runner.run(spoiler_guardrail_agent, input=input)
    output = result.final_output_as(SpoilerOutput)

    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=output.is_spoiler,
    )


agent = Agent(
    name="main_agent",
    instructions="あなたは「ヴィンランド・サガ」が大好きなアシスタントです。ヴィンランド・サガに関するユーザーの質問にオタクの早口の勢いで圧倒的な知識を持って答えてください。",
    model="gpt-4.1",
    output_guardrails=[spoiler_guardrail],
)


async def main():
    msg = input("こんにちは！ヴィンランド・サガに関する質問をどうぞ！： ")
    msg = msg.encode("utf-8", errors="ignore").decode("utf-8")
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        try:
            result = await Runner.run(agent, input=inputs)
            message = result.final_output
            print(f"アシスタント: {message}")
            inputs = result.to_input_list()
        except OutputGuardrailTripwireTriggered:
            message = "申し訳ありませんが、回答にネタバレが含まれるようです。"
            print(message)
            inputs.append({"content": message, "role": "assistant"})
        print("\n")

        try:
            msg = input("あなた: ")
            msg = msg.encode("utf-8", errors="ignore").decode("utf-8")
            inputs.append({"content": msg, "role": "user"})
        except EOFError, KeyboardInterrupt:
            print()
            break


if __name__ == "__main__":
    asyncio.run(main())
