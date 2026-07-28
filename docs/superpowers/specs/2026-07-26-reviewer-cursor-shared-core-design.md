# Reviewer Shared Core + Cursor Port Design

## Goal

Collapse the reviewer plugin onto one shared workflow and specialist prompt tree, then expose that core through thin harness adapters for Claude Code, Codex, Cursor, and opencode. Maximize shared behavior; keep harness files limited to discovery, permissions, and dispatch mechanics.

## Non-goals

- Changing the role set, scoring bands, risk tiers, or domain-detection rules except where required for cross-harness consistency.
- Vendoring Cursor built-ins (Bugbot, Security Review) or Superpowers.
- Auto-invoking the Cursor skill from ambient chat; invocation stays explicit.
- Merging pull requests under any path.

## Background

Today reviewer maintains three largely independent surfaces:

| Surface | Orchestrator | Specialist prompts |
| --- | --- | --- |
| Claude Code | `commands/review.md` (~25k) | `agents/*.md` |
| Codex | `skills/parallel-review/SKILL.md` (~9k) | `references/reviewers/*.md` |
| opencode | `opencode/commands/parallel-review.md` (~25k) | `opencode/agents/*.md` |

Claude and opencode agent bodies are nearly identical to each other; Codex prompts are rewritten. Orchestrators duplicate triage, depth selection, synthesis, scoring, and GitHub posting with drift risk. Cursor has no surface yet.

