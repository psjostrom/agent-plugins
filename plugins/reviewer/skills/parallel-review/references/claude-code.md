# Claude Code Dispatch Reference

Read this file completely only when parallel review is running in Claude Code. The shared `SKILL.md` owns triage, depth selection, synthesis, scoring, and the decision gate.

## Harness identification

You are in **Claude Code** when the user invokes `/reviewer:review` or its `/r` alias from this plugin.

Require `${CLAUDE_PLUGIN_ROOT}` for every shared-file read. Never load `skills/parallel-review/...` relative to the reviewed repository.

## Orchestrator entry

The thin command shell is `commands/review.md`. It parses Claude-specific flags, then you execute the shared workflow.

Always load shared files with `${CLAUDE_PLUGIN_ROOT}` so paths resolve from the installed plugin, not the reviewed repository:

- `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/claude-code.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/reviewer-contract.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/reviewers/<role>.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/scoring.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/github-actions.md`

## Argument parsing (Claude-specific)

Parse `$ARGUMENTS` before shared workflow steps:

- `--opus` → subagent model **opus** (default **sonnet**)
- `--deep` / `--quick` → depth overrides (`--deep` wins if both are present)
- Remove recognized flags; pass the remainder to shared input parsing as PR number/URL, branch/base comparison, or empty for local/current PR discovery

## Spawn children

Dispatch via Claude Code's `Agent` tool with `subagent_type` values from this table. Each specialist shell in `agents/<role>.md` reads the matching shared reviewer prompt via `${CLAUDE_PLUGIN_ROOT}`; the `prompt` you pass should contain only orchestration context (diff, tiered file list, one-line summary, repository guidance).

| Role | `subagent_type` | Shared prompt |
| --- | --- | --- |
| Bug Hunter | `reviewer:bug-hunter` | `bug-hunter.md` |
| Guidelines | `reviewer:guidelines` | `guidelines.md` |
| Error & Edge Cases | `reviewer:error-edges` | `error-edges.md` |
| Architecture & Quality | `reviewer:architecture` | `architecture.md` |
| Test Reviewer | `reviewer:test-reviewer` | `test-reviewer.md` |
| Strimma Coroutine & Lifecycle | `reviewer:strimma-coroutine` | `strimma-coroutine.md` |
| Strimma Medical Data Integrity | `reviewer:strimma-medical` | `strimma-medical.md` |
| Springa API Contract & Schema | `reviewer:springa-api` | `springa-api.md` |
| Springa React & Next.js Patterns | `reviewer:springa-react` | `springa-react.md` |
| Garmin/Connect IQ | `reviewer:garmin-ciq` | `garmin-ciq.md` |
| Frontload Core Correctness | `reviewer:frontload-core` | `frontload-core.md` |
| Frontload Integration & Safety | `reviewer:frontload-integration` | `frontload-integration.md` |
| Agent Plugins Surface Parity | `reviewer:agent-plugins` | `agent-plugins.md` |

Launch every selected reviewer in one parallel response. Use the model chosen during argument parsing.

If the `Agent` tool is unavailable, disclose that the specialist panel cannot run and ask whether to continue as a single-agent review.

## GitHub posting

After the decision gate, PR fixes and inline comment posting may use Claude GitHub MCP tools where available, or follow `${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/github-actions.md` for standalone `gh api` posting.
