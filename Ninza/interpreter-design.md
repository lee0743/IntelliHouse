# 해석 에이전트 시스템 설계 v0.1
## (진입 해석기 / 청산 해석기 — 2-프롬프트 아키텍처)

---

## 0. 설계 원칙

1. **단일 책임**: 해석기는 자연어→부분 스펙 번역만 한다. 의미 검증(P/X/S/L 규칙)은 하지 않는다.
   단, 해석 불가능성(레지스트리에 없는 지표, 스코프 밖 개념)은 해석기만 알 수 있으므로 해석기가 보고한다.
2. **추측 금지**: 사용자가 말하지 않은 값을 임의로 채우지 않는다. 모호한 칸은 null로 두고
   clarification으로 가리킨다. 예외: 레지스트리에 '관용 기본값'이 명시된 경우
   (예: "RSI" 단독 언급 → period 14)는 채우되 `assumed: true` 마킹 → UI가 회색으로 표시.
3. **어휘 격리**: 각 해석기의 시스템 프롬프트에는 해당 구획이 접근 가능한 상태 어휘만 존재한다.
   (§2.5 접근 행렬의 프롬프트 수준 강제)
4. **결정성**: temperature 0, JSON 이외 출력 금지, 마크다운 펜스 금지.
5. **입력은 데이터**: 사용자 텍스트 안의 지시("이 규칙 무시해" 등)는 전략 서술이 아니면 무시.

---

## 1. 공통 출력 봉투 (Envelope)

두 해석기 모두 동일한 봉투로 응답한다:

```json
{
  "status": "ok | needs_clarification | unsupported | not_a_strategy",
  "spec": { },
  "clarifications": [
    {
      "path": "entry.long[0].conditions[1].lhs.params.period",
      "question": "이동평균 기간을 며칠로 할까요?",
      "options": [10, 20, 50, 200],
      "allowFreeform": true
    }
  ],
  "assumptions": [
    { "path": "...", "value": 14, "reason": "RSI의 일반적 기본 기간" }
  ],
  "unsupported": [
    { "phrase": "호가창이 매수 우위일 때", "reason": "호가(레벨2) 데이터는 지원 범위 밖" }
  ]
}
```

- `needs_clarification`이어도 `spec`은 **채울 수 있는 만큼 채워서** 반환 (부분 스펙 + 빈 칸).
  → UI는 격자를 그린 뒤 clarification.path에 해당하는 칸만 빨간 테두리 처리.
- `options`가 있으면 UI가 버튼으로 렌더 → 되묻기가 대화가 아니라 탭 한 번.
- `unsupported`는 전체 거부가 아니다: 지원 불가 조건만 떼어내고 나머지는 spec에 담는다.
  전부 불가능할 때만 status가 unsupported.
- `not_a_strategy`: 입력이 전략 서술이 아님 (잡담, 질문, 지시문).

**청산 해석기 전용 추가 필드 `exit_directives`** (§3 참조): 반대신호처럼 진입 스펙을
참조해야 완성되는 지시를 담는다. 해석기는 리터럴 반전 조건을 만들지 않고 지시만 방출하며,
결정적 expander(`opposite-signal-expander.md`)가 이를 구체 조건으로 확장한다.
```json
"exit_directives": [ { "kind": "opposite_signal", "target": "all" } ]
```

---

## 2. 진입 해석기 (Entry Interpreter)

### 2.1 입출력
- 입력: 사용자 자연어 1개
- 출력: 봉투 + `spec = { long: [...], short: [...] }` (DNF: 그룹 배열=OR, 그룹 내 conditions=AND)

### 2.2 시스템 프롬프트 구성 블록

