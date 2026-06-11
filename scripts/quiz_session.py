#!/usr/bin/env python3
"""
IntelliHouse Quiz Session
Usage:
  python scripts/quiz_session.py --template "기본"
  python scripts/quiz_session.py --grade "10 - Inbox/퇴직연금 답안 (기본) 2026-06-10.md"
  python scripts/quiz_session.py --grade "..." --save-memory
"""
import sys
import os
import re
import json
import argparse
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from config import VAULT_PATH

# Quiz name → file path mapping
QUIZ_FILES = {
    "기본": "퇴직연금/Notes/퇴직연금 - 점검문제 (기본).md",
    "심화": "퇴직연금/Notes/퇴직연금 - 점검문제 (심화).md",
    "jsp-기본": "JSP/Notes/JSP - 점검문제 (기본).md",
    "jsp-심화": "JSP/Notes/JSP - 점검문제 (심화).md",
}


def generate_template(quiz_name: str) -> Path:
    """Generate an answer template from a quiz file (no API call)."""
    if quiz_name not in QUIZ_FILES:
        print(f"Error: unknown quiz '{quiz_name}'. Available: {list(QUIZ_FILES.keys())}")
        sys.exit(1)

    quiz_path = VAULT_PATH / QUIZ_FILES[quiz_name]
    if not quiz_path.exists():
        print(f"Error: quiz file not found: {quiz_path}")
        sys.exit(1)

    content = quiz_path.read_text(encoding="utf-8")

    # Remove <details>...</details> blocks (answer keys)
    content = re.sub(r"<details>.*?</details>", "", content, flags=re.DOTALL)

    # After each ### Q{n}. heading + question body, insert blank answer field
    content = re.sub(
        r"(### Q\d+\..+?)(\n---|\Z)",
        lambda m: m.group(1) + "\n\n**내 답안:** \n\n---",
        content,
        flags=re.DOTALL,
    )

    # Replace front-matter title and add submission date
    today = date.today().isoformat()
    header = (
        f"---\n"
        f"tags: 퇴직연금, 답안, {quiz_name}\n"
        f"date: {today}\n"
        f"quiz: [[퇴직연금 - 점검문제 ({quiz_name})]]\n"
        f"---\n\n"
        f"# 퇴직연금 답안 ({quiz_name}) {today}\n\n"
        f"> 문제지: [[퇴직연금 - 점검문제 ({quiz_name})]]\n\n---\n\n"
    )

    # Strip original front-matter and title
    body = re.sub(r"^---.*?---\n+#[^\n]+\n+", "", content, flags=re.DOTALL)
    # Remove top-level links block
    body = re.sub(r"^>.*?\n\n", "", body, flags=re.DOTALL)

    output = header + body.strip() + "\n"
    out_path = VAULT_PATH / "10 - Inbox" / f"퇴직연금 답안 ({quiz_name}) {today}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    return out_path


def run_grading_session(answer_path_str: str, save_memory: bool) -> None:
    import anthropic
    from agents.grading_agent import run as grade
    from agents.analysis_agent import run as analyze

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set. Add to .env or export in shell.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Resolve answer file
    answer_path = Path(answer_path_str)
    if not answer_path.is_absolute():
        answer_path = VAULT_PATH / answer_path
    if not answer_path.exists():
        print(f"Error: answer file not found: {answer_path}")
        sys.exit(1)

    # Detect quiz name and find quiz file from answer file front-matter
    content = answer_path.read_text(encoding="utf-8")
    quiz_name_match = re.search(r"tags:.*?(기본|심화)", content)
    quiz_name = quiz_name_match.group(1) if quiz_name_match else "기본"
    quiz_path = VAULT_PATH / QUIZ_FILES.get(quiz_name, QUIZ_FILES["기본"])

    print(f"\n{'='*60}")
    print(f" 퇴직연금 퀴즈 채점 세션")
    print(f"{'='*60}")
    print(f" 문제지: {quiz_name} ({quiz_path.name})")
    print(f" 답안지: {answer_path.name}")
    print(f"{'='*60}\n")

    # Agent 1: Grade
    print("▶ Agent 1 (채점) 실행 중...")
    grading = grade(client, str(quiz_path), str(answer_path))
    print(f"\n── 채점 결과: {grading.get('score', '?')} ──")
    for r in grading.get("results", []):
        mark = "✓" if r.get("correct") else "✗"
        print(f"  {mark} {r['question']}. {r.get('title', '')} — {r.get('feedback', '')}")

    # Agent 2: Analyze
    print(f"\n▶ Agent 2 (분석) 실행 중...")
    analysis = analyze(client, grading, str(answer_path))
    print(f"\n── 학습 분석 ──")
    print(f"강점:")
    for s in analysis.get("strengths", []):
        print(f"  + {s}")
    print(f"약점:")
    for w in analysis.get("weaknesses", []):
        print(f"  - {w}")
    print(f"보완 영역:")
    for i in analysis.get("improvement_areas", []):
        print(f"  → {i}")
    print(f"\n총평: {analysis.get('summary', '')}")

    # Agent 3: Memory (optional)
    if save_memory:
        from agents.memory_agent import run as memorize
        print(f"\n▶ Agent 3 (기억 저장) 실행 중...")
        today = date.today().isoformat()
        mem = memorize(client, grading, analysis, today, f"점검문제 ({quiz_name})")
        print(f"✓ 학습 프로파일 업데이트: {mem.get('profile_path', '')}")

    print(f"\n{'='*60}")
    print(f" 완료")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="IntelliHouse Quiz Session")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--template", metavar="QUIZ_NAME", help="답안 템플릿 생성 (기본|심화)")
    group.add_argument("--grade", metavar="ANSWER_FILE", help="답안 파일 채점")
    parser.add_argument("--save-memory", action="store_true", help="분석 결과를 학습 프로파일에 저장")
    args = parser.parse_args()

    if args.template:
        out = generate_template(args.template)
        print(f"✓ 답안 템플릿 생성 완료: {out.relative_to(VAULT_PATH)}")
        print("  → Obsidian에서 열어 각 문제 아래 '내 답안:' 줄에 답을 작성하세요.")
    elif args.grade:
        run_grading_session(args.grade, args.save_memory)


if __name__ == "__main__":
    main()
