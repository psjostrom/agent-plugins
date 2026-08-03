# Plugin findings — 2026-08-03

Developer-facing findings from installing this marketplace into Claude Code and
exercising one plugin at a time. Each finding records what was observed, the
evidence, and whether it is fixed or still open.

Baseline: marketplace cache at `main` `c298d6c`. Claude Code 2.1.220,
Superpowers 6.2.0, active session Opus 5 (`claude-opus-5[1m]`).

## Shipwright

### S1 — Controller gate pinned one exact model version — FIXED

`skills/shipwright/references/claude-code.md` accepted only exact model ID
`claude-opus-4-7`, or alias `opus` resolved to Opus 4.7, and stated that a
"future model, renamed model, or generic family label is not accepted until
this reference explicitly allowlists it from first-party compatibility
evidence."

Effect: every Opus release after 4.7 failed the controller gate, so
`/shipwright:shipwright` stopped at preflight on an Opus 5 session and demanded
a downgrade. An allowlist keyed to exact versions guarantees the plugin breaks
on every model release, and the failure mode is a hard stop rather than a
warning.

Replaced with a numeric version floor: resolved Opus family at version `4.6` or
newer, effort rank `xhigh` or stronger, with a higher major version meeting the
floor regardless of minor version. Context-size suffixes such as `[1m]` are
explicitly capability-neutral. Rejection still covers non-Opus families, Opus
below the floor, and unresolved evidence including the bare word `opus`.

Changed: `skills/shipwright/references/claude-code.md`,
`evals/v1/claude-code-runbook.md`, `evals/v1/scenarios.md`
(`gate-claude-pass`, `gate-claude-reject`), and the corresponding
`scripts/validate_shipwright.py` markers plus
`scripts/test_validate_shipwright.py` fixtures. Validator and its 57 unit tests
pass. Still static-only; no behavioral gate pass observed yet.

### S2 — The same brittleness remains on Codex and Cursor — OPEN

Codex pins exact `gpt-5.6-sol` and Cursor pins `Grok 4.5`
(`scripts/validate_shipwright.py:900`, `:922`). Cursor's gate is already
expressed as a resolved *family* rather than an exact build, so Claude Code was
the strictest of the three. Both will fail the same way S1 did on the next
provider release.

Recommend applying the S1 floor treatment per harness. Deliberately not changed
here — one plugin surface at a time, and neither harness was exercised.

### S3 — Worker-family order does not say version is irrelevant — FIXED

`skills/shipwright/references/claude-code.md` normalized worker families as
`Haiku < Sonnet < Opus`, which is version-agnostic and correct, but the same
section rejected any "unknown, generic, future, or unallowlisted family", which
read as though an Opus 5 *worker* might be "future" and therefore unverified.

Fixed alongside S13: the worker section now states that family alone governs
worker routing, version comparison applies only at the controller gate, and a
newer allowlisted Haiku/Sonnet/Opus worker is not unverified merely for being
newer. The word `future` was dropped from the family-rejection list.

### S4 — `environment-seed.md` is unparseable when the checkout is dirty — OPEN

The eval runbook writes the seed as flat `key=value` lines
(`evals/v1/claude-code-runbook.md`), but `shipwright_status` carries the full
`git status --short` output. On a dirty checkout the value spills across
multiple lines with no delimiter or terminator, so a reader cannot tell where
the status ends and `shipwright_plugin_source` begins.

Observed with a 6-entry dirty tree: the seed became 9 lines for 4 keys. The
runbook nonetheless calls the seed "the authoritative recorded checkout
identity" and instructs the agent to record `shipwright_commit` and
`shipwright_status` from it.

Fix by fencing the status block, indenting continuation lines, or emitting an
explicit terminator.

### S5 — Setup block and failure path verified — NO ACTION

