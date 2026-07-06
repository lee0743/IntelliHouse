"""템플릿 렌더러 — 병합 스펙 → NinjaScript(C#) 결정적 생성.

LLM은 관여하지 않는다. 스펙의 노출 필드를 고정 골격에 기계적으로 채운다.
"""
from __future__ import annotations

_CMP = {
    "GreaterThan": ">", "LessThan": "<",
    "GreaterThanOrEqual": ">=", "LessThanOrEqual": "<=",
    "Equals": "==", "NotEquals": "!=",
}
_CROSS = {"CrossAbove", "CrossBelow"}


def _inst_id(o: dict) -> str:
    params = "".join(str(v) for v in o.get("params", {}).values())
    return f"{o['name'].lower()}{params}"


def _series_expr(o: dict) -> str:
    """Cross 연산용 series 표현식."""
    t = o["type"]
    if t == "indicator":
        return _inst_id(o)
    if t == "price":
        return o.get("field", "Close")
    if t == "constant":
        return f"{o['value']}"
    raise ValueError(f"series 표현 불가 피연산자: {t}")


def _value_expr(o: dict) -> str:
    """비교 연산용 스칼라 표현식."""
    t = o["type"]
    if t == "indicator":
        return f"{_inst_id(o)}[0]"
    if t == "price":
        return f"{o.get('field', 'Close')}[0]"
    if t == "constant":
        return f"{o['value']}"
    if t == "entryPrice":
        return "Position.AveragePrice"
    if t == "barsSinceEntry":
        return "BarsSinceEntryExecution()"
    raise ValueError(f"value 표현 불가 피연산자: {t}")


def _leaf_expr(leaf: dict) -> str:
    op = leaf["op"]
    if op in _CROSS:
        return f"{op}({_series_expr(leaf['lhs'])}, {_series_expr(leaf['rhs'])}, 1)"
    if op in _CMP:
        return f"{_value_expr(leaf['lhs'])} {_CMP[op]} {_value_expr(leaf['rhs'])}"
    raise ValueError(f"렌더 불가 연산자: {op}")


def _dnf_expr(dnf: list[dict]) -> str:
    groups = []
    for g in dnf:
        anded = " && ".join(_leaf_expr(l) for l in g["conditions"])
        groups.append(f"({anded})" if len(g["conditions"]) > 1 else anded)
    return " || ".join(f"({g})" for g in groups) if len(groups) > 1 else groups[0]


def _stop_call(fn: str, slot: dict) -> str:
    mode, value = slot["mode"], slot["value"]
    if mode == "percent":
        return f"{fn}(CalculationMode.Percent, {value / 100.0:g});  // {value}% (0.0x = x%)"
    if mode == "ticks":
        return f"{fn}(CalculationMode.Ticks, {value});"
    if mode == "price":
        return f"{fn}(CalculationMode.Price, {value});"
    raise ValueError(f"미지원 stop mode: {mode}")


def render(merged: dict, derived: dict, class_name: str = "GeneratedStrategy") -> str:
    entry, exit_, risk = merged["entry"], merged["exit"], merged.get("risk", {})
    bars = derived["barsRequiredToTrade"]
    qty = risk.get("quantity", 1)
    calc = merged.get("execution", {}).get("calculate", "OnBarClose")

    # 지표 인스턴스 생성 라인
    inst_lines = [f"\t\t\t\t{_inst_id(o)} = {o['name']}({o.get('input', 'Close')}, "
                  f"{', '.join(str(v) for v in o.get('params', {}).values())});"
                  for o in derived["indicatorInstances"]]
    field_lines = [f"\t\tprivate {o['name']} {_inst_id(o)};" for o in derived["indicatorInstances"]]

    # Set류 (DataLoaded)
    set_lines = []
    if exit_.get("stopLoss"):
        set_lines.append("\t\t\t\t" + _stop_call("SetStopLoss", exit_["stopLoss"]))
    if exit_.get("profitTarget"):
        set_lines.append("\t\t\t\t" + _stop_call("SetProfitTarget", exit_["profitTarget"]))
    if exit_.get("trailStop"):
        set_lines.append("\t\t\t\t" + _stop_call("SetTrailStop", exit_["trailStop"]))

    # 진입/청산 OnBarUpdate
    body = []
    if entry.get("long"):
        cond = _dnf_expr(entry["long"])
        body += [
            "\t\t\t// 진입 (entry.long)",
            "\t\t\tif (Position.MarketPosition == MarketPosition.Flat",
            f"\t\t\t\t&& {cond})",
            "\t\t\t{",
            f"\t\t\t\tEnterLong({qty}, \"LE\");",
            "\t\t\t}",
            "",
        ]
    if exit_.get("conditions"):
        cond = _dnf_expr(exit_["conditions"])
        body += [
            "\t\t\t// 조건 청산 (exit.conditions; expander 미러 반전 결과)",
            "\t\t\tif (Position.MarketPosition == MarketPosition.Long",
            f"\t\t\t\t&& {cond})",
            "\t\t\t{",
            "\t\t\t\tExitLong(\"LX\", \"LE\");",
            "\t\t\t}",
        ]

    nl = "\n"
    return f"""#region Using declarations
using System;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
#endregion

// 렌더러 산출물 — 03-merged-spec.json 에서 결정적으로 생성. 손으로 수정하지 말 것.
// 실제 컴파일 검증은 MVP 6단계 Roslyn + NT8 DLL 하니스에서 수행.
namespace NinjaTrader.NinjaScript.Strategies
{{
\tpublic class {class_name} : Strategy
\t{{
{nl.join(field_lines)}

\t\tprotected override void OnStateChange()
\t\t{{
\t\t\tif (State == State.SetDefaults)
\t\t\t{{
\t\t\t\tName                         = "{class_name}";
\t\t\t\tCalculate                    = Calculate.{calc};
\t\t\t\tEntriesPerDirection          = 1;
\t\t\t\tEntryHandling                = EntryHandling.AllEntries;
\t\t\t\tDefaultQuantity              = {qty};
\t\t\t\tBarsRequiredToTrade          = {bars};
\t\t\t\tTimeInForce                  = TimeInForce.Gtc;
\t\t\t\tStartBehavior                = StartBehavior.WaitUntilFlat;
\t\t\t\tIsExitOnSessionCloseStrategy = false;
\t\t\t\tIncludeCommission            = true;
\t\t\t}}
\t\t\telse if (State == State.DataLoaded)
\t\t\t{{
{nl.join(inst_lines)}
{nl.join(set_lines)}
\t\t\t}}
\t\t}}

\t\tprotected override void OnBarUpdate()
\t\t{{
\t\t\tif (CurrentBar < BarsRequiredToTrade)
\t\t\t\treturn;

{nl.join(body)}
\t\t}}
\t}}
}}
"""
