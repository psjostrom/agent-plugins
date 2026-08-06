# Shipwright field-report hardening design

Date: 2026-08-06  
Source: field report from `nordnet-private/mobile-app` dead-duck deletion run (Shipwright `f9877de`, PR #12463)  
Scope: all 12 ranked fixes from that report  
Approach: new cross-cutting “Reading evidence” section plus targeted edits to §§1, 7–15 and platform references (not a full QA/auth rewrite)

## Problem

Shipwright enforces “worker statements are not verification” downward, but the controller’s completion report and PR can be pure assertion. QA evidence is routed to a git-excluded path that humans do not open. Authorization treats restoring declared project state (`npm install`, etc.) as ask-first while §§1/11/13 demand a workspace that can build and test. Several measurement rules invite misreading tool output (counts vs sets, harness exit vs tool exit, discovery without execution).

## Goals

1. Evidence reaches the human (session user always; PR reviewers when a PR is opened) at the same standard the controller demands of children.
2. Controllers self-unblock by restoring declared state without asking, then prove nothing declared changed.
3. Close the remaining ranked gaps (effort noise, fresh sim, reading traps, test readiness, `--no-verify`, plan/ledger authority, loaded skill version, harness run IDs, single-task consolidation).

## Non-goals

- Requiring harness-inline image display (CLI cannot reliably do this; Cursor/Codex desktop not verified as a universal channel).
- Official GitHub attachment API support (does not exist in `gh`); no hard dependency on undocumented upload endpoints or third-party `gh` extensions.
- Public third-party image hosts for app UI (forbidden for banking/private UI).
- Broad documentation churn outside Shipwright skill, references, validators/tests, and evals as needed for the new rules.

## Constraint

`plugins/shipwright/skills/shipwright/SKILL.md` must stay under 500 lines (validator). Prefer compact rules in the shared skill; put harness-specific effort-disclosure nuance in platform references. Update `validate_shipwright.py` / unit tests / eval scenarios when they assert wording that changes.

---

## A. Reading evidence + controller proof upward

**Add** a short cross-cutting section immediately after §8 step 2 (“Worker statements are not verification”). Cite it from §1/§11/§12 as needed. It does not add a new workflow phase.

**Principle:** Controller statements are not verification either. The completion report and any authorized PR must carry evidence, not assertion alone.

**Hard rules:**

1. Gate results come from the narrowest output that can only mean one thing.
2. Exit status is read from a value the controller wrote to a file — never from a harness background/async completion code for a compound command (that code is usually the last element, e.g. `tee`).
3. Discovery and similar metrics use filtered path *sets* and set diffs, not line counts; discard stderr and banners.
4. Prefer probes that cannot be misread (`lsof -nP -iTCP:<port> -sTCP:LISTEN` for listeners, not `lsof -ti`).

**§8 extension:** Inspecting child artifacts is necessary but not sufficient. Human-facing completion output must include the evidence (paths, numbers, observations). Assertion-only completion fails the spirit of the gate.

---

## B. Mandatory before/after QA and publish channels

### Capture and compare

1. **Baseline in §1 preflight** at the merge base, before implementation, when a visual QA surface applies (web/mobile) or is expected: capture screens of flows the change can affect. Skip baseline only when no visual surface applies. On JS/Metro, swapping to the base ref and reloading is enough when native binary is unchanged; otherwise boot the applicable surface.
2. **No exemption for “no UI change.”** That case requires before/after of the *unchanged* flow; identical screens are the required artifact.
3. **Quantitative diff under matched conditions** (same device/binary class, settled UI, JS swap by reload only when claiming pixel equivalence). Prefer `screenshot-diff` / equivalent. Eyeball alone is insufficient for a “behaves identically” DoD.
4. **Depth:** exercise a path that depends on the changed behavior — not only boot/consent. Boot ≠ `verified`.
5. **Device policy:** prefer a fresh simulator/emulator (or copy-bundle + `reinstall-app`) over interrupting a device already in use. Ask only when no alternative exists (physical device, or build obtainable nowhere else).

### Publish (two audiences)

**Session human (required for applicable visual QA → `verified`):**

- Floor: absolute path to the QA evidence directory.
- Plus: quantitative diff verdict (and other core observation numbers) in the completion report.
- When the OS allows: open the folder/files (`open` on macOS).
- Do **not** require or claim harness-inline image rendering. CLI shells cannot reliably show images to the user; desktop harness behavior is not assumed.

**PR reviewers (when authorized to open/update a PR):**

| Rank | Channel | Notes |
| --- | --- | --- |
| A | Native GitHub `user-attachments` (or equivalent private-repo-scoped) URLs embedded in PR body/comment | Prefer when obtainable without new credentials or policy breach; undocumented/`gh` extension paths are allowed only if already available or user-authorized — not a hard preflight dependency |
| B | Repo-scoped alternatives that stay private (e.g. prerelease assets) | Only when A fails and repo policy allows |
| C | PR text with absolute QA paths + diff numbers; state explicitly that images are not yet on the PR | Always available; author may paste |

Forbidden: public image hosts for app UI. Never imply screenshots are on the PR when only local paths exist. Gitignored `.superpowers/sdd/qa/` alone is storage, not publication.

---

## C. Self-unblocking (§14)

**Principle:** Self-unblocking is an obligation. Reporting `BLOCKED` for a condition standard project setup would repair is a failure of the run.

**Do without asking** (restore declared state):

- `npm install` / `npm ci` when dependencies are already declared
- `pod install`, `bundle install`
- generate gitignored artifacts the project’s build expects
- native rebuild of a dev client
- clear tool caches (Metro `--clear`, watchman, etc.)

**Then prove:** package manifests and lockfiles are byte-identical (or record and surface any unexpected declared-state drift). Record the action and the proof in the ledger.

**Still ask first:** adding/upgrading dependencies; intentional lockfile edits; global tool installs; MCP/plugin configuration; CI/build/`package.json` changes; credentials; remote or other-machine effects; production contact; push/PR/deploy without authorization.

Replace the current broad “Install/download tools…” ask-first row with this discriminator: changing declared/shipped state or leaving the project asks; restoring declared state does not.

---

## D. Remaining ranked items

| # | Change |
| --- | --- |
| 3 | Effort: always record in ledger; suppress from user-facing completion report and PR when `unverifiable`. Claude Code reference: effort often unobservable — do not surface unknown noise to the user. Never block on effort. |
| 5 | §11: harness completion exit ≠ tool exit (in addition to existing pipe warning); cite Reading evidence. |
| 6 | §1: discovery **and** one real known-good test run to green before dispatch; keep ban on using that single test as discovery proof. |
| 7 | Never `git commit --no-verify` / `-n`; hooks fail → fix or `BLOCKED`. |
| 8 | §1: compare discovered-test path sets, not counts. |
| 9 | When remediation overrides an approved plan constraint: amend the plan and record supersession, **or** declare plan frozen with ledger authoritative; record which. |
| 10 | §1/§2: note loaded skill base path/commit; compare to plugin install record; stop on mismatch. |
| 11 | §7: controller takes child run ID from harness spawn result; children need not self-report it. |
| 12 | §10: with exactly one task, consolidating that task’s final §8 gate with the whole-change gate is allowed under existing conditions. |

---

## Implementation sketch

1. Edit `plugins/shipwright/skills/shipwright/SKILL.md` (§§1, 7–15 + new Reading evidence block); stay under 500 lines.
2. Edit platform refs as needed (effort disclosure on Claude Code; any Cursor/Codex wording that forces `unverifiable` into the user-facing completion report).
3. Update validator marker checks / unit tests for new required phrases and removed contradictory ones.
4. Update eval scenarios/runbooks that encode old ask-first install, soft screenshot, or effort-in-completion-report behavior.
5. Run `python3 plugins/shipwright/scripts/validate_shipwright.py` and unit tests.

## Success criteria

- A controller following the skill cannot mark visual QA `verified` without a QA path + diff/observation numbers in the completion report, and cannot claim PR-published screenshots without A/B or an explicit C gap statement.
- Restoring `node_modules` / pods / gitignored env artifacts / dev-client rebuild does not require a user stop when declared state is unchanged afterward.
- `unverifiable` effort does not appear in the user-facing completion report.
- Fresh sim preferred; `--no-verify` forbidden; discovery sets + one green test; loaded skill version checked; child run IDs from harness; plan/ledger authority after remediation override is explicit.

## Out of scope for this change

- Changing Superpowers upstream skills (`using-git-worktrees`, etc.).
- Building or vendoring a `gh` image-upload extension inside this repo.
- Retroactive edits to the mobile-app PR that prompted the report.
