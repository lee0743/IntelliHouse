# 반대신호 Expander 명세 v0.1

> 언어 중립 명세. 실제 코드는 MVP 5·6단계에서 이 문서를 단위 테스트 사양으로 삼아 구현.

## 0. 목적
청산 해석기가 방출한 `exit_directives`(반대신호 지시)를, **동결된 진입 스펙** 위에서
**결정적으로** 구체 DNF 청산 조건으로 확장한다.
이로써 "반대 신호 반전"이 LLM 판단(category-2, 오류 시 silent intent error)에서
코드 실행(category-1, 구조 강제)으로 승격된다.

핵심 원칙: **LLM은 '반대신호 요청'임을 분류(directive)만, 실제 연산자 반전은 이 컴포넌트가 수행.**

---

## 1. 의미 정의 — mirror-signal (De Morgan 아님)
"반대 신호"는 **연산자별 미러 반전**이다:
- 피연산자(lhs/rhs, 지표, 파라미터, input)는 **불변**.
- 비교/교차 **연산자만** 반전.
- 예: `SMA20 CrossAbove SMA60` → `SMA20 CrossBelow SMA60` (골든크로스→데드크로스)

이는 논리 부정과 **다르다**: `¬(A∧B) = ¬A ∨ ¬B`(De Morgan)는 CNF가 되고 트레이딩 직관과 어긋남.
미러 반전은 DNF 구조를 보존한다.

---

## 2. 입출력 계약

### 입력
```
{
  entrySpec:  동결된 진입 스펙 { long: DNF, short: DNF },
  directive:  { kind: "opposite_signal", target: <selector> }
}
```

### selector 형태
| selector | 의미 |
|---|---|
| `"all"` | 진입 전체 조건 미러 반전 (구조 보존) |
| `{ "group": i, "condition": j }` | 특정 leaf 하나만 |
| `[ {group,condition}, ... ]` | 지정된 leaf들만 |

### 출력
```
성공: { conditions: DNF(구체), assumptions: [ {path, value, reason} ] }
실패: { error: { code, message, suggestClarification? } }
```
출력 `conditions`는 병합 스펙의 `exit.conditions`에 append되고, directive는 clear.

---

## 3. 반전표 (결정적, 프롬프트에 두지 않음)

| entry op | inverted op | 비고 |
|---|---|---|
| CrossAbove | CrossBelow | |
| CrossBelow | CrossAbove | |
| GreaterThan | LessThan | strict 유지 |
| LessThan | GreaterThan | strict 유지 |
| GreaterThanOrEqual | LessThanOrEqual | 경계 포함(inclusivity) 유지 |
| LessThanOrEqual | GreaterThanOrEqual | 경계 포함 유지 |
| Equals | — | **반전 불가** (미러 불명) |
| NotEquals | — | **반전 불가** |

**불변식**: 연산자만 flip. lhs/rhs/params/input는 바이트 단위로 동일 복사.

---

## 4. DNF 대상 의미 (target별 확장 규칙)

진입 DNF: `그룹배열=OR, 그룹내 conditions=AND`

| 케이스 | 규칙 |
|---|---|
| 단일 그룹·단일 leaf | 그 leaf flip → 단일 그룹·단일 조건 청산 |
| 단일 그룹 AND, target=특정 leaf | 그 leaf만 flip, 단독 조건으로 청산 |
| 단일 그룹 AND, target="all" | 모든 leaf flip, **AND 유지** (모든 미러 동시 성립 시 청산) |
| 다중 그룹 OR, target="all" | 모든 그룹의 모든 leaf flip, **구조(OR/AND) 보존** |
| 다중 그룹 OR, target 모호 | expander가 판단 불가 → 해석기 단계에서 clarification으로 선해소 |

> 다중 조건의 "어느 신호가 뒤집힐 때 청산?"은 언어 이해가 필요하므로 **해석기가 clarification으로 처리**,
> expander는 확정된 selector만 받는다 (재해석 없이 기계 주입).

---

## 5. 에러 케이스

| code | 상황 | 처리 |
|---|---|---|
| `NON_INVERTIBLE_OP` | Equals 등 반전표에 미러 없음 | error + suggestClarification: "이 조건은 반대 신호로 자동 변환할 수 없습니다. 청산 조건을 직접 지정해 주세요." |
| `TARGET_OUT_OF_RANGE` | selector가 가리키는 group/condition 인덱스가 진입 스펙에 없음 | 하드 error (해석기 계약 위반 — selector는 진입 스펙에서 파생되어야 함) |
| `EMPTY_ENTRY` | 진입 스펙에 조건이 없음 | 하드 error (반대신호를 만들 원본 없음) |

---

## 6. 테스트 매트릭스 (= 향후 단위 테스트)

| # | 진입 | directive.target | 기대 출력 |
|---|---|---|---|
| 1 | SMA20 **CrossAbove** SMA60 | "all" | SMA20 **CrossBelow** SMA60 (← examples/sma-crossover) |
| 2 | RSI(14) **GreaterThanOrEqual** 70 | "all" | RSI(14) **LessThanOrEqual** 70 (경계 포함 유지) |
| 3 | (A **CrossAbove** B) AND (C **GreaterThan** D) | "all" | (A CrossBelow B) AND (C LessThan D), AND 유지 |
| 4 | (A **CrossAbove** B) AND (C **GreaterThan** D) | {group:0,condition:1} | C **LessThan** D 단독 |
| 5 | (A CrossAbove B) OR (C GreaterThan D) | "all" | (A CrossBelow B) OR (C LessThan D), 구조 보존 |
| 6 | A **Equals** B | "all" | error: NON_INVERTIBLE_OP |
| 7 | SMA20 CrossAbove SMA60 | {group:5,condition:0} | error: TARGET_OUT_OF_RANGE |

테스트 #1은 `examples/sma-crossover/`의 01→03 변환과 정확히 일치해야 한다 (회귀 앵커).
