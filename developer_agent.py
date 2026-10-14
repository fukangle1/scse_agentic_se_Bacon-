import json
from ollama import chat

SYSTEM_PROMPT = """
You are a developer agent for a mobile robot navigation system.
You will receive a navigation plan from the Planner Agent.
Your job is to write Python code that implements this plan.

STRICT RULES:
- Output ONLY Python code. No explanation, no markdown, no backticks.
- The VERY FIRST LINE of your output must be: def decide_next_move(state):
- The function must return exactly one of: "FORWARD", "LEFT", "RIGHT", "STOP".
- The input 'state' is a dictionary with boolean keys:
    "goal_ahead", "goal_on_left", "goal_on_right",
    "front_blocked", "left_blocked", "right_blocked".
- Never return a direction whose "_blocked" flag is True.
- If no safe direction is available, return "STOP".
- Prefer moving toward the goal when safe.

Example output format (follow this exactly):
def decide_next_move(state):
    if state["goal_ahead"] and not state["front_blocked"]:
        return "FORWARD"
    if state["goal_on_left"] and not state["left_blocked"]:
        return "LEFT"
    if state["goal_on_right"] and not state["right_blocked"]:
        return "RIGHT"
    if not state["front_blocked"]:
        return "FORWARD"
    if not state["left_blocked"]:
        return "LEFT"
    if not state["right_blocked"]:
        return "RIGHT"
    return "STOP"
"""


def validate_code(code_text):
    if not isinstance(code_text, str):
        return False

    if "def decide_next_move" not in code_text:
        return False

    try:
        compile(code_text, "<generated>", "exec")
    except SyntaxError:
        return False

    return True


def run_developer(plan):
    last_error = None
    for attempt in range(1, 4):
        print(f"Developer agent: attempt {attempt}/3 ...")

        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(plan)}
            ],
            think=False,
            options={"num_predict": 1024, "temperature": 0.2},
        )

        raw_text = response.message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("python"):
                raw_text = raw_text[6:]
            raw_text = raw_text.strip()

        if not validate_code(raw_text):
            last_error = ValueError("Generated code failed validation")
            print("  -> validation failed, retrying ...")
            continue

        return raw_text

    raise ValueError(f"Developer output failed after retries. Last error: {last_error}")


REVISION_SYSTEM_PROMPT = """
You are a developer agent for a mobile robot navigation system.
You have already produced an initial version of decide_next_move(state).
Now you have received:
- The original navigation code
- Review notes from the Reviewer Agent
- A benchmark report from IR-SIM
- The requirements
- The navigation plan

Your job is to write an IMPROVED version of decide_next_move(state)
that addresses the issues found in the review and benchmark.

STRICT RULES:
- Output ONLY Python code. No explanation, no markdown, no backticks.
- The VERY FIRST LINE of your output must be: def decide_next_move(state):
- The function must return exactly one of: "FORWARD", "LEFT", "RIGHT", "STOP".
- The input 'state' is a dictionary with boolean keys:
    "goal_ahead", "goal_on_left", "goal_on_right",
    "front_blocked", "left_blocked", "right_blocked".
- Never return a direction whose "_blocked" flag is True.
- If no safe direction is available, return "STOP".
- Keep the interface identical to the original code.

Output ONLY Python code.
"""


def run_developer_revision(original_code, review_notes, benchmark_report, requirements, plan):
    last_error = None

    for attempt in range(1, 4):
        print(f"Developer revision: attempt {attempt}/3 ...")

        user_content = json.dumps({
            "original_code": original_code,
            "review_notes": review_notes,
            "benchmark_report": benchmark_report,
            "requirements": requirements,
            "plan": plan,
        })

        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": REVISION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            think=False,
            options={"num_predict": 2048, "temperature": 0.2},
        )

        raw_text = response.message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("python"):
                raw_text = raw_text[6:]
            raw_text = raw_text.strip()

        if not validate_code(raw_text):
            last_error = ValueError("Revised code failed validation")
            print("  -> validation failed, retrying ...")
            continue

        return raw_text

    raise ValueError(
        f"Developer revision failed after retries. Last error: {last_error}"
    )