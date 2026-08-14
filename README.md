# Agent Plugins

Per Sjöström's marketplace/catalog of agent plugins.

Implementations live in standalone repositories:

- [Reviewer](https://github.com/psjostrom/reviewer) — risk-based parallel code review.
- [Shipwright](https://github.com/psjostrom/shipwright) — strict end-to-end development.
- [Handoff](https://github.com/psjostrom/handoff) — self-contained continuation dossiers.
- [Homey](https://github.com/psjostrom/homey) — Homey Pro flow management for Claude Code.

## Harness coverage

| Plugin | Claude Code | Codex | Cursor | opencode |
| --- | --- | --- | --- | --- |
| Reviewer | yes | yes | yes | yes |
| Shipwright | yes | yes | yes | no port |
| Handoff | yes | yes | yes | yes |
| Homey | yes | no | no | no |

## Plugin versus skill

A plugin is the installable package discovered by a harness. A skill is an
instruction entrypoint inside a plugin. Reviewer, Shipwright, and Handoff expose
skills where supported; Homey is a Claude Code command plugin, not an Agent
Skill.

## Install

### Claude Code

Existing marketplace commands stay unchanged:

```sh
claude plugin marketplace add psjostrom/agent-plugins
claude plugin install reviewer@agent-plugins
claude plugin install homey@agent-plugins
claude plugin install shipwright@agent-plugins
claude plugin install handoff@agent-plugins
```

### Codex

Existing marketplace commands stay unchanged:

```sh
codex plugin marketplace add psjostrom/agent-plugins
codex plugin add reviewer@agent-plugins
codex plugin add shipwright@agent-plugins
codex plugin add handoff@agent-plugins
```

Start a new task after installation so installed skills are available.

### Cursor migration

This repository no longer publishes a Cursor marketplace. Its old marketplace
URL no longer updates these plugins. Install the standalone
[Reviewer](https://github.com/psjostrom/reviewer),
[Shipwright](https://github.com/psjostrom/shipwright), and
[Handoff](https://github.com/psjostrom/handoff) listings through Cursor's
plugin UI. Shipwright also requires Superpowers 6.1.1 or newer as a separate
Cursor plugin. Homey has no Cursor port.

### OpenCode migration

OpenCode users clone each supported standalone repository and run its installer:

```sh
git clone https://github.com/psjostrom/reviewer.git
cd reviewer
git checkout a96927c6bd11d72a40f1f34610e53a2f3a19e2ee
./install-opencode.sh install
cd ..

git clone https://github.com/psjostrom/handoff.git
cd handoff
git checkout 7c6ce811f81631aa8d73cf45ae3a6c8f37b5ce3a
./install-opencode.sh install
```

These replace the catalog commands `./install-opencode.sh install reviewer` and
`./install-opencode.sh install handoff`. Reviewer and Handoff require the global
install for trusted shared-file resolution; `--project` adds discovery links but
does not replace it. Existing Handoff users must follow the
[guarded legacy-link replacement](https://github.com/psjostrom/handoff#migration)
before installing. Shipwright and Homey have no OpenCode port.

## Invoke

| Plugin | Codex | Claude Code | Cursor | opencode |
| --- | --- | --- | --- | --- |
| Reviewer | `$parallel-review` | `/reviewer:review` | `/parallel-review` | `/parallel-review` |
| Shipwright | `$shipwright:shipwright` | `/shipwright:shipwright` | `/shipwright` | — |
| Handoff | `$handoff:handoff` | `/handoff:handoff` | `/handoff` | `/handoff` |
| Homey | — | `/homey:homey-flows` | — | — |

See each standalone repository for behavior, safety, uninstall, and development
documentation.
