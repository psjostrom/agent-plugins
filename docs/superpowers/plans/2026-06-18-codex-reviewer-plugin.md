# Codex Reviewer Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a native Codex distribution of the existing reviewer plugin while preserving the Claude plugin and its review behavior.

**Architecture:** Package one explicit-invocation Codex skill under the existing `plugins/reviewer` directory. Keep the orchestration procedure in `SKILL.md`, move detailed scoring, GitHub posting, and specialist reviewer instructions into one-level references, and validate the bundle with a deterministic Python script before installing it from a repo-local Codex marketplace.

**Tech Stack:** Markdown Agent Skills, Codex plugin JSON, Codex marketplace JSON, YAML UI metadata, Python 3 validation, Git.

---

## File Structure

- Create `.agents/plugins/marketplace.json`
  - Exposes the repository-local `reviewer` plugin to Codex.
- Create `plugins/reviewer/.codex-plugin/plugin.json`
  - Defines Codex plugin metadata and the skills directory.
- Create `plugins/reviewer/skills/review-pr/SKILL.md`
  - Orchestrates target discovery, context gathering, triage, parallel review, synthesis, scoring, reporting, and the user decision gate.
- Create `plugins/reviewer/skills/review-pr/agents/openai.yaml`
  - Supplies Codex UI metadata and disables implicit invocation.
- Create `plugins/reviewer/skills/review-pr/references/reviewer-contract.md`
  - Defines the shared read-only role, findings schema, evidence rules, and scope discipline.
- Create `plugins/reviewer/skills/review-pr/references/scoring.md`
  - Defines deduplication, scoring, severity adjustments, verification, and final output.
- Create `plugins/reviewer/skills/review-pr/references/github-actions.md`
  - Defines safe opt-in fixing and GitHub inline-comment posting.
- Create `plugins/reviewer/skills/review-pr/references/reviewers/*.md`
  - Ports the ten existing Claude reviewer roles.
- Create `plugins/reviewer/scripts/validate_codex_reviewer.py`
  - Deterministically validates manifest, marketplace, skill, metadata, references, and role invariants.
- Modify `plugins/reviewer/README.md`
  - Documents Claude and Codex invocation and installation.
- Modify `README.md`
  - Describes the repository as plugins for multiple coding agents.

## Task 1: Add a Failing Bundle Validator

**Files:**
- Create: `plugins/reviewer/scripts/validate_codex_reviewer.py`

- [ ] **Step 1: Write the validator**

Implement a Python 3 script that checks:

```python
required_paths = [
    ".codex-plugin/plugin.json",
    "skills/review-pr/SKILL.md",
    "skills/review-pr/agents/openai.yaml",
    "skills/review-pr/references/reviewer-contract.md",
    "skills/review-pr/references/scoring.md",
    "skills/review-pr/references/github-actions.md",
]
reviewer_names = {
    "architecture",
    "bug-hunter",
    "error-edges",
    "garmin-ciq",
    "guidelines",
    "springa-api",
    "springa-react",
    "strimma-coroutine",
    "strimma-medical",
    "test-reviewer",
}
```

The script must also parse the JSON files, confirm plugin name `reviewer`, confirm `skills` points to `./skills/`, confirm the marketplace source is `./plugins/reviewer`, verify `allow_implicit_invocation: false`, reject placeholder text, and require every reviewer prompt to contain scope boundaries plus either `No issues found` or the shared contract reference.

- [ ] **Step 2: Run the validator and verify RED**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: non-zero exit because the Codex manifest and skill files do not exist.

- [ ] **Step 3: Commit the failing validator**

```bash
git add plugins/reviewer/scripts/validate_codex_reviewer.py
git commit -m "Add Codex reviewer bundle validator"
```

## Task 2: Add Codex Plugin and Marketplace Metadata

**Files:**
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/reviewer/.codex-plugin/plugin.json`

- [ ] **Step 1: Create the Codex manifest**

Use plugin name `reviewer`, version `1.1.0`, `skills: "./skills/"`, repository `https://github.com/psjostrom/agent-plugins`, and interface metadata for a code-quality plugin. Do not declare MCP servers, apps, hooks, or assets.

- [ ] **Step 2: Create the repo marketplace**

Create marketplace name `agent-plugins` with one available plugin:

```json
{
  "name": "reviewer",
  "source": {
    "source": "local",
    "path": "./plugins/reviewer"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Developer Tools"
}
```

- [ ] **Step 3: Run metadata validators**

Run:

