# Bakery Tracker

A complete point-of-sale and business-management system for a bakery. Runs on a
computer and on a phone from the same server, with live-synced data.

**Zero npm dependencies.** The whole thing — HTTP server, router, sessions,
password hashing, database, charts, service worker — is built on Node's standard
library and the browser's standard APIs. There is no `node_modules` folder and
nothing to install.

| | |
|---|---|
| Requires | Node.js **22.5.0** or newer |
| Database | SQLite, built into Node (`node:sqlite`) |
| Currency | Burundian franc (BIF, `FBu`, 0 decimal places) |
| Timezone | Africa/Bujumbura by default, configurable |
| Front-end | Vanilla ES modules, installable PWA |
| Code | ~7,000 lines across 34 files |

---

## Quick start

```bash
cd bakery
npm start
```

Open <http://localhost:3000>. On a phone on the same network, open
`http://<your-computer-ip>:3000`.

The first run creates `data/bakery.sqlite` and seeds **60 days of realistic demo
data** so every screen has something to show. The sign-in screen prints the demo
logins:

| Role | Phone | Password |
|---|---|---|
| Owner | `079000000` | `changeme` |
| Staff | `079111111` | `staff123` |

Both are flagged *must change password* — the app asks on first sign-in.

### Starting with a clean database instead

```bash
BAKERY_SEED=empty npm start
```

You get a first-run setup screen where you name the business and create the
owner account. Everything starts at zero.

---

## What it does

### Point of sale
Product tiles grouped by category, a cart with quantity steppers, discounts,
four payment methods (cash, mobile money, card, credit), change calculation, and
a receipt you can print or share over WhatsApp. Keyboard shortcuts on desktop;
a thumb-reach cart bar and full-screen sheets on phones.

### Recipes and costing
Every product has a recipe of ingredient quantities. Unit cost is calculated
from live ingredient prices, so profit margins stay honest as flour prices move.
The product editor shows the cost building up line by line and can **suggest a
selling price** for a target margin.

### Inventory
Ingredients with stock levels, reorder points, suppliers, and a full movement
ledger. Sales deduct stock automatically through the recipe. Purchases, waste,
returns and corrections can be recorded manually. Low-stock alerts surface on
the dashboard and at the till.

### Sales, expenses, customers
Searchable sale history with reprintable receipts and voiding (stock is returned
when a sale is voided). Expense tracking by category with monthly budgets.
Customer records with credit balances, loyalty notes, and purchase history.

### Reports (owner only)
Profit & loss, revenue trends, peak hours, best and worst sellers, payment mix,
expense breakdown, staff performance, top customers, and ingredient usage.
Everything exports to CSV. Historical profit is calculated from a cost snapshot
taken at the moment of sale, so old reports never shift when you update a recipe.

---

## Roles

**Owner** — everything: costs, margins, reports, the product catalogue,
suppliers, expenses, staff accounts, and business settings.

**Staff** — the till, their own sales, stock levels, and recording waste. They
cannot see costs, profit, reports, other people's sales, or any management
screen. Cost fields are stripped from the API responses themselves, not merely
hidden in the interface.

---

## Commands

```bash
npm start                 # run the server on port 3000
npm run dev               # run with --watch, restarts on file changes

npm run seed-demo         # load 60 days of demo data (fails if data exists)
npm run reset-password    # interactively reset a user's password
npm run backup            # copy the database into data/backups/
npm run wipe              # delete all data (asks for confirmation)

node server/cli.js stats       # table row counts
node server/cli.js list-users  # every account and role
node server/cli.js create-owner
```

Environment variables: `PORT` (default 3000), `HOST` (default 0.0.0.0),
`BAKERY_DB`, `BAKERY_DATA_DIR`, `BAKERY_SEED` (`demo` or `empty`).

---

## How it is put together

```
server/
  index.js     HTTP entry point, static files, ETag, CSP, SPA fallback
  router.js    dependency-free router, JSON body parsing, auth injection
  api.js       ~50 REST endpoints
  reports.js   reporting engine + CSV generation (owner only)
  auth.js      sessions, scrypt hashing, throttling, cookies
  db.js        schema (13 tables), settings, transactions, costing
  seed.js      the demo dataset
  util.js      validation, money rounding, timezone dates, CSV, escaping
  cli.js       command-line tools

public/
  index.html   app shell
  css/styles.css   design system: mobile tab bar, desktop sidebar
  js/
    app.js       boot, navigation, route rendering with a race guard
    router.js    hash router
    store.js     session state, cached data loading, settings
    api.js       fetch wrapper, endpoint methods
    format.js    money, dates, quantities, percentages, escaping
    ui.js        toasts, sheets, dialogs, icons, skeletons
    charts.js    hand-written SVG charts, no library
    views/       one module per screen, lazy-loaded on demand
  manifest.webmanifest, sw.js, icon.svg   installable PWA
```

Server modules import each other in one direction only:
`index.js → router.js → api.js / reports.js → auth.js → db.js → util.js`.

The front-end is a single-page app with a hash router. Each screen is a separate
module fetched only when you navigate to it, and a render token discards any
response that arrives after you have already moved on.

---

## Security

- Passwords hashed with **scrypt** (N=16384) and a per-user salt; compared with
  `crypto.timingSafeEqual`.
- Sessions are opaque 32-byte random tokens. Only their SHA-256 hash is stored,
  so reading the database does not hand over active sessions. They slide forward
  on use and expire after 30 days.
- Cookies are `HttpOnly`, `SameSite=Strict`, and `Secure` whenever the request
  arrived over HTTPS or through a proxy that said so.
- Every request gets `Content-Security-Policy` (no inline scripts, `self` only),
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, and a `Permissions-Policy`.
- All SQL is parameterised. Identifiers are never interpolated.
- Static serving is confined to `public/`. Paths that name a file which does not
  exist return 404 rather than the app shell, and any dot-prefixed path segment
  (`/.git/config`, `/.env`) is refused outright.
- Login attempts are throttled by phone number and IP, with a 10-minute lockout
  after 8 failures.
- Every value rendered into HTML passes through an escaping helper.
- Owner-only endpoints reject staff with 403 before running any query.

**Before real use:** put the server behind HTTPS (Caddy or nginx make this a
few lines), change both demo passwords, and run `npm run backup` on a schedule.

---

## Data

Everything lives in `data/bakery.sqlite`. That directory is git-ignored.

- Back up by copying the file while the server is stopped, or with
  `npm run backup`.
- `npm run wipe` deletes it and starts over.
- Invoice numbering is self-healing: it takes the higher of the stored counter
  and the largest existing invoice number, so a restored backup never collides.

---

## Installing as an app

The site is a Progressive Web App. On Android Chrome, the menu offers **Install
app**; on iOS Safari, **Share → Add to Home Screen**. It then launches
full-screen with its own icon. The service worker caches only the app shell, so
the screens open instantly, while every data request always goes to the network
— you never see stale numbers.

---

## Notes

- Money is stored as integers in BIF and rounded to the configured number of
  decimal places (0 for BIF). Changing `currency_decimals` in settings affects
  display only.
- Timestamps are stored in UTC and rendered in the business timezone. "Today"
  comes from the server, so a phone set to the wrong date still reports the
  right day.
- The demo data is deterministic for a given day: re-seeding on the same date
  produces the same numbers.