The `## Prerequisites` shell block extracts and runs as written. With no
credential exported it fails at exactly the documented step
("select one explicit Claude credential"), prints the `UNVERIFIED` instruction,
and does not launch Claude. Fixture mechanics were exercised separately without
credentials: temp repo init, `evaluation-input/` copies, `.superpowers/`
exclusion, seed write, and `check-ignore` verification all succeed.

### S6 — No Codex eval runbook — OPEN

`evals/v1/` contains `claude-code-runbook.md` and `cursor-runbook.md` only, but
the README lists Codex as a supported Shipwright harness and the shared skill
ships `references/codex.md`. Codex behavior therefore has no committed
evaluation contract.

### S7 — Validator asserts substrings, not gate semantics — OPEN, LOW

`_require_markers` only checks literal substring presence, so a future edit
could reintroduce an exact-version pin and still pass validation as long as the
marker strings survive. Optional hardening: assert the floor language, or
assert that no `claude-opus-<n>-<n>` literal appears as an acceptance
condition.

### S8 — Documented validation commands dirty the working tree — OPEN, LOW

`python3 -m unittest plugins/shipwright/scripts/test_validate_shipwright.py`
creates `plugins/shipwright/scripts/__pycache__/`, which is not ignored, so the
repo's own documented validation step leaves the tree dirty. This also feeds
S4, since the eval seed then records a dirty status. Add `__pycache__/` to
`.gitignore`.

### S9 — Full runbook not executed — BLOCKED

The 18-case evaluation was not run. It requires a separately authorized Claude
account plus exactly one of `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`
(neither is set in the environment), and the case list demands fresh sessions
with repetitions to 3/3 for hard gates and safety boundaries. Per the runbook's
own rubric, every case is `UNVERIFIED` until that runs. The S1 fix is validated
statically only; no behavioral evidence exists for it yet.

The QA tool floors are no longer a blocker: `agent-browser` is now 0.33.2
(floor 0.32.3) and `@swmansion/argent` 0.18.0 (floor 0.16.0). Both had to be
installed from the public npm registry, because the machine's default registry
does not carry them.

### S10 — The hand-rolled runbook duplicates a native, cost-capped eval runner — OPEN, HIGH VALUE

**Corrected recommendation:** confirm early-access availability and read a real
scaffolded case, then port — do not port to an unseen format. A
`claude plugin eval init --bare` probe printed "plugin eval is currently in
early access" and wrote nothing, so neither author nor receiver has seen the
case schema. Porting before that is a rework risk.

Direction (once access is confirmed and a real case file has been read):

- Reduce prose runbooks to harness preconditions the runner cannot express
  (credential choice, tool floors). Use `scaffold_script` instead of the
  hand-written seed (kills S4). Keep `--max-cost-usd` as a hard ceiling.
- **Sequence:** do not port gate or routing cases until S13 is decided. Cases
  blocked by the effort-evidence problem are `gate-claude-pass` /
  `gate-claude-reject` and the
  `explicit-routing` / `inherited-routing` / `child-evidence-match` /
  `child-evidence-reject` family — roughly a third of the suite and the ones
  with 3/3 hard-gate thresholds. If S13 drops effort floors where the harness
  exposes no effort selector, their expected decisions change. Early value, if
  desired after schema confirmation: harness-independent cases
  `trivial-reduction`, `dependency-preflight`, `dependency-incompatible`,
  `authorization-boundaries`, `qa-cli-backend`.
- **No synthetic-evidence path.** A test-only injector that fabricates a
  `/status` readout is the bypass the gate exists to forbid. If reachable
  outside tests the gate is decorative; if not, you are testing a fake and
  `gate-claude-pass` becomes a tautology. The unattended-gate caveat and S13
  are the same defect: the spec demanded evidence the platform cannot emit
  unattended. Fix the evidence model (S13) rather than faking evidence. If that
  still leaves the controller gate attended-only, document it as a limitation —
  and accept that Shipwright cannot run in CI on Claude Code — rather than
  hiding it behind a test harness.
