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
newer, with a higher major version meeting the floor regardless of minor
version. Context-size suffixes such as `[1m]` are explicitly capability-neutral.
Rejection still covers non-Opus families, Opus below the floor, and unresolved
evidence including the bare word `opus`. Controller effort was initially kept as
a hard `xhigh+` floor; that was later demoted — see S14.

Changed: `skills/shipwright/references/claude-code.md`,
`evals/v1/claude-code-runbook.md`, `evals/v1/scenarios.md`
(`gate-claude-pass`, `gate-claude-reject`), and the corresponding
`scripts/validate_shipwright.py` markers plus
`scripts/test_validate_shipwright.py` fixtures. Validator and its unit tests
pass (58 at `91dc04f` and after S14).

**Behaviorally confirmed on the model dimension at `91dc04f`.** A headless run
with the platform reference readable reported: model `claude-opus-5` from harness
turn metadata, "concrete versioned Opus ID; major `5` > `4`, clears the `4.6`
floor" — **Pass**. Before the fix this same session was rejected outright. The
effort dimension could not be confirmed unattended and is no longer a hard gate
(S14).

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

### S8 — Documented validation commands dirty the working tree — FIXED

`python3 -m unittest plugins/shipwright/scripts/test_validate_shipwright.py`
creates `plugins/shipwright/scripts/__pycache__/`, which was not ignored, so the
repo's own documented validation step left the tree dirty. This also fed S4,
since the eval seed then recorded a dirty status. Added `__pycache__/` to
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

### S10 — The hand-rolled runbook duplicates a native, cost-capped eval runner — OPEN, PORTABLE

**The schema is no longer unseen.** The subcommand is gated behind
`Ke("tengu_walnut_spire", false) || CLAUDE_CODE_WALNUT_SPIRE`; with that env var
set, `claude plugin eval init --bare` scaffolds a real case. Full verified
contract — both case formats, all six grader types, frontmatter key sets,
defaults and limits — is in `task/eval-schema.md`, with the CLI surface in
`task/eval-help.txt`. Nothing below rests on inference now.

Two constraints the contract imposes:

- Authoring needs no runtime; **executing the suite does**, and the runner is
  early-access behind that flag. A port can be written anywhere but can only be
  run where Claude Code is installed and flagged.
- `context.scaffold_script` is reachable only from `case.yaml`, not from
  `prompt.md` frontmatter.

Direction:

- Reduce prose runbooks to harness preconditions the runner cannot express
  (credential choice, tool floors). Use `scaffold_script` instead of the
  hand-written seed (kills S4). Keep `--max-cost-usd` as a hard ceiling.
- **Sequence:** the S13 gate is lifted — S13 is fixed, so the expected decisions
  for `gate-claude-pass` / `gate-claude-reject` and the `explicit-routing` /
  `inherited-routing` / `child-evidence-match` / `child-evidence-reject` family
  are now settled against the child-effort waiver. Those cases still carry 3/3
  hard-gate thresholds and the unattended-gate caveat below, so start with the
  harness-independent ones: `trivial-reduction`, `dependency-preflight`,
  `dependency-incompatible`, `authorization-boundaries`, `qa-cli-backend`.
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
  checks; an LLM judge scores them unreliably and costs money. Four free
  deterministic grader types cover them — `file_exists`, `regex`, `tool_used`,
  and `tool_order` (which also expresses gate-before-artifacts ordering). Paid
  graders are `llm` and `baseline`; on a cost breach those are skipped while free
  graders still score the run. Reserve LLM criteria
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

Decision: accept attributable model-family evidence without effort only when
the selected route has no effort floor, or when this platform reference
explicitly waives the effort dimension because the live schema has no effort
selector and child effort is not attributable. Under that waiver, Ordinary /
Integration / Critical child routes may accept absent effort; do not fallback
solely because effort is absent. Restore route effort floors when a later probe
finds a usable effort selector or attributable child effort. Controller
recommended effort is a separate shared disclosure rule (S14), not preserved as
a child-style hard floor.

Changed: `references/claude-code.md` worker routing, native-dispatch, and child
evidence; `SKILL.md` §7 waiver; `evals/v1/scenarios.md` `explicit-routing`;
validator markers. Inherited-controller fallback is not the normal path.

### S14 — Controller effort conflated verifiable and unverifiable checks — FIXED

Observed behaviorally at `91dc04f`. A headless Claude Code run with the platform
reference readable reached the controller gate and stopped: model passed from
harness metadata (`claude-opus-5`), effort came back Unverified, and
`--effort xhigh` was correctly rejected as a launch argument. Cursor has the same
controller observability hole (family/model readable; effort often not). Codex
may emit effort in metadata, but keeping a hard effort precondition only where
observable would make the product mean different things per harness.

