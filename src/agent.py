"""A transparent ReAct loop: Thought -> Action -> Observation, repeated until done.

The loop is implemented explicitly (no agent framework magic) so every step of the
reasoning is visible, debuggable, and easy to explain in an interview.
"""
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import settings
from .tools import build_tools

REACT_SYSTEM = """You are InsightAgent, a research agent that reasons step by step and uses tools.

Available tools:
{tool_descriptions}

Every turn, respond in EXACTLY one of these two formats:

Thought: <your reasoning about what to do next>
Action: <one of: {tool_names}>
Action Input: <the input for the tool>

... or, when you have gathered enough information to answer, respond with:

Final Answer:
## Recommendation
<your clear recommendation>

## Key findings
<bullet points of the most important facts you found>

## Options compared
<concise comparison of the main options>

## Risks / open questions
<what is uncertain or risky>

## Sources
<list the sources behind your findings>

Rules:
- You may use at most {max_steps} tool actions. Budget them wisely.
- Prefer 2-4 web searches with different angles before summarizing.
- Never invent facts: every claim in the Final Answer must come from an observation.
- If a tool errors, acknowledge it in your Thought and try a different approach.
"""

_human_template = "Task: {task}\n\n{history}\n"


def _tool_descriptions(tools: dict) -> str:
    return "\n".join(f"- {name}: {spec['description']}" for name, spec in tools.items())


def parse_step(text: str) -> dict:
    """Parse one LLM turn into thought / action / action_input / final_answer."""
    final_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
    if final_match:
        return {"final_answer": final_match.group(1).strip()}

    thought = re.search(r"Thought:\s*(.+?)(?=\nAction:|\Z)", text, re.DOTALL)
    action = re.search(r"Action:\s*([^\n]+)", text)
    action_input = re.search(r"Action Input:\s*(.+)", text, re.DOTALL)
    return {
        "thought": thought.group(1).strip() if thought else "",
        "action": action.group(1).strip() if action else "",
        "action_input": action_input.group(1).strip() if action_input else "",
    }


class InsightAgent:
    def __init__(self, max_steps: int | None = None) -> None:
        self.max_steps = max_steps or settings.max_steps
        self.llm = ChatOpenAI(
            model=settings.chat_model,
            temperature=settings.temperature,
            api_key=settings.openai_api_key,
        )
        self.tools = build_tools(self.llm)
        system = REACT_SYSTEM.format(
            tool_descriptions=_tool_descriptions(self.tools),
            tool_names=", ".join(self.tools),
            max_steps=self.max_steps,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", system), ("human", _human_template)]
        )

    def _format_history(self, trajectory: list) -> str:
        if not trajectory:
            return "No steps taken yet."
        lines = []
        for i, step in enumerate(trajectory, 1):
            lines.append(f"Step {i}:\nThought: {step['thought']}")
            lines.append(f"Action: {step['action']}\nAction Input: {step['action_input']}")
            lines.append(f"Observation: {step['observation']}")
        return "\n".join(lines)

    def run(self, task: str) -> dict:
        """Run the ReAct loop. Returns the trajectory and the final decision brief."""
        trajectory: list = []
        for _ in range(self.max_steps):
            messages = self.prompt.format_messages(
                task=task, history=self._format_history(trajectory)
            )
            raw = self.llm.invoke(messages).content
            parsed = parse_step(raw)

            if "final_answer" in parsed:
                return {
                    "task": task,
                    "trajectory": trajectory,
                    "brief": parsed["final_answer"],
                    "steps_used": len(trajectory),
                }

            action, action_input = parsed.get("action", ""), parsed.get("action_input", "")
            if action not in self.tools:
                observation = (
                    f"Unknown tool '{action}'. Available tools: "
                    f"{', '.join(self.tools)}. Use exactly one of these names."
                )
                thought = parsed.get("thought", "")
            else:
                thought = parsed.get("thought", "")
                try:
                    observation = str(self.tools[action]["run"](action_input))
                except Exception as exc:
                    observation = f"Tool '{action}' raised an error: {exc}"

            trajectory.append(
                {
                    "thought": thought,
                    "action": action,
                    "action_input": action_input,
                    "observation": observation,
                }
            )

        return {
            "task": task,
            "trajectory": trajectory,
            "brief": (
                "Stopped after reaching the maximum number of steps without a final "
                "answer. Review the trajectory above and re-run with a narrower task "
                "or a higher --max-steps value."
            ),
            "steps_used": len(trajectory),
        }