Shipwright PR [#9](https://github.com/psjostrom/agent-plugins/pull/9) establishes the preferred Cursor packaging pattern: `.cursor-plugin` manifests, `install-cursor.sh` symlinking into `~/.cursor/plugins/local/<name>`, shared skill tree, and a harness-specific `references/cursor.md` adapter.

## Architecture

### Canonical core

All review behavior lives under:

```text
plugins/reviewer/skills/parallel-review/
  SKILL.md
  agents/openai.yaml                 # Codex skill metadata (unchanged role)
  references/
    reviewer-contract.md
    scoring.md
    github-actions.md
    reviewers/*.md                   # sole specialist bodies
    codex.md
    cursor.md
    claude-code.md
    opencode.md
```

`SKILL.md` owns the shared workflow end-to-end. Harness adapters own only dispatch, tool/permission wiring, and harness-specific invocation syntax.

### Thin harness shells

| Harness | Entry | Specialist shells | Install / discovery |
| --- | --- | --- | --- |
| Codex | `.codex-plugin/plugin.json` → `./skills/` | none; prompts loaded from `references/reviewers/` | existing Codex marketplace |
| Cursor | `.cursor-plugin/plugin.json` → `./skills/` | none; same references | `install-cursor.sh` → `~/.cursor/plugins/local/reviewer` |
| Claude Code | `commands/review.md` (thin) | `agents/*.md` = frontmatter + read shared reviewer | existing Claude marketplace |
| opencode | `opencode/commands/parallel-review.md` (thin) | `opencode/agents/*.md` = frontmatter + read shared reviewer | existing `install-opencode.sh` |

### Rules

1. Behavior changes go only in the shared skill tree.
2. Harness files may differ only in discovery metadata, tool permissions, and dispatch mechanics.
3. Claude/opencode specialist shells must not re-host divergent specialist prose.
4. Role parity is required across all four harnesses. Cursor has no agent files; its parity is shared roles plus adapter wiring in `references/cursor.md` and `SKILL.md`.
5. Review mode remains read-only until findings are reported and the user chooses an action. Never merge.

## Shared workflow

`SKILL.md` defines these steps for every harness:

1. **Parse inputs** — PR number/URL, branch/base comparison, `quick` / `standard` / `deep` override, local/current changes, optional repository-relative path filters, stop-after-report.
2. **Resolve mode** — exactly one of PR, BRANCH, LOCAL, CURRENT PR. Stop if nothing to review.
3. **Resolve path scope** — repository-relative filters only; reject absolute/outside-repo paths; filter changed files before triage; stop if nothing in scope. Findings must identify defects in scoped changed code; related outside-scope reads are evidence-only.
4. **Gather context (read-only)** — for every changed file, read every `AGENTS.md` and `CLAUDE.md` from repo root through the file’s parent; apply broad-to-narrow; same-scope conflicts prefer `AGENTS.md`. Gather patches/metadata per mode without mutating staging (no `git add -N`).
5. **Triage risk** — one-line change summary; tier files Critical / Standard / Low; count changed lines; for diffs above 1,500 lines focus Critical+Standard (Guidelines and role-specific test checks may still inspect Low).
6. **Select depth and panel** — user overrides win; otherwise Quick / Standard / Deep rules and domain detection remain as today (Frontload, Agent Plugins, Strimma, Springa, Garmin CIQ). Always announce depth, reason, panel, and override instructions.
7. **Dispatch parallel reviewers** — read contract + selected prompts; spawn one self-contained child per role in one parallel batch; never silently simulate a multi-reviewer panel if subagents are unavailable (disclose and ask whether to continue single-agent).
8. **Synthesize and score** — follow `references/scoring.md`. Do not execute PR code during the review phase. Claims that would score above 75 require read-only verification; unverified claims stay at 50 or below.
9. **Decision gate** — report scored results; ask which findings to address; in PR mode also ask fix vs post comments. Act only after the user answers, following `references/github-actions.md`.

### Report shape (shared product behavior)

Promote into `SKILL.md` / `scoring.md` as needed so Claude/opencode fat-orchestrator output is not lost:

- Summary (2–4 sentences of intent/scope)
- Issues table for score > 25
- Probably Fine table for score ≤ 25
- Sequential numbering across both tables
- No raw per-agent dumps in user-facing output
- Scores are internal; never appear in GitHub comments

### GitHub posting (shared)

`references/github-actions.md` remains the posting contract. When collapsing Claude/opencode orchestrators, promote any intentional hard rules still missing from that file (for example self-PR APPROVE→COMMENT fallback with identical body) into the shared reference. Prefer Codex shared wording for stylistic differences.

## Harness adapters

Each adapter file is read only when that harness is active. It must not redefine triage, scoring, or role scope.

### Common adapter responsibilities

- How to identify the harness
- How to spawn a child (tool name, arguments, isolation flags)
- How to pass model/effort overrides when the live schema supports them
- How specialist tool allowlists / permissions are expressed
- What to do when the child API is missing or fails (retry once narrower; disclose missing coverage)

### Codex — `references/codex.md`

- Spawn built-in Codex subagents; `fork_context: false` when available
- Prefer read-oriented agent type; never combine explicit agent/model/reasoning override with a full-history fork
- Each child prompt includes: full contract, one specialist prompt, mode/target, summary, tiered files, guidance, patch or retrieval instructions, structured-findings-only requirement

### Cursor — `references/cursor.md`

- Packaging mirrors Shipwright PR #9: plugin skill discovery; skill name `parallel-review` with `disable-model-invocation: true`; users invoke it explicitly (for example “use parallel-review” / `/parallel-review` when Cursor surfaces the slash command)
- Inspect live `Task` schema; use `generalPurpose` (or the closest available type) with the full contract + one reviewer prompt inlined — Cursor has no custom `reviewer:*` subagent types
- Pass `model` only when a usable selector exists; never fabricate unsupported arguments
- Same decision gate, scoring, and no-merge rules as other harnesses
- If Task/subagents are unavailable: disclose and ask about single-agent fallback; do not silently simulate the panel

### Claude Code — `references/claude-code.md`

- Orchestrator entry remains `/reviewer:review` (and `/r` alias if already wired)
- Dispatch via `Agent` with `subagent_type` values `reviewer:<role>`
- Model flag behavior (`sonnet` default, `--opus` override) stays adapter-local
- Specialist agent files keep Claude frontmatter (`name`, `description`, `tools`) and instruct the agent to apply the matching shared reviewer file + contract

### opencode — `references/opencode.md`

- Entry remains `/parallel-review` on the `reviewer` primary agent
- Dispatch via `Task` with bare agent names; model selection via `opencode.json`, not per-call flags (`--opus` accepted as no-op with existing messaging)
- Specialist agent files keep opencode frontmatter (`mode`, `hidden`, `permission`) and instruct reading the matching shared reviewer file + contract
- Do not introduce Claude plugin prefixes or Codex skill syntax into opencode files

## Cursor packaging

Add:

```text
.cursor-plugin/marketplace.json          # repo marketplace; include reviewer (and shipwright if present)
plugins/reviewer/.cursor-plugin/plugin.json
install-cursor.sh                        # symlink plugins/<name> → ~/.cursor/plugins/local/<name>
```

`plugins/reviewer/.cursor-plugin/plugin.json` requirements:

- `name`: `reviewer`
- `skills`: `./skills/`
- relative paths only; no machine-specific data

`install-cursor.sh` requirements (align with Shipwright PR #9):

- Discover plugins that contain `.cursor-plugin/plugin.json`
- `install` / `uninstall` / `list`
- Symlink the whole plugin directory
- Refuse to replace a non-symlink destination
- Honor `CURSOR_PLUGINS_LOCAL` override (default `~/.cursor/plugins/local`)

If Shipwright’s Cursor port lands first, reuse the same installer rather than inventing a second one. If this work lands first, implement the installer in the shared form both plugins can use.

## Thin shell contracts

### Claude / opencode orchestrator shells

Must:

1. Identify the active harness
2. Instruct the controller to read `skills/parallel-review/SKILL.md` completely
3. Instruct the controller to read the matching harness adapter completely
4. Preserve harness-native argument parsing only where needed (`$ARGUMENTS`, flags)
5. Not duplicate triage tables, scoring rubrics, or posting recipes

### Claude / opencode specialist shells

Must:

1. Keep harness-required frontmatter and INTERNAL-only description wording
2. Point at `skills/parallel-review/references/reviewers/<role>.md` (path relative to plugin root as appropriate for the harness)
3. Require the common contract and structured findings / `No issues found`
4. Remain read-only (tools/permissions already enforce this)

### Content collapse policy

- Prefer Codex shared wording when Claude/opencode differ only stylistically
- Promote Claude/opencode-only behavioral rules into shared docs when they are product requirements
- After the port, do not keep three full orchestrator novels

## Validation

Extend `plugins/reviewer/scripts/validate_codex_reviewer.py` in place (keep the filename to minimize churn; broaden the module docstring to state it validates the full multi-harness reviewer bundle).

Required checks:

1. Shared tree exists: `SKILL.md`, contract, scoring, github-actions, all reviewer prompts, all four harness refs
2. Cursor manifest + root marketplace entry parse and point at `./plugins/reviewer` / `./skills/`
3. `install-cursor.sh` exists, is executable, and encodes symlink-only install safety
4. Role parity: every role in `REVIEWER_NAMES` is present in shared reviewers and wired in Claude/opencode shells + Cursor/Codex adapters
5. Thin-shell constraints: Claude/opencode agent bodies must reference the matching shared reviewer path and must not contain divergent full specialist prose (detect by requiring the shared-read instruction and forbidding large duplicated marker blocks, or by requiring body length below a documented ceiling plus the shared-read marker)
6. Existing Codex invariants remain: path scope, domain detection, decision gate, no merge, relative reference resolution from `SKILL.md`
7. Unit tests cover new Cursor/shared-core assertions

Run:

```sh
python3 plugins/reviewer/scripts/validate_codex_reviewer.py
python3 -m unittest plugins/reviewer/scripts/test_validate_codex_reviewer.py
python3 -m json.tool .cursor-plugin/marketplace.json
python3 -m json.tool plugins/reviewer/.cursor-plugin/plugin.json
```

## Documentation updates

- `AGENTS.md` — Cursor is a supported harness; role parity across four surfaces; `install-cursor.sh` and `.cursor-plugin/marketplace.json` documented; validator commands remain accurate
- Root `README.md` — Cursor install for reviewer
- `plugins/reviewer/README.md` — four-harness layout; shared-core ownership; Cursor invoke examples

## Migration plan

Execute in this order:

1. **Inventory gaps** — list Claude/opencode behavioral rules missing from the Codex shared tree (report tables, clean-review fallback, local untracked handling differences, etc.) and decide promote-vs-drop per the content policy above. Default: promote intentional product behavior; drop staging-mutating patterns such as `git add -N`.
2. **Normalize shared core** — update `SKILL.md`, `scoring.md`, and `github-actions.md` so they are the complete product contract.
3. **Add harness adapter refs** — `codex.md`, `cursor.md`, `claude-code.md`, `opencode.md`; slim `SKILL.md` dispatch section to “read the active harness adapter”.
4. **Thin Claude/opencode shells** — replace fat orchestrators and specialist bodies with adapters/shells.
5. **Add Cursor packaging** — manifests, marketplace entry, `install-cursor.sh`, `disable-model-invocation: true` on the shared skill, explicit-invoke docs.
6. **Docs** — AGENTS.md, READMEs.
7. **Validator + tests** — shared-core and Cursor checks; green suite required before done.

## Success criteria

- One shared workflow and one set of specialist prompts define review behavior.
- Claude, Codex, Cursor, and opencode can all run parallel-review with the same depth/panel/scoring/gate semantics.
- Cursor installs via `./install-cursor.sh install reviewer` and exposes explicit `parallel-review`.
- Validator passes, including thin-shell and Cursor packaging checks.
- No harness file reintroduces a full forked orchestrator or divergent specialist prompt body.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Thin Claude/opencode shells fail because agents cannot resolve shared paths | Document exact relative paths from each shell; validator asserts the path string |
| Cursor Task schema lacks model selectors | Adapter records limitation; dispatch without fabricated args; keep shared panel logic |
| Shipwright and reviewer race on `install-cursor.sh` / marketplace | Prefer one shared installer; merge-friendly marketplace array |
| Behavioral regressions while collapsing Claude posting rules | Promote hard rules into `github-actions.md` before deleting fat orchestrators; validator markers cover them |
| Accidental auto-invocation in Cursor | `disable-model-invocation: true` on the skill |

## Open decisions resolved in this design

- Packaging: Shipwright-style Cursor plugin install (`~/.cursor/plugins/local`)
- Sharing model: Approach 1 — canonical `skills/parallel-review/` + thin adapters
- Scope: Cursor port **and** full shared-core refactor for all harnesses (not Cursor-only)
