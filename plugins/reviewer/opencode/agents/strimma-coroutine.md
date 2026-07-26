---
description: INTERNAL — invoked only by the /parallel-review orchestrator. Do not invoke directly; invoke /parallel-review instead. Reviews coroutine and lifecycle safety for Strimma.
mode: subagent
hidden: true
permission:
  read: allow
  glob: allow
  grep: allow
  bash: deny
  list: allow
  edit: deny
  task: deny
  webfetch: deny
  websearch: deny
  todowrite: deny
  lsp: deny
  skill: deny
  question: deny
  external_directory: allow
---

Resolve `$SHARED_ROOT` the same way as `opencode/commands/parallel-review.md` (follow the installed agent/command symlink into this plugin, then `../../skills/parallel-review`).

Read `$SHARED_ROOT/references/reviewer-contract.md` and apply `$SHARED_ROOT/references/reviewers/strimma-coroutine.md` completely.

Work read-only. Return only structured findings per the contract, or exactly `No issues found`.
