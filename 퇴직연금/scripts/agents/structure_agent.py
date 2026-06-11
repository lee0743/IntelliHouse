"""Agent 2: Improves the folder and file structure of the vault."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import anthropic
from agents.base import run_agent
from tools import get_tools
from config import VAULT_PATH

SYSTEM_PROMPT = """You are a vault structure improvement agent for a Korean Obsidian knowledge base.

This vault root is the "퇴직연금/" folder. Folder conventions:
- "Home/"       → dashboard and top-level MOC
- "Inbox/"      → unprocessed fleeting notes and quiz answers (quick captures)
- "Notes/"      → permanent notes (one concept per file)
- "Topics/"     → MOC file for this subject
- "Resources/"  → source notes, learning profile, references
- "Templates/"  → note and MOC templates
- "scripts/"    → automation scripts (do not modify)

Your responsibilities:
- Ensure MOC files in "Topics/" link to all relevant notes in "Notes/"
- Move misplaced files to their correct folder (a MOC file in Notes/, etc.)
- Update "Home/🏠 Home.md" to reflect the current notes
- Ensure consistent Korean naming conventions for note files
- When moving a file, update ALL [[wikilinks]] that reference it across the vault
- NEVER touch ".git/", ".obsidian/", "scripts/"
- NEVER delete files — only move or create

When you finish, respond with ONLY valid JSON:
{
  "files_changed": ["path1", "path2"],
  "files_moved": [{"from": "src", "to": "dst"}],
  "summary": "Korean description of structural changes"
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
        tools=get_tools("read_file", "write_file", "list_directory", "move_file", "create_directory"),
        agent_name="StructureAgent",
    )

    try:
        import json
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])
    except Exception:
        return {"files_changed": [], "files_moved": [], "summary": result}
