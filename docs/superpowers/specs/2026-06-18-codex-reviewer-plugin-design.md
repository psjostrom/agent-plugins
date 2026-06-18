# Codex Reviewer Plugin Design

**Date:** 2026-06-18

## Goal

Port the existing Claude `reviewer` plugin to Codex without weakening its core workflow: risk-based multi-agent review, structured findings, root-cause deduplication, calibrated scoring, mandatory verification of high-severity claims, and an explicit user decision before fixes or GitHub comments.

The Claude plugin remains unchanged. Codex support is added alongside it in the same `plugins/reviewer` directory.

## Packaging

The existing reviewer directory becomes a dual-surface plugin:

- `.claude-plugin/plugin.json` and `commands/` continue serving Claude Code.
- `.codex-plugin/plugin.json` exposes the plugin to Codex.
- `skills/review-pr/` contains the Codex orchestration skill and UI metadata.
- `.codex/agents/` contains project-scoped custom reviewer definitions.
- `.agents/plugins/marketplace.json` exposes the repository as a Codex marketplace.

The Codex skill is named `review-pr`. It is explicitly invoked with prompts such as:

```text
Use $review-pr to review PR #6 with parallel subagents.
```

Explicit invocation is the default because reviews fan out into multiple agent threads and therefore carry meaningful cost.

## Review Workflow

The Codex skill preserves these stages from the Claude command:

1. Determine whether the target is a numbered PR, the current branch PR, or a local diff.
2. Load repository guidance from applicable `AGENTS.md` files and, for compatibility, `CLAUDE.md`.
3. Gather the complete diff, changed files, PR metadata, comments, and checks without changing repository state.
4. Classify changed files as Critical, Standard, or Low risk.
5. Select Quick, Standard, or Deep review depth using risk and diff size.
6. Spawn the selected specialist agents in parallel and wait for all results.
7. Normalize findings into a shared schema, resolve code locations, merge semantic duplicates by root cause, and cross-reference related findings.
8. Score each issue from 0–100. Verify every claim before assigning a score above 75.
9. Present a concise summary, blocking issues, and a separate Probably Fine section.
10. Stop and ask which findings the user wants addressed and whether PR findings should be fixed or posted as comments.
11. Act only on the user-selected findings.

The skill never merges a pull request.

## Reviewer Agents

Each existing Claude reviewer maps to a read-only Codex custom agent:

- `bug-hunter`
- `guidelines`
- `error-edges`
- `architecture`
- `test-reviewer`
- `strimma-coroutine`
- `strimma-medical`
- `springa-api`
- `springa-react`
- `garmin-ciq`

Each agent receives only the orchestration context it needs: diff or patch data, changed-file risk tiers, change summary, and repository guidance. Agent instructions preserve the original scope boundaries so reviewers do not duplicate one another unnecessarily.

Custom agents use `sandbox_mode = "read-only"`. Universal reviewers default to a cost-conscious model suitable for read-heavy analysis with higher reasoning effort where correctness matters. The orchestrator may request stronger reasoning for Deep reviews, but model names are not encoded as user-facing flags equivalent to Claude's `--sonnet` or `--opus`.

## Codex-Specific Adaptations

### Subagents

Claude `Agent` calls become Codex custom-agent dispatch. The skill explicitly requires parallel subagents because Codex does not spawn them implicitly.

### Repository guidance

`AGENTS.md` is authoritative for Codex. `CLAUDE.md` is also read when present so repositories can share existing review rules during migration. If instructions conflict, `AGENTS.md` wins for Codex.

### GitHub access

Structured GitHub connector tools are preferred for PR metadata, patches, comments, reviews, and review-thread state. Local `git` and `gh` fill gaps such as current-branch PR discovery, workflow logs, exact commit content, or API operations not covered by the connector.

Posting review comments remains opt-in. Scores are never included in GitHub comments. Each selected inline comment is posted individually and verified before a summary review is submitted. The workflow stops on the first posting failure.

### Local diffs

The Claude workflow uses `git add -N` to expose untracked files. The Codex port must remain non-mutating during review. It gathers:

- tracked changes with `git diff` and `git diff --cached`;
- untracked paths with `git ls-files --others --exclude-standard`;
- untracked file contents through bounded direct reads.

The reviewer does not alter staging state.

### Fixes

Review agents remain read-only. Only the parent thread may edit code after the user selects findings. Fixing a PR requires checking out or creating an isolated worktree for the PR branch, applying targeted changes, running proportionate verification, and asking separately before commit or push unless those actions were already explicitly requested.

## Review Depth

The original depth policy is retained:

| Depth | Trigger | Reviewers |
| --- | --- | --- |
| Quick | Only Low-risk files, or explicit quick request | Bug Hunter, Guidelines |
| Standard | No Critical files and fewer than 400 changed lines | Bug Hunter, Guidelines, Test Reviewer when source changed, matching domain reviewers |
| Deep | Critical files, at least 400 changed lines, or explicit deep request | All universal and matching domain reviewers |

Diffs above 1,500 changed lines prioritize Critical and Standard files. Low-risk files receive only targeted scrutiny.

## Findings Contract

Every subagent finding must contain:

- description;
- repository-relative file path;
- exact code context;
- best-effort line number;
- category;
- concrete suggestion.

The orchestrator must reject positive observations and unsupported speculation. Multiple symptoms caused by the same defect become one issue. Claims about compilation, missing APIs, races, null dereferences, security, explicit guidance violations, or other scores above 75 require direct verification against source, tests, documentation, or an executable check.

## Safety Boundaries

- Reviewing is read-only until the user selects findings.
- No automatic fixes, commits, pushes, comments, approvals, or merges.
- No score or confidence metadata appears in GitHub comments.
- Review comments target the current PR head SHA.
- A failed inline comment prevents submission of the summary review.
- Domain reviewers may increase scrutiny but cannot invent project requirements absent from source guidance or established domain rules.
- Existing unrelated working-tree changes are preserved.

## Validation

Validation has four layers:

1. Validate `.codex-plugin/plugin.json` with the bundled Codex plugin validator.
2. Validate `skills/review-pr/SKILL.md` and `agents/openai.yaml` with the bundled skill validator.
3. Parse every custom-agent TOML file and verify required fields, read-only sandboxing, and unique agent names.
4. Forward-test the installed skill against PRs #6 and #7:
   - confirm appropriate review depth;
   - confirm the intended agents are dispatched;
   - confirm the parent waits for all findings;
   - confirm findings are deduplicated and scored;
   - confirm high-severity findings are verified;
   - confirm no repository or GitHub mutation occurs before user selection.

The initial forward tests stop after reporting findings; they do not post comments or modify either PR.

## Compatibility and Scope

This port targets the Codex app and CLI. It does not redesign the Claude workflow, modify existing Claude prompts, add CI enforcement, or configure GitHub branch protection. Mechanical merge enforcement can be added later as a separate required GitHub check.
