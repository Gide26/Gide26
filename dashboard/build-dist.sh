#!/usr/bin/env bash
# Build a 5-file bundle you can upload to a fresh repo by hand (no git needed):
#
#   dist/index.html   — CSS + JS inlined, ONE file
#   dist/manifest.json
#   dist/sw.js        — offline cache
#   dist/icon-192.png
#   dist/icon-512.png
#
#   bash build-dist.sh
#
# Your private config.js is NOT included — the bundle ships demo numbers,
# so it's safe to upload to a public repo. Enter your rates in ⚙ Settings.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DIST="$SRC/dist"

rm -rf "$DIST"
mkdir -p "$DIST"

python3 - "$SRC" "$DIST" <<'PY'
import json, os, re, shutil, sys
src, dist = sys.argv[1], sys.argv[2]

html = open(os.path.join(src, 'index.html'), encoding='utf-8').read()
css  = open(os.path.join(src, 'styles.css'), encoding='utf-8').read()
js   = open(os.path.join(src, 'app.js'), encoding='utf-8').read()

html = html.replace('<link rel="stylesheet" href="styles.css" />',
                    '<style>\n' + css + '\n</style>')
html = re.sub(r'<script src="config\.js"[^>]*></script>\s*', '', html)
html = html.replace('<script src="app.js"></script>',
                    '<script>\n' + js + '\n</script>')
# icons sit at the root of the bundle
html = html.replace('href="icons/', 'href="')
html = html.replace('href="apple-touch-icon.png"', 'href="icon-192.png"')
open(os.path.join(dist, 'index.html'), 'w', encoding='utf-8').write(html)

m = json.load(open(os.path.join(src, 'manifest.json'), encoding='utf-8'))
for i in m['icons']:
    i['src'] = i['src'].replace('icons/', '')
json.dump(m, open(os.path.join(dist, 'manifest.json'), 'w', encoding='utf-8'), indent=2)

FILES = "const FILES = [\n  './',\n  './index.html',\n  './manifest.json',\n  './icon-192.png',\n  './icon-512.png'\n];"
sw = open(os.path.join(src, 'sw.js'), encoding='utf-8').read()
sw = re.sub(r'const FILES = \[.*?\];', FILES, sw, flags=re.S)
open(os.path.join(dist, 'sw.js'), 'w', encoding='utf-8').write(sw)

shutil.copy(os.path.join(src, 'icons', 'icon-192.png'), dist)
shutil.copy(os.path.join(src, 'icons', 'icon-512.png'), dist)
print('→ built ' + dist)
PY

echo "✓ 5 files ready in $DIST:"
ls -1 "$DIST"
