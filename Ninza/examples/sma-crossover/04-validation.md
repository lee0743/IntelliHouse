# 단계 4 — 검증기 판정 (11종 규칙)

입력: `03-merged-spec.json` (entry + exit + risk 병합, expander 적용 완료)

## 파생값 도출
- **BarsRequiredToTrade** = max(지표 lookback) = max(SMA20=20, SMA60=60) = **60**
- 지표 인스턴스 2종 (sma20, sma60) — OnStateChange DataLoaded에서 생성

## 규칙 판정표

| ID | 규칙 | 판정 | 근거 |
|---|---|---|---|
| E-01 | entry가 포지션 상태 참조 | ✅ PASS | entry는 지표 크로스만 참조, 포지션 상태 없음 |
| E-02 | risk 블록에 시장 조건 | ✅ PASS | risk는 quantity=1만 |
| X-01 | 진입 정의 + 청산 완전 부재 | ✅ PASS | stopLoss + conditions 존재 |
| X-02 | 손절 부재 (익절만) | ✅ PASS | stopLoss(5%) 존재 |
| X-03 | stopLoss + trailStop 동시 | ✅ PASS | trailStop = null |
| X-04 | OnBarClose + 미세 틱 목표 | ✅ PASS | 손절이 percent(5%), 미세 틱 아님 → 경고 없음 |
| P-01 | 지표 파라미터 범위 밖 | ✅ PASS | SMA period 20/60, 유효 범위 내 |
| P-02 | 범위 지표 vs 상수 범위 밖 | — N/A | 상수 비교 없음 |
| P-03 | 가격 vs 범위 지표 직접 비교 | — N/A | 지표 vs 지표 (단위 일치) |
| S-01 | sessionFilter start ≥ end | — N/A | 세션 필터 없음 |
| L-01 | barsAgo > BarsRequiredToTrade | ✅ PASS | 크로스 lookback=1 ≪ 60 |

## 결론
**검증 통과.** 오류 0건, 경고 0건. 템플릿 렌더 단계로 진행 가능.