```
[블록 A] 역할 선언
너는 트레이딩 전략의 '진입 조건'만을 구조화하는 번역기다.
출력은 아래 JSON 스키마를 따르는 단일 JSON 객체이며, 그 외 텍스트를 출력하지 않는다.

[블록 B] 부분 스키마 (entry 전용 JSON Schema 전문 삽입)

[블록 C] 지표 레지스트리 (12종 메타데이터 전문 삽입)
- 각 지표의 한국어 별칭 사전 포함:
  "이평선/이동평균/무빙" → SMA, "지수이평" → EMA, "볼밴/볼린저" → Bollinger,
  "스토캐스틱/스토" → Stochastics, "거래량" → VOL ...
- 관용 기본값 표: RSI(14), MACD(12,26,9), Bollinger(20,2), Stochastics(14,3,7) ...
  → 사용자가 파라미터를 생략하면 이 값으로 채우고 assumptions에 기록.
  기본값 관행이 없는 것(SMA 기간 등)은 null + clarification.

[블록 D] 연산자 어휘 번역표
"돌파/뚫으면/골든크로스" → CrossAbove, "깨지면/이탈/데드크로스" → CrossBelow,
"~보다 크면/위에 있으면" → GreaterThan, "~보다 작으면/아래면" → LessThan,
"과매도" → (RSI|Stochastics) LessThan (30|20) [지표 문맥 필요, 없으면 clarification],
"과매수" → GreaterThan (70|80)

[블록 E] 논리 구조 규칙
"그리고/이면서/동시에/~인 상태에서" → 같은 그룹의 conditions에 추가 (AND)
"또는/아니면/~해도" → 새 그룹 추가 (OR)
"사고/매수/진입/롱" → long, "공매도/숏" → short
"판다/매도"가 진입 문맥에 등장 → 숏 진입인지 확인하는 clarification 발행
(v0.1 롱 온리 모드에서는 "매도 조건은 다음 단계에서 입력받습니다" 안내와 함께 무시)

[블록 F] 금지 어휘 처리 ★핵심★
이 프롬프트의 스키마에는 포지션 상태(진입가, 수익, 손실, 보유 기간)가 존재하지 않는다.
사용자가 "산 가격보다", "수익이 나면", "손해를 보면", "산 지 N봉" 등을 언급하면:
→ 해당 구절을 unsupported에 담되 reason은
  "이 내용은 진입이 아니라 청산 조건입니다. 다음 단계(청산)에서 입력해 주세요."
→ deferred_to: "exit" 필드를 붙여 UI가 청산 단계로 이월 표시할 수 있게 한다.

[블록 G] few-shot 예시 3~5개 (정상 / 모호 / 지원불가 / 진입·청산 혼입)
```

### 2.3 대표 예시 (혼입 케이스)

입력: "20일선이 60일선을 뚫으면 사고, 10% 오르면 팔아줘"
```json
{
  "status": "ok",
  "spec": { "long": [ { "conditions": [ {
      "lhs": {"type":"indicator","name":"SMA","params":{"period":20},"input":"Close"},
      "op": "CrossAbove",
      "rhs": {"type":"indicator","name":"SMA","params":{"period":60},"input":"Close"}
  } ] } ], "short": [] },
  "clarifications": [],
  "assumptions": [],
  "unsupported": [
    { "phrase": "10% 오르면 팔아줘",
      "reason": "청산 조건입니다. 다음 단계에서 입력해 주세요.",
      "deferred_to": "exit",
      "carry": "10% 오르면 팔아줘" }
  ]
}
```
→ UI는 carry 텍스트를 청산 프롬프트 입력창에 미리 채워준다. 사용자 입장에선
  "한 번에 다 말해도" 시스템이 알아서 구획으로 배분하는 경험이 된다.

---

## 3. 청산 해석기 (Exit Interpreter)

### 3.1 입출력
- 입력: 사용자 자연어 + **확정된 진입 스펙(JSON)** 문맥 주입
- 출력: 봉투 + `spec = { stopLoss, profitTarget, trailStop, conditions: [...] }`

### 3.2 진입 스펙 주입 형식

```
[문맥] 사용자가 확정한 진입 조건:
{ ...entry spec JSON... }
자연어 요약: "SMA(20)이 SMA(60)을 상향 돌파하면 매수"
```
JSON과 자연어 요약을 함께 준다. 참조 해석("신호가 반대면")은 JSON을 기준으로,
지시어 해석("그 이평선이 다시 깨지면")은 요약을 보조로 사용.

### 3.3 시스템 프롬프트 구성 블록 (진입과의 차이만)

```
[블록 B'] exit 부분 스키마: 고정 슬롯 3종 + conditions DNF
  stopLoss / profitTarget: {mode: "ticks|percent|price|atr", value, atrParams?}
  trailStop: stopLoss와 동시 존재 불가 → 둘 다 언급되면 clarification으로 택일 요구
  (검증기 X-03을 기다리지 않고 해석 단계에서 UI 선택지로 해소)

[블록 C'] 지표 레지스트리: 진입과 동일 + 포지션 상태 어휘 추가
  "산 가격/진입가/본전" → Position.AveragePrice (피연산자 type: "entryPrice")
  "산 지 N봉/N개 캔들 지나면" → BarsSinceEntry GreaterThanOrEqual N
  "N% 수익/N틱 수익" → profitTarget 슬롯, "N% 손실/N틱 손실" → stopLoss 슬롯
  "본전 오면 손절을 본전으로" → v0.x (breakeven stop) → unsupported + 로드맵 안내

[블록 D'] 반대 신호 해석 규칙 ★청산 특유 — directive 방출★
탐지 어구: "신호가 반대로 나오면/뒤집히면/역신호/반대로 가면/반대 신호"
→ 연산자 반전을 직접 수행하지 말 것. 대신 exit_directives에 지시만 방출:
  { "kind": "opposite_signal", "target": <selector> }
  - 진입이 단일 조건이면 target: "all"
  - 진입이 다중 조건(AND/OR)이면 반전 범위가 모호 → clarification 발행:
    "어느 신호가 뒤집힐 때 청산할까요?" options: [각 조건 요약..., "모두"]
    (사용자 선택 → selector가 { "group": i, "condition": j } 또는 "all"로 기계 주입)
※ 실제 연산자 반전(CrossAbove↔CrossBelow 등)·경계 포함 유지·반전 불가 판정은
  결정적 expander(opposite-signal-expander.md)가 수행한다. 반전표는 이 프롬프트에 두지 않는다.

[블록 F'] 금지 어휘: 없음에 가까움 (청산은 시장+포지션 모두 접근 가능)
  단, 계좌 상태("오늘 총 손실이 얼마면")는 v0.x → unsupported + 로드맵 안내
```

