# Shipwright Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a private-beta `shipwright` plugin to this repository that gives Codex and Claude Code one shared, strict, end-to-end development workflow.

**Architecture:** One platform-neutral Agent Skill owns the workflow and loads exactly one thin platform reference for runtime evidence, model routing, and dispatch syntax. Two native plugin manifests and the repository's two marketplace catalogs expose the same physical skill. A deterministic Python validator and unit tests enforce package shape and content contracts; committed behavioral scenarios define the separate model-behavior evaluation surface.

**Tech Stack:** Markdown Agent Skills, JSON plugin and marketplace manifests, YAML Codex UI metadata, Python 3 standard-library validation and `unittest`.

## Global Constraints

- Keep one shared workflow at `plugins/shipwright/skills/shipwright/SKILL.md`; do not duplicate platform workflows.
- Support Codex and Claude Code only; do not add opencode support.
- Require Superpowers 6.1.1 or newer, Codex CLI 0.139.0 or newer or an equivalent desktop runtime, and Claude Code 2.1.117 or newer.
- A compatible newer release proceeds with a recorded warning; block only below-minimum, explicitly incompatible, mixed-root, unverified, or missing dependency states.
- Keep the strict controller gate at Codex GPT-5.6 Sol / High-or-stronger and Claude Opus 4.7 / xhigh-or-stronger using current-session evidence rather than configuration claims.
- Use explicit worker model selection only when the harness exposes it; otherwise use one verified inherited-controller fallback and never claim an unproved tier.
- Use Argent 0.16.0 or compatible newer for Android/iOS QA and `agent-browser` 0.32.3 or compatible newer plus Playwright for web QA.
- Never install tools, push, open a PR, deploy, publish, contact production, use paid quota or credentials, or perform destructive actions without explicit authorization.
- Preserve independent task review, bounded remediation, whole-change review, fresh verification, and applicable real-world QA.
- Do not require personal Codex agent profiles; the plugin must work from its packaged configuration.
- Keep `.superpowers/` run outputs untracked; commit only `plugins/shipwright/evals/v1/scenarios.md` as the behavioral contract.

---

### Task 1: Cross-platform plugin package shell

**Files:**
- Create: `plugins/shipwright/.codex-plugin/plugin.json`
- Create: `plugins/shipwright/.claude-plugin/plugin.json`
- Create: `plugins/shipwright/skills/shipwright/SKILL.md`
- Create: `plugins/shipwright/skills/shipwright/agents/openai.yaml`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`

**Interfaces:**
- Produces plugin namespace `shipwright` and the shared skill discovery path `./skills/`.
- Produces public invocations `$shipwright:shipwright` for Codex and `/shipwright:shipwright` for Claude Code.
- Provides the physical skill and metadata paths consumed by Tasks 2 and 3.

- [ ] **Step 1: Generate disposable reference scaffolds**

Run both required authoring helpers in task-specific temporary directories, never against the repository:

```bash
plugin_tmp=$(mktemp -d)
skill_tmp=$(mktemp -d)
plugin_creator_root="<plugin-creator-root>"
skill_creator_root="<skill-creator-root>"
python3 "$plugin_creator_root/scripts/create_basic_plugin.py" shipwright --path "$plugin_tmp" --with-skills
python3 "$skill_creator_root/scripts/init_skill.py" shipwright --path "$skill_tmp" --resources references --interface 'display_name=Shipwright' --interface 'short_description=Strict end-to-end development workflow' --interface 'default_prompt=Use $shipwright to build this feature end to end with independent review and real verification.'
```

Expected: both commands exit 0 and create disposable `shipwright` scaffolds. Inspect their manifest and metadata shapes, then leave the temporary directories outside the repository.

- [ ] **Step 2: Create the Codex manifest**

Create this schema, using a timestamp cachebuster suffix only if the repository's Codex validator requires one:

```json
{
  "name": "shipwright",
  "version": "1.0.0",
  "description": "Strict end-to-end development with adaptive subagents, independent review, and real verification.",
  "author": {
    "name": "psjostrom",
    "url": "https://github.com/psjostrom"
  },
  "repository": "https://github.com/psjostrom/agent-plugins",
  "keywords": ["development", "subagents", "code-review", "verification", "qa"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Shipwright",
    "shortDescription": "Strict end-to-end development workflow",
    "longDescription": "Build approved work through adaptive implementation, independent iterative review, fresh verification, and applicable browser, mobile, CLI, or backend QA.",
    "developerName": "psjostrom",
    "category": "Developer Tools",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": ["Use $shipwright:shipwright to build this feature end to end with independent review and real verification."]
  }
}
```

- [ ] **Step 3: Create the Claude manifest**

```json
{
  "name": "shipwright",
  "version": "1.0.0",
  "description": "Strict end-to-end development with adaptive subagents, independent review, and real verification.",
  "author": {"name": "psjostrom"},
  "keywords": ["development", "subagents", "code-review", "verification", "qa"]
}
```

- [ ] **Step 4: Create the minimal discoverable skill and Codex metadata**

Create `SKILL.md` with only final frontmatter, title, core promise, exact invocation identifiers, and the platform-selection rule: load one platform reference and stop if the platform cannot be identified. Do not use placeholders, implementation-plan commentary, or the old public name.

Create `agents/openai.yaml`:

```yaml
interface:
  display_name: "Shipwright"
  short_description: "Strict end-to-end development workflow"
  default_prompt: "Use $shipwright:shipwright to build this feature end to end with independent review and real verification."
