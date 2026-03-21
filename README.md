# hello-agents

Hands-on exercises following [@mocobeta](https://github.com/mocobeta)'s [Agents SDK+α Tips Advent Calendar 2025](https://adventar.org/calendars/12523).

## What's this?

A learning repository to explore [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) patterns — Runner, Streaming, Session, Handoffs, Guardrails, Evals, and more.

## Key topics covered

- Day 1-3: Runner, Streaming output, Session (agent memory)
- Day 12: Orchestration — Handoffs (routing pattern)
- Day 13-14: Agents as Tools, LLM as a Judge
- Day 16-17: Input/Output Guardrails

## Read-through

- Day 4-10: ChatKit UI, Files API, OpenAI Logs
- Day 19-22: Evals — AgentKit, Prompt Optimizer, Graders, Evals API

## Setup

```bash
uv sync
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

## References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [mocobeta's blog](https://blog.mocobeta.dev/tags/ai-agents/)
