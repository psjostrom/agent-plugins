# Handoff Plugin Design

## Goal

Add a cross-platform **handoff** plugin that writes a self-contained handoff dossier so a fresh agent can continue a specific task without the prior conversation’s polluted (or expensive) context. The skill recommends a target agent tier (**standard** or **frontier**), applies matching dossier emphasis, and supports explicit overrides. Create-only: no separate takeover/consume skill.

## Non-goals

- No takeover / resume skill; the dossier itself is the handoff contract.
- No automatic dispatch or model switching of the next agent (soft receiver tier gate in the dossier only — under-tier agents must stop and ask; harnesses cannot hard-block model selection).
- No Shipwright ledger coupling (a Shipwright path may appear as a workspace fact if relevant).
- No committing dossiers to git; local exclude of `.handoff/` only.
- No mutating the dirty worktree as part of handoff (no stash/commit/cleanup).
- No rewriting or summarizing the full chat transcript into the dossier; capture what the next agent needs to continue, verified against the workspace when cheap.

## Background

Use cases:

1. Outgoing agent is losing coherence from context pollution → hand off to a fresh session.
2. Frontier agent finished judgment-heavy work → continue cheaper on a **standard** agent.
3. Remaining work is still ambiguous / architectural → hand off to a **frontier** agent with intent-heavy context.

Packaging follows the reviewer shared-core / Shipwright pattern: one shared skill tree, thin harness adapters, marketplace + install hooks for Claude Code, Codex, Cursor, and opencode.

## Decisions (locked)

| Topic | Choice |
| --- | --- |
| Artifact location | `.handoff/<slug>-YYYYMMDD-HHMM.md` in the repo, locally gitignored |
| Create vs consume | Create-only; dossier includes receiver startup instructions **with a soft tier capability gate** |
| Packaging | Standalone `plugins/handoff/` |
| Shared vs harness | ~99% shared behavior in `skills/handoff/`; thin adapters only |
| Tier confirmation | Always ask unless user already passed `/handoff standard` or `/handoff frontier` |
| Invocation | Explicit preferred; agent may *offer* handoff when appropriate; never auto-run without user yes |
| Mode model | Shared dossier spine + tier emphasis (not two divergent templates) |
| Tier names | `standard` and `frontier` (not model-branded) |

## Architecture

### Canonical core

All behavior lives under:

```text
plugins/handoff/
  skills/handoff/
    SKILL.md
    agents/openai.yaml
    references/
      dossier.md
      tier-selection.md
      claude-code.md
      codex.md
      cursor.md
      opencode.md
```

| File | Responsibility |
| --- | --- |
| `SKILL.md` | End-to-end workflow: offer/invoke, gather, tier resolve, exclude, write, close out |
| `references/dossier.md` | Shared section spine + **standard** vs **frontier** emphasis rules + resume-prompt shape |
| `references/tier-selection.md` | Recommendation heuristics and override parsing |
| `references/<harness>.md` | Invocation syntax, argument parsing quirks, discovery only — no divergent workflow |

### Thin harness shells

| Harness | Entry | Install / discovery |
| --- | --- | --- |
| Codex | `.codex-plugin/plugin.json` → `./skills/` | `.agents/plugins/marketplace.json` |
| Cursor | `.cursor-plugin/plugin.json` → `./skills/` | `.cursor-plugin/marketplace.json` + `install-cursor.sh` |
| Claude Code | `commands/handoff.md` (thin) → read `SKILL.md` + `references/claude-code.md` | `.claude-plugin/marketplace.json` |
| opencode | `opencode/commands/handoff.md` (thin) → resolve shared skill root, read `SKILL.md` + `references/opencode.md` | `install-opencode.sh` |

### Rules for adding harnesses

1. Behavior changes go only in `skills/handoff/` (`SKILL.md` + shared references).
2. Harness files may differ only in discovery metadata, permissions, invocation syntax, and how they locate/read the shared skill.
3. Claude/opencode command shells must not re-host divergent workflow prose.
4. A new harness = thin adapter + marketplace/install wiring + one `references/<harness>.md` + validator updates. No behavior rewrite.

### Layout (full)

```text
plugins/handoff/
  .claude-plugin/plugin.json
  .codex-plugin/plugin.json
  .cursor-plugin/plugin.json
  commands/handoff.md
  opencode/commands/handoff.md
  skills/handoff/
    SKILL.md
    agents/openai.yaml
    references/
      dossier.md
      tier-selection.md
      claude-code.md
      codex.md
      cursor.md
      opencode.md
  scripts/validate_handoff.py
  scripts/test_validate_handoff.py
```

