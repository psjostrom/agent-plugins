# Parallel Code Review Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the Codex reviewer skill to `$parallel-review` and support optional repository-relative path scoping for PR, branch, and local reviews.

**Architecture:** Keep the `reviewer` plugin and Claude surface stable. Move the Codex skill directory to `skills/parallel-review`, update invocation metadata and documentation, and enforce the new naming and path-scope contract through the existing deterministic validator.

**Tech Stack:** Markdown Agent Skills, YAML UI metadata, JSON plugin metadata, Python 3 validation, Git.

---

### Task 1: Make the validator describe the new contract

**Files:**
- Modify: `plugins/reviewer/scripts/validate_codex_reviewer.py`

- [ ] **Step 1: Change validator expectations**

Set `SKILL_ROOT` to `skills/parallel-review`; require frontmatter `name: parallel-review`, display name `Parallel Code Review`, and `$parallel-review` in both skill and plugin prompts. Require the skill to define repository-relative path validation, changed-file filtering, empty-scope behavior, and the rule that findings remain in scoped changed code. Reject an active `skills/review-pr` directory.

- [ ] **Step 2: Run the validator to verify RED**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: FAIL because `skills/parallel-review` does not exist and active metadata still uses `$review-pr`.

### Task 2: Rename the skill and implement path scoping

**Files:**
- Move: `plugins/reviewer/skills/review-pr/` to `plugins/reviewer/skills/parallel-review/`
- Modify: `plugins/reviewer/skills/parallel-review/SKILL.md`
- Modify: `plugins/reviewer/skills/parallel-review/agents/openai.yaml`
- Modify: `plugins/reviewer/.codex-plugin/plugin.json`
- Modify: `plugins/reviewer/README.md`
- Modify: `docs/superpowers/specs/2026-06-18-codex-reviewer-plugin-design.md`

- [ ] **Step 1: Rename all skill files**

Move the orchestrator, metadata, shared references, and ten reviewer prompts without changing their specialist behavior.

- [ ] **Step 2: Update identity and invocation**

Use:

```yaml
name: parallel-review
```

and:

```yaml
interface:
  display_name: "Parallel Code Review"
  short_description: "Risk-based parallel review of PRs or local changes"
  default_prompt: "Use $parallel-review to review the current changes with parallel subagents."
```

- [ ] **Step 3: Add path-scope semantics**

Accept one or more repository-relative files or directories. Resolve them from the repository root, reject paths outside the repository, filter target changed files and patches before triage, stop when no changed paths match, and require every finding to point to scoped changed code.

- [ ] **Step 4: Update active documentation**

Replace active `$review-pr` examples and `skills/review-pr` paths with `$parallel-review` and `skills/parallel-review`. Preserve historical implementation-plan text.

- [ ] **Step 5: Verify GREEN**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
PYTHONPATH=/private/tmp/codex-validator-deps python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/reviewer
PYTHONPATH=/private/tmp/codex-validator-deps python3 /Users/psjostrom/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/reviewer/skills/parallel-review
```

Expected: all commands exit 0.

### Task 3: Refresh, reinstall, and verify

**Files:**
- Modify: `plugins/reviewer/.codex-plugin/plugin.json`

- [ ] **Step 1: Refresh the cachebuster**

Run:

```bash
python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/reviewer
```

- [ ] **Step 2: Reinstall**

Run:

```bash
codex plugin add reviewer@agent-plugins --json
```

- [ ] **Step 3: Verify installed source**

Confirm the active plugin points to `/Users/psjostrom/code/agent-plugins/plugins/reviewer`, the installed artifact matches source, `skills/parallel-review/SKILL.md` exists, and `skills/review-pr` does not.

- [ ] **Step 4: Commit**

```bash
git add docs plugins/reviewer
git commit -m "Rename Codex reviewer skill to parallel review"
```
