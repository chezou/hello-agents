from openai.types.responses import ResponseTextDeltaEvent
from agents import (
    Agent,
    input_guardrail,
    RunContextWrapper,
    TResponseInputItem,
    GuardrailFunctionOutput,
    Runner,
    RawResponsesStreamEvent,
    InputGuardrailTripwireTriggered,
)
from pydantic import BaseModel
import asyncio


class SpoilerOutput(BaseModel):
    is_spoiler: bool  # tripwrireを発動させるかどうか
    reasoning: str  # 判断の根拠


spoiler_guardrail_agent = Agent(
    name="spoiler_guardrail_agent",
    instructions="ユーザーが「ヴィンランド・サガ」のネタバレを含む質問をした場合、ネタバレを避けるように警告してください。",
    model="gpt-4.1-mini",
    output_type=SpoilerOutput,
)


# Guardrail function
# run_in_parallel=Trueにすることで、エージェントの応答を待たずにGuardrail関数を実行することができる。これにより、エージェントの応答とGuardrailのチェックを同時に行うことができる。
@input_guardrail(run_in_parallel=False)
async def spoiler_guardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(spoiler_guardrail_agent, input=input, context=context)
    output = result.final_output_as(SpoilerOutput)
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_spoiler,
    )


agent = Agent(
    name="main_agent",
    instructions="あなたはヴィンランド・サガのトルフィンを演じるAIです。常にトルフィンとして振る舞うこと。",
    model="gpt-4.1",
    input_guardrails=[spoiler_guardrail],
)


async def main():
    msg = input("こんにちは！トルフィンと話しましょう。何か質問はありますか？： ")
    msg = msg.encode("utf-8", errors="ignore").decode("utf-8")
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        try:
            result = Runner.run_streamed(agent, input=inputs)
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        print(event.data.delta, end="", flush=True)
                    else:
                        pass
            inputs = result.to_input_list()
        except InputGuardrailTripwireTriggered:
            message = "申し訳ありませんが、ネタバレの質問にはお答えできません。"
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
