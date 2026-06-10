"""Agent 1: Grades user answers against the quiz answer key."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import anthropic
from agents.base import run_agent
from tools import get_tools

SYSTEM_PROMPT = """You are a quiz grading agent for a Korean retirement pension (퇴직연금) study vault.

You will be given:
1. A quiz file (contains questions with hidden answers in <details> tags)
2. A user answer file (contains the user's submitted answers)

Your job:
- Read both files carefully
- For each question (Q1, Q2, ...), compare the user's answer to the correct answer
- Be fair but thorough: partial credit is allowed for partially correct answers
- Mark as correct (true) if the answer captures the key concepts, even if wording differs
- Mark as incorrect (false) if key facts are missing or wrong

Respond with ONLY valid JSON:
{
  "quiz_name": "문제지 이름",
  "score": "7/10",
  "score_numeric": 7,
  "total": 10,
  "results": [
    {
      "question": "Q1",
      "title": "문제 제목",
      "correct": true,
      "user_answer": "사용자 답안 요약",
      "correct_answer": "정답 핵심 요약",
      "feedback": "잘 했거나 틀린 이유 한 줄"
    }
  ],
  "wrong_questions": ["Q3", "Q5"]
}"""


def run(client: anthropic.Anthropic, quiz_path: str, answer_path: str) -> dict:
    user_msg = (
        f"Quiz file: {quiz_path}\n"
        f"Answer file: {answer_path}\n\n"
        "Please read both files and grade the answers."
    )

    result = run_agent(
        client,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        tools=get_tools("read_file"),
        agent_name="GradingAgent",
    )

    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])
    except Exception:
        return {"score": "?", "score_numeric": 0, "total": 0, "results": [], "wrong_questions": [], "raw": result}
