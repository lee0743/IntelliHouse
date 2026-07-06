"""LLM 해석기 호출 하니스 — 인증된 Claude API(claude CLI print 모드)로 실제 해석 수행.

파이프라인 앞단(비결정 구간). 자연어 → 봉투 JSON.
결정성 한계: CLI는 temperature를 노출하지 않고, 모델이 마크다운 펜스를 붙일 수 있으므로
_strip_fence로 방어한다. 프로덕션에서는 Messages API + structured output으로 대체 권장.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
PROMPTS = HERE.parent / "prompts"


def _strip_fence(text: str) -> str:
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.DOTALL)
    if m:
        return m.group(1).strip()
    return t


def call_interpreter(system_prompt_file: str, user_input: str,
                     model: str = "claude-haiku-4-5") -> dict:
    """claude CLI를 통해 해석기 1회 호출 → 파싱된 봉투 dict."""
    proc = subprocess.run(
        ["claude", "-p", user_input,
         "--system-prompt-file", str(PROMPTS / system_prompt_file),
         "--model", model,
         "--allowedTools", "",
         "--exclude-dynamic-system-prompt-sections",
         "--output-format", "text"],
        capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI 실패 (rc={proc.returncode}): {proc.stderr[:500]}")
    raw = proc.stdout
    cleaned = _strip_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"봉투 JSON 파싱 실패: {e}\n원문:\n{raw[:800]}")


def interpret_entry(user_input: str, model: str = "claude-haiku-4-5") -> dict:
    return call_interpreter("entry-interpreter.txt", user_input, model)


def interpret_exit(user_input: str, entry_spec: dict, summary: str,
                   model: str = "claude-haiku-4-5") -> dict:
    injected = (f"{user_input}\n\n확정된 진입 스펙:\n{json.dumps(entry_spec, ensure_ascii=False)}\n"
                f"자연어 요약: {summary}")
    return call_interpreter("exit-interpreter.txt", injected, model)