Also update:

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.cursor-plugin/marketplace.json`
- `AGENTS.md` (brief plugin mention + validator commands)
- Root README only if it already enumerates plugins

## Tiers

| Tier | Name | Example models (illustrative, not exhaustive) |
| --- | --- | --- |
| Mid-capability | **standard** | Claude Sonnet, GPT 5.6 Terra, Composer 2.5, … |
| High-capability | **frontier** | Claude Opus, Grok 4.5, GPT 5.6 Sol, … |

Overrides and aliases:

- Primary flags: `standard`, `frontier`

## Workflow

1. **Invoke or offer**
   - Explicit: `/handoff`, `/handoff standard`, `/handoff frontier` (and platform equivalents: `$handoff:handoff`, `/handoff:handoff`, etc.).
   - Ambient: agent may offer handoff when context is polluted or a cost step-down fits; never execute the write workflow without user confirmation.
   - Skill metadata must remain discoverable enough to offer (do **not** set `disable-model-invocation: true`). `SKILL.md` must forbid silent auto-execution.

2. **Gather facts (prefer verify)**
   Capture what the receiver needs: repo root, worktree path if any, branch, HEAD, dirty/untracked summary, mission, done vs not, decisions/hidden facts, risks, commands that matter. Prefer cheap tool verification over chat memory for workspace facts. If there is no code yet, the dossier is still valid — lean harder on mission, decisions, and next actions.

3. **Resolve target tier**
   - Explicit override in the invoke args → use it; **no** confirmation ask.
   - Else recommend using `tier-selection.md`, then ask: `I recommend a <tier> agent for this one — do you agree?`
   - Proceed only after agreement or an explicit override answer.

4. **Ensure local exclude, then author dossier**
   - Before writing any `.handoff/` path, establish repository-local exclusion of `.handoff/` via `git rev-parse --git-path info/exclude` (Shipwright-style). Never edit a global gitignore. Re-check with `git check-ignore`. If exclusion cannot be established, stop and ask before using an alternate location.
   - Write `.handoff/<slug>-YYYYMMDD-HHMM.md` using the shared spine and the chosen tier’s emphasis.

5. **Close out**
   - Report absolute or repo-relative path, chosen tier, and a one-line paste-ready resume prompt for the next agent.
   - Stop. Do not continue the original implementation task unless the user asks.

### Failure behavior

Stop and ask (do not write a partial dossier) when:

- Workspace / git root cannot be identified
- Local `.handoff/` exclusion cannot be established and no alternate was approved
- User rejects the recommended tier without choosing the other tier
- Required facts for a useful handoff are unknown and the user cannot supply them

## Dossier content

### Filename

`.handoff/<slug>-YYYYMMDD-HHMM.md`

- `<slug>`: short kebab-case task hint from the mission (fallback `handoff`)
- Timestamp: local time at write

### Shared spine (every dossier)

1. **Receiver startup** — **tier gate first** (classify live model vs metadata `tier`; under-tier / Auto / unknown for `frontier` → stop and ask to switch or await `proceed anyway`; do not explore or edit until then); then read fully; verify workspace; restate next action before editing
2. **Mission** — goal, definition of done, explicit non-goals
3. **Workspace** — repo, worktree path, branch, HEAD, remotes if relevant, dirty/untracked summary
4. **State of work** — done / in progress / not started; key paths; tests/commands run and results
5. **Decisions & hidden facts** — not obvious from code alone (rejected options, constraints, tribal knowledge)
6. **Risks & open questions**
7. **Next actions** — ordered; concrete enough for the chosen tier
8. **Handoff metadata** — created-at, source harness if known, recommended/chosen tier, optional outgoing model note
9. **Resume prompt** — one copy-paste block for the next chat (absolute dossier path, worktree, branch, **Required tier**, and an explicit stop-if-under-tier instruction)

### Emphasis by tier

| Area | **standard** | **frontier** |
| --- | --- | --- |
| Next actions | Step-by-step, file-level, commands, verify steps | Outcome-oriented; leave sequencing to the receiver when safe |
| Hidden facts | Implementation gotchas and local conventions | Architectural constraints and design rationale |
| Plan quality | Do not assume a good plan will be invented | Trust derivation; invest tokens in intent, tradeoffs, risks |
| Length | Longer when the path is mechanical but non-obvious | Shorter on how-to; denser on why / boundaries |

Both tiers still include the full spine. Emphasis is depth and wording, not dropping sections.

### Tier recommendation heuristics

Prefer **standard** when:

- Remaining work is bounded implementation with clear interfaces
- Design/judgment is largely settled and this is a cost step-down
- Outgoing agent mostly finished the ambiguous part

Prefer **frontier** when:

- Architecture or approach is still open
- Ambiguity, cross-system debugging, or high risk remains
- The handoff is mostly “figure out the right approach”

When unsure, recommend **standard** (cheaper continuation default).

## Skill description (intent)

Third-person, WHAT + WHEN, including offer triggers, for example:

> Creates a self-contained handoff dossier for continuing work in a fresh agent session at standard or frontier capability. Use when the user invokes /handoff, asks for a handoff, context is polluted, or work should continue on a cheaper or stronger model.

Exact final string is set during implementation and locked in the validator.

## Validation

`plugins/handoff/scripts/validate_handoff.py` (+ unit tests) must enforce:

- Shared skill tree and required references exist
- All four harness adapters exist and point at the shared core (thin Claude/opencode shells; no divergent workflow tables)
- Plugin manifests parse and agree on name/description basics
- Marketplace entries include `handoff` for Codex, Claude, and Cursor
- Tier names `standard` / `frontier` appear in shared skill/references as specified
- Invocation strings documented per harness

Commands (also document in `AGENTS.md`):

```sh
python3 plugins/handoff/scripts/validate_handoff.py
python3 -m unittest plugins/handoff/scripts/test_validate_handoff.py
```

## Success criteria

- Invoking the skill on any of the four harnesses produces one locally-ignored markdown dossier under `.handoff/` following the shared spine.
- Tier override skips confirmation; recommendation path always confirms.
- Standard vs frontier dossiers differ in emphasis as specified, not in section inventory.
- Receiver startup and resume prompt instruct under-tier / Auto / unknown models to stop before work on a `frontier` dossier (soft gate; user may override with `proceed anyway`).
- Adding a fifth harness requires only thin adapter + reference + validator/marketplace updates.
- Validator passes on a complete bundle.

## Open implementation details (non-blocking)

These may be chosen during implementation without revisiting product design:

- Exact slugification rules and collision handling (append suffix if file exists)
- Exact resume-prompt wording template
- Whether Claude also exposes the skill via skills directory in addition to `commands/handoff.md` (prefer both if the Claude plugin layout allows; command remains the primary slash entry)
- How aggressive ambient “offer” wording is in the description vs body
