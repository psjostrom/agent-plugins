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

From a local checkout, symlink plugins that have a `.cursor-plugin/` surface:

```sh
git clone https://github.com/psjostrom/agent-plugins.git
cd agent-plugins
./install-cursor.sh install reviewer
./install-cursor.sh install shipwright
./install-cursor.sh list
```

Reload the Cursor window afterward. Shipwright requires Superpowers 6.1.1 or
newer as a separate Cursor plugin. Invoke reviewer explicitly — for example
"use parallel-review" or `/parallel-review` when Cursor surfaces the slash
command. Uninstall with:

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

