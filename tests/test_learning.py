"""Matched actual-cost comparisons, quality floors, sample independence and proposal preservation."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adaptive
import learning
import metrics
import router
from test_metrics import task


def measured(case="case-01", arm="baseline", model="large", amount="1.00", **overrides):
    value = task(case + ":r1", schema=3, arm=arm)
    value["metadata"] = {"case_id": case, "stack": "PYTHON", "task_class": "implement", "level": 2,
                         "revision": "a" * 40, "repetition": 1, "review": "manual", "capabilities": []}
    value["attempts"][0].update(provider="fixture", model=model, effort="medium", disposition="succeeded")
    value["attempts"][0]["cost"]["amount"] = amount
    value.update(overrides)
    return value


class ComparisonsTests(unittest.TestCase):
    def test_fixed_trial_savings_include_failure_and_recovery(self):
        left, right = measured(), measured(arm="kit-fixed", amount="0.20", rework=1)
        right["attempts"].append(copy.deepcopy(right["attempts"][0]))
        result = learning.compare([left, right], "trial")
        self.assertEqual(result["candidate_cost_per_correct"], "0.40")
        self.assertEqual(result["savings_percent"], "60.0")

    def test_unknown_or_confounded_trials_never_claim_savings(self):
        mutations = [lambda r: r["attempts"][0].update(cost=None),
                     lambda r: r["attempts"][0]["cost"].update(source="estimate"),
                     lambda r: r["attempts"][0].update(model="other"),
                     lambda r: r["metadata"].update(revision=None),
                     lambda r: r.update(outcome="incorrect"),
                     lambda r: (r.update(outcome="incomplete"), r["metadata"].update(review="pending"))]
        for mutate in mutations:
            right = measured(arm="kit-fixed", amount="0.20")
            mutate(right)
            with self.subTest(mutate=mutate):
                result = learning.compare([measured(), right], "trial")
                self.assertIsNone(result["savings_percent"])
                self.assertTrue(result["unknown_reasons"])
        self.assertIsNone(learning.compare([measured()], "trial")["savings_percent"])

    def test_zero_baseline_and_no_correct_results(self):
        result = learning.compare([measured(amount="0"), measured(arm="kit-fixed", amount="0")], "trial")
        self.assertIsNone(result["savings_percent"])
        self.assertIn("Baseline cost is zero", result["unknown_reasons"])

    def test_stacks_and_legacy_unknown(self):
        report = learning.by_stack([measured(), task("old")])
        self.assertEqual(set(report["stacks"]), {"PYTHON", "unknown"})
        group = metrics.summarize([measured(rework=None, escalations=None)])["groups"][0]
        self.assertIsNone(group["rework"])
        self.assertEqual(group["intervention_coverage"]["rework"], {"known": 0, "total": 1})
        with self.assertRaises(ValueError):
            metrics.validate_record(task(rework=None))

    def test_cross_experiment_identity_is_not_collapsed(self):
        first, second = task(), task(experiment="other", outcome="incorrect")
        result = metrics.analyze([first, second])["providers"][0]
        self.assertEqual((result["tasks"], result["correct_tasks"]), (2, 1))

    def test_estimates_cannot_be_actual_cost_per_correct(self):
        value = measured()
        value["attempts"][0]["cost"]["source"] = "estimate"
        self.assertIsNone(metrics.summarize([value])["groups"][0]["cost_per_correct_result"])
        self.assertIsNone(metrics.analyze([value])["providers"][0]["cost_per_correct"])


class LearningTests(unittest.TestCase):
    def evidence(self):
        return [measured(f"case-{n:02d}", arm=arm, model=model, amount=cost)
                for n in range(20) for arm, model, cost in
                (("kit-fixed", "large", "1"), ("kit-adaptive", "small", "0.20"))]

    def recommend(self, rows):
        return learning.recommend(rows, {"provider": "fixture", "model": "large", "effort": "medium"},
                                  stack="PYTHON", task_class="implement", level=2, capabilities=[])

    def test_cheaper_matched_model_with_equal_quality_is_recommended(self):
        result = self.recommend(self.evidence())
        self.assertEqual(result["model"], "small")
        self.assertEqual(result["distinct_cases"], 20)
        # Adding the instruction baseline must not duplicate the incumbent's model trials.
        rows = self.evidence()
        rows += [measured(f"case-{n:02d}", arm="baseline") for n in range(20)]
        self.assertEqual(self.recommend(rows)["model"], "small")
        for row in rows:
            if row["arm"] == "kit-adaptive":
                row["experiment"] = "different-task-pack"
        result = self.recommend(rows)
        self.assertTrue(result is None or result["model"] == "large")

    def test_single_success_repeats_cannot_make_sufficient_evidence(self):
        with self.assertRaises(ValueError):
            learning.candidates([], stack="PYTHON", task_class="private task text", level=2, capabilities=[])
        with self.assertRaises(ValueError):
            learning.candidates([], stack="PYTHON", task_class="implement", level=99, capabilities=[])
        rows = []
        for n in range(30):
            row = measured(arm="kit-fixed")
            row["metadata"]["repetition"] = n + 1
            row["task_id"] = f"case-01:r{n + 1}"
            rows.append(row)
        result = learning.candidates(rows, stack="PYTHON", task_class="implement", level=2, capabilities=[])[0]
        self.assertEqual(result["distinct_cases"], 1)
        self.assertFalse(result["eligible"])

    def test_quality_loss_missing_cost_and_unequal_cases_block_downgrade(self):
        for mutation in ("quality", "cost", "cases"):
            rows = self.evidence()
            row = next(r for r in rows if r["arm"] == "kit-adaptive")
            if mutation == "quality":
                row["outcome"] = "incorrect"
            elif mutation == "cost":
                row["attempts"][0]["cost"] = None
            else:
                row["metadata"]["case_id"] = "unmatched"
            result = self.recommend(rows)
            self.assertTrue(result is None or result["model"] == "large")

    def test_multi_model_recovery_is_not_attributed_as_single_model_success(self):
        row = measured(arm="kit-fixed")
        other = copy.deepcopy(row["attempts"][0])
        other["model"] = "escalation"
        row["attempts"].append(other)
        result = learning.candidates([row], stack="PYTHON", task_class="implement", level=2, capabilities=[])[0]
        self.assertFalse(result["eligible"])
        self.assertEqual(result["mixed_strategy_trials"], 1)
        self.assertEqual(result["cost_per_correct"], "2.00")

    def test_pending_and_reviewed_incomplete_trials_are_not_dropped(self):
        rows = self.evidence()
        row = next(r for r in rows if r["arm"] == "kit-adaptive")
        row.update(outcome="incomplete")
        row["metadata"]["review"] = "pending"
        groups = learning.candidates(rows, stack="PYTHON", task_class="implement", level=2, capabilities=[])
        small = next(g for g in groups if g["model"] == "small")
        self.assertEqual((small["trials"], small["pending_reviews"]), (20, 1))
        self.assertFalse(small["eligible"])
        row["metadata"]["review"] = "manual"
        small = next(g for g in learning.candidates(rows, stack="PYTHON", task_class="implement", level=2, capabilities=[]) if g["model"] == "small")
        self.assertEqual((small["trials"], small["correct"]), (20, 19))
        unknown = measured("unknown-model", arm="kit-adaptive", outcome="incorrect")
        unknown["attempts"] = [{"disposition": "inconclusive"}]
        groups = learning.candidates([*self.evidence(), unknown], stack="PYTHON", task_class="implement", level=2, capabilities=[])
        self.assertTrue(all(g["unattributed_trials"] == 1 and not g["eligible"] for g in groups))

    def test_immutable_history_and_explicit_rollback(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            path = root / "ai-kit/router/selection.json"
            path.parent.mkdir(parents=True)
            selection = {"schema": 1, "default_provider": None, "roles": {}, "local_models": {}}
            path.write_text(json.dumps(selection), encoding="utf-8")
            before = path.read_bytes()
            preview = learning.save_proposal(root, {"candidates": []})
            self.assertFalse(Path(preview["path"]).exists())
            saved = learning.save_proposal(root, {"candidates": []}, apply=True)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(saved, learning.save_proposal(root, {"candidates": []}, apply=True))
            selection["default_provider"] = "fixture"
            path.write_text(json.dumps(selection), encoding="utf-8")
            self.assertTrue(learning.restore_selection(root, saved["proposal_id"])["changed"])
            self.assertNotEqual(path.read_bytes(), before)
            learning.restore_selection(root, saved["proposal_id"], apply=True)
            self.assertEqual(path.read_bytes(), before)
            history = Path(saved["path"])
            history.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "modified"):
                learning.restore_selection(root, saved["proposal_id"])


class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.providers = {"fixture": {"roles": {"cheap": {"model": "small"}, "work": {"model": "large"}},
                                      "supported_efforts": {"cheap": ["low"], "work": ["low", "medium", "high"]}}}
        self.selection = {"schema": 1, "default_provider": "fixture", "roles": {}, "local_models": {}}

    def route(self, **kwargs):
        return adaptive.recommend_route("implement a feature", self.selection, self.providers, **kwargs)

    def test_modes_and_task_pin_precedence(self):
        with self.assertRaises(ValueError):
            self.route(mode="fixed")
        config = {"mode": "fixed", "project_pin": {"provider": "fixture", "model": "large", "effort": "medium"},
                  "task_pins": {"case": {"provider": "fixture", "model": "small", "effort": None}}}
        result = self.route(config=config, task_id="case")
        self.assertEqual((result["model"], result["effort"]), ("small", None))
        self.assertFalse(result["execution_confirmed"])
        result = self.route(config=config, task_id="case", model="large", effort="high")
        self.assertEqual((result["model"], result["effort"]), ("large", "high"))
        result = self.route(config=config, task_id="case", effort="low")
        self.assertEqual((result["model"], result["effort"]), ("small", "low"))
        with self.assertRaises(ValueError):
            self.route(mode="fixed", effort="low")

    def test_profiles_and_existing_effort_are_preserved(self):
        self.assertEqual(self.route(profile="economy")["effort"], "low")
        quality = self.route(profile="quality")
        self.assertEqual(quality["effort"], "high")
        self.assertTrue(quality["independent_review"])
        self.selection["roles"]["work"] = {"effort": "medium"}
        self.assertEqual(self.route(profile="quality")["effort"], "medium")

    def test_adaptive_only_recommends_from_comparable_declared_models(self):
        rows = LearningTests().evidence()
        result = self.route(mode="adaptive", records=rows, stack="PYTHON")
        # Fixture cheap model has only low; measured medium is not a supported control.
        self.assertEqual(result["model"], "large")
        self.providers["fixture"]["supported_efforts"]["cheap"].append("medium")
        result = self.route(mode="adaptive", records=rows, stack="PYTHON")
        self.assertEqual(result["model"], "small")
        self.assertEqual(result["recommendation_source"], "matched measurements")
        self.assertFalse(result["execution_confirmed"])
        self.providers["other"] = self.providers["fixture"]
        for row in rows:
            if row["arm"] == "kit-adaptive":
                row["attempts"][0]["provider"] = "other"
        self.assertEqual(self.route(mode="adaptive", records=rows, stack="PYTHON")["provider"], "fixture")
        self.selection["roles"]["escalation"] = "other"
        self.assertEqual(self.route(mode="adaptive", records=rows, stack="PYTHON")["provider"], "other")

    def test_adaptive_missing_data_keeps_current_recommendation(self):
        result = self.route(mode="adaptive")
        self.assertEqual(result["model"], "large")
        self.assertIn("Insufficient", result["adjustments"][-1])

    def test_capabilities_must_be_declared_even_with_measured_success(self):
        rows = LearningTests().evidence()
        for row in rows:
            row["metadata"]["capabilities"] = ["tool-use"]
        self.providers["fixture"]["supported_efforts"]["cheap"].append("medium")
        result = self.route(mode="adaptive", records=rows, stack="PYTHON", capabilities=["tool-use"])
        self.assertEqual(result["model"], "large")
        self.assertFalse(result["capabilities_verified"])
        self.providers["fixture"]["roles"]["cheap"]["capabilities"] = ["tool-use"]
        result = self.route(mode="adaptive", records=rows, stack="PYTHON", capabilities=["tool-use"])
        self.assertEqual(result["model"], "small")
        self.assertTrue(result["capabilities_verified"])
