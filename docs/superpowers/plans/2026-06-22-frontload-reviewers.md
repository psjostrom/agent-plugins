# Frontload Reviewer Subagents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two Frontload-specific domain reviewers to the Codex parallel-review skill without changing the Claude reviewer surface.

**Architecture:** Extend the existing repository-level domain reviewer selection with a paired Frontload panel. Keep each role in a focused Markdown prompt, enforce prompt presence and orchestration wiring through the deterministic Python validator, and document support only in the Codex section of the shared README.

**Tech Stack:** Markdown Agent Skills, Python 3 validation, Codex plugin validation, Git.

---

### Task 1: Make the validator require Frontload coverage

**Files:**
- Modify: `plugins/reviewer/scripts/validate_codex_reviewer.py`

- [ ] **Step 1: Add the failing reviewer expectations**

Add `frontload-core` and `frontload-integration` to `REVIEWER_NAMES`. Add:

```python
"frontload-core": ("model-visible payload", "index freshness", "savings"),
"frontload-integration": ("CLI and MCP", "repository boundary", "unrelated user configuration"),
```

to `REVIEWER_MARKERS`.

In `validate_skill`, require the domain reviewer section to contain:

```python
for marker in (
    "Frontload: `frontload-core.md`, `frontload-integration.md`",
    "Domain reviewers run at Standard and Deep, never Quick.",
):
    require(marker in text, f"{skill_path}: missing domain reviewer invariant {marker!r}", errors)
```

- [ ] **Step 2: Run the validator to verify RED**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: FAIL because `frontload-core.md`, `frontload-integration.md`, and the Frontload orchestration entry do not exist.

### Task 2: Add the Frontload reviewer prompts and orchestration

**Files:**
- Create: `plugins/reviewer/skills/parallel-review/references/reviewers/frontload-core.md`
- Create: `plugins/reviewer/skills/parallel-review/references/reviewers/frontload-integration.md`
- Modify: `plugins/reviewer/skills/parallel-review/SKILL.md`

- [ ] **Step 1: Add Frontload Core Correctness**

Create a read-only prompt that applies `../reviewer-contract.md` and checks:

```text
index freshness; dossier/search ranking; budgeted read excerpts; diff accounting;
event aggregation; token, byte, and savings calculations; and consistency with
the actual model-visible payload.
```

Explicitly exclude installation, hooks, command policy, and packaging.

- [ ] **Step 2: Add Frontload Integration & Safety**

Create a read-only prompt that applies `../reviewer-contract.md` and checks:

```text
CLI and MCP parity; hook contracts; command rewriting and allowlists; repository
boundary enforcement; init/config merging; Codex packaging; inert behavior
outside initialized repositories; and preservation of unrelated user configuration.
```

Explicitly exclude recalculation of core savings metrics unless integration changes the measured payload.

- [ ] **Step 3: Wire repository-level selection**

Add this entry under Domain reviewers:

```markdown
- Frontload: `frontload-core.md`, `frontload-integration.md`
```

Keep the existing Standard/Deep-only rule unchanged.

- [ ] **Step 4: Run the deterministic validator to verify GREEN**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: `Codex reviewer validation passed.`

### Task 3: Document Codex-only Frontload support

**Files:**
- Modify: `plugins/reviewer/README.md`

- [ ] **Step 1: Add Codex domain reviewer documentation**

After the Codex behavior paragraph, add:

```markdown
For Standard and Deep reviews, Codex auto-detects Strimma, Springa, Garmin
Connect IQ, and Frontload repositories and adds the matching domain reviewers.
Frontload reviews add separate core-correctness and integration-safety agents.
```

Do not change the Claude section's existing project list.

- [ ] **Step 2: Verify Claude files remain untouched**

Run:

```bash
git diff --name-only e57f20f -- plugins/reviewer/agents plugins/reviewer/commands plugins/reviewer/.claude-plugin
```

Expected: no output.

### Task 4: Validate and refresh the Codex plugin

**Files:**
- Modify: `plugins/reviewer/.codex-plugin/plugin.json`

- [ ] **Step 1: Run all source validators**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
PYTHONPATH=/private/tmp/codex-validator-deps python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/reviewer
PYTHONPATH=/private/tmp/codex-validator-deps python3 /Users/psjostrom/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/reviewer/skills/parallel-review
```

Expected: all three commands exit 0.

- [ ] **Step 2: Refresh the local plugin cachebuster**

Run:

```bash
python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/reviewer
```

Expected: the Codex manifest version receives a new `+codex.<timestamp>` suffix.

- [ ] **Step 3: Re-run all validators after the manifest change**

Run the three commands from Step 1 again.

Expected: all three commands exit 0.

- [ ] **Step 4: Review the final diff**

Run:

```bash
git diff --check
git diff --stat e57f20f
git status --short
```

Expected: only the plan, two Codex reviewer prompts, Codex skill, validator, Codex README text, and Codex manifest are changed.

- [ ] **Step 5: Commit the implementation**

```bash
git add docs/superpowers/plans/2026-06-22-frontload-reviewers.md plugins/reviewer
git commit -m "Add Frontload reviewer subagents"
```
