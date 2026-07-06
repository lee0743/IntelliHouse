"""라이브 엔드투엔드 점검 — 실제 Claude 해석기 → 결정적 파이프라인 → C#.

자연어를 진짜 Claude에 보내 얻은 봉투가:
  (1) 스키마상 유효하고
  (2) 손으로 쓴 기대 스펙(examples/sma-crossover)과 의미상 일치하며
  (3) 파이프라인을 통과해 기대 C#을 생성하는지
를 점검한다.

실행:  cd Ninza && python -m pipeline.check_live
"""
from __future__ import annotations

import json
import pathlib

from . import interpret, pipeline

EXAMPLE = pathlib.Path(__file__).resolve().parent.parent / "examples" / "sma-crossover"

ENTRY_INPUT = "20일 이동평균선이 60일 이동평균선을 상향 돌파하면 매수"
EXIT_INPUT = "신호가 반대로 가거나 5% 떨어지면 팔아"
ENTRY_SUMMARY = "SMA(20)이 SMA(60)을 상향 돌파하면 매수"


def _canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def main() -> int:
    print("① 진입 해석기 호출 (실제 Claude)…")
    entry_env = interpret.interpret_entry(ENTRY_INPUT)
    print("   status:", entry_env["status"])

    print("② 청산 해석기 호출 (진입 스펙 주입)…")
    exit_env = interpret.interpret_exit(EXIT_INPUT, entry_env["spec"], ENTRY_SUMMARY)
    print("   status:", exit_env["status"], "| exit_directives:", exit_env.get("exit_directives"))

    # 점검 A: 기대 스펙과 의미 일치 (손으로 쓴 예제 = 골드)
    gold_entry = json.loads((EXAMPLE / "01-entry-spec.json").read_text(encoding="utf-8"))
    gold_exit = json.loads((EXAMPLE / "02-exit-spec.json").read_text(encoding="utf-8"))
    checks = []
    checks.append(("진입 spec 일치", _canon(entry_env["spec"]) == _canon(gold_entry["spec"])))
    checks.append(("청산 stopLoss 일치", _canon(exit_env["spec"]["stopLoss"]) == _canon(gold_exit["spec"]["stopLoss"])))
    checks.append(("청산 directive 일치", _canon(exit_env.get("exit_directives")) == _canon(gold_exit["exit_directives"])))
    checks.append(("리터럴 반전 미방출(directive만)", exit_env["spec"].get("conditions") in ([], None)))

    # 점검 B: 파이프라인 통과 → C# 생성
    result = pipeline.run(entry_env, exit_env, {"quantity": 1})
    checks.append(("파이프라인 검증 통과", result.ok))

    # 점검 C: 생성 C#이 손 예제와 동일
    gold_cs = (EXAMPLE / "GeneratedStrategy.cs").read_text(encoding="utf-8")
    checks.append(("C# 산출물 == 손 예제", result.csharp == gold_cs))

    print("\n=== 점검 결과 ===")
    all_ok = True
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        all_ok = all_ok and ok

    if not all_ok and result.csharp:
        print("\n--- 라이브 생성 C# (참고) ---")
        print(result.csharp)
    print("\n종합:", "전부 통과 ✅" if all_ok else "불일치 있음 ❌")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
