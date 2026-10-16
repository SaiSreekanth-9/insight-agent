"""InsightAgent CLI.

Usage:
    python main.py research "Should a seed-stage SaaS startup choose PostgreSQL or MongoDB?"
    python main.py research "Is LangGraph or CrewAI better for multi-agent workflows?" --max-steps 10
"""
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from src.agent import InsightAgent
from src.config import validate


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "research"


def save_report(task: str, result: dict) -> str:
    out_dir = Path("examples")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"report-{slugify(task)}.md"
    lines = [
        f"# InsightAgent report",
        f"_Task: {task}_",
        f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}, "
        f"{result['steps_used']} steps_\n",
        "## Reasoning trajectory\n",
    ]
    for i, step in enumerate(result["trajectory"], 1):
        lines.append(f"### Step {i}")
        lines.append(f"**Thought:** {step['thought']}")
        lines.append(f"**Action:** `{step['action']}`")
        lines.append(f"**Action Input:** {step['action_input']}")
        lines.append(f"**Observation:** {step['observation'][:1200]}\n")
    lines.append("## Decision brief\n")
    lines.append(result["brief"])
    path.write_text("\n".join(lines), encoding="utf8")
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="InsightAgent research CLI")
    parser.add_argument("command", choices=["research"])
    parser.add_argument("task", help="Research question or decision to investigate")
    parser.add_argument("--max-steps", type=int, default=None)
    args = parser.parse_args()

    validate()
    agent = InsightAgent(max_steps=args.max_steps)
    print(f"Researching: {args.task}\n")
    result = agent.run(args.task)

    for i, step in enumerate(result["trajectory"], 1):
        print(f"--- Step {i} ---")
        print(f"Thought: {step['thought']}")
        print(f"Action: {step['action']}({step['action_input'][:100]})")
        print(f"Observation: {step['observation'][:300]}...\n")

    print("=" * 60)
    print(result["brief"])
    print("=" * 60)
    print(f"\nFull report saved to {save_report(args.task, result)}")


if __name__ == "__main__":
    main()
