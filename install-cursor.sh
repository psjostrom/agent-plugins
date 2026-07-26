#!/bin/sh
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CURSOR_PLUGINS="${CURSOR_PLUGINS_LOCAL:-${HOME}/.cursor/plugins/local}"

usage() {
  cat <<EOF
Usage:
  ./install-cursor.sh install <plugin>    Symlink plugin into ~/.cursor/plugins/local/
  ./install-cursor.sh uninstall <plugin>  Remove plugin symlink
  ./install-cursor.sh list                Show available plugins and install state

Environment:
  CURSOR_PLUGINS_LOCAL   Override the local plugins directory
                         (default: ~/.cursor/plugins/local)
EOF
}

available_plugins() {
  for dir in "$SCRIPT_DIR"/plugins/*/.cursor-plugin; do
    [ -d "$dir" ] || continue
    basename "$(dirname "$dir")"
  done
}

install_plugin() {
  plugin="$1"
  src="$SCRIPT_DIR/plugins/$plugin"
  manifest="$src/.cursor-plugin/plugin.json"
  if [ ! -f "$manifest" ]; then
    echo "Plugin \"$plugin\" not found or has no Cursor surface."
    echo "Available: $(available_plugins | tr '\n' ' ')"
    exit 1
  fi
  mkdir -p "$CURSOR_PLUGINS"
  dest="$CURSOR_PLUGINS/$plugin"
  if [ -L "$dest" ]; then
    :
  elif [ -e "$dest" ]; then
    echo "Refusing to install $plugin: $dest exists and is not a symlink."
    echo "Remove or rename that path, then retry."
    exit 1
  fi
  ln -sfn "$src" "$dest"
  echo "Installed $plugin -> $dest"
}

uninstall_plugin() {
  plugin="$1"
  dest="$CURSOR_PLUGINS/$plugin"
  if [ ! -L "$dest" ]; then
    echo "Plugin \"$plugin\" is not installed as a symlink at $dest"
    exit 1
  fi
  rm "$dest"
  echo "Uninstalled $plugin from $CURSOR_PLUGINS"
}

list_plugins() {
  echo "Target: $CURSOR_PLUGINS"
  echo
  for plugin in $(available_plugins); do
    dest="$CURSOR_PLUGINS/$plugin"
    if [ -L "$dest" ]; then
      echo "  [x] $plugin -> $(readlink "$dest")"
    else
      echo "  [ ] $plugin"
    fi
  done
}

command="${1:-}"
plugin="${2:-}"

case "$command" in
  install)
    [ -z "$plugin" ] && { echo "Specify a plugin to install."; echo; usage; exit 1; }
    install_plugin "$plugin"
    ;;
  uninstall)
    [ -z "$plugin" ] && { echo "Specify a plugin to uninstall."; echo; usage; exit 1; }
    uninstall_plugin "$plugin"
    ;;
  list)
    list_plugins
    ;;
  *)
    usage
    exit 1
    ;;
esac
