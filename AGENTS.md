# Repository Guidelines

These instructions apply to the whole repository.

## Project Shape

- This repo contains personal agent plugins for Claude Code, Codex, Cursor, and
  opencode.
- `plugins/reviewer/` is the main cross-platform plugin. It has a Claude surface
  (`.claude-plugin/`, `commands/`, `agents/`), a Codex surface
  (`.codex-plugin/`, `skills/parallel-review/`, `skills/.../references/`), a
  Cursor surface (`.cursor-plugin/`, shared `skills/parallel-review/`), and
  an opencode surface (`opencode/agents/`, `opencode/commands/`) when the
  opencode port is present.
- `plugins/homey/` is a Claude plugin for Homey Pro flow management. Treat Homey
  commands as potentially state-changing against a real local Homey instance.
- `.agents/plugins/marketplace.json` is the local Codex marketplace entry.
  `.claude-plugin/marketplace.json` is the Claude marketplace entry.
  `.cursor-plugin/marketplace.json` is the Cursor marketplace entry.
- `install-cursor.sh` symlinks each `plugins/<name>/` directory that contains
  `.cursor-plugin/plugin.json` into `~/.cursor/plugins/local/<name>` for local
  Cursor plugin discovery. It refuses to replace a non-symlink path.
- `install-opencode.sh` symlinks files from `plugins/*/opencode/` into
  opencode discovery directories. opencode has no plugin manifest in this repo;
  it discovers agents and commands by directory convention.

## Editing Rules

- Keep changes narrow. Do not reintroduce generated planning artifacts or broad
  documentation churn unless the user explicitly asks for them.
- Preserve platform boundaries: Claude command/agent files, Codex skill files,
  and opencode agent/command files are separate surfaces, but behavior that is
  intentionally mirrored should stay consistent across all supported agents.
- Reviewer role parity is required across all supported reviewer surfaces. If a
  reviewer role exists for Claude Code, Codex, Cursor, or opencode, it must exist
  and be wired for all four unless an intentional exception is documented in the
  same change.
- For Codex reviewer changes, resolve `references/...` paths relative to
  `plugins/reviewer/skills/parallel-review/SKILL.md`, matching the skill's own
  instructions.
- When adding, removing, or renaming Codex reviewer prompts, update the validator
  constants in `plugins/reviewer/scripts/validate_codex_reviewer.py` and the
  related tests as needed.
- For opencode reviewer changes, keep the primary orchestrator agent in
  `plugins/reviewer/opencode/agents/reviewer.md`, reviewer subagents in
  `plugins/reviewer/opencode/agents/*.md`, and the `/parallel-review` command in
  `plugins/reviewer/opencode/commands/parallel-review.md`.
- In opencode files, do not add Claude plugin prefixes or Codex skill syntax.
  opencode uses bare agent names, the `Task` tool with `subagent_type`, and
  model selection through `opencode.json` rather than per-call flags.
- Keep reviewer agents and reviewer reference prompts read-only in review mode.
  The orchestrator may offer fixes or posting only after findings are reported
  and the user chooses an action.
- Use relative repository paths in plugin manifests and marketplace entries.
  Do not hard-code local absolute paths, credentials, or machine-specific data.

## Validation

- Run the reviewer bundle validator after changing reviewer platform files:

  ```sh
  python3 plugins/reviewer/scripts/validate_codex_reviewer.py
  ```

- Run the validator unit tests after changing validator logic:

  ```sh
  python3 -m unittest plugins/reviewer/scripts/test_validate_codex_reviewer.py
  ```

- For JSON-only manifest or marketplace edits, also check the touched JSON files
  parse cleanly, for example with `python3 -m json.tool <file>`.

- Run the Shipwright bundle validator after changing Shipwright platform files:

  ```sh
  python3 plugins/shipwright/scripts/validate_shipwright.py
  ```

- Run the Shipwright validator unit tests after changing validator logic:

  ```sh
  python3 -m unittest plugins/shipwright/scripts/test_validate_shipwright.py
  ```
