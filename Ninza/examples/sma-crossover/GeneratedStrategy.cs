#region Using declarations
using System;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
#endregion

// 렌더러 산출물 — 03-merged-spec.json 에서 결정적으로 생성. 손으로 수정하지 말 것.
// 실제 컴파일 검증은 MVP 6단계 Roslyn + NT8 DLL 하니스에서 수행.
namespace NinjaTrader.NinjaScript.Strategies
{
	public class GeneratedStrategy : Strategy
	{
		private SMA sma20;
		private SMA sma60;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name                         = "GeneratedStrategy";
				Calculate                    = Calculate.OnBarClose;
				EntriesPerDirection          = 1;
				EntryHandling                = EntryHandling.AllEntries;
				DefaultQuantity              = 1;
				BarsRequiredToTrade          = 60;
				TimeInForce                  = TimeInForce.Gtc;
				StartBehavior                = StartBehavior.WaitUntilFlat;
				IsExitOnSessionCloseStrategy = false;
				IncludeCommission            = true;
			}
			else if (State == State.DataLoaded)
			{
				sma20 = SMA(Close, 20);
				sma60 = SMA(Close, 60);
				SetStopLoss(CalculationMode.Percent, 0.05);  // 5% (0.0x = x%)
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < BarsRequiredToTrade)
				return;

			// 진입 (entry.long)
			if (Position.MarketPosition == MarketPosition.Flat
				&& CrossAbove(sma20, sma60, 1))
			{
				EnterLong(1, "LE");
			}

			// 조건 청산 (exit.conditions; expander 미러 반전 결과)
			if (Position.MarketPosition == MarketPosition.Long
				&& CrossBelow(sma20, sma60, 1))
			{
				ExitLong("LX", "LE");
			}
		}
	}
}
