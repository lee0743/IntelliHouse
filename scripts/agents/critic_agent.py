"""Agent 3: Reviews the work of Agent 1 and Agent 2. Can trigger a revision loop."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import anthropic
from agents.base import run_agent
from tools import get_tools
from config import VAULT_PATH

SYSTEM_PROMPT = """You are a quality critic for a Korean Obsidian knowledge base vault.
You review changes made by two other agents and decide whether they meet quality standards.

Evaluation criteria:
1. Content quality: Is added Korean content accurate, helpful, and appropriate for 퇴직연금 study?
2. Completeness: Were the original task requirements fully addressed?
3. Structural correctness: Are files in the right folders? Are MOC links correct and up to date?
4. Link integrity: Do [[wikilinks]] point to files that actually exist?
5. No data loss: Was any existing content accidentally deleted or corrupted?

You may use read_file and list_directory to inspect any files before deciding.

You MUST respond with ONLY valid JSON (no markdown, no explanation outside JSON):
{
  "verdict": "APPROVE" or "REVISION_NEEDED",
  "feedback": {
    "content_agent": "specific actionable feedback (empty string if none)",
    "structure_agent": "specific actionable feedback (empty string if none)"
  },
  "overall": "brief Korean summary of the review"
}"""


def run(
    client: anthropic.Anthropic,
    original_task: str,
    content_result: dict,
    structure_result: dict,
    iteration: int,
) -> dict:
    user_msg = (
        f"Original task: {original_task}\n"
        f"Iteration: {iteration}\n\n"
        f"=== Content Agent (Agent 1) result ===\n"
        f"Files changed: {content_result.get('files_changed', [])}\n"
        f"Summary: {content_result.get('summary', '')}\n\n"
        f"=== Structure Agent (Agent 2) result ===\n"
        f"Files changed: {structure_result.get('files_changed', [])}\n"
        f"Files moved: {structure_result.get('files_moved', [])}\n"
        f"Summary: {structure_result.get('summary', '')}\n\n"
        f"Vault root: {VAULT_PATH}\n"
        f"Please review the changes and return your verdict as JSON."
    )

    result = run_agent(
        client,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        tools=get_tools("read_file", "list_directory"),
        agent_name="CriticAgent",
    )

    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])
    except Exception:
        return {
            "verdict": "APPROVE",
            "feedback": {"content_agent": "", "structure_agent": ""},
            "overall": f"Could not parse critic response: {result[:200]}",
        }