```bash
python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/reviewer
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: the official plugin validator may pass, while the bundle validator still fails because the skill is not implemented.

- [ ] **Step 4: Commit metadata**

```bash
git add .agents/plugins/marketplace.json plugins/reviewer/.codex-plugin/plugin.json
git commit -m "Add Codex reviewer plugin metadata"
```

## Task 3: Implement the Review Orchestration Skill

**Files:**
- Create: `plugins/reviewer/skills/review-pr/SKILL.md`
- Create: `plugins/reviewer/skills/review-pr/agents/openai.yaml`
- Create: `plugins/reviewer/skills/review-pr/references/reviewer-contract.md`
- Create: `plugins/reviewer/skills/review-pr/references/scoring.md`
- Create: `plugins/reviewer/skills/review-pr/references/github-actions.md`

- [ ] **Step 1: Write the common reviewer contract**

Require read-only analysis, changed-code focus, exact code context, repository-relative paths, best-effort lines, category, concrete suggestion, explicit `No issues found`, no positive observations, and no unsupported claims.

- [ ] **Step 2: Write scoring and synthesis rules**

Port the original 0–100 scale, Critical `+10`, Low `-10`, root-cause deduplication, cross-agent evidence merging, and mandatory direct verification for scores above 75.

- [ ] **Step 3: Write GitHub action safety rules**

Require explicit user selection before any mutation. Prefer the GitHub connector for reads and thread state; use individual `gh api` calls for inline comments when standalone comment creation is required. Never expose scores in comments, refresh the head SHA, stop on the first failed inline comment, and never merge.

- [ ] **Step 4: Write `SKILL.md`**

The skill must:

1. Resolve PR, current-branch PR, or local mode.
2. Read applicable `AGENTS.md` and `CLAUDE.md`.
3. Gather diffs without mutating staging state.
4. Classify risk and choose Quick, Standard, or Deep depth.
5. Explicitly spawn selected built-in subagents in parallel with the common contract, one specialist prompt, and bounded review context.
6. Wait for every selected reviewer.
7. Synthesize, deduplicate, verify, score, and report.
8. Stop at the user decision gate.
9. Load `github-actions.md` only if the user requests fixes or comments.

Keep detailed role and posting material outside the main skill.

- [ ] **Step 5: Generate UI metadata**

Create `agents/openai.yaml` with:

```yaml
interface:
  display_name: "Review Pull Request"
  short_description: "Risk-based parallel code review"
  default_prompt: "Use $review-pr to review the current pull request with parallel subagents."
policy:
  allow_implicit_invocation: false
```

- [ ] **Step 6: Validate the skill**

Run:

```bash
python3 /Users/psjostrom/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/reviewer/skills/review-pr
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: skill validation passes; bundle validation still reports missing reviewer prompts.

- [ ] **Step 7: Commit the orchestrator**

```bash
git add plugins/reviewer/skills/review-pr
git commit -m "Add Codex review orchestration skill"
```

## Task 4: Port the Specialist Reviewers

**Files:**
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/architecture.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/bug-hunter.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/error-edges.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/garmin-ciq.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/guidelines.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/springa-api.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/springa-react.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/strimma-coroutine.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/strimma-medical.md`
- Create: `plugins/reviewer/skills/review-pr/references/reviewers/test-reviewer.md`

- [ ] **Step 1: Port universal reviewers**

Preserve the original scope boundaries and risk-tier focus for Bug Hunter, Guidelines, Error & Edge Cases, Architecture & Quality, and Test Reviewer. Replace Claude-specific tool references with instructions to inspect provided context and use read-only repository tools.

- [ ] **Step 2: Port domain reviewers**

Preserve the original Strimma, Springa, and Garmin checks, including medical temporal correctness, coroutine/process-death behavior, API compatibility, Next.js async request APIs, and Connect IQ release/device pitfalls.

- [ ] **Step 3: Run complete bundle validation**

Run:

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/reviewer
python3 /Users/psjostrom/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/reviewer/skills/review-pr
```

Expected: all commands exit 0.

- [ ] **Step 4: Commit reviewer prompts**

```bash
git add plugins/reviewer/skills/review-pr/references/reviewers
git commit -m "Port reviewer roles to Codex"
```

## Task 5: Document and Install the Plugin

**Files:**
- Modify: `plugins/reviewer/README.md`
- Modify: `README.md`

- [ ] **Step 1: Document Codex usage**

Document:

```text
Use $review-pr to review PR #6 with parallel subagents.
Use $review-pr to review the current local changes with a quick review.
Use $review-pr to review PR #6 deeply with parallel subagents.
```

Include repo marketplace installation:

```bash
codex plugin marketplace add /Users/psjostrom/code/agent-plugins
codex plugin add reviewer@agent-plugins
```

- [ ] **Step 2: Update repository description**

Change the root README from “Plugins for coding agents” to a concise explanation that the repository contains Claude Code and Codex plugins.

- [ ] **Step 3: Validate documentation and repository state**

Run:

```bash
git diff --check
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
```

Expected: both exit 0.

- [ ] **Step 4: Commit documentation**

```bash
git add README.md plugins/reviewer/README.md
git commit -m "Document Codex reviewer usage"
```

- [ ] **Step 5: Install the marketplace and plugin**

Run:

```bash
codex plugin marketplace add /Users/psjostrom/code/agent-plugins
codex plugin add reviewer@agent-plugins
```

If the local marketplace is already configured, use the corresponding upgrade or reinstall command rather than creating a duplicate entry.

## Task 6: Forward-Test Against PRs 6 and 7

**Files:**
- No repository changes expected.

- [ ] **Step 1: Run a clean, non-mutating review of PR #7**

Start a fresh Codex thread or non-interactive Codex run with:

```text
Use $review-pr to review PR #7 with parallel subagents. Stop after reporting findings. Do not edit files or post GitHub comments.
```

Verify Standard or Quick depth is chosen based on the actual risk classification, all selected reviewers complete, findings use the contract, and no mutation occurs.

- [ ] **Step 2: Run a non-mutating review of PR #6**

Use:

```text
Use $review-pr to review PR #6 deeply with parallel subagents. Stop after reporting findings. Do not edit files or post GitHub comments.
```

Verify Deep depth, complete reviewer fan-out, synthesis, scoring, and direct verification of any score above 75.

- [ ] **Step 3: Run final repository verification**

Run:

```bash
git status --short
git diff --check
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
python3 /Users/psjostrom/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/reviewer
python3 /Users/psjostrom/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/reviewer/skills/review-pr
```

Expected: only the known untracked `.DS_Store` files remain; every validator exits 0.
