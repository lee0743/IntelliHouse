"""지표 레지스트리 v0.1 (닫힌 레지스트리).

각 지표의 params(min/max/default), outputs, 값 범위, minLookback을 담는다.
검증기·렌더러가 이 메타데이터에서 파라미터 범위·BarsRequiredToTrade·상수 비교 범위를 도출한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Param:
    min: float
    max: float
    default: float | None = None


@dataclass(frozen=True)
class Indicator:
    name: str
    params: dict[str, Param]
    outputs: list[str]
    value_range: tuple[float, float] | None  # None = 무한(가격 단위)
    min_lookback: Callable[[dict], int]
    aliases: list[str] = field(default_factory=list)


REGISTRY: dict[str, Indicator] = {
    "SMA": Indicator(
        name="SMA", params={"period": Param(1, 1000)}, outputs=["Default"],
        value_range=None, min_lookback=lambda p: int(p["period"]),
        aliases=["이평선", "이동평균", "무빙", "단순이동평균"],
    ),
    "EMA": Indicator(
        name="EMA", params={"period": Param(1, 1000)}, outputs=["Default"],
        value_range=None, min_lookback=lambda p: int(p["period"]),
        aliases=["지수이평", "지수이동평균"],
    ),
    "RSI": Indicator(
        name="RSI", params={"period": Param(1, 1000, 14), "smooth": Param(1, 1000, 3)},
        outputs=["Default", "Avg"], value_range=(0, 100),
        min_lookback=lambda p: int(p["period"]) + int(p.get("smooth", 3)),
        aliases=["알에스아이", "상대강도"],
    ),
    "ATR": Indicator(
        name="ATR", params={"period": Param(1, 1000, 14)}, outputs=["Default"],
        value_range=None, min_lookback=lambda p: int(p["period"]),
        aliases=["에이티알", "변동성"],
    ),
}


def get(name: str) -> Indicator:
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(f"레지스트리에 없는 지표: {name}")
