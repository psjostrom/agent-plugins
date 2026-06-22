# Frontload Reviewer Subagents Design

**Date:** 2026-06-22

## Goal

Add two Frontload-specific domain reviewers to the Codex `parallel-review`
skill. Preserve the existing Claude reviewer surface unchanged.

## Scope

The change applies only to:

- `plugins/reviewer/skills/parallel-review/`
- the deterministic Codex reviewer validator;
- Codex-facing reviewer documentation.

Do not add Frontload agents under `plugins/reviewer/agents/` and do not modify
the Claude `/reviewer:review` command.

## Reviewer Roles

### Frontload Core Correctness

Review Frontload's core data and accounting behavior:

- repository indexing and index freshness;
- dossier ranking and indexed search;
- budgeted reads and edit-safe excerpts;
- diff summaries and changed-file accounting;
- event recording and aggregation;
- token, byte, and savings calculations;
- consistency between reported metrics and the actual model-visible payload.

This reviewer owns correctness of Frontload's internal outputs and measurement
claims. It does not own host installation, hooks, command policy, or packaging.

### Frontload Integration & Safety

Review Frontload's host-facing behavior and safety boundaries:

- CLI and MCP behavior parity;
- Codex hook input and output contracts;
- command classification, rewriting, and allowlists;
- path resolution and repository-boundary enforcement;
- installation, initialization, and configuration merging;
- Codex skill, manifest, and hook packaging;
- inert behavior outside initialized Frontload repositories;
- preservation of unrelated user configuration.

This reviewer owns integration contracts and operational safety. It does not
recalculate core savings metrics unless an integration changes the payload
used by those calculations.

## Selection and Dispatch

Detect Frontload only when the repository name is `frontload` or a root package
manifest identifies the project as `frontload`. Arbitrary mentions of
Frontload in changed text must not activate the reviewers.

At Standard or Deep depth, select both Frontload reviewers. Never select them
at Quick depth. Dispatch them as independent, read-only Codex subagents using
the existing common reviewer contract.

Repository-level pairing is intentional: changes to one Frontload subsystem
can affect another subsystem without sharing a narrow path prefix. Path-based
selection would risk omitting relevant cross-cutting review.

## Validation

Extend `validate_codex_reviewer.py` so:

- both Frontload prompt files are required;
- unexpected reviewer prompt files still fail validation;
- each new prompt must contain role-specific markers proving its scope;
- the active Domain reviewers section must list Frontload and both prompt
  filenames;
- the Standard and Deep panel rows must continue selecting all matching domain
  reviewers;
- regression tests must reject stale mappings outside the active domain
  section, missing panel wiring, and ambiguous changed-text detection;
- the Claude reviewer files and command are not required to change.

Use a test-first validation cycle:

1. Update validator expectations and observe failure because the prompts and
   orchestration wiring are missing.
2. Add the prompts and selection wiring.
3. Run the deterministic reviewer validator, Codex plugin validator, and skill
   validator.

## Documentation

Update the reviewer README's Codex description to include Frontload among the
auto-detected projects. Do not advertise Frontload support in the Claude
section because this initial version is Codex-only.

## Non-goals

- Adding Frontload-specific Claude agents.
- Changing universal reviewer behavior.
- Changing scoring, GitHub mutation rules, or review depth thresholds.
- Adding changed-path heuristics for selecting only one Frontload reviewer.
- Modifying the separate `/Users/psjostrom/code/frontload` repository.
