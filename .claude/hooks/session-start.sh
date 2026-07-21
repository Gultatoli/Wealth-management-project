#!/bin/bash
# SessionStart hook: install the Superpowers skills library into .claude/skills/
# so it is available in every Claude Code on the web session.
#
# Superpowers (https://github.com/obra/superpowers, MIT, (c) Jesse Vincent) is
# NOT vendored into this repo — it is fetched fresh here to keep the repo clean.
# See .claude/skills/NOTICE.md for attribution. The personal `the-humanizer`
# skill IS committed and is not touched by this hook.
set -euo pipefail

# Only run in Claude Code on the web (remote) sessions. Local installs should
# use the plugin marketplace instead (`claude plugin install superpowers`).
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SKILLS_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/skills"

# Idempotent: if the library is already present in this container, do nothing.
if [ -f "$SKILLS_DIR/using-superpowers/SKILL.md" ]; then
  exit 0
fi

mkdir -p "$SKILLS_DIR"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if git clone --quiet --depth 1 https://github.com/obra/superpowers.git "$TMP/superpowers" 2>/dev/null; then
  # Copy each skill directory in; never overwrites the personal the-humanizer skill.
  cp -R "$TMP/superpowers/skills/." "$SKILLS_DIR/"
  echo "Superpowers skills installed into .claude/skills/"
else
  echo "WARNING: could not fetch superpowers from GitHub (network policy?); continuing without it." >&2
fi
