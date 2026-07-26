# agent-plugins

Personal plugins for Claude Code, Codex, Cursor, and opencode.

- `reviewer` — risk-based parallel review for pull requests and local changes.
- `homey` — Homey Pro flow management for Claude Code.
- `shipwright` — strict end-to-end development via `$shipwright:shipwright` in Codex or `/shipwright:shipwright` in Claude Code.

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

### Cursor

Install reviewer (and any other Cursor-packaged plugins) from a local checkout:

```sh
git clone https://github.com/psjostrom/agent-plugins.git
cd agent-plugins
./install-cursor.sh install reviewer
```

List available plugins and install state:

```sh
./install-cursor.sh list
```

Uninstall:

```sh
./install-cursor.sh uninstall reviewer
```

Invoke parallel review explicitly in Cursor — for example "use parallel-review"
or `/parallel-review` when Cursor surfaces the slash command. The skill does
not auto-invoke from ambient chat.
