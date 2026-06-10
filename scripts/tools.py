import shutil
from pathlib import Path
from config import VAULT_PATH, IGNORE_PATHS


def _safe_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = VAULT_PATH / path
    path = path.resolve()
    if not str(path).startswith(str(VAULT_PATH)):
        raise ValueError(f"Path outside vault: {path}")
    rel = path.relative_to(VAULT_PATH)
    for ignore in IGNORE_PATHS:
        if str(rel) == ignore or str(rel).startswith(ignore + "/"):
            raise ValueError(f"Path is in restricted directory: {rel}")
    return path


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "read_file":
            return read_file(**tool_input)
        elif tool_name == "write_file":
            return write_file(**tool_input)
        elif tool_name == "list_directory":
            return list_directory(**tool_input)
        elif tool_name == "move_file":
            return move_file(**tool_input)
        elif tool_name == "create_directory":
            return create_directory(**tool_input)
        return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Error: {e}"


def read_file(path: str) -> str:
    return _safe_path(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written: {path}"


def list_directory(path: str = "") -> str:
    base = _safe_path(path) if path else VAULT_PATH
    if not base.is_dir():
        return f"Not a directory: {path}"
    items = []
    for item in sorted(base.iterdir()):
        rel = item.relative_to(VAULT_PATH)
        if any(str(rel) == ig or str(rel).startswith(ig + "/") for ig in IGNORE_PATHS):
            continue
        prefix = "[DIR] " if item.is_dir() else "[FILE]"
        items.append(f"{prefix} {rel}")
    return "\n".join(items) if items else "(empty)"


def move_file(src: str, dst: str) -> str:
    s = _safe_path(src)
    d = _safe_path(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))
    return f"Moved: {src} → {dst}"


def create_directory(path: str) -> str:
    _safe_path(path).mkdir(parents=True, exist_ok=True)
    return f"Created: {path}"


TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the full contents of a file in the vault.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to vault root or absolute"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file (creates parent dirs if needed).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string", "description": "Full file content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and subdirectories in a vault directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (empty = vault root)"}
            },
            "required": [],
        },
    },
    {
        "name": "move_file",
        "description": "Move or rename a file within the vault.",
        "input_schema": {
            "type": "object",
            "properties": {
                "src": {"type": "string", "description": "Source path"},
                "dst": {"type": "string", "description": "Destination path"},
            },
            "required": ["src", "dst"],
        },
    },
    {
        "name": "create_directory",
        "description": "Create a directory (and parents) in the vault.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"],
        },
    },
]

TOOL_MAP = {t["name"]: t for t in TOOL_DEFINITIONS}


def get_tools(*names: str) -> list:
    return [TOOL_MAP[n] for n in names if n in TOOL_MAP]
