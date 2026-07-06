# NinjaScript 자연어 전략 생성기 — 설계 요약 (프로젝트 인계)

> 이 폴더(`Ninza/`)를 프로젝트 최상위로 취급한다. 상위/형제 폴더(`JSP`, `old`, `퇴직연금`)는 건드리지 않는다.

## 문제 정의
일반인이 자연어로 트레이딩 전략을 서술하면 컴파일되는 NinjaScript(C#) 전략이 나오는 시스템. LLM에게 코드를 직접 쓰게 하면 컴파일 오류·논리 오류를 일반인이 감지·수정할 수 없다는 게 핵심 문제.

## 핵심 아키텍처 결정
1. **LLM은 자연어→스펙 번역만, 스펙→C#은 결정적 템플릿이 담당.** 오류의 근원(LLM 자유 코드 생성)을 제거.
2. **파이프라인**: 자연어 → 해석 에이전트(구조화 스펙 JSON) → 스펙 검증기 → 템플릿 코드 생성 → Roslyn+NT8 DLL 컴파일 검증 → 백테스트 스모크 → 설명 에이전트(역번역 확인).
3. **격자 UI = 스펙의 시각적 표현이자 해석 결과 확인 화면.** 자연어 입력이 격자를 채우고, 사용자가 격자에서 확인·수정.

## 스펙 스키마 결정사항
- 조건식은 **DNF**(그룹 배열=OR, 그룹 내 conditions=AND) — 격자 UI와 1:1 대응, 표현력 손실 없음.
- 피연산자는 태그된 유니온: constant / indicator / price (+청산 전용 entryPrice).
- 지표는 닫힌 레지스트리 12종 (SMA, EMA, WMA, RSI, MACD, Bollinger, ATR, Stochastics, ADX, CCI, Momentum, VOL) + 메타데이터(params 범위, outputs, 값 범위, minLookback).
- **Managed Approach만 사용, Unmanaged 영구 제외.** v0.1: Market 진입 + SetStopLoss/SetProfitTarget/SetTrailStop + 조건 청산.
- v0.1 롱 온리 기본, 멀티 타임프레임·지정가·계좌 상태는 v0.x.

## 구획화 원칙 (설계 전체의 척추)
- 진입/청산/리스크 구획은 상태 접근이 **비대칭**: 진입=시장+세션, 청산=시장+세션+**포지션**(진입가, 경과 봉), 리스크=포지션+세션.
- 이 접근 행렬에서 검증 규칙이 자동 도출 (E-01: 진입이 포지션 상태 참조 시 오류 등, 총 11종 초안: E/X/P/S/L 계열).
- 주요 규칙: X-01 청산 완전 부재=오류, X-03 stopLoss+trailStop 병용 불가, X-04 OnBarClose+미세 틱 목표 → Higher Resolution Fill 경고.

## 2-프롬프트 해석기 설계
- **진입과 청산을 별도 프롬프트로 분리** — 사용자가 직접 구획화를 수행, LLM의 경계 판별 오류 제거, 출력 스키마 축소.
- 순서: 진입 먼저 → 확정된 진입 스펙을 청산 해석기 문맥으로 주입 (단방향 의존, "반대 신호" 해석에 필수).
- 공통 출력 봉투: `{status, spec(부분 채움), clarifications(path+question+options→UI 버튼), assumptions(관용 기본값 마킹), unsupported(구절별 분리 거부)}`.
- **혼입 이월**: 진입 프롬프트에 청산 구절이 오면 `deferred_to: "exit" + carry` 텍스트로 반환 → UI가 청산 입력창에 프리필.
- **clarification 응답은 재해석 없이 path에 기계 주입** — LLM 재호출은 자연어 재입력 시만.
- 반대 신호 규칙: **LLM은 `exit_directives`로 지시만 방출, 실제 연산자 반전(CrossAbove↔CrossBelow)은 결정적 expander가 동결된 진입 스펙 위에서 수행** (silent intent error 제거). 다중 조건이면 대상 선택 clarification. 명세: `opposite-signal-expander.md`.
- 어휘 격리: 진입 프롬프트에는 포지션 상태 어휘 자체가 없음 (E-01의 사전 차단).

## UI 흐름
① 진입 프롬프트 → 격자 확인/수정 → ② 청산 프롬프트(진입 요약 표시, carry 프리필) → 손절/익절/조건청산 슬롯 확인 → ③ 리스크 폼(해석기 없음, 안전 기본값) → ④ 전체 요약(설명 에이전트 역번역) → 생성. 청산 패널은 손절을 조건이 아닌 **필수 슬롯**으로 위계화.

## 산출물
### 설계 문서
- `nt8-classification.md`: 이벤트/상태/행동 3축 + 전략 속성 분류표, 지표 레지스트리, 검증 규칙 11종
- `interpreter-design.md`: 두 해석기 시스템 프롬프트 블록 구성, 봉투 스키마, few-shot 예시, 파이프라인 계약
- `opposite-signal-expander.md`: 반대신호 expander 명세 (반전표, DNF 대상 의미, 에러, 테스트 매트릭스)

### 구현 (결정적 구간, 파이썬)
- `pipeline/`: registry / expander / validator / renderer / pipeline / run / test
  - 실행: `cd Ninza && python -m pipeline.run` (예제 → C# 생성)
  - 테스트: `python -m unittest pipeline.test_pipeline -v` (11종 통과)
- `examples/sma-crossover/`: 자연어→스펙→검증→C# 워크드 예제 (`GeneratedStrategy.cs`는 렌더러 산출물)

### 해석기 (LLM 구간, 실측 검증됨)
- `prompts/entry-interpreter.txt`, `prompts/exit-interpreter.txt`: 실제 해석기 시스템 프롬프트(블록 A~G)
- `pipeline/interpret.py`: 인증된 Claude API 호출 하니스 (claude CLI print 모드)
- `pipeline/check_live.py`: 자연어 → **실제 Claude** → 파이프라인 → C# 라이브 점검
  - 실행: `python -m pipeline.check_live` — Haiku로 2회 연속 전항목 통과(스펙·directive·C# 골드 일치)
  - **실측 소견**: ① 반대신호를 리터럴 반전 없이 `exit_directives`로 정확히 방출(directive 설계 유효). ② 모델이
    "JSON 펜스 금지" 지시를 어기고 ```json 펜스를 붙임 → `_strip_fence`로 방어. 프로덕션은 Messages API +
    structured output으로 결정성 강제 필요(CLI는 temperature 미노출).
- `pipeline/stress_test.py` + `examples/stress-eval.md`: 실패 모드 9종 스트레스 테스트(실제 Claude). 단발 8/9.
- `pipeline/repeat_eval.py` + `examples/model-eval.md`: N=5 반복 + Haiku/Sonnet A/B.
  - **Haiku 87% > Sonnet 78%** — 더 큰 모델이 낫지 않음(잡담엔 Sonnet이 더 자주 자연어로 응답).
  - 실패는 ① 출력 형식(structured output으로 제거) ② 다중조건 반대신호(프롬프트·few-shot 문제)에 집중.
  - **모델 업그레이드로는 둘 다 안 풀림** → MVP 해석기 = Haiku + structured output 권장.
- `schemas/`: 봉투 JSON Schema (structured output 계약). `interpret.py`가 FormatError로 위반 탐지.

### 남은 최우선 soft spot
- **모호한 다중조건 반대신호**: clarification 대신 target:"all" 맹목 방출 경향(Haiku 1/5, Sonnet 0/5).
  exit 프롬프트에 다중조건 전용 few-shot + clarification 예시 강화 필요(모델 아닌 프롬프트 문제).

### 아직 미구현
- Roslyn + NT8 DLL 컴파일 하니스 (MVP 6단계) — 현재 C#은 구조 점검만, 실제 컴파일 미검증.
- 프로덕션 해석기: Messages API + structured output(현재는 claude CLI 하니스로 대체 검증).

## 다음 작업 후보 (미착수)
1. entry+exit+risk 통합 JSON Schema 본체 확정
2. 지표 레지스트리 메타데이터 파일 (params/outputs/range/minLookback)
3. 해석기 few-shot 예시 세트 (실패 모드 커버리지 기준 5개씩)
4. 검증 규칙 11종의 규칙 엔진 명세
5. 템플릿 조각 (골격 + 조건식 렌더러 + Set류 렌더러)
6. Roslyn 컴파일 하니스 (NT8 DLL 참조)
7. 한국어 별칭 사전 ("눌림목" 등 표현 불가 패턴의 unsupported 문구 포함)
8. 격자 UI 목업

**MVP 권장 순서**: 1→2→5→6 (스키마→레지스트리→템플릿→컴파일 확인)으로 "자연어 없이도 스펙→컴파일되는 코드" 경로부터 증명 후 해석기 결합.
