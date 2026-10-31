import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from fixture import ADAPTER, Project, story

from sanchin_validator.cli import collect_errors, main
from sanchin_validator.config import AdapterError, load_config
from sanchin_validator.markdown import parse_frontmatter


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.project.write("docs/index.md", "# Docs\n\n[stories superseded](stories-superseded.md)\n")
        self.project.write(
            "docs/stories-superseded.md",
            "# Superseded\n\n[Docs](index.md)\n\n<!-- sanchin:superseded-by:start -->\n<!-- sanchin:superseded-by:end -->\n",
        )
        self.project.write("app/features/thing.feature", FEATURE)
        self._trust_directory = tempfile.TemporaryDirectory()
        trust_env = mock.patch.dict("os.environ", {"SANCHIN_TRUST_FILE": f"{self._trust_directory.name}/trusted.json"})
        trust_env.start()
        self.addCleanup(trust_env.stop)

    def tearDown(self):
        self.project.close()
        self._trust_directory.cleanup()

    def trust(self, project=None):
        with redirect_stdout(io.StringIO()):
            main(["--project", str(project or self.project.root), "trust"])

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

    # --- fixes -------------------------------------------------------------

    def test_implemented_story_needs_a_date(self):
        self.project.write("docs/stories/story-1.md", story("ST-1", "implemented"))
        self.assertTrue(any("needs its 'date'" in error for error in self.errors("stories")))

    def test_legacy_story_needs_no_date(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER.replace("  superseded_index:", "  legacy: [docs/stories/story-1.md]\n  superseded_index:"),
        )
        self.project.write("docs/stories/story-1.md", story("ST-1", "implemented"))
        self.write_superseded_index()
        self.assertEqual(self.errors("stories", "plans"), [])

    def test_plan_answers_only_its_components_constitution(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER.replace("components: [app]", "components: [app, api]").replace(
                "globs: [docs/constitution/*.md]", "globs: [docs/constitution/*.md, 'docs/constitution/{component}/*.md']"
            ),
        )
        self.project.write("docs/constitution/tramp-data.md", "# Tramp data\n")
        self.project.write("docs/constitution/app/ui-state.md", "# UI state\n")
        self.project.write("docs/constitution/api/idempotency.md", "# Idempotency\n")
        plan = PLAN_IN_PROGRESS.replace("- tramp-data: n/a", "- tramp-data: n/a\n- ui-state: ok")
        self.project.write("docs/plans/app/p.md", plan)
        self.project.write("docs/plans/p.md", plan)
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/app/p.md, docs/plans/p.md\n"))
        errors = self.errors("plans")
        self.assertEqual([error for error in errors if "plans/app/p.md" in error], [])
        # A plan whose component can't be told from its path answers every component's rules.
        self.assertTrue(any("docs/plans/p.md" in error and "'idempotency'" in error for error in errors))

    def git(self, *arguments):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.project.root), *arguments],
            check=True,
            capture_output=True,
        )

    def close_story_in_git(self):
        self.project.write("docs/plans/p.md", PLAN_IMPLEMENTED)
        self.project.write(
            "docs/stories/story-1.md",
            story("ST-1", "implemented", "date: 2025-01-01\nplan: docs/plans/p.md\n"),
        )
        self.write_superseded_index()
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "close ST-1")

    def immutability_errors(self):
        return [error for error in self.errors("stories") if "edited after it was implemented" in error]

    def test_untouched_implemented_story_passes(self):
        self.close_story_in_git()
        self.assertEqual(self.immutability_errors(), [])

    def test_editing_an_implemented_story_fails(self):
        self.close_story_in_git()
        path = self.project.root / "docs/stories/story-1.md"
        path.write_text(path.read_text().replace("The first thing.", "Something else."))
        self.assertEqual(len(self.immutability_errors()), 1)

    def test_editing_an_implemented_storys_plan_fails(self):
        self.close_story_in_git()
        (self.project.root / "docs/plans/p.md").write_text(PLAN_IMPLEMENTED + "\nlater note\n")
        self.git("commit", "-q", "-am", "touch plan")
        self.assertIn("docs/plans/p.md", self.immutability_errors()[0])

    def test_story_closing_in_the_working_tree_is_not_yet_frozen(self):
        self.project.write("docs/stories/story-1.md", story("ST-1", "in progress", "plan: docs/plans/p.md\n"))
        self.project.write("docs/plans/p.md", PLAN_IN_PROGRESS)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "start ST-1")
        self.project.write(
            "docs/stories/story-1.md",
            story("ST-1", "implemented", "date: 2025-01-01\nplan: docs/plans/p.md\n"),
        )
        self.assertEqual(self.immutability_errors(), [])

    def git_hook(self, level, stdin=""):
        with mock.patch("sys.stdin", io.StringIO(stdin)), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return main(["--project", str(self.project.root), "git-hook", level])

    def test_pre_commit_hook_runs_gates_on_staged_files_only(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER_HEAD + "gates:\n  - {name: log, glob: '*.py', run: 'echo {file} >> ran.log', level: pre-commit}\n",
        )
        self.git("init", "-q", "-b", "main")
        self.project.write("app/staged.py", "x = 1\n")
        self.project.write("app/unstaged.py", "x = 1\n")
        self.git("add", "app/staged.py")
        self.assertEqual(self.git_hook("pre-commit"), 0)
        self.assertEqual((self.project.root / "ran.log").read_text().split(), ["app/staged.py"])

    def test_pre_push_hook_runs_gates_on_pushed_commits_and_the_check(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER_HEAD + "gates:\n  - {name: suite, glob: '*.py', run: 'echo run >> ran.log', level: pre-push}\n",
        )
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending"))
        self.write_superseded_index()
        self.git("init", "-q", "-b", "main")
        self.project.write("app/main.py", "x = 1\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "one")
        head = subprocess.run(["git", "-C", str(self.project.root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(self.git_hook("pre-push", f"refs/heads/main {head} refs/heads/main {'0' * 40}\n"), 0)
        self.assertEqual((self.project.root / "ran.log").read_text().split(), ["run"])
        self.project.write("docs/guide.md", "# Guide\n\nno navigation\n")
        self.assertEqual(self.git_hook("pre-push", ""), 1)

    def test_feature_in_another_language_is_traced(self):
        self.project.write(
            "app/features/thing.feature",
            "# language: fr\nFonctionnalité: chose\n\n  Règle: r\n\n    # ST-1: AC 1\n    @lent\n    Scénario: première chose\n      Soit rien\n",
        )
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending"))
        self.write_superseded_index()
        self.assertEqual(self.errors("stories"), [])

    def test_feature_that_does_not_parse_fails(self):
        self.project.write("app/features/thing.feature", "Feature: thing\n  Scenario: x\n    Given a\n    Gven typo after a step\n")
        self.assertTrue(any("does not parse as Gherkin" in error for error in self.errors("stories")))

    def test_unknown_merge_mode_is_rejected(self):
        self.project.write(".claude/sanchin.yaml", ADAPTER.replace("components: [app]", "components: [app]\nmerge: squash"))
        with self.assertRaises(AdapterError):
            load_config(self.project.root)

    def test_duplicated_story_id_fails(self):
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending"))
        self.project.write("docs/stories/story-2.md", story("ST-1", "pending"))
        self.assertTrue(any("id ST-1 is also used by" in error for error in self.errors("stories")))

    def test_frontmatter_comments_are_ignored(self):
        self.project.write(
            "docs/stories/story-1.md",
            story("ST-1", "pending            # pending | in progress | implemented", "# a comment line\n"),
        )
        self.write_superseded_index()
        self.assertEqual(self.errors("stories"), [])

    def test_frontmatter_keeps_link_anchors(self):
        fields, _ = parse_frontmatter("---\nplan: docs/plans/p.md#design  # why\n---\n")
        self.assertEqual(fields["plan"], "docs/plans/p.md#design")

    def test_loose_trace_comment_covers_nothing(self):
        self.project.write("app/features/thing.feature", "Feature: thing\n\n  # ST-1: AC 1\n  Background:\n    Given x\n")
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending"))
        self.assertTrue(any("trace comment is not above a scenario" in error for error in self.errors("stories")))

    def test_trace_comment_may_sit_above_tags(self):
        self.project.write("app/features/thing.feature", "Feature: thing\n\n  # ST-1: AC 1\n  @slow\n  Scenario: x\n")
        self.project.write("docs/stories/story-1.md", story("ST-1", "pending"))
        self.write_superseded_index()
        self.assertEqual(self.errors("stories"), [])

    def test_code_reference_matches_whole_path_segments(self):
        self.project.write("app/data.py", "x = 1\n")
        self.project.write("docs/guide.md", "# Guide\n\n[Docs](index.md)\n\nSee `a.py:1`.\n")
        self.project.write("docs/index.md", "# Docs\n\n[g](guide.md) [s](stories-superseded.md)\n")
        self.assertTrue(any("path not found: a.py" in error for error in self.errors("docs")))

    def test_suite_gate_runs_once_for_many_files(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER_HEAD + "gates:\n  - {name: suite, glob: '*.py', run: 'echo run >> runs.log', level: pre-push}\n",
        )
        main(["--project", str(self.project.root), "gates", "--level", "pre-push", "a.py", "b.py", "c.py"])
        self.assertEqual((self.project.root / "runs.log").read_text().count("run"), 1)

    def test_gate_timeout_is_a_failure_not_a_crash(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER_HEAD + "gates:\n  - {name: slow, glob: '*.py', run: 'sleep 5', level: pre-push, timeout: 1}\n",
        )
        self.assertEqual(main(["--project", str(self.project.root), "gates", "--level", "pre-push", "a.py"]), 1)

    def test_hook_reports_a_broken_adapter(self):
        self.project.write(".claude/sanchin.yaml", "version: 1\n")
        self.assertEqual(self.run_hook_code({"tool_input": {"file_path": str(self.project.root / "x.py")}}), 1)

    # --- hook --------------------------------------------------------------

    def test_hook_blocks_on_failing_edit_gate(self):
        self.trust()
        path = self.project.write("app/main.py", "# TODO later\n")
        output = self.run_hook({"tool_input": {"file_path": str(path)}})
        self.assertEqual(json.loads(output)["decision"], "block")
        self.assertIn("gate no-todo failed", output)

    def test_hook_does_not_run_untrusted_gates(self):
        self.project.write(
            ".claude/sanchin.yaml",
            ADAPTER_HEAD + "gates:\n  - {name: evil, glob: '*.py', run: 'touch ran'}\n",
        )
        path = self.project.write("app/main.py", "x = 1\n")
        output = json.loads(self.run_hook({"tool_input": {"file_path": str(path)}}))
        self.assertFalse((self.project.root / "ran").exists())
        self.assertIn("not trusted", output["systemMessage"])
        self.assertNotIn("decision", output)

    def test_changed_gates_need_trust_again(self):
        self.trust()
        self.project.write(".claude/sanchin.yaml", ADAPTER.replace("! grep -n TODO", "touch ran; ! grep -n TODO"))
        path = self.project.write("app/main.py", "x = 1\n")
        self.run_hook({"tool_input": {"file_path": str(path)}})
        self.assertFalse((self.project.root / "ran").exists())

    def test_hook_is_silent_without_adapter(self):
        (self.project.root / ".claude/sanchin.yaml").unlink()
        self.assertEqual(self.run_hook({"tool_input": {"file_path": str(self.project.root / "x.py")}}), "")

    def run_hook(self, payload):
        stdout = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))), redirect_stdout(stdout):
            main(["--project", str(self.project.root), "hook"])
        return stdout.getvalue()

    def test_hook_checks_the_worktree_that_holds_the_file(self):
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.project.root)]
        subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
        subprocess.run([*git, "add", "-A"], check=True)
        subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
        with tempfile.TemporaryDirectory() as outside:
            worktree = Path(outside) / "story"
            subprocess.run([*git, "worktree", "add", "-q", "-b", "story", str(worktree)], check=True)
            # The worktree's adapter differs from main's: only it has the gate.
            (self.project.root / ".claude/sanchin.yaml").write_text(ADAPTER_HEAD, encoding="utf-8")
            self.trust(worktree)
            edited = worktree / "app/main.py"
            edited.write_text("# TODO later\n", encoding="utf-8")
            output = self.run_hook({"tool_input": {"file_path": str(edited)}})
        self.assertIn("gate no-todo failed", output)

    def run_hook_code(self, payload):
        with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return main(["--project", str(self.project.root), "hook"])


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

ADAPTER_HEAD = ADAPTER[: ADAPTER.index("gates:")]

PLAN_IMPLEMENTED =PLAN_IN_PROGRESS + "\n## Implementation\n\nz\n\n## Review\n\nw\n"


if __name__ == "__main__":
    unittest.main()