- **Prefer deterministic graders.** Most Shipwright assertions are process
  compliance (no `.superpowers/`, repo unchanged, zero artifacts before the
  gate, ledger delta holds exactly one dispatch). Those are git/filesystem
  checks; an LLM judge scores them unreliably and costs money. Confirm free /
  non-LLM graders exist before committing (`--max-cost-usd` help implies paid
  graders can be skipped while free graders still score). Reserve LLM criteria
  for genuinely subjective cases: review quality and
  `false-positive-adjudication`. Cheap judge only where a judge is the right
  tool.

Also makes S6 cheap once a Codex suite is case files rather than a second prose
runbook.

### S11 — The §3 trivial reduction bypasses the §1 controller gate — FIXED

Observed behaviorally. A headless run
(`claude -p "/shipwright:shipwright <trivial task>" --plugin-dir <checkout>`) in
a throwaway git repo could not read
`skills/shipwright/references/claude-code.md`, because the plugin was loaded
from a path outside the machine's read allowlist and print mode has nobody to
approve the prompt.

Shipwright did not stop. It took the §3 reduction path and wrote three files
(`util.js` modified, `util.test.js` and `package.json` created), then reported
afterwards that "Shipwright's Claude Code controller gate was never applied."

Fixed in `SKILL.md`: §1 now stops when the platform reference cannot be read,
applies the controller gate before any §3 reduction, and treats an unreadable
reference as a stop rather than a downgrade. §3 may run only after harness
identification and a passed gate. `trivial-reduction` scenario variants cover
unreadable-reference and pre-gate stops. Behavioral re-probe still needed.

### S13 — Every gated Sonnet/Opus dispatch may dead-end in `BLOCKED_RUNTIME` — FIXED

Confirmed from platform sources without an attended run: Claude Code's Agent
tool exposes per-invocation `model` but no effort selector; frontmatter `effort`
is documented but Task-spawned agents do not propagate or expose attributable
child effort ([subagents docs](https://code.claude.com/docs/en/subagents),
[anthropics/claude-code#43083](https://github.com/anthropics/claude-code/issues/43083)).

Decision: when the live schema has a model selector but no effort selector,
accept attributable model-family evidence with absent effort for every route,
including Sonnet and Opus; do not fallback solely because effort is absent;
restore effort floors if a later probe finds a usable effort selector or
attributable child effort. Controller Opus / xhigh+ effort floor remains.

Changed: `references/claude-code.md` worker routing, native-dispatch, and child
evidence; `SKILL.md` §7 waiver; `evals/v1/scenarios.md` `explicit-routing`;
validator markers. Inherited-controller fallback is not the normal path.

### S12 — Reduced runs still scaffold unrequested project files — OPEN, LOW

The same run created `package.json` in a repo that had none, to make an ESM test
runnable. Defensible in a throwaway fixture, but on a real repository that is
unrequested scope from a task that asked for one function. Worth an explicit
rule that the reduced path may not add project-level configuration without
asking.

## Handoff

### H1 — The command shadows the skill, losing the proactive-offer trigger — OPEN

`handoff` ships both `commands/handoff.md` and `skills/handoff/SKILL.md`. In
Claude Code the command occupies the `handoff:handoff` identifier: invoking it
loads the command shell, and the listing shows the command's description
("Write a handoff dossier for a fresh standard or frontier agent"), not the
skill's.

That is the intended thin-shell chain and the workflow still resolves — the
shell reads the skill by plugin-root path. But the skill's description is where
the proactive cue lives ("context is polluted, or work should continue on a
cheaper or stronger model"), and `skills/handoff/SKILL.md` relies on it for
"You may **offer** a handoff." Because the description is never surfaced, the
offer path cannot trigger from it.

Fix by carrying the trigger language into the command's `description:`. That
duplicates one string rather than workflow prose, so it does not breach the
thin-shell rule, but check `_validate_thin_shell` in
`scripts/validate_handoff.py` for constraints first.

## Reviewer

Not yet exercised.
