#!/usr/bin/env bash
# Publish the tracker to its own repo — for GitHub Pages or any static host.
# Copies this folder into a clean temp repo, leaving your private config.js behind,
# then pushes it to the remote you give it.
#
#   bash publish.sh https://github.com/Gide26/tracker.git
#
# The target repo must already exist and be empty (no README on first push).
set -euo pipefail

REMOTE="${1:?Usage: bash publish.sh <git-remote-url>}"
SRC="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ copying $SRC (excluding config.js)"
tar -cf - --exclude='./config.js' --exclude='./.DS_Store' . 2>/dev/null | tar -xf - -C "$TMP" 2>/dev/null || \
  (cd "$SRC" && tar -cf - --exclude='config.js' --exclude='.DS_Store' .) | (cd "$TMP" && tar -xf -)

cd "$TMP"
rm -f config.js
git init -q -b main
git add -A
git -c user.name="Gide" -c user.email="gide26@users.noreply.github.com" \
  commit -q -m "Money tracker — update $(date +%Y-%m-%d)"
git push -q "$REMOTE" main

echo "✓ pushed to $REMOTE (branch main)"
echo "  If Pages is enabled on that repo, it rebuilds in a minute or two."
