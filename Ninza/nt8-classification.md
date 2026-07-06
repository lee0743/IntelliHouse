# NT8 NinjaScript 표면 분류표 (v0.1 스코프 정의)

목적: 자연어 → 스펙 → 코드 파이프라인의 스펙 스키마가 참조할 전체 집합을 조사하고,
각 항목을 **포함 수준** × **노출 수준**으로 태깅한다.

- 포함 수준: `v0.1`(초기 지원) / `v0.x`(보류, 향후 확장) / `제외`(영구 제외)
- 노출 수준: `노출`(사용자 스펙에 등장) / `내부`(템플릿이 내부 처리, 사용자에게 안 보임)

---

## 축 1 — 이벤트 (언제 평가되는가)

| 이벤트 | 설명 | 포함 | 노출 | 비고 |
|---|---|---|---|---|
| OnStateChange() | 생명주기(SetDefaults→Configure→DataLoaded→…→Terminated). 지표 인스턴스 생성, Set류 초기화 위치 | v0.1 | 내부 | 템플릿 고정 골격 |
| OnBarUpdate() | 봉 갱신마다 호출. 호출 빈도는 Calculate 속성이 결정. 전략 로직의 유일한 홈 | v0.1 | 내부 | 스펙에는 `calculate` 필드로만 간접 노출 |
| OnExecutionUpdate() | 체결 이벤트 | v0.1 | 내부 | 진입 체결 후 상태 갱신용으로 템플릿이 선택적 사용 |
| OnOrderUpdate() | 주문 상태 변화 | v0.x | 내부 | 주문 거부 처리 등 고급 오류 복구 시 |
| OnPositionUpdate() | 포지션 변화 | v0.x | 내부 | |
| OnMarketData() | 레벨1 틱 스트림. 실시간 전용(Tick Replay 없으면 백테스트 불가) | v0.x | — | 백테스트 일관성 깨짐 → 초기 제외 |
| OnMarketDepth() | 레벨2 호가창 | 제외 | — | 오더플로우 전략은 스코프 밖 |
| OnRender() / 그리기 | 차트 렌더링 | 제외 | — | 전략 생성기와 무관 |
| AddDataSeries() (멀티 시리즈) | 다중 타임프레임/종목 | v0.x | 노출(예정) | BarsInProgress 필터 등 오류 표면 큼 → v0.2 이후 |

**v0.1 이벤트 결론**: 사용자 관점에서 이벤트 축은 완전히 사라진다.
스펙에 남는 흔적은 `execution.calculate` (OnBarClose / OnEachTick / OnPriceChange) 하나뿐.

---

## 축 2 — 상태 (무엇을 읽는가)

### 2.1 시장 상태
| 항목 | API | 포함 | 노출 | 비고 |
|---|---|---|---|---|
| 가격 시리즈 | Close/Open/High/Low[i] | v0.1 | 노출 | barsAgo 인덱스는 0~N 제한 |
| 거래량 | Volume[i] | v0.1 | 노출 | |
| 봉 시각 | Time[i] | v0.1 | 내부 | 세션 필터가 내부적으로 사용 |
| 지표 | 닫힌 레지스트리 (§4) | v0.1 | 노출 | |
| 현재 호가 | GetCurrentBid()/Ask() | v0.x | 내부 | 지정가 가격 산출용 |
| 시리즈 간 교차 | CrossAbove()/CrossBelow() | v0.1 | 노출 | 연산자로 표현 |

### 2.2 포지션 상태 (청산·리스크 구획 전용)
| 항목 | API | 포함 | 노출 |
|---|---|---|---|
| 포지션 방향 | Position.MarketPosition | v0.1 | 내부 (템플릿 가드) |
| 평균 진입가 | Position.AveragePrice | v0.1 | 노출 (청산 조건 피연산자) |
| 수량 | Position.Quantity | v0.x | 내부 |
| 진입 후 경과 봉 | BarsSinceEntryExecution() | v0.1 | 노출 (시간 청산) |
| 미실현 손익 | Position.GetUnrealizedProfitLoss() | v0.x | 노출(예정) |