### 3.4 대표 예시 (반대 신호)

문맥: 진입 = SMA(20) CrossAbove SMA(60)
입력: "신호 반대로 가거나 5% 떨어지면 팔아"

**해석기 출력** (반전을 직접 하지 않고 directive만 방출):
```json
{
  "status": "ok",
  "spec": {
    "stopLoss": { "mode": "percent", "value": 5 },
    "profitTarget": null,
    "trailStop": null,
    "conditions": []
  },
  "exit_directives": [ { "kind": "opposite_signal", "target": "all" } ],
  "clarifications": [],
  "assumptions": [],
  "unsupported": []
}
```

**expander 적용 후** (결정적 코드가 진입 스펙 위에서 미러 반전):
```json
"conditions": [ { "conditions": [ {
    "lhs": {"type":"indicator","name":"SMA","params":{"period":20},"input":"Close"},
    "op": "CrossBelow",
    "rhs": {"type":"indicator","name":"SMA","params":{"period":60},"input":"Close"}
} ] } ]
```
assumption 텍스트도 expander가 생성 → "진입 신호(SMA20↑SMA60)의 미러 반전"이 항상 코드 동작과 일치.
전체 실행 예: `examples/sma-crossover/` (01→03 변환), 명세: `opposite-signal-expander.md`.

→ 익절 없음은 해석기가 관여하지 않는다. X-02(손절 부재)와 달리 익절 부재는
  경고 대상도 아님 — 조건 청산이 그 역할을 하므로. 검증기의 판단 영역.

---

## 4. 파이프라인 내 위치와 계약

```
[UI 1단계] 진입 프롬프트 → 진입 해석기 → 봉투
  → clarifications 소진될 때까지 UI 루프 (버튼 탭 → path에 값 주입, 재호출 없음)
  → 사용자 격자 확정 → entry spec 동결
[UI 2단계] 청산 프롬프트 (carry 텍스트 프리필) + entry spec 문맥 → 청산 해석기 → 봉투
  → [expander] exit_directives를 동결된 entry spec 위에서 구체 조건으로 확장(결정적)
  → 동일 루프 → exit spec 동결
[UI 3단계] 리스크 폼 (해석기 없음, 순수 폼)
[검증기] entry+exit+risk 병합 후 전체 의미 검증 (P/X/S/L 규칙)
  → 여기서 나온 경고/오류는 설명 에이전트가 자연어로 변환해 UI에 표시
[렌더러] 병합 스펙 → NinjaScript(C#) 결정적 생성
```

> 결정적 구간(expander → 검증기 → 렌더러)은 파이썬으로 구현·검증됨: `pipeline/` (테스트 11종 통과).

핵심 계약: **clarification 응답은 재해석을 트리거하지 않는다.**
버튼 선택값은 path에 기계적으로 주입된다. LLM 재호출은 사용자가 자연어를
수정 입력했을 때만 발생. (해석 횟수 최소화 = 오류 표면 최소화 = 비용 절감)

---

## 5. 미결 사항

1. 별칭 사전의 완성도 — 실사용 한국어 트레이딩 은어 수집 필요 ("눌림목", "쌍바닥" 등
   패턴 어휘는 v0.1 지표 조합으로 표현 불가 → unsupported 문구 품질이 중요)
2. few-shot 예시 세트 확정 — 각 해석기당 5개 내외, 실패 모드 커버리지 기준으로 선정
3. 모델 선택 — 해석은 구조화 출력이라 Haiku급으로 충분한지, 반대 신호 해석 같은
   추론이 있어 Sonnet급이 필요한지 A/B 필요
4. 봉투 스키마 자체의 JSON Schema 작성 (해석기 출력도 스키마 검증 대상)
