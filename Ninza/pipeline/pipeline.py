"""파이프라인 오케스트레이터 (결정적 구간).

진입 스펙 + 청산 스펙(봉투) → expander 적용 → 병합 → 검증 → C# 렌더.
LLM 해석기 구간은 이 파이프라인 앞단(별도)에서 수행하며, 여기서는 그 출력(JSON)을 입력으로 받는다.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import expander, renderer, validator


@dataclass
class Result:
    merged: dict
    derived: dict
    findings: list
    csharp: str | None
    ok: bool


def run(entry_env: dict, exit_env: dict, risk: dict, class_name: str = "GeneratedStrategy") -> Result:
    entry_spec = entry_env["spec"]
    exit_spec = dict(exit_env["spec"])

    # 1) expander: exit_directives → 구체 conditions
    exit_conditions = list(exit_spec.get("conditions") or [])
    expander_assumptions = []
    for directive in exit_env.get("exit_directives", []):
        expanded = expander.expand(entry_spec, directive)
        exit_conditions += expanded["conditions"]
        expander_assumptions += expanded["assumptions"]
    exit_spec["conditions"] = exit_conditions

    # 2) 병합
    merged = {
        "name": class_name,
        "execution": {"calculate": "OnBarClose"},
        "entry": {"long": entry_spec.get("long", []), "short": entry_spec.get("short", [])},
        "exit": exit_spec,
        "risk": risk,
    }

    # 3) 검증 + 파생값
    findings, derived = validator.validate(merged)
    merged["_derived"] = derived
    merged["_expander_assumptions"] = expander_assumptions

    errors = [f for f in findings if f.level == "error"]
    ok = not errors

    # 4) 렌더 (오류 없을 때만)
    csharp = renderer.render(merged, derived, class_name) if ok else None
    return Result(merged=merged, derived=derived, findings=findings, csharp=csharp, ok=ok)
