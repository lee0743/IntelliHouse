#!/usr/bin/env python3
"""
IntelliHouse Vault Agent
Usage: python scripts/main.py "<task description>"
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

import anthropic
from agents.orchestrator import run


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/main.py \"<task>\"")
        print('Example: python scripts/main.py "20 - Notes/ 폴더의 노트 내용을 보완하고 구조를 정리해줘"')
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Add it to .env file or export it in your shell.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n{'='*60}")
    print(f" IntelliHouse Vault Agent")
    print(f"{'='*60}")
    print(f" Task: {task}")
    print(f"{'='*60}\n")

    report = run(client, task)

    print(f"\n{'='*60}")
    print(f" Final Report")
    print(f"{'='*60}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
