#!/bin/sh
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_TARGET="${HOME}/.config/opencode"
PROJECT_TARGET="$(pwd)/.opencode"

usage() {
  cat <<EOF
Usage:
  ./install-opencode.sh install <plugin>           Symlink globally (~/.config/opencode/)
  ./install-opencode.sh install <plugin> --project  Symlink to .opencode/ in current directory
  ./install-opencode.sh uninstall <plugin>          Remove from global config
  ./install-opencode.sh uninstall <plugin> -p       Remove from project config
  ./install-opencode.sh list                        Show available plugins
EOF
}

available_plugins() {
  for dir in "$SCRIPT_DIR"/plugins/*/opencode; do
    [ -d "$dir" ] || continue
    basename "$(dirname "$dir")"
  done
}

# Remove symlinks in the target that point into the plugin's source dir but
# no longer resolve (the backing file was renamed or deleted). Handles upgrades
# across file renames — e.g. review.md -> parallel-review.md — where the prior
# install left a dangling link opencode would still discover.
prune_stale_links() {
  p_src="$1"
  p_target="$2"
  for sub in "$p_src"/*; do
    [ -d "$sub" ] || continue
    category="$(basename "$sub")"
    [ -d "$p_target/$category" ] || continue
    for link in "$p_target/$category"/*; do
      [ -L "$link" ] || continue
      case "$(readlink "$link")" in
        "$p_src"/*)
          [ -e "$link" ] || { rm "$link"; echo "  pruned stale $link"; }
          ;;
      esac
    done
  done
}

link_plugin() {
  plugin="$1"
  target="$2"
  src="$SCRIPT_DIR/plugins/$plugin/opencode"
  if [ ! -d "$src" ]; then
    echo "Plugin \"$plugin\" not found or has no opencode port."
    echo "Available: $(available_plugins | tr '\n' ' ')"
    exit 1
  fi

  prune_stale_links "$src" "$target"

  for sub in "$src"/*; do
    [ -e "$sub" ] || continue
    category="$(basename "$sub")"
    mkdir -p "$target/$category"
    for file in "$sub"/*; do
      [ -e "$file" ] || continue
      name="$(basename "$file")"
      dest="$target/$category/$name"
      if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        echo "  skip $dest — exists and is not a symlink (use uninstall first if you want to replace it)"
        continue
      fi
      ln -sfn "$file" "$dest"
      echo "  linked $dest"
    done
  done
  echo "Installed $plugin -> $target"
}

unlink_plugin() {
  plugin="$1"
  target="$2"
  src="$SCRIPT_DIR/plugins/$plugin/opencode"
  if [ ! -d "$src" ]; then
    echo "Plugin \"$plugin\" not found."
    exit 1
  fi

  prune_stale_links "$src" "$target"

  for sub in "$src"/*; do
    [ -e "$sub" ] || continue
    category="$(basename "$sub")"
    for file in "$sub"/*; do
      [ -e "$file" ] || continue
      name="$(basename "$file")"
      link="$target/$category/$name"
      if [ -L "$link" ]; then
        rm "$link"
        echo "  removed $link"
      fi
    done
  done
  echo "Uninstalled $plugin from $target"
}

command="${1:-}"
plugin=""
project=false

for arg in "$@"; do
  case "$arg" in
    --project|-p) project=true ;;
    -*) ;;
    *) [ "$arg" != "$command" ] && plugin="$arg" ;;
  esac
done

target="$GLOBAL_TARGET"
[ "$project" = true ] && target="$PROJECT_TARGET"

case "$command" in
  install)
    [ -z "$plugin" ] && { echo "Specify a plugin to install.\n"; usage; exit 1; }
    link_plugin "$plugin" "$target"
    ;;
  uninstall)
    [ -z "$plugin" ] && { echo "Specify a plugin to uninstall.\n"; usage; exit 1; }
    unlink_plugin "$plugin" "$target"
    ;;
  list)
    echo "Target: $target\n"
    for p in $(available_plugins); do
      if [ -L "$target/agents/reviewer.md" ] && [ "$p" = "reviewer" ]; then
        echo "  [x] $p"
      else
        echo "  [ ] $p"
      fi
    done
    ;;
  *)
    usage
    exit 1
    ;;
esac
