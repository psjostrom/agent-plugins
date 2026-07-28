# agent-plugins

Personal plugins for Claude Code, Codex, Cursor, and opencode.

- `reviewer` — risk-based parallel review for pull requests and local changes.
- `homey` — Homey Pro flow management for Claude Code.
- `shipwright` — strict end-to-end development via `$shipwright:shipwright` in Codex, `/shipwright:shipwright` in Claude Code, or `/shipwright` in Cursor.

## Install

### Codex

Add this repository as a marketplace, then install the plugins you want:

```sh
codex plugin marketplace add psjostrom/agent-plugins
codex plugin add reviewer@agent-plugins
codex plugin add shipwright@agent-plugins
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
6.1.1+ as a separate Cursor marketplace plugin) and reviewer
(`/parallel-review`, or “use parallel-review”).

#### Local iteration (plugin development only)

`~/.cursor/plugins/local` is for testing unpublished changes, not durable
installs. Cursor rejects symlinks whose target is outside that directory, so
this repo's installer copies the plugin tree:

```sh
./install-cursor.sh install reviewer
./install-cursor.sh install shipwright
./install-cursor.sh list
```

Reload the Cursor window afterward (`Developer: Reload Window`). Re-run install
after source edits. Uninstall with:

```sh
./install-cursor.sh uninstall reviewer
./install-cursor.sh uninstall shipwright
```

### opencode

opencode currently supports the `reviewer` plugin. Clone this repository, then
run the installer from its root:

```sh
git clone https://github.com/psjostrom/agent-plugins.git
cd agent-plugins
./install-opencode.sh install reviewer
```

This installs global symlinks under `~/.config/opencode/`. For a repository-only
installation, run the installer from that repository and pass `--project`:

```sh
/path/to/agent-plugins/install-opencode.sh install reviewer --project
```