Decision (shared across Claude Code, Cursor, and Codex):

- **Model/family floor** remains a hard gate.
- **Recommended controller effort** is a disclosed assumption, not a
  precondition. Record resolved effort, `below recommended`, or `unverifiable`;
  never stop solely because effort is missing, weak, or unverifiable. Disclose
  that state in the completion report and any authorized PR body, not only the
  ledger.
- **Child waiver vs controller disclosure are different mechanisms.** Child
  effort is unrequestable on Claude Code (no Agent effort selector) — waiving
  proof of an unsettable dimension is coherent. Controller effort is settable
  but often unobservable — record and disclose rather than hard-stop or pretend
  to verify.
- Necessity of the recommended ranks (`xhigh` / `high`) remains unmeasured;
  they stay as recommendations pending a medium-vs-xhigh comparison. Dropping
  them entirely is still available if measurement shows no material gap.

Changed: `SKILL.md` §1 and §15; `references/claude-code.md`, `cursor.md`,
`codex.md` controller gates; `evals/v1/scenarios.md` gate cases and
`explicit-routing`; Claude/Cursor runbooks; validator markers and unit tests.
`validate_shipwright.py` passes; 58 unit tests OK.

### S15 — §3 reduction classifies on development size and ignores QA risk — OPEN, HIGH

`SKILL.md` §3 reduces when work is "tiny, mechanical, locally obvious, and does
not justify independent subagents." Every one of those criteria describes the
*change*. None describes the verification surface.

That misclassifies a whole category of real work: low-diff, high-QA tasks. A
dependency bump is one line in `package.json` — tiny, mechanical, locally
obvious on all four counts, so §3 reduces it — while being exactly the change
that needs a real device, a real launch, and a regression sweep. The concrete
case that surfaced this is a mobile Expo bump, where the diff is trivial and the
QA surface is the entire app.

Compounding it, the reduced path's obligations are undefined. §3 says "route it
to a smaller workflow" without stating which Shipwright gates survive, and §11
verification and §12 QA routing are not conditioned either way. One observation
at `b221944` showed a reduced run retaining both — it ran the test suite before
and after, checked the diff for unrelated changes, and reported "No QA surface
applies" after assessing web/mobile/CLI/backend. So the reduced path is not
skipping QA in practice. But that is a single observation of an underspecified
rule, on a repo that happened to have no QA surface at all, so it does not show
what a reduced run does when a surface *does* apply.

Two fixes, both cheap:

- Add a verification-surface dimension to the §3 criteria. Reduce only when the
  change is small **and** the surface it can affect is narrow. Small diff plus
  wide surface is not trivial work.
- State explicitly that reduction never waives §11 verification or §12 QA
  routing, so the reduced path's obligations stop depending on the reader.

### S16 — The mobile QA probe checks the CLI version, not the capability — OPEN, HIGH

§12's Android/iOS route says "Probe `argent --version`; require 0.16.0 or
compatible newer." That probe cannot establish the capability it gates.

argent is driven entirely through **MCP tools**, not the CLI. The target
repository's own `.claude/rules/argent.md` is explicit: "All simulator/emulator
interactions go through argent MCP tools — never use `xcrun simctl`, raw `curl`
to simulator ports, or the simulator-server binary directly." CLI presence and
tool availability are independent facts, and the probe only observes the first.

Demonstrated directly, in one repository, across two sessions:

| | `argent --version` | argent MCP tools | Mobile QA possible |
| --- | --- | --- | --- |
| Server not registered for this scope | `0.18.0` | none | no |
| Server registered user-scoped | `0.18.0` | present, `list-devices` returns 32 simulators | yes |

