# Publishing the viewer to GitHub Pages

GitHub gives **one Pages site per repository**, and `Gide26/Gide26` already
uses its site (https://gide26.github.io/Gide26/) for the photography guide,
built from `/docs` on `arena/01a0e417-gide26`. So the artwork viewer gets its
own repository.

The Arena GitHub app can read and write this repository but **cannot create new
ones** (403 Resource not accessible by integration), so the empty repository has
to be made once by hand — 30 seconds:

1. https://github.com/new
2. Name: **bcm-signage** · Public · do **not** add a README, .gitignore or licence
3. Create repository — then tell me, and I will run the publish.

What I run once it exists:

```bash
cd /home/user/Gide26
git fetch -q origin arena/65a67965-gide26 && git reset --hard -q origin/arena/65a67965-gide26
gh repo clone Gide26/bcm-signage /tmp/bcm-site
cp -r bcm/. /tmp/bcm-site/
cd /tmp/bcm-site && git add -A && git commit -m "BCM Medical Centre signage viewer"
git push -q origin HEAD:main
gh api -X POST repos/Gide26/bcm-signage/pages -f 'source[branch]=main' -f 'source[path]=/'
```

Result: **https://gide26.github.io/bcm-signage/** — hub at the root,
`/premises/` for the in-situ views, `/premises/in-place.html` for the single
file, `/print/PRINT-INDEX.pdf` for the 30 print files.

The photography site is untouched.

## If you would rather not make a repository

Repoint the existing site at this branch instead (the photography guide stops
being served):

```bash
gh api -X PUT repos/Gide26/Gide26/pages \
  -f 'source[branch]=arena/65a67965-gide26' -f 'source[path]=/bcm'
```

Back to the old one:

```bash
gh api -X PUT repos/Gide26/Gide26/pages \
  -f 'source[branch]=arena/01a0e417-gide26' -f 'source[path]=/docs'
```
