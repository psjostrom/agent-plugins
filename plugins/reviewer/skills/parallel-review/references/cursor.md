# Cursor Dispatch Reference

Read this file completely only when parallel review is running in Cursor. The shared `SKILL.md` owns triage, depth selection, synthesis, scoring, and the decision gate.

## Harness identification

You are in **Cursor** when this plugin is installed under `~/.cursor/plugins/local/reviewer` (or `CURSOR_PLUGINS_LOCAL`) and the user explicitly invokes the `parallel-review` skill — for example "use parallel-review" or `/parallel-review` when Cursor surfaces the slash command. The skill sets `disable-model-invocation: true`; do not auto-invoke it from ambient chat.

## Spawn children

Cursor has no custom `reviewer:*` subagent types. Inspect the live `Task` tool schema and dispatch with the closest available general-purpose subagent type (commonly `generalPurpose`).

Conceptual shape:

```text
Task({ subagent_type, prompt, model /* only if schema exposes a usable selector */ })
```

Rules:

1. Pass `model` only when the live schema exposes a usable selector for the intended reviewer tier; never fabricate unsupported arguments.
2. Inline the complete `references/reviewer-contract.md` plus exactly one specialist prompt from `references/reviewers/<role>.md` in each child prompt, along with mode/target, summary, tiered files, guidance, patch or retrieval instructions, and structured-findings-only requirement.
3. Launch every selected reviewer in one parallel batch.
4. If `Task` or subagents are unavailable, disclose that the specialist panel cannot run and ask whether to continue as a single-agent review. Do not silently simulate multiple reviewers.
5. If one child fails, retry that role once with a narrower prompt; if it still fails, disclose the missing coverage.

Resolve every `references/...` path from the directory containing `SKILL.md`.

## Specialist roles

Load shared specialist bodies from `references/reviewers/`:

| Role | Shared prompt |
| --- | --- |
| Bug Hunter | `bug-hunter.md` |
| Guidelines | `guidelines.md` |
| Error & Edge Cases | `error-edges.md` |
| Architecture & Quality | `architecture.md` |
| Test Reviewer | `test-reviewer.md` |
| Strimma Coroutine & Lifecycle | `strimma-coroutine.md` |
| Strimma Medical Data Integrity | `strimma-medical.md` |
| Springa API Contract & Schema | `springa-api.md` |
| Springa React & Next.js Patterns | `springa-react.md` |
| Garmin/Connect IQ | `garmin-ciq.md` |
| Frontload Core Correctness | `frontload-core.md` |
| Frontload Integration & Safety | `frontload-integration.md` |
| Agent Plugins Surface Parity | `agent-plugins.md` |

## Decision gate

Follow the shared decision gate, scoring rules, and no-merge rules exactly. Act on fixes or GitHub posting only after the user selects findings and an action.
