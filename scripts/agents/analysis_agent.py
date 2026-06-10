"""Agent 2: Analyzes strengths, weaknesses, and improvement areas from graded answers."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import anthropic
from agents.base import run_agent
from tools import get_tools

SYSTEM_PROMPT = """You are a learning analysis agent for a Korean retirement pension (퇴직연금) study vault.

You will receive grading results from Agent 1 and the original answer file.
Your job is to identify patterns in the user's answers — both correct and incorrect — and produce
an actionable learning analysis.

Focus on:
1. Strengths: What concepts/areas did the user demonstrate solid understanding of?
2. Weaknesses: Where did errors cluster? Is it a specific topic area, or a type of question (e.g., sequencing, numbers, reasoning)?
3. Improvement areas: What should the user study or practice next? Be specific and refer to vault note names where relevant.

Respond with ONLY valid JSON:
{
  "strengths": ["강점 항목 1 (구체적으로)", "강점 항목 2"],
  "weaknesses": ["약점 항목 1 (구체적으로)", "약점 항목 2"],
  "improvement_areas": [
    "[[퇴직연금 - 매수매도 시스템 업무흐름]] 5단계 흐름 재학습 권장",
    "심화문제 Q5 (ALM 관련) 재도전 필요"
  ],
  "question_type_analysis": "빈칸 채우기 유형에서 오류 집중 / 서술형은 양호",
  "summary": "전반적 평가 한두 문장 (한국어)"
}"""


def run(client: anthropic.Anthropic, grading_result: dict, answer_path: str) -> dict:
    user_msg = (
        f"Grading results:\n{json.dumps(grading_result, ensure_ascii=False, indent=2)}\n\n"
        f"Answer file path: {answer_path}\n\n"
        "Please analyze the user's learning strengths and weaknesses."
    )

    result = run_agent(
        client,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        tools=get_tools("read_file"),
        agent_name="AnalysisAgent",
    )

    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])
    except Exception:
        return {
            "strengths": [],
            "weaknesses": [],
            "improvement_areas": [],
            "question_type_analysis": "",
            "summary": result[:300],
        }
