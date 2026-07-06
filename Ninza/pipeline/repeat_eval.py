"""반복 + 멀티모델 평가 — 스트레스 케이스를 N회씩, 여러 모델로 돌려 통계를 낸다.

각 시행 결과를 3분류: pass(판단 정확) / judgment_fail(판단 오류) / format_fail(형식 위반, FormatError).
format_fail을 분리하는 이유: 형식 위반은 structured output으로 구조적 제거 가능하므로 판단 오류와 성격이 다르다.

실행:  cd Ninza && python -m pipeline.repeat_eval --n 5 --models claude-haiku-4-5,claude-sonnet-4-5
"""
from __future__ import annotations

import argparse
import collections
from concurrent.futures import ThreadPoolExecutor

from . import interpret
from .interpret import FormatError
from .stress_test import CASES


def run_case(case, model) -> str:
    try:
        if case.kind == "entry":
            env = interpret.interpret_entry(case.prompt, model=model)
        else:
            env = interpret.interpret_exit(case.prompt, case.entry_spec, case.summary, model=model)
    except FormatError:
        return "format_fail"
    except Exception:
        return "format_fail"  # 파싱 불가 등도 형식 실패로 취급
    try:
        ok, _ = case.check(env)
    except Exception:
        return "judgment_fail"
    return "pass" if ok else "judgment_fail"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--models", default="claude-haiku-4-5,claude-sonnet-4-5")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    models = [m.strip() for m in args.models.split(",")]

    # (model, case_idx) -> Counter
    jobs = [(m, i, c) for m in models for i, c in enumerate(CASES) for _ in range(args.n)]
    results: dict = collections.defaultdict(collections.Counter)

    def work(job):
        m, i, c = job
        return (m, i), run_case(c, m)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for (m, i), outcome in ex.map(work, jobs):
            results[(m, i)][outcome] += 1

    for m in models:
        print(f"\n{'='*74}\n모델: {m}  (N={args.n}/케이스)\n{'='*74}")
        print(f"{'케이스':<28}{'pass':>6}{'판단실패':>8}{'형식실패':>8}")
        tot = collections.Counter()
        for i, c in enumerate(CASES):
            ct = results[(m, i)]
            tot.update(ct)
            print(f"{c.name[:26]:<28}{ct['pass']:>6}{ct['judgment_fail']:>8}{ct['format_fail']:>8}")
        n_all = sum(tot.values())
        print("-" * 50)
        print(f"{'합계':<28}{tot['pass']:>6}{tot['judgment_fail']:>8}{tot['format_fail']:>8}"
              f"   (pass율 {tot['pass']/n_all*100:.0f}%, 판단정확률 "
              f"{tot['pass']/(tot['pass']+tot['judgment_fail'] or 1)*100:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
