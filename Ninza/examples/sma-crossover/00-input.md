# 예제: SMA 크로스오버 전략 (엔드투엔드 입력)

자연어 입력이 파이프라인을 거쳐 컴파일 대상 NinjaScript(C#)까지 나오는지 증명하는 워크드 예제.

## 사용자 자연어 입력

| 구획 | 입력 |
|---|---|
| **진입 (entry)** | "20일 이동평균선이 60일 이동평균선을 상향 돌파하면 매수" |
| **청산 (exit)** | "신호가 반대로 가거나 5% 떨어지면 팔아" |
| **리스크 (risk)** | 수량 1 (기본값) |

## 이 예제가 exercise하는 것
- 진입 해석기 → DNF 단일 조건 스펙
- 청산 해석기 → **반대신호 directive** 방출 (리터럴 반전 X) + percent 손절
- **directive expander** → 미러 반전(CrossAbove→CrossBelow) 결정적 수행
- 검증기 11종 통과
- 템플릿 렌더 → NinjaScript C#

## 파이프라인 단계별 산출물
```
00-input.md        (이 파일)         자연어 입력
01-entry-spec.json 진입 해석기 출력   봉투 + entry DNF
02-exit-spec.json  청산 해석기 출력   봉투 + exit_directives
03-merged-spec.json expander+병합     구체 조건으로 확장된 전체 스펙
04-validation.md   검증기             11종 판정 + BarsRequiredToTrade 도출
GeneratedStrategy.cs 렌더러           NinjaScript(대표형)
```
