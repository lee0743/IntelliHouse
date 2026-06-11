"""Agent 1: Improves the content of notes in the vault."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import anthropic
from agents.base import run_agent
from tools import get_tools
from config import VAULT_PATH

SYSTEM_PROMPT = """You are a content improvement agent for a Korean Obsidian knowledge base vault.
This vault root is the "퇴직연금/" folder containing retirement pension study notes.

Your responsibilities:
- Browse notes in the vault (primarily in "Notes/")
- Fill in empty or incomplete sections: empty "My Thoughts", thin "Key Points", missing "References"
- Add [[wikilinks]] to connect related notes where relevant
- Improve clarity and add helpful context where content is sparse
- NEVER delete or overwrite existing meaningful content
- NEVER modify files outside "Notes/", "Topics/", "Resources/"
- Write all content in Korean (한국어)

When you finish, respond with ONLY valid JSON:
{
  "files_changed": ["relative/path1.md", "relative/path2.md"],
  "summary": "Korean description of what was changed and why"
}

If given critic feedback, address it specifically before finalizing."""


def run(client: anthropic.Anthropic, task: str, critic_feedback: str = "") -> dict:
    user_msg = f"Task: {task}"
    if critic_feedback:
        user_msg += f"\n\nCritic feedback to address:\n{critic_feedback}"
    user_msg += f"\n\nVault root: {VAULT_PATH}"

    result = run_agent(
        client,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        tools=get_tools("read_file", "write_file", "list_directory"),
        agent_name="ContentAgent",
    )

    try:
        import json
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])
    except Exception:
        return {"files_changed": [], "summary": result}