### 2.3 세션/시간 상태
| 항목 | 포함 | 노출 |
|---|---|---|
| 거래 시간대 필터 (start/end) | v0.1 | 노출 |
| 세션 종료 청산 (flatten) | v0.1 | 노출 |
| 요일 필터 | v0.x | 노출(예정) |
| 세션 첫 봉 (IsFirstBarOfSession) | v0.x | 내부 |

### 2.4 계좌/성과 상태
| 항목 | 포함 | 비고 |
|---|---|---|
| 계좌 잔고, 일일 손익 한도 | v0.x | 프롭펌 컴플라이언스에 필수 → 우선순위 높은 v0.2 후보 |
| SystemPerformance (거래 이력) | 제외 | 전략 정지 로직 등 고급 기능 |

### 2.5 구획별 상태 접근 행렬 (검증기 규칙의 원천)

| 상태 \ 구획 | 진입(entry) | 청산(exit) | 리스크(risk) |
|---|---|---|---|
| 시장 상태 (가격/지표) | ✅ | ✅ | ❌ |
| 세션 상태 | ✅ | ✅ | ✅ (flatten) |
| 포지션 상태 | ❌ | ✅ | ✅ |
| 계좌 상태 (v0.x) | ❌ | ❌ | ✅ |

파생 검증 규칙:
- E-01: entry 조건이 포지션 상태(AveragePrice, BarsSinceEntry)를 참조 → **오류**
- E-02: risk 블록에 지표 조건 등장 → **오류** (ATR 기반 손절은 exit의 stopLoss.mode=indicator로 표현)

---

## 축 3 — 행동 (무엇을 하는가)

**대원칙: Managed Approach만 사용. Unmanaged는 영구 제외.**
Managed는 주문 상태 머신·OCO·포지션 정합성을 닌자가 관리 → 오류 표면 최소화.

### 3.1 진입 메서드
| 메서드 | 포함 | 스펙 표현 |
|---|---|---|
| EnterLong() / EnterShort() | v0.1 | orderType: "Market" |
| EnterLongLimit() / EnterShortLimit() | v0.x | orderType: "Limit" + 가격 오프셋 |
| EnterLongStopMarket() 등 Stop류 | v0.x | 돌파 진입 표현에 유용 → v0.2 후보 |
| EnterLongMIT() 등 MIT류 | 제외 | 사용 빈도 낮음 |

### 3.2 청산 메서드
| 메서드 | 포함 | 스펙 표현 |
|---|---|---|
| SetStopLoss() | v0.1 | exit.stopLoss {mode: ticks/price/percent, value} |
| SetProfitTarget() | v0.1 | exit.profitTarget |
| SetTrailStop() | v0.1 | exit.trailStop (stopLoss와 상호배타 — 검증 규칙 X-03) |
| ExitLong() / ExitShort() (조건 청산) | v0.1 | exit.conditions (DNF) |
| SetParabolicStop() | v0.x | |
| ExitLongLimit() 등 지정가 청산 | v0.x | |

### 3.3 전략 속성 (템플릿 고정/노출 구분)
| 속성 | 포함 | 노출 | 기본값 |
|---|---|---|---|
| Calculate | v0.1 | 노출 | OnBarClose |
| EntriesPerDirection / EntryHandling | v0.1 | 내부 | 1 / AllEntries (피라미딩 금지 고정) |
| BarsRequiredToTrade | v0.1 | 내부 | max(지표 lookback)로 자동 산출 |
| DefaultQuantity | v0.1 | 노출 | risk.quantity |
| TimeInForce | v0.1 | 내부 | GTC |
| Slippage / IncludeCommission | v0.1 | 내부 | 백테스트 현실화를 위해 보수적 기본값 |
| StartBehavior | v0.1 | 내부 | WaitUntilFlat |
| IsExitOnSessionCloseStrategy | v0.1 | 노출 | sessionFilter.flatten과 매핑 |
| OrderFillResolution | v0.1 | 내부 | 검증기가 High 권장 경고 발생 시 안내 (스캘핑 OnBarClose 이슈) |

