import asyncio
import uuid
from dataclasses import dataclass
from agents import Agent, trace, Runner, TResponseInputItem

instructions = """
あなたはエッセイライターです。与えられたテーマについてのエッセイを書いてください。
マークアップ言語は使わずプレーンテキストで書くこと。
もし、フィードバックが与えられたら、フィードバックを反映してエッセイを改善してください。
"""

writer_agent = Agent(
    name="writer_agent",
    model="gpt-4.1",
    instructions=instructions,
)


@dataclass
class EvalAndFeedback:
    """ジャッジエージェントのアウトプット型"""

    evaluation: int  # 1-10のスコア。評価方法は柔軟に設計してよい。
    feedback: str  # 改善のためのフィードバック


eval_instructions = """
あなたは経験豊富なエッセイの批評家です。与えられたエッセイを読み，1から10のスケールで評価してください。1が最低評価，10が最高評価です。甘い評価はせず，厳しく評価してください。
エッセイの評価ポイントは以下の通りです：
- タイトルは魅力的かつ独創的か。
- 本文は長すぎず，短すぎないか。エッセイ本文は100語から200語の範囲であるべきです。
- エッセイはテーマに沿っているか
- 文法や使われている単語は正確か。引用されている事実は正確か。
- エッセイの構成は論理的で不自然な飛躍がないか。段落のつながりはスムーズか。不自然な改行や，過剰な接続詞はないか？
- エッセイは読みやすい日本語か。くだけすぎていないか，または堅苦しすぎないか。
- エッセイは過度に抽象的または一般的ではないか。独創的な視点や洞察が含まれているか。
- エッセイは情景を思い浮かべやすく，読者の感情に訴えるか。
エッセイの評価とともに，エッセイを改善するための具体的なフィードバックも提供してください。
"""

evaluator_agent = Agent(
    name="evaluator_agent",
    model="gpt-4.1",
    instructions=eval_instructions,
    output_type=EvalAndFeedback,
)


async def main():
    conversation_id = str(uuid.uuid7().hex[:16])

    msg = input("エッセイのテーマを入力してください: ")
    msg = msg.encode("utf-8", errors="ignore").decode("utf-8")
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    with trace("LLM as a judge", group_id=conversation_id):
        writer_result = await Runner.run(
            writer_agent,
            input=inputs,
        )
        essay_content = writer_result.final_output
        print("\n=== First essay ===")
        print(essay_content)

        eval_result = await Runner.run(
            evaluator_agent, input=writer_result.to_input_list()
        )
        evaluation: EvalAndFeedback = eval_result.final_output

        turn_count = 1
        while evaluation.evaluation < 9:
            print(
                f"\n=== Feedback for improvement (turn {turn_count}): {evaluation.evaluation} ==="
            )

            inputs.append(
                {
                    "content": f"エッセイの評価は{evaluation.evaluation}点でした。改善のためのフィードバックは以下の通りです。\n{evaluation.feedback}\nこのフィードバックを反映してエッセイを改善してください。",
                    "role": "user",
                }
            )
            writer_result = await Runner.run(
                writer_agent,
                input=inputs,
            )
            essay_content = writer_result.final_output
            eval_result = await Runner.run(
                evaluator_agent, input=writer_result.to_input_list()
            )
            evaluation: EvalAndFeedback = eval_result.final_output
            turn_count += 1

        print(f"\n=== Final essay (evaluation: {evaluation.evaluation}) ===")
        print("\n=== Final essay ===")
        print(essay_content)


if __name__ == "__main__":
    asyncio.run(main())
