"""의미 검증기 — nt8-classification.md §5 규칙 초안의 실행 구현 (v0.1 부분집합).

해석기와 분리된 결정적 규칙 엔진. 병합 스펙(entry+exit+risk)을 입력받아
오류/경고 목록과 파생값(BarsRequiredToTrade)을 산출한다.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import registry


@dataclass
class Finding:
    id: str
    level: str  # "error" | "warning"
    message: str


POSITION_OPERANDS = {"entryPrice", "barsSinceEntry"}


def _iter_leaves(dnf: list[dict]):
    for group in dnf or []:
        for leaf in group.get("conditions", []):
            yield leaf


def _indicator_instances(merged: dict) -> list[dict]:
    seen: dict[tuple, dict] = {}
    dnfs = [merged["entry"].get("long"), merged["entry"].get("short"),
            merged["exit"].get("conditions")]
    for dnf in dnfs:
        for leaf in _iter_leaves(dnf or []):
            for side in ("lhs", "rhs"):
                o = leaf.get(side, {})
                if o.get("type") == "indicator":
                    key = (o["name"], o.get("input", "Close"),
                           tuple(sorted(o.get("params", {}).items())))
                    seen.setdefault(key, o)
    return list(seen.values())


def bars_required(merged: dict) -> int:
    lookbacks = [0]
    for o in _indicator_instances(merged):
        ind = registry.get(o["name"])
        lookbacks.append(ind.min_lookback(o.get("params", {})))
    return max(lookbacks)


def validate(merged: dict) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    entry, exit_, risk = merged["entry"], merged["exit"], merged.get("risk", {})

    # E-01: entry가 포지션 상태 참조
    for leaf in _iter_leaves(entry.get("long", [])) if entry.get("long") else []:
        for side in ("lhs", "rhs"):
            if leaf.get(side, {}).get("type") in POSITION_OPERANDS:
                findings.append(Finding("E-01", "error", "진입 조건이 포지션 상태를 참조합니다."))

    # X-01: 청산 완전 부재
    has_exit = any([exit_.get("stopLoss"), exit_.get("profitTarget"),
                    exit_.get("trailStop"), exit_.get("conditions")])
    if (entry.get("long") or entry.get("short")) and not has_exit:
        findings.append(Finding("X-01", "error", "진입은 정의됐으나 청산 수단이 전혀 없습니다."))

    # X-02: 손절 부재 (경고)
    if not exit_.get("stopLoss") and not exit_.get("trailStop"):
        findings.append(Finding("X-02", "warning", "손절이 없습니다. 리스크 통제를 권장합니다."))

    # X-03: stopLoss + trailStop 병용
    if exit_.get("stopLoss") and exit_.get("trailStop"):
        findings.append(Finding("X-03", "error", "stopLoss와 trailStop은 병용할 수 없습니다."))

    # P-01: 지표 파라미터 범위
    for o in _indicator_instances(merged):
        ind = registry.get(o["name"])
        for pname, pval in o.get("params", {}).items():
            spec = ind.params.get(pname)
            if spec and not (spec.min <= pval <= spec.max):
                findings.append(Finding("P-01", "error",
                    f"{o['name']}.{pname}={pval} 이(가) 허용 범위 [{spec.min},{spec.max}] 밖입니다."))

    # P-02: 범위 지표 vs 상수 비교에서 상수가 범위 밖
    for leaf in list(_iter_leaves(entry.get("long", []) or [])) + list(_iter_leaves(exit_.get("conditions", []) or [])):
        ind_side = next((leaf[s] for s in ("lhs", "rhs")
                         if leaf.get(s, {}).get("type") == "indicator"), None)
        const_side = next((leaf[s] for s in ("lhs", "rhs")
                           if leaf.get(s, {}).get("type") == "constant"), None)
        if ind_side and const_side:
            rng = registry.get(ind_side["name"]).value_range
            if rng and not (rng[0] <= const_side["value"] <= rng[1]):
                findings.append(Finding("P-02", "error",
                    f"{ind_side['name']} 범위 {rng} 밖의 상수 {const_side['value']} 비교."))

    # S-01: sessionFilter start >= end
    sf = merged.get("sessionFilter")
    if sf and sf.get("start") is not None and sf.get("end") is not None and sf["start"] >= sf["end"]:
        findings.append(Finding("S-01", "error", "세션 필터 start가 end 이상입니다."))

    derived = {
        "barsRequiredToTrade": bars_required(merged),
        "indicatorInstances": _indicator_instances(merged),
    }
    return findings, derived