---

## 4 — 지표 레지스트리 v0.1

선정 기준: 사용 빈도 + 파라미터 단순성 + 단일/소수 출력. NT8 내장 100+개 중 12개.

| 지표 | 파라미터 | 출력 | 비고 |
|---|---|---|---|
| SMA | period | 단일 | |
| EMA | period | 단일 | |
| WMA | period | 단일 | |
| RSI | period, smooth | Default, Avg | 0~100 범위 → 상수 비교 검증(0≤c≤100) |
| MACD | fast, slow, smooth | Default(macd선), Avg(시그널), Diff(히스토그램) | 다중 출력 대표 사례 |
| Bollinger | period, numStdDev | Upper, Middle, Lower | |
| ATR | period | 단일 | 손절 모드 피연산자로도 사용 |
| Stochastics | periodD, periodK, smooth | D, K | 0~100 |
| ADX | period | 단일 | 0~100 |
| CCI | period | 단일 | |
| Momentum | period | 단일 | |
| VOL (거래량) | — | 단일 | Volume 시리즈의 지표형 접근 |

v0.x 후보: VWAP(OrderFlow 라이선스 의존 확인 필요), KeltnerChannel, DonchianChannel, Parabolic SAR, Pivots(다중 출력 복잡), SuperTrend(내장 아님 — 서드파티 제외 원칙과 충돌 검토).

레지스트리 항목의 스키마 메타데이터: `{name, params: {이름: {type, min, max, default}}, outputs: [], range: [min,max]|null, minLookback: fn(params)}`
→ 검증기가 파라미터 범위·상수 비교 범위·BarsRequiredToTrade를 이 메타데이터에서 자동 도출.

---

## 5 — 분류에서 파생되는 검증 규칙 초안

| ID | 규칙 | 수준 |
|---|---|---|
| E-01 | entry가 포지션 상태 참조 | 오류 |
| E-02 | risk 블록에 시장 조건 | 오류 |
| X-01 | 진입 정의됨 + 청산 완전 부재 (stopLoss/profitTarget/trailStop/conditions 모두 없음) | 오류 |
| X-02 | 손절 부재 (profitTarget만 존재) | 경고(강) |
| X-03 | stopLoss와 trailStop 동시 지정 | 오류 (NT8 문서상 병용 불가) |
| X-04 | calculate=OnBarClose + 손절/익절 tick 단위 < 봉 평균 범위 | 경고: Higher Resolution Fill(OrderFillResolution=High) 권장 |
| P-01 | 지표 파라미터가 레지스트리 min/max 밖 | 오류 |
| P-02 | 범위 지표(RSI 등) vs 상수 비교에서 상수가 범위 밖 | 오류 |
| P-03 | 가격 시리즈 vs 범위 지표(RSI 등) 직접 비교 | 오류 (단위 불일치) |
| S-01 | sessionFilter.start ≥ end | 오류 |
| L-01 | barsAgo 인덱스 > BarsRequiredToTrade | 오류 |

---

## 6 — 다음 단계

1. 이 분류표를 기반으로 v0.1 JSON Schema 확정 (지난 대화의 DNF 구조 + 이 문서의 노출 필드만 포함)
2. 지표 레지스트리 12종의 메타데이터 파일 작성 (params/outputs/range/minLookback)
3. 검증 규칙 11종을 규칙 엔진 형태로 명세 (스키마 검증과 의미 검증 분리)
4. 템플릿 조각: 골격 1종(OnStateChange+OnBarUpdate) + 조건식 렌더러 + Set류 렌더러
