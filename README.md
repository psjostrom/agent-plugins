# agent-plugins

Personal plugins for Claude Code, Codex, Cursor, and opencode.

- `reviewer` — risk-based parallel review for pull requests and local changes.
- `homey` — Homey Pro flow management for Claude Code.
- `shipwright` — strict end-to-end development via `$shipwright:shipwright` in Codex, `/shipwright:shipwright` in Claude Code, or `/shipwright` in Cursor.
- `handoff` — write `.handoff/` dossiers for standard/frontier continuation via `$handoff:handoff` / `/handoff:handoff` / `/handoff`.

## Harness coverage

| Plugin | Claude Code | Codex | Cursor | opencode |
| --- | --- | --- | --- | --- |
| `reviewer` | yes | yes | yes | yes |
| `shipwright` | yes | yes | yes | no port |
| `handoff` | yes | yes | yes | yes |
| `homey` | yes | no | no | no |

## Install

### Codex

Add this repository as a marketplace, then install the plugins you want:

```sh
codex plugin marketplace add psjostrom/agent-plugins
codex plugin add reviewer@agent-plugins
codex plugin add shipwright@agent-plugins
codex plugin add handoff@agent-plugins
```

Start a new Codex task after installation so the installed skills are available.

To test an existing local checkout instead, run the marketplace command from
the repository root with `.` as the source:

```sh
codex plugin marketplace add .
```

### Claude Code

Add the marketplace and install the plugins you want:

```sh
claude plugin marketplace add psjostrom/agent-plugins
claude plugin install reviewer@agent-plugins
claude plugin install homey@agent-plugins
claude plugin install shipwright@agent-plugins
claude plugin install handoff@agent-plugins
```

Reload plugins in an active session with `/reload-plugins`, or start a new
Claude Code session. To install from a local checkout, replace
`psjostrom/agent-plugins` with `.` in the marketplace command.

### Cursor

This repository is a **marketplace of multiple plugins**, not a single plugin.
Cursor reads [`.cursor-plugin/marketplace.json`](.cursor-plugin/marketplace.json).
Add the marketplace once, then install each plugin you want from it.

**1. Add the marketplace**

- **Teams / Enterprise (preferred):** Dashboard → Plugins → Add Marketplace →
  Import from Repo → paste `https://github.com/psjostrom/agent-plugins`.
  Optionally enable Auto Refresh after connecting the Cursor GitHub App.
- **Personal:** Customize → Plugins → paste
  `https://github.com/psjostrom/agent-plugins` (or `/add-plugin` with that URL).
  That registers the marketplace catalog; it does not install every plugin.
  Personal GitHub marketplace imports can pin a stale commit; if
  Update/Reinstall does not move forward, re-import the marketplace or use
  local iteration below.

**2. Install individual plugins**

From the imported marketplace, install each plugin you want (user or project
scope). Currently listed: shipwright (`/shipwright`; requires Superpowers
6.1.1+ as a separate Cursor marketplace plugin), reviewer
(`/parallel-review`, or “use parallel-review”), and handoff (`/handoff`).

#### Local iteration (plugin development only)

`~/.cursor/plugins/local` is for testing unpublished changes, not durable
installs. Cursor rejects symlinks whose target is outside that directory, so
this repo's installer copies the plugin tree:

```sh
./install-cursor.sh install reviewer
./install-cursor.sh install shipwright
./install-cursor.sh install handoff
./install-cursor.sh list
```

Reload the Cursor window afterward (`Developer: Reload Window`). Re-run install
after source edits.

### opencode

opencode currently supports the `reviewer` and `handoff` plugins. Clone this
repository, then run the installer from its root:

```sh
git clone https://github.com/psjostrom/agent-plugins.git
cd agent-plugins
./install-opencode.sh install reviewer
./install-opencode.sh install handoff
```

This installs global symlinks under `~/.config/opencode/`. For a repository-only
installation, run the installer from that repository and pass `--project`:

```sh
/path/to/agent-plugins/install-opencode.sh install reviewer --project
```

## Uninstall

There is no single cross-harness uninstall. Use the matching harness below.

### Codex

```sh
codex plugin remove reviewer@agent-plugins
codex plugin remove shipwright@agent-plugins
codex plugin remove handoff@agent-plugins
```

`homey` is not a Codex plugin.

### Claude Code

```sh
claude plugin uninstall reviewer@agent-plugins
claude plugin uninstall homey@agent-plugins
claude plugin uninstall shipwright@agent-plugins
claude plugin uninstall handoff@agent-plugins
```

If the plugin was installed with a non-default scope, pass `--scope user`,
`--scope project`, or `--scope local` to match the install. You can also use
`/plugin` in a Claude Code session to uninstall interactively.

### Cursor

**Marketplace installs (durable):** Cursor does **not** ship a CLI uninstall for
marketplace plugins. Remove each plugin from **Customize → Plugins** (or the
Plugins UI): uninstall `reviewer`, `shipwright`, and/or `handoff` there.
`homey` is not a Cursor plugin.

**Local iteration copies only** (`~/.cursor/plugins/local`):

```sh
./install-cursor.sh uninstall reviewer
./install-cursor.sh uninstall shipwright
./install-cursor.sh uninstall handoff
```

Local uninstall does not remove a marketplace install, and vice versa.

### opencode

```sh
./install-opencode.sh uninstall reviewer
./install-opencode.sh uninstall handoff
```

If you installed with `--project` / `-p`, uninstall the same way:

```sh
./install-opencode.sh uninstall reviewer --project
./install-opencode.sh uninstall handoff --project
```

`shipwright` and `homey` have no opencode port, so there is nothing to uninstall
for them on opencode.
