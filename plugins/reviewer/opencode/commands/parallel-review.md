---
description: "Review uncommitted changes or a PR — scored issues, interactive fixing or inline GitHub comments"
agent: reviewer
---

# Code Review

**Argument:** "$ARGUMENTS"

## Active harness

You are the **opencode** orchestrator for parallel review on the `reviewer` primary agent.

Resolve the shared skill root first (installed command is a symlink into this plugin):

```bash
SHARED_ROOT=""
for base in "${HOME}/.config/opencode" "$(pwd)/.opencode"; do
  f="$base/commands/parallel-review.md"
  if [ -e "$f" ]; then
    real=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$f")
    SHARED_ROOT=$(cd "$(dirname "$real")/../../skills/parallel-review" && pwd)
    break
  fi
done
if [ -z "$SHARED_ROOT" ] || [ ! -f "$SHARED_ROOT/SKILL.md" ]; then
  echo "Could not resolve shared parallel-review skill root. Run ./install-opencode.sh install reviewer first." >&2
  exit 1
fi
printf 'SHARED_ROOT=%s\n' "$SHARED_ROOT"
```

Read completely, in order, using absolute paths under `$SHARED_ROOT`:

1. `$SHARED_ROOT/SKILL.md`
2. `$SHARED_ROOT/references/opencode.md`

## opencode argument parsing

Before following the shared workflow, parse `$ARGUMENTS`:

- `--opus` → remove it; opencode configures subagent models in `opencode.json`, not per-call flags
- `--deep` / `--quick` → depth overrides (`--deep` wins if both are present)
- Remove recognized flags; use the remainder for shared input parsing (PR number/URL, branch/base comparison, or empty for local/current PR)

Then execute the shared workflow end-to-end. Do not duplicate triage tables, scoring rubrics, or posting recipes here.
