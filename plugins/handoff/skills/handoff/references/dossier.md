# Dossier format

## Path

Write exactly one new file:

`.handoff/<slug>-YYYYMMDD-HHMM.md`

- `<slug>`: kebab-case from the mission (2–6 words). Fallback: `handoff`.
- Timestamp: local time at write (`YYYYMMDD-HHMM`).
- If the path exists, append `-2`, `-3`, … before `.md`.

## Shared spine (every tier)

Use these sections in order, with these headings:

1. `# Handoff: <short title>`
2. `## Receiver startup`
3. `## Mission`
4. `## Workspace`
5. `## State of work`
6. `## Decisions & hidden facts`
7. `## Risks & open questions`
8. `## Next actions`
9. `## Handoff metadata`
10. `## Resume prompt`

### Section contents

**Receiver startup** — Instruct the receiving agent to: read this file fully; verify workspace fields match reality; restate the next action; then begin work. Do not edit before that.

**Mission** — Goal, definition of done, explicit non-goals.

**Workspace** — Absolute worktree/repo path, branch, HEAD SHA, whether this is a linked git worktree, remotes if relevant, dirty/untracked summary (`git status --short`).

**State of work** — Done / in progress / not started. Key paths touched. Commands/tests run and results. If no code exists yet, say so and lean on mission + decisions.

**Decisions & hidden facts** — Anything important that is not obvious from the tree (rejected options, constraints, tribal knowledge, “we agreed X”).

**Risks & open questions** — Remaining unknowns and failure modes.

**Next actions** — Ordered list; depth follows tier emphasis below.

**Handoff metadata** — `created_at`, `tier` (`standard`|`frontier`), `recommended_tier` (if different from override), source harness if known, optional outgoing model note. Never invent secrets.

**Resume prompt** — A single fenced line the user can paste into a new chat, for example:

```text
Continue from the handoff dossier at .handoff/<filename>. Read it fully, verify the workspace, then execute the next actions for a <tier> agent.
```

## Emphasis by tier

Both tiers use the full spine. Change depth, not inventory.

| Area | **standard** | **frontier** |
| --- | --- | --- |
| Next actions | Step-by-step, file-level, exact commands, verify steps | Outcome-oriented; leave sequencing to the receiver when safe |
| Hidden facts | Implementation gotchas and local conventions | Architectural constraints and design rationale |
| Plan quality | Do not assume a good plan will be invented | Trust derivation; invest tokens in intent, tradeoffs, risks |
| Length | Longer when the path is mechanical but non-obvious | Shorter on how-to; denser on why / boundaries |
