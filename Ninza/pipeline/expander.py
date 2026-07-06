"""반대신호 Expander — opposite-signal-expander.md 명세의 실행 구현.

LLM이 방출한 exit_directives(반대신호 지시)를 동결된 진입 스펙 위에서
결정적으로 구체 DNF 청산 조건으로 확장한다. 연산자만 미러 반전, 피연산자 불변.
"""
from __future__ import annotations

import copy

# 반전표 (프롬프트가 아니라 코드에 위치)
INVERT = {
    "CrossAbove": "CrossBelow",
    "CrossBelow": "CrossAbove",
    "GreaterThan": "LessThan",
    "LessThan": "GreaterThan",
    "GreaterThanOrEqual": "LessThanOrEqual",
    "LessThanOrEqual": "GreaterThanOrEqual",
}
NON_INVERTIBLE = {"Equals", "NotEquals"}


class ExpanderError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _invert_leaf(leaf: dict) -> dict:
    """단일 조건(leaf)의 연산자만 반전. lhs/rhs/params/input은 그대로 복사."""
    op = leaf["op"]
    if op in NON_INVERTIBLE or op not in INVERT:
        raise ExpanderError(
            "NON_INVERTIBLE_OP",
            f"'{op}'은(는) 반대 신호로 자동 변환할 수 없습니다. 청산 조건을 직접 지정해 주세요.",
        )
    out = copy.deepcopy(leaf)
    out["op"] = INVERT[op]
    return out


def _summary(leaf: dict) -> str:
    def side(o):
        if o["type"] == "indicator":
            ps = ",".join(str(v) for v in o.get("params", {}).values())
            return f"{o['name']}({ps})"
        if o["type"] == "constant":
            return str(o["value"])
        return o.get("field", o["type"])
    return f"{side(leaf['lhs'])} {leaf['op']} {side(leaf['rhs'])}"


def expand(entry_spec: dict, directive: dict) -> dict:
    """반대신호 directive를 구체 청산 conditions(DNF)로 확장.

    반환: {"conditions": DNF, "assumptions": [...]}
    """
    if directive.get("kind") != "opposite_signal":
        raise ExpanderError("UNKNOWN_DIRECTIVE", f"미지원 directive: {directive.get('kind')}")

    groups = entry_spec.get("long") or []
    if not groups or not any(g.get("conditions") for g in groups):
        raise ExpanderError("EMPTY_ENTRY", "반대 신호를 만들 진입 조건이 없습니다.")

    target = directive["target"]
    out_conditions: list[dict] = []
    assumptions: list[dict] = []

    if target == "all":
        # 모든 그룹의 모든 leaf flip, OR/AND 구조 보존
        for g in groups:
            inverted = [_invert_leaf(l) for l in g["conditions"]]
            out_conditions.append({"conditions": inverted})
        for gi, g in enumerate(groups):
            for ci, leaf in enumerate(g["conditions"]):
                assumptions.append({
                    "path": f"exit.conditions[{gi}].conditions[{ci}]",
                    "value": _summary(_invert_leaf(leaf)),
                    "reason": f"진입 신호({_summary(leaf)})의 미러 반전 (De Morgan 부정 아님, 연산자만 flip)",
                })
    else:
        refs = [target] if isinstance(target, dict) else target
        inverted_leaves = []
        for ref in refs:
            gi, ci = ref["group"], ref["condition"]
            try:
                leaf = groups[gi]["conditions"][ci]
            except (IndexError, KeyError):
                raise ExpanderError(
                    "TARGET_OUT_OF_RANGE",
                    f"selector가 가리키는 조건(group={gi}, condition={ci})이 진입 스펙에 없습니다.",
                )
            inv = _invert_leaf(leaf)
            inverted_leaves.append(inv)
            assumptions.append({
                "path": f"exit.conditions[0].conditions[{len(inverted_leaves)-1}]",
                "value": _summary(inv),
                "reason": f"진입 신호({_summary(leaf)})의 미러 반전",
            })
        out_conditions.append({"conditions": inverted_leaves})

    return {"conditions": out_conditions, "assumptions": assumptions}