policy:
  allow_implicit_invocation: false
```

- [ ] **Step 5: Add both marketplace entries and the root README line**

Append a Codex entry with local source `./plugins/shipwright`, `AVAILABLE`, `ON_INSTALL`, and category `Developer Tools`. Append a Claude entry with source `./plugins/shipwright`, version `1.0.0`, the same description and author, keywords, and category `development`. Add a concise root README bullet documenting both invocations.

- [ ] **Step 6: Validate package syntax and discovery**

Run:

```bash
skill_creator_root="<skill-creator-root>"
plugin_creator_root="<plugin-creator-root>"
python3 -m json.tool plugins/shipwright/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/shipwright/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 "$skill_creator_root/scripts/quick_validate.py" plugins/shipwright/skills/shipwright
python3 "$plugin_creator_root/scripts/validate_plugin.py" plugins/shipwright
```

Expected: every command exits 0.

- [ ] **Step 7: Commit**

```bash
git add plugins/shipwright/.codex-plugin/plugin.json plugins/shipwright/.claude-plugin/plugin.json plugins/shipwright/skills/shipwright/SKILL.md plugins/shipwright/skills/shipwright/agents/openai.yaml .agents/plugins/marketplace.json .claude-plugin/marketplace.json README.md
git commit -m "Add Shipwright plugin package"
```

### Task 2: Shared workflow and platform contracts

**Files:**
- Modify: `plugins/shipwright/skills/shipwright/SKILL.md`
- Create: `plugins/shipwright/skills/shipwright/references/codex.md`
- Create: `plugins/shipwright/skills/shipwright/references/claude-code.md`
- Create: `plugins/shipwright/evals/v1/scenarios.md`

**Interfaces:**
- The shared skill owns all platform-neutral phase order, ledger, authorization, remediation, verification, and QA contracts.
- `references/codex.md` owns Codex evidence classes, tier normalization, native dispatch syntax, and inherited fallback behavior.
- `references/claude-code.md` owns Claude Code evidence classes, alias resolution, model/effort dispatch syntax, and inherited fallback behavior.
- `evals/v1/scenarios.md` is a human-readable behavioral contract, not a claim that static validation proves model behavior.

- [ ] **Step 1: Record the observed no-Shipwright baseline**

Read the three result files under `.superpowers/sdd/evals/baseline-*-result.md`. Preserve these observed lessons in the committed scenario descriptions without copying run transcripts: default behavior was already safe on missing runtime evidence and missing QA authorization, but it over-provisioned the integration reviewer and did not define Shipwright's stable ledger, retry, and terminal-state contracts. The new skill must add consistent orchestration and cost routing rather than duplicate generic safety prose.

- [ ] **Step 2: Write the shared skill**

Keep it below 500 lines. Use final frontmatter:

```yaml
---
name: shipwright
description: Use when the user explicitly requests Shipwright, full end-to-end development, autonomous implementation with subagents, or implementation plus independent iterative review and real verification; do not use for factual questions, read-only review, diagnosis without a requested fix, or tiny mechanical edits.
---
```

Implement these ordered sections: platform selection and preflight; dependency/capability check; trivial-work reduction; approved design and plan handoff through the required Superpowers skills; artifact exclusion and controller-owned ledger; task-local dispatch and adaptive routing; child-evidence transitions and `BLOCKED_RUNTIME`; task implementation/review/remediation; stable finding IDs and bounded terminal states; whole-change review; fresh verification; surface routing for web, Android/iOS, CLI, and backend; QA result states and `BLOCKED_QA`; authorization matrix; branch finishing. Reference Superpowers skills by namespaced skill name rather than copying them.

- [ ] **Step 3: Write the Codex reference**

Define Codex 0.139.0-or-newer capability probing, exact `gpt-5.6-sol` controller evidence and High-or-stronger effort ranks, Luna/Terra/Sol worker tiers, accepted current-turn evidence including matching-thread `turn_context`, `spawn_agent`/collaboration syntax when present, and the one-dispatch inherited-controller fallback when model selection is absent. State that the current generic spawn interface may not expose model selection and therefore must not be described as adaptive cost routing when it inherits Sol.

- [ ] **Step 4: Write the Claude Code reference**

Define Claude Code 2.1.117-or-newer capability probing, exact Opus 4.7 alias resolution and xhigh-or-stronger gate, Haiku/Sonnet/Opus tiers, Task/Agent dispatch with explicit model and effort only when exposed, child current-turn evidence, and the same one-dispatch inherited-controller fallback.

- [ ] **Step 5: Write behavioral scenarios v1**

Include every case in the design matrix with exact input condition, expected decision, forbidden decisions, required artifact/ledger delta, and pass criteria. State the no-guidance control plus five fresh-context wording repetitions and three fresh installed-session integrated repetitions policy. Mark unavailable harness runs as behaviorally unverified rather than statically passed.

- [ ] **Step 6: Validate and inspect stale names**

Run:

```bash
skill_creator_root="<skill-creator-root>"
python3 "$skill_creator_root/scripts/quick_validate.py" plugins/shipwright/skills/shipwright
rg -n 'legacy invocation|personal-profile dependency' plugins/shipwright .agents/plugins/marketplace.json .claude-plugin/marketplace.json README.md
wc -l plugins/shipwright/skills/shipwright/SKILL.md
```

Expected: skill validation exits 0; stale-name search exits 1 with no matches; shared skill is fewer than 500 lines.

- [ ] **Step 7: Commit**

```bash
git add plugins/shipwright/skills/shipwright/SKILL.md plugins/shipwright/skills/shipwright/references/codex.md plugins/shipwright/skills/shipwright/references/claude-code.md plugins/shipwright/evals/v1/scenarios.md
git commit -m "Implement Shipwright workflow"
```

### Task 3: Deterministic validator and regression tests

**Files:**
- Create: `plugins/shipwright/scripts/validate_shipwright.py`
- Create: `plugins/shipwright/scripts/test_validate_shipwright.py`

**Interfaces:**
- `validate_bundle(repo_root: Path) -> list[str]` returns every invariant failure without exiting early.
- `main() -> int` validates the real repository, prints `Shipwright validation passed.` on success, prints `Shipwright validation failed:` plus every error on failure, and returns 0 or 1.
- Tests copy the relevant repository bundle into a temporary directory and mutate the copy; they never edit the working tree fixture.

- [ ] **Step 1: Write failing validator tests**

Cover a valid bundle plus temporary broken copies for malformed JSON, missing manifests, missing shared skill/reference/metadata, wrong manifest or skill names, wrong Codex skills path, invalid Codex interface metadata, wrong marketplace paths/policies, wrong invocation identifiers, duplicate extra `SKILL.md` workflow surfaces, missing controller gates, missing child evidence/retry states, missing QA routes/states, missing authorization boundaries, stale public names/profile dependencies, and absent committed scenario cases.

Run:

```bash
python3 -m unittest plugins/shipwright/scripts/test_validate_shipwright.py
```

Expected: FAIL because `validate_shipwright.py` does not exist.

- [ ] **Step 2: Implement the validator**

Use only the Python standard library. Parse JSON rather than matching it as text. Parse `SKILL.md` frontmatter sufficiently to verify the exact skill name and require only the content markers that represent package contracts; do not present token checks as behavioral proof. Restrict the stale-name scan to `plugins/shipwright`, the two `shipwright` marketplace entry objects, and the Shipwright README bullet so historical design documents do not fail validation.

- [ ] **Step 3: Run focused tests and the validator**

```bash
python3 -m unittest plugins/shipwright/scripts/test_validate_shipwright.py
python3 plugins/shipwright/scripts/validate_shipwright.py
```

Expected: all unit tests pass and validator prints `Shipwright validation passed.`

- [ ] **Step 4: Run repository regression validation**

```bash
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
python3 -m unittest plugins/reviewer/scripts/test_validate_codex_reviewer.py
```

Expected: reviewer validation passes and 8 unit tests pass.

- [ ] **Step 5: Commit**

```bash
git add plugins/shipwright/scripts/validate_shipwright.py plugins/shipwright/scripts/test_validate_shipwright.py
git commit -m "Validate Shipwright plugin bundle"
```

### Task 4: Installed-session behavioral smoke evaluation

**Files:**
- Modify only if an observed failure requires correction: `plugins/shipwright/skills/shipwright/SKILL.md`
- Modify only if an observed failure requires correction: `plugins/shipwright/skills/shipwright/references/codex.md`
- Modify only if an observed failure requires correction: `plugins/shipwright/skills/shipwright/references/claude-code.md`
- Run artifacts: `.superpowers/sdd/evals/<run-id>/` (untracked)

**Interfaces:**
- Produces an evidence report separating static validation, Codex behavioral results, Claude Code behavioral results, and unavailable surfaces.
- Any tracked correction returns through Task 3 validation and an independent task review before completion.

- [ ] **Step 1: Install or load only already-authorized local plugin surfaces**

Use the repository marketplace or direct local plugin loading supported by the current harness. Do not publish, push, edit personal plugin state beyond the existing local-development flow, or install missing external tools without authorization.

- [ ] **Step 2: Run fresh-context Codex smoke cases**

At minimum exercise a controller reject case, inherited-routing case, bounded-remediation case, and missing-web/mobile-tool authorization case. Store prompt, raw output, classification, runtime evidence, and redactions under the untracked eval run directory.

- [ ] **Step 3: Run Claude Code smoke cases when the harness is available**

Use the same minimum case set in fresh sessions. If Claude Code or the local plugin-loading surface is unavailable, record `behaviorally unverified` with the exact missing capability; do not substitute Codex or static validation.

- [ ] **Step 4: Remediate observed contract failures once**

Make the smallest wording correction supported by the failing raw output, rerun the affected case, then rerun all Task 3 commands. Do not add hypothetical prose for cases whose controls already behaved correctly.

- [ ] **Step 5: Commit corrections only when tracked files changed**

```bash
git add plugins/shipwright/skills/shipwright/SKILL.md plugins/shipwright/skills/shipwright/references/codex.md plugins/shipwright/skills/shipwright/references/claude-code.md
git commit -m "Refine Shipwright behavior"
```

Skip the commit when the smoke evaluation required no tracked correction.