The probe returns the identical passing answer in both rows. In the first, §12
would record the capability as present and then have nothing to drive the
simulator with. §13 already carries the right rule ("Missing a core capability
is `unverified`, not equivalent"); the specified probe simply tests the wrong
thing.

Fix by probing for the interaction tools themselves — the capability is the
loaded MCP toolset, not an executable on `PATH`. A CLI version check is at best
a secondary compatibility check *after* the tools are known to be present.

This also refines S14's scope. Mobile QA is not inherently attended-only: with a
user-scoped server the tools load in unrelated repositories, so an unattended
mobile QA route is achievable. But it depends on the operator's install topology,
which Shipwright cannot assume — which is exactly why it must probe the toolset
rather than infer availability from the binary.

### S12 — Reduced runs still scaffold unrequested project files — OPEN, LOW

The same run created `package.json` in a repo that had none, to make an ESM test
runnable. Defensible in a throwaway fixture, but on a real repository that is
unrequested scope from a task that asked for one function. Worth an explicit
rule that the reduced path may not add project-level configuration without
asking.

### S17 — Cross-repository invocation has no defined subject repository — OPEN

Invoked from a session rooted in this plugin repository, with a prompt naming a
target in another checkout (`/Users/persjo/code/nordnet/mobile-app/src/ducks/
userSettings`). Nothing in the skill resolves which repository is the subject.

`SKILL.md` §1 inspects "repository instructions, fresh upstream baseline when
relevant, branch/worktree, tracked and untracked changes" without naming a
repository, so every one of those reads resolves against the process working
directory. §5 then runs `git check-ignore` on the `.superpowers/` path and
`git rev-parse --git-path info/exclude`, and writes
`.superpowers/sdd/progress.md` and `runs/<dispatch-id>/` — all against that same
wrong root.

The two §1 safety rules degrade the same way. "Do not implement on `main` or
`master` without explicit authorization" and "Preserve unrelated work" get
evaluated against the plugin repository, which sat on `main` clean, while the
actual target sat on a feature branch carrying an unrelated modified file. The
guard passes by reading the wrong branch.

§14 gives "Write outside the repository or task-specific temporary directories |
Ask first", so the best case is a stall on an authorization question mid-run.
The worse case is a ledger and worktree created beside the plugin while product
edits land in the target, splitting the run's evidence from its diff.

Fix in §1: make the subject repository an explicit preflight output, and stop
when a requested target path lies outside the current repository root, directing
the user to re-invoke from that repository. That is one added stop condition and
it removes the ambiguity from every cross-repo prompt.

### S18 — Merged fixes are absent from the installed cache, so FIXED findings still reproduce — OPEN, HIGH

The `c298d6c` baseline recorded at the top of this document is not only the
baseline; it is still the install state. `installed_plugins.json` pins
`shipwright@agent-plugins` to `gitCommitSha c298d6c` with `lastUpdated`
`2026-08-03T08:17:25Z`. That commit is #17, predating #18 (`91dc04f`), #19
(`b221944`), and #30 (`99c6707`).

After `/plugin marketplace update agent-plugins`, the marketplace clone advanced
to `99c6707`, but `/plugin` still reported "already at the latest version
(1.0.0)" and the installed cache stayed on `c298d6c`. `handoff` and `reviewer`
share that same frozen SHA.

So the cached `references/claude-code.md` still carries the pre-S1 gate:

> Accept either: active alias `opus` only when current runtime evidence resolves
> it to Claude Opus 4.7; or exact active model ID `claude-opus-4-7`. Require
> effort rank `xhigh` or stronger.

An operator invoking Shipwright on this machine therefore reproduces S1 and S14
in full: `claude-opus-5[1m]` fails the exact pin, harness metadata carries no
effort, and the run hard-stops at §1 demanding a downgrade. Every finding marked
FIXED here is fixed in git and unfixed in the plugin that actually loads.

Root cause: both the Claude `plugin.json` and the Claude marketplace entry pinned
`version` to `1.0.0`. Claude Code keys `/plugin update` on that resolved version
string, so commits that leave it unchanged never replace the cache. The project's
own validators closed both remedies — they hard-asserted the Claude (and Cursor)
manifest version is exactly `1.0.0`, so bumping failed validation and omitting
failed too (`None != "1.0.0"`). Three consecutive merged PRs therefore delivered
nothing to the installed copy.

Fix: adopt the SHA-tracked channel. Omit `version` from the Claude-side
`plugin.json` and the Claude marketplace entry for `shipwright` and `handoff`,
and change those validators to require its absence. Cursor and Codex keep their
version pins. Extend the validator unit tests so absence passes and a
reintroduced Claude `version` fails.

Two consequences for how this register is used:

- Behavioral re-verification of any FIXED finding must be preceded by
  `/plugin marketplace update agent-plugins` **and a session restart**. Skill
  content resolves at session start, so an in-session update does not apply. A
  re-verification run skipping that step measures `c298d6c` and reads as a
  regression in already-fixed behavior.
- Confirmations against a checkout and against the installed cache are different
  claims. S1's confirmation was a headless run over a checkout supplied by
  `--plugin-dir` (`evals/v1/claude-code-runbook.md:110`), which proves the
  source is correct but says nothing about what an ordinary invocation loads.

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
