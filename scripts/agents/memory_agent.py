"""Agent 3: Persists analysis conclusions to the learning profile note for future personalization."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import anthropic
from agents.base import run_agent
from tools import get_tools

PROFILE_PATH = "40 - Resources/학습 프로파일.md"

SYSTEM_PROMPT = f"""You are a learning memory agent for a Korean retirement pension study vault.

You manage the user's cumulative learning profile at: {PROFILE_PATH}

Your job:
1. Read the current profile file
2. Update it with the new session's data:
   - Add a new entry under "## 세션 기록" with date, quiz name, score, and key notes
   - Update "## 현재 강점" to reflect the latest strengths (merge with existing, remove outdated items)
   - Update "## 현재 약점" similarly
   - Update "## 다음 출제 시 집중 영역" with the most actionable improvement areas
3. Write the updated file back

Keep the profile concise. The "다음 출제 시 집중 영역" section should contain at most 5 items,
prioritizing the most recent and most persistent weaknesses.

After writing, respond with: {{"status": "saved", "profile_path": "{PROFILE_PATH}"}}"""


def run(
    client: anthropic.Anthropic,
    grading_result: dict,
    analysis_result: dict,
    session_date: str,
    quiz_name: str,
) -> dict:
    user_msg = (
        f"Session date: {session_date}\n"
        f"Quiz: {quiz_name}\n"
        f"Score: {grading_result.get('score', '?')}\n\n"
        f"Analysis:\n{json.dumps(analysis_result, ensure_ascii=False, indent=2)}\n\n"
        f"Wrong questions: {grading_result.get('wrong_questions', [])}\n\n"
        f"Please update the learning profile at {PROFILE_PATH}."
    )

    result = run_agent(
        client,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        tools=get_tools("read_file", "write_file"),
        agent_name="MemoryAgent",
    )

    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])
    except Exception:
        return {"status": "saved", "profile_path": PROFILE_PATH}
