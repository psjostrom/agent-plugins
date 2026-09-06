# Agent Plugins

A small catalog for installing four agent plugins across their supported coding
harnesses: parallel code review, end-to-end implementation, task handoff, and
Homey Pro flow management.

## Plugins

| Plugin | What it does | Claude Code | Codex | Cursor | OpenCode | Antigravity |
| --- | --- | --- | --- | --- | --- | --- |
| [Reviewer](https://github.com/psjostrom/reviewer) | Runs a risk-based panel of parallel code reviewers. | yes | yes | yes | yes | yes |
| [Shipwright](https://github.com/psjostrom/shipwright) | Drives approved development through implementation, review, verification, and QA. | yes | yes | yes | no | yes |
| [Handoff](https://github.com/psjostrom/handoff) | Writes a self-contained dossier for a fresh agent to continue a task. | yes | yes | yes | yes | yes |
| [Homey](https://github.com/psjostrom/homey) | Creates and manages Homey Pro flows through its local API. | yes | no | no | no | no |

Implementations, behavior, safety rules, and development instructions live in
the linked standalone repositories.

## Install

### Claude Code

Add this catalog, then install the plugins you want:

```sh
claude plugin marketplace add psjostrom/agent-plugins
claude plugin install reviewer@agent-plugins
claude plugin install shipwright@agent-plugins
claude plugin install handoff@agent-plugins
claude plugin install homey@agent-plugins
```

### Codex

Add this catalog, then install the supported plugins you want:

```sh
codex plugin marketplace add psjostrom/agent-plugins
codex plugin add reviewer@agent-plugins
codex plugin add shipwright@agent-plugins
codex plugin add handoff@agent-plugins
```

Start a new task after installation so Codex discovers the installed skills.

### Cursor

Public listings are not available for Reviewer, Shipwright, or Handoff. To use
one in Cursor, clone its standalone repository and load it as a local plugin.
Shipwright also requires Superpowers 6.1.1 or newer. Homey has no Cursor plugin.

### OpenCode

Clone Reviewer or Handoff and run its installer from the repository root:

```sh
git clone https://github.com/psjostrom/reviewer.git
cd reviewer
./install-opencode.sh install
cd ..

git clone https://github.com/psjostrom/handoff.git
cd handoff
./install-opencode.sh install
```

Both require the global install for trusted shared-file resolution.
`--project` adds local discovery links but does not replace it. Shipwright and
Homey have no OpenCode plugin.

### Antigravity

Install each supported standalone repository directly:

```sh
agy plugin install https://github.com/psjostrom/reviewer
agy plugin install https://github.com/psjostrom/shipwright
agy plugin install https://github.com/psjostrom/handoff
```

## Use

| Plugin | Claude Code | Codex | Cursor | OpenCode | Antigravity |
| --- | --- | --- | --- | --- | --- |
| Reviewer | `/reviewer:review` | `$parallel-review` | `/parallel-review` | `/parallel-review` | `/parallel-review` |
| Shipwright | `/shipwright:shipwright` | `$shipwright:shipwright` | `/shipwright` | — | `/shipwright` |
| Handoff | `/handoff:handoff` | `$handoff:handoff` | `/handoff` | `/handoff` | `/handoff` |
| Homey | `/homey:homey-flows` | — | — | — | — |

## Plugin versus skill

A plugin is the installable package discovered by a harness. A skill is an
instruction entrypoint inside a plugin. Reviewer, Shipwright, and Handoff expose
skills where supported. Homey is a Claude Code command plugin.

Licensed under [MIT](LICENSE).
