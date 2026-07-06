"""examples/sma-crossover 를 파이프라인에 태워 C#을 생성하고 리포트를 출력한다.

실행:  python -m Ninza.pipeline.run
    또는  cd Ninza && python -m pipeline.run
"""
from __future__ import annotations

import json
import pathlib

from . import pipeline

HERE = pathlib.Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "examples" / "sma-crossover"


def main() -> None:
    entry_env = json.loads((EXAMPLE / "01-entry-spec.json").read_text(encoding="utf-8"))
    exit_env = json.loads((EXAMPLE / "02-exit-spec.json").read_text(encoding="utf-8"))
    risk = {"quantity": 1}

    result = pipeline.run(entry_env, exit_env, risk, class_name="GeneratedStrategy")

    print("=" * 70)
    print("입력:")
    print("  진입:", entry_env.get("_input"))
    print("  청산:", exit_env.get("_input"))
    print("=" * 70)
    print("expander assumptions:")
    for a in result.merged["_expander_assumptions"]:
        print(f"  - {a['path']}: {a['value']}")
        print(f"      ({a['reason']})")
    print("=" * 70)
    print("검증 (BarsRequiredToTrade =", result.derived["barsRequiredToTrade"], "):")
    if not result.findings:
        print("  통과 — 오류/경고 0건")
    for f in result.findings:
        print(f"  [{f.level.upper()}] {f.id}: {f.message}")
    print("=" * 70)

    if result.ok:
        out = EXAMPLE / "GeneratedStrategy.cs"
        out.write_text(result.csharp, encoding="utf-8")
        print(f"C# 생성 완료 → {out}")
        print("-" * 70)
        print(result.csharp)
    else:
        print("오류로 인해 C# 생성 중단.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
