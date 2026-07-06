"""파이프라인 단위 테스트 — 표준 unittest (외부 의존 없음).

실행:  cd Ninza && python -m unittest pipeline.test_pipeline -v
opposite-signal-expander.md §6 테스트 매트릭스 7종 + 엔드투엔드 검증.
"""
from __future__ import annotations

import json
import pathlib
import unittest

from . import expander, pipeline, validator

HERE = pathlib.Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "examples" / "sma-crossover"


def ind(name, period, input_="Close"):
    return {"type": "indicator", "name": name, "params": {"period": period}, "input": input_}


def leaf(lhs, op, rhs):
    return {"lhs": lhs, "op": op, "rhs": rhs}


class TestExpanderMatrix(unittest.TestCase):
    """opposite-signal-expander.md §6 매트릭스."""

    def test_1_single_crossabove(self):
        entry = {"long": [{"conditions": [leaf(ind("SMA", 20), "CrossAbove", ind("SMA", 60))]}]}
        out = expander.expand(entry, {"kind": "opposite_signal", "target": "all"})
        self.assertEqual(out["conditions"][0]["conditions"][0]["op"], "CrossBelow")
        # 피연산자 불변
        self.assertEqual(out["conditions"][0]["conditions"][0]["lhs"]["params"]["period"], 20)

    def test_2_gte_boundary_preserved(self):
        entry = {"long": [{"conditions": [
            leaf(ind("RSI", 14), "GreaterThanOrEqual", {"type": "constant", "value": 70})]}]}
        out = expander.expand(entry, {"kind": "opposite_signal", "target": "all"})
        self.assertEqual(out["conditions"][0]["conditions"][0]["op"], "LessThanOrEqual")

    def test_3_and_group_all(self):
        entry = {"long": [{"conditions": [
            leaf(ind("SMA", 20), "CrossAbove", ind("SMA", 60)),
            leaf(ind("RSI", 14), "GreaterThan", {"type": "constant", "value": 50})]}]}
        out = expander.expand(entry, {"kind": "opposite_signal", "target": "all"})
        ops = [l["op"] for l in out["conditions"][0]["conditions"]]
        self.assertEqual(ops, ["CrossBelow", "LessThan"])  # 둘 다 flip, AND(같은 그룹) 유지

    def test_4_and_group_specific(self):
        entry = {"long": [{"conditions": [
            leaf(ind("SMA", 20), "CrossAbove", ind("SMA", 60)),
            leaf(ind("RSI", 14), "GreaterThan", {"type": "constant", "value": 50})]}]}
        out = expander.expand(entry, {"kind": "opposite_signal",
                                      "target": {"group": 0, "condition": 1}})
        self.assertEqual(len(out["conditions"][0]["conditions"]), 1)
        self.assertEqual(out["conditions"][0]["conditions"][0]["op"], "LessThan")

    def test_5_or_multigroup_structure_preserved(self):
        entry = {"long": [
            {"conditions": [leaf(ind("SMA", 20), "CrossAbove", ind("SMA", 60))]},
            {"conditions": [leaf(ind("RSI", 14), "GreaterThan", {"type": "constant", "value": 50})]}]}
        out = expander.expand(entry, {"kind": "opposite_signal", "target": "all"})
        self.assertEqual(len(out["conditions"]), 2)  # OR 그룹 2개 보존
        self.assertEqual(out["conditions"][0]["conditions"][0]["op"], "CrossBelow")
        self.assertEqual(out["conditions"][1]["conditions"][0]["op"], "LessThan")

    def test_6_non_invertible_equals(self):
        entry = {"long": [{"conditions": [
            leaf(ind("SMA", 20), "Equals", ind("SMA", 60))]}]}
        with self.assertRaises(expander.ExpanderError) as ctx:
            expander.expand(entry, {"kind": "opposite_signal", "target": "all"})
        self.assertEqual(ctx.exception.code, "NON_INVERTIBLE_OP")

    def test_7_target_out_of_range(self):
        entry = {"long": [{"conditions": [leaf(ind("SMA", 20), "CrossAbove", ind("SMA", 60))]}]}
        with self.assertRaises(expander.ExpanderError) as ctx:
            expander.expand(entry, {"kind": "opposite_signal",
                                    "target": {"group": 5, "condition": 0}})
        self.assertEqual(ctx.exception.code, "TARGET_OUT_OF_RANGE")


class TestValidator(unittest.TestCase):
    def test_e01_entry_position_state_is_error(self):
        merged = {
            "entry": {"long": [{"conditions": [
                leaf({"type": "entryPrice"}, "GreaterThan", {"type": "constant", "value": 100})]}], "short": []},
            "exit": {"stopLoss": {"mode": "percent", "value": 5}, "conditions": []},
            "risk": {},
        }
        findings, _ = validator.validate(merged)
        self.assertTrue(any(f.id == "E-01" and f.level == "error" for f in findings))

    def test_x01_missing_exit_is_error(self):
        merged = {
            "entry": {"long": [{"conditions": [leaf(ind("SMA", 20), "CrossAbove", ind("SMA", 60))]}], "short": []},
            "exit": {"stopLoss": None, "profitTarget": None, "trailStop": None, "conditions": []},
            "risk": {},
        }
        findings, _ = validator.validate(merged)
        self.assertTrue(any(f.id == "X-01" and f.level == "error" for f in findings))

    def test_p01_param_out_of_range(self):
        merged = {
            "entry": {"long": [{"conditions": [leaf(ind("SMA", 5000), "CrossAbove", ind("SMA", 60))]}], "short": []},
            "exit": {"stopLoss": {"mode": "percent", "value": 5}, "conditions": []},
            "risk": {},
        }
        findings, _ = validator.validate(merged)
        self.assertTrue(any(f.id == "P-01" for f in findings))


class TestEndToEnd(unittest.TestCase):
    def test_sma_crossover_produces_csharp(self):
        entry_env = json.loads((EXAMPLE / "01-entry-spec.json").read_text(encoding="utf-8"))
        exit_env = json.loads((EXAMPLE / "02-exit-spec.json").read_text(encoding="utf-8"))
        result = pipeline.run(entry_env, exit_env, {"quantity": 1})

        self.assertTrue(result.ok, msg=str([f.__dict__ for f in result.findings]))
        self.assertEqual(result.derived["barsRequiredToTrade"], 60)
        cs = result.csharp
        # 결정적 렌더 산출물 핵심 앵커
        self.assertIn("class GeneratedStrategy : Strategy", cs)
        self.assertIn("CrossAbove(sma20, sma60, 1)", cs)   # 진입
        self.assertIn("CrossBelow(sma20, sma60, 1)", cs)   # expander 미러 청산
        self.assertIn("SetStopLoss(CalculationMode.Percent, 0.05)", cs)  # 5% → 0.05
        self.assertIn("BarsRequiredToTrade          = 60;", cs)
        self.assertIn("EnterLong(1, \"LE\")", cs)
        self.assertIn("ExitLong(\"LX\", \"LE\")", cs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
