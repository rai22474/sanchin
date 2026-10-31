import io
import json
import unittest
from contextlib import redirect_stdout
from unittest import mock

from fixture import Project, story

from sanchin_validator.cli import collect_errors, main
from sanchin_validator.config import AdapterError, load_config


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.project.write("docs/index.md", "# Docs\n\n[stories superseded](stories-superseded.md)\n")
        self.project.write(
            "docs/stories-superseded.md",
            "# Superseded\n\n[Docs](index.md)\n\n<!-- sanchin:superseded-by:start -->\n<!-- sanchin:superseded-by:end -->\n",
        )
        self.project.write("app/features/thing.feature", FEATURE)

    def tearDown(self):
        self.project.close()

    def errors(self, *checks):
        return collect_errors(load_config(self.project.root), list(checks))

    def write_superseded_index(self):
        main(["--project", str(self.project.root), "superseded", "--write"])

    # --- adapter -----------------------------------------------------------

    def test_missing_adapter_is_reported(self):
        (self.project.root / ".claude/sanchin.yaml").unlink()
        with self.assertRaises(AdapterError):
            load_config(self.project.root)

    # --- docs --------------------------------------------------------------

    def test_doc_without_navigation_line_fails(self):
        self.project.write("docs/guide.md", "# Guide\n\nNo navigation.\n")
        self.assertTrue(any("missing navigation line" in error for error in self.errors("docs")))

    def test_broken_link_fails(self):
        self.project.write("docs/guide.md", "# Guide\n\n[Docs](index.md) · [gone](nowhere.md)\n")
        self.assertTrue(any("broken link nowhere.md" in error for error in self.errors("docs")))

    def test_stale_code_reference_fails(self):
        self.project.write("app/main.py", "print('one line')\n")
        self.project.write("docs/guide.md", "# Guide\n\n[Docs](index.md)\n\nSee `app/main.py:40`.\n")
        self.assertTrue(any("line 40 out of range" in error for error in self.errors("docs")))

    def test_index_must_link_every_document(self):
        self.project.write("docs/guide.md", "# Guide\n\n[Docs](index.md)\n")
        self.assertTrue(any("does not link guide.md" in error for error in self.errors("docs")))

    # --- stories -----------------------------------------------------------

    def test_unknown_state_fails(self):
        self.project.write("docs/stories/story-1.md", story("ST-1", "someday"))
        self.assertTrue(any("'someday' is not one of" in error for error in self.errors("stories")))

    def test_in_progress_story_needs_its_plan(self):
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress"))
        self.assertTrue(any("needs its 'plan'" in error for error in self.errors("stories")))

    def test_doubt_marker_blocks_leaving_pending(self):
        self.project.write("docs/plans/p.md", PLAN_IN_PROGRESS)
        self.project.write(
            "docs/stories/story-1.md",
            story("ST-1", "in progress", "plan: docs/plans/p.md\n", "\n[DOUBT: which unit?]\n"),
        )
        self.assertTrue(any("unresolved '[DOUBT:' marker" in error for error in self.errors("stories")))

    def test_doubt_marker_is_fine_while_pending(self):
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending", body="\n[DOUBT: which unit?]\n"))
        self.write_superseded_index()
        self.assertEqual(self.errors("stories"), [])

    def test_implemented_story_needs_every_criterion_cited(self):
        self.project.write("docs/plans/p.md", PLAN_IMPLEMENTED)
        self.project.write(
            "docs/stories/story-1.md",
            story("ST-1", "implemented", "date: 2026-02-01\nplan: docs/plans/p.md\nscenarios: app/features/thing.feature\n"),
        )
        self.assertTrue(any("criteria 2 not cited" in error for error in self.errors("stories")))

    def test_citation_of_missing_criterion_fails(self):
        self.project.write("app/features/other.feature", "Feature: other\n\n  # ST-1: AC 9\n  Scenario: nine\n")
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending"))
        self.assertTrue(any("cites criterion 9 of ST-1" in error for error in self.errors("stories")))

    def test_supersedes_must_point_to_an_existing_story(self):
        body = "\n**Supersedes:** criterion 1 of [ST-0](story-0.md)\n"
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending", body=body))
        self.assertTrue(any("supersedes 'story-0.md'" in error for error in self.errors("stories")))

    def test_superseded_index_must_be_regenerated(self):
        self.project.write("docs/stories/story-0.md", story("ST-0", "pending"))
        body = "\n**Supersedes:** criterion 1 of [ST-0](story-0.md)\n"
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending", body=body))
        self.assertTrue(any("superseded-by table is stale" in error for error in self.errors("stories")))
        self.write_superseded_index()
        self.assertEqual(self.errors("stories"), [])
        self.assertIn("[story-1]", (self.project.root / "docs/stories-superseded.md").read_text())

    def test_delta_before_implementation_needs_changed_scenarios_to_exist(self):
        body = "\n## Scenario delta\n\n- ~ app/features/thing.feature: a scenario that is not there\n"
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending", body=body))
        self.assertTrue(any("'a scenario that is not there' should exist" in error for error in self.errors("stories")))

    def test_delta_after_implementation_needs_removed_scenarios_gone(self):
        self.project.write("docs/plans/p.md", PLAN_IMPLEMENTED)
        body = "\n## Scenario delta\n\n- − app/features/thing.feature: first thing happens\n"
        extra = "date: 2025-01-01\nplan: docs/plans/p.md\n"
        self.project.write("docs/stories/story-1.md", story("ST-1", "implemented", extra, body))
        self.assertTrue(any("'first thing happens' should be gone" in error for error in self.errors("stories")))

    # --- plans -------------------------------------------------------------

    def test_plan_of_in_progress_story_needs_minimum_sections(self):
        self.project.write("docs/plans/p.md", "# Plan\n\n## Current state\n\nx\n")
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/p.md\n"))
        errors = self.errors("plans")
        self.assertTrue(any("missing section 'Design'" in error for error in errors))
        self.assertTrue(any("missing section 'Steps'" in error for error in errors))

    def test_open_questions_must_be_closed(self):
        plan = PLAN_IN_PROGRESS + "\n## Open questions\n\n- Q1 — still open\n"
        self.project.write("docs/plans/p.md", plan)
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/p.md\n"))
        self.assertTrue(any("still has open items" in error for error in self.errors("plans")))

    def test_constitution_checklist_answers_every_item(self):
        self.project.write("docs/constitution/tramp-data.md", "# Tramp data\n")
        self.project.write("docs/constitution/god-module.md", "# God module\n")
        plan = PLAN_IN_PROGRESS.replace("- tramp-data: n/a\n", "- tramp-data: exception, no reason\n")
        self.project.write("docs/plans/p.md", plan)
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/p.md\n"))
        errors = self.errors("plans")
        self.assertTrue(any("does not answer 'god-module'" in error for error in errors))
        self.assertTrue(any("must name the decision" in error for error in errors))

    def test_legacy_plan_is_skipped(self):
        adapter = self.project.root / ".claude/sanchin.yaml"
        adapter.write_text(adapter.read_text().replace("  rules_since: '2026-01-01'\n  required", "  rules_since: '2026-01-01'\n  legacy: [docs/plans/p.md]\n  required"))
        self.project.write("docs/plans/p.md", "# Plan written before the rules\n")
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/p.md\n"))
        self.assertEqual(self.errors("plans"), [])

    def test_compliant_plan_passes(self):
        self.project.write("docs/constitution/tramp-data.md", "# Tramp data\n")
        self.project.write("docs/plans/p.md", PLAN_IN_PROGRESS)
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/p.md\n"))
        self.assertEqual(self.errors("plans"), [])

    # --- hook --------------------------------------------------------------

    def test_hook_blocks_on_failing_edit_gate(self):
        path = self.project.write("app/main.py", "# TODO later\n")
        output = self.run_hook({"tool_input": {"file_path": str(path)}})
        self.assertEqual(json.loads(output)["decision"], "block")
        self.assertIn("gate no-todo failed", output)

    def test_hook_is_silent_without_adapter(self):
        (self.project.root / ".claude/sanchin.yaml").unlink()
        self.assertEqual(self.run_hook({"tool_input": {"file_path": str(self.project.root / "x.py")}}), "")

    def run_hook(self, payload):
        stdout = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))), redirect_stdout(stdout):
            main(["--project", str(self.project.root), "hook"])
        return stdout.getvalue()


FEATURE = """
Feature: thing

  # ST-1: AC 1
  Scenario: first thing happens
    Given nothing
"""

PLAN_IN_PROGRESS = """
# Plan

## 1. Current state

x

## 2. Design

y

## Constitution checklist

- tramp-data: n/a

## 3. Steps

- [ ] one
"""

PLAN_IMPLEMENTED = PLAN_IN_PROGRESS + "\n## Implementation\n\nz\n\n## Review\n\nw\n"


if __name__ == "__main__":
    unittest.main()
