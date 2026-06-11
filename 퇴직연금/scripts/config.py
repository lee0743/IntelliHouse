import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

VAULT_PATH = Path(os.environ.get("VAULT_PATH", str(Path(__file__).parent.parent))).resolve()
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "3"))
IGNORE_PATHS = ["old", ".git", ".obsidian", "scripts"]
