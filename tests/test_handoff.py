import copy
import json
from pathlib import Path
import unittest

from agent_handoff_kit import create_handoff, schema_text, transition, validate_handoff


class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.record = create_handoff("Review", "Verify the implementation", "planner", "reviewer-agent", "human", handoff_id="h1")

    def test_full_lifecycle(self):
        self.record["next_actions"].append("Run tests")
        transition(self.record, "ready", "planner")
        transition(self.record, "accepted", "reviewer-agent")
        self.record["verification"].append("12 tests passed")
        transition(self.record, "completed", "human")
        self.assertEqual("completed", self.record["status"])
        self.assertEqual([], validate_handoff(self.record))

    def test_ready_requires_next_action(self):
        with self.assertRaisesRegex(ValueError, "at least one next action"):
            transition(self.record, "ready", "planner")
        self.assertEqual("draft", self.record["status"])

    def test_invalid_transition_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "draft -> completed"):
            transition(self.record, "completed", "human")

    def test_return_requires_reason(self):
        self.record["next_actions"].append("Review")
        transition(self.record, "ready", "planner")
        with self.assertRaisesRegex(ValueError, "return reason"):
            transition(self.record, "returned", "human")

    def test_validator_reports_malformed_artifact(self):
        bad = copy.deepcopy(self.record)
        bad["artifacts"].append({"kind": "unknown"})
        errors = validate_handoff(bad)
        self.assertTrue(any("uri" in error for error in errors))
        self.assertTrue(any("kind" in error for error in errors))

    def test_packaged_schema_matches_repository_schema(self):
        repository_schema = Path(__file__).parents[1] / "schema" / "handoff.schema.json"
        self.assertEqual(json.loads(repository_schema.read_text(encoding="utf-8")), json.loads(schema_text()))


if __name__ == "__main__":
    unittest.main()
