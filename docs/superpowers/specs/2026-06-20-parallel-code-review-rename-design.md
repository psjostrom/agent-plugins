# Parallel Code Review Rename Design

**Date:** 2026-06-20

## Goal

Rename the Codex reviewer skill so its name reflects every supported target, and add explicit repository-relative path scoping. The existing Claude command and the shared `reviewer` plugin name remain unchanged.

## User Interface

- Codex display name: **Parallel Code Review**
- Explicit invocation: `$parallel-review`
- Supported targets:
  - a numbered pull request or PR URL;
  - the current branch's pull request;
  - a branch diff;
  - staged, unstaged, and untracked local changes;
  - any of those targets restricted to one or more repository-relative files or directories.

Examples:

```text
$parallel-review Review PR 6 deep
$parallel-review Review my local changes
$parallel-review Review local changes under src/auth
$parallel-review Review PR 7, limited to apps/web and packages/api
```

## Path Scope

The user may supply one or more repository-relative paths. The orchestrator validates that each path is inside the repository, rejects paths that escape the repository, and limits changed-file discovery, patches, risk classification, reviewer context, synthesis, and reporting to matching changed paths.

A path filter does not turn unchanged files into review targets. If no changed files match, the skill reports that there is nothing in scope and stops. Reviewers may inspect directly related source outside the scope as read-only evidence, but findings must identify a defect in the scoped changed code.

## Packaging and Compatibility

Rename `skills/review-pr/` to `skills/parallel-review/`, update the skill frontmatter and UI metadata, and remove stale `$review-pr` references from active plugin metadata and documentation. Keep the plugin identifier `reviewer@agent-plugins`, the Claude files, specialist roles, scoring, and safety boundaries unchanged.

Because the skill has `allow_implicit_invocation: false`, users must explicitly select or mention `$parallel-review`.

## Validation

The deterministic validator must require:

- the `skills/parallel-review/` path;
- frontmatter name `parallel-review`;
- display name `Parallel Code Review`;
- `$parallel-review` in default prompts;
- explicit path-scope validation, filtering, empty-scope behavior, and finding boundaries;
- no active `skills/review-pr` directory or `$review-pr` invocation metadata.

After updating the cachebuster, reinstall the plugin from `/Users/psjostrom/code/agent-plugins` and verify that Codex exposes the renamed skill from the durable marketplace path.
