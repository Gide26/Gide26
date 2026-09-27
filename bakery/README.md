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
| Code | ~10,200 lines across 32 source files |

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
npm test                  # end-to-end checks against a RUNNING server

node server/cli.js stats       # table row counts
node server/cli.js list-users  # every account and role
node server/cli.js create-owner
```

Environment variables: `PORT` (default 3000), `HOST` (default 0.0.0.0),
`BAKERY_DB`, `BAKERY_DATA_DIR`, `BAKERY_SEED` (`demo` or `empty`).

### Tests

`npm test` runs `test/smoke.sh` against a running server. It signs in as owner
and as staff and asserts the guarantees the offline design depends on: a
replayed sale returns the original record instead of selling twice; an edit
carrying a stale `updated_at` is refused with `409` carrying both timestamps and
is never applied; a delete replayed after the row is gone is satisfied rather
than erroring; staff cannot edit products or read owner reports; and the PWA
manifest and icon set are served as branded. It is deliberately a black-box
script over HTTP, so it tests the contract a phone actually relies on.

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
    offline.js   IndexedDB outbox: queue writes offline, replay them idempotently
    api.js       fetch wrapper, endpoint methods
    format.js    money, dates, quantities, percentages, escaping
    ui.js        toasts, sheets, dialogs, icons, skeletons
    charts.js    hand-written SVG charts, no library
    views/       one module per screen, lazy-loaded on demand
  manifest.webmanifest, sw.js, icons/   installable PWA
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
- Offline writes carry a `client_ref` idempotency key, backed by a unique partial
  index on `sales`, `expenses` and `stock_moves`. Replaying a queued item can
  never double-count it.

---

## Offline and online

**Online** is the normal case: every device talks to the same server, so a sale
rung up on the phone appears on the desktop immediately.

**Offline** the till keeps working. This matters — a bakery cannot stop trading
because the connection dropped.

| While offline | |
|---|---|
| Open the app | Yes — the shell is cached, screens open instantly |
| Take a sale | Yes — queued on the device |
| Record an expense | Yes — queued on the device |
| Record waste or a purchase | Yes — queued on the device |
| **Edit** an expense, product, customer or ingredient | Yes — queued on the device |
| **Delete** one of those | Yes — queued on the device |
| Correct a price at the counter | Yes — the till grid and product list come from cache |
| Print a receipt | Yes — a provisional one, marked as not yet sent |
| Add a brand-new product | **No** — needs a connection (see below) |
| See stock quantities | **No** — deliberately hidden |
| Read reports or history | No — that needs the server |

Queued writes go to **IndexedDB**, not `localStorage`, because it is durable
storage and survives clearing browsing data in an installed PWA. They survive
closing the tab and rebooting the phone. The queue drains automatically when the
connection returns, oldest first, and can be sent by hand from the Sales screen,
which also lists everything still waiting.

Two guarantees make this safe:

**Nothing is duplicated.** Every queued write carries a client-generated
`client_ref`, which the server treats as an idempotency key (a unique partial
index on each table). This matters because the dangerous case is ambiguous: the
request reached the server, the sale was recorded, and the reply was lost. The
client cannot tell, so it retries — and the server returns the original record
instead of selling twice. A sale replayed five times is stored once.

**Nothing is dated wrongly.** An offline sale is timestamped in the *business*
timezone at the moment it was taken, not when it syncs. A phone set to another
timezone, or a queue that drains the next morning, still reports the sale on the
day it actually happened.

Stock quantities are hidden offline on purpose. A number that looks current but
is hours stale is worse than no number, because someone will reorder against it.
Movements are still recorded; the level updates when they reach the server.

If the server rejects a queued item — a product was deleted mid-outage, say —
that item is parked with the server's exact reason and shown on the Sales screen
for someone to fix, rather than silently retried forever or blocking the rest of
the queue.

### Editing offline, and what happens when two people edit the same thing

An edit or delete is queued like a sale, and carries the `updated_at` stamp the
device last saw as `base_updated_at`. On reconnect the server compares them:

- **The stamp matches** — nobody touched the record in between, so the change is
  applied and the stamp advances.
- **The stamp is older** — someone else changed that record while this device was
  offline. The server refuses with `409` and returns *both* timestamps. The item
  is parked on the device as a **conflict**, showing what the server has and what
  you had, with two buttons: **Keep mine** (sends your version, deliberately
  dropping the check) and **Keep the server's** (discards your queued change).
- **The record is gone** — a queued delete is treated as already satisfied; a
  queued edit is parked with the reason, because dropping it would lose work
  nobody knows about.

Last-write-wins was rejected on purpose. Two cashiers correcting the same
expense during an outage would otherwise silently destroy one of the
corrections, and for money data an unresolved question beats a confident wrong
answer. A conflict is parked for a human, and it steps aside rather than
blocking the queue — one disputed expense must not stop the till sending sales.

Replayed edits and deletes are safe: the server keeps a `sync_log` of every
offline write it has applied, keyed by `client_ref`, so a retry is answered from
the log instead of being applied a second time.

`updated_at` carries milliseconds even though business timestamps do not. It is
never read as a time — only compared for equality — and at whole-second
precision two writes in the same second look identical, which would let a stale
edit through as current.

Creating a *new product* offline is refused rather than queued. A new product has
no server-side identity yet, so two devices each inventing one would produce
duplicates that no idempotency key can reconcile. Editing an existing one is
safe, which covers the case that actually happens at a counter: the price was
wrong.

Screens that fall back to cached data say so on screen, because a cost figure
from the last sync may be stale and should not be trusted as current.

## Installing as an app

The site is a Progressive Web App: install it and it launches full-screen with
its own icon, no browser chrome, and keeps working through an outage.

### 1. Start the server (once, on the computer that holds the data)

```bash
cd bakery
npm start
```

Leave this computer on. Every device — including this one — reads and writes the
same database through it. Nothing is stored per-device except the offline queue.

To find the address other devices need, print the computer's LAN IP:

```bash
ip addr show | grep 'inet ' | grep -v 127.0.0.1     # Linux
ipconfig | findstr IPv4                              # Windows
```

Use the `192.168.x.x` (or `10.x.x.x`) address. Phones must be on the **same
Wi-Fi network**.

### 2. Install on the computer (Chrome or Edge)

1. Open <http://localhost:3000> and sign in.
2. Click the **install icon** — a small monitor with a down arrow — at the right
   end of the address bar. If it is not there, open the menu (⋮) → **Install
   Bakery Tracker…** / **Apps → Install this site as an app**.
3. Confirm. It now appears in the start menu / Applications and opens in its own
   window with no address bar.

### 3. Install on an Android phone (Chrome)

1. On the same Wi-Fi, open `http://<computer-ip>:3000` — for example
   `http://192.168.1.20:3000`.
2. Sign in.
3. Tap the menu (⋮) → **Install app** (on some versions: **Add to Home
   screen**).
4. Confirm **Install**. The icon lands on the home screen and opens full-screen.

### 4. Install on an iPhone or iPad (Safari)

1. On the same Wi-Fi, open `http://<computer-ip>:3000` **in Safari** — Chrome on
   iOS cannot install PWAs.
2. Sign in.
3. Tap the **Share** button (the square with an up arrow).
4. Scroll and tap **Add to Home Screen**, then **Add**.

### 5. After installing

- Sign in once on each device. The session is remembered, so staff do not re-enter
  a password every shift.
- Open the app once while online so the shell caches. From then on it opens
  instantly and keeps working offline.
- The offline queue lives in **IndexedDB**, which survives closing the app and
  rebooting the phone. Do not clear site data for the app or you will lose
  anything not yet sent.
- To update after a code change, bump `VERSION` in `public/sw.js`; installed apps
  pick up the new shell on their next launch.

### If the phone cannot reach the computer

- Check both are on the same Wi-Fi — a phone on mobile data will not see a LAN
  address.
- Check the computer's firewall allows incoming connections on port 3000.
- Confirm the server prints `Listening on http://0.0.0.0:3000`. If it says
  `127.0.0.1`, other devices cannot reach it.

The service worker caches the app shell — every JS module, the stylesheet and the
icon — so screens open instantly, while data requests always go to the network. It
never caches `/api/`, so two devices can never disagree about what has been sold.

---

## Notes

- Money is stored as integers in BIF and rounded to the configured number of
  decimal places (0 for BIF). Changing `currency_decimals` in settings affects
  display only.
- Product and category breakdowns allocate each sale's discount pro-rata across
  its lines, so they sum exactly to headline revenue rather than overstating it.
- Timestamps are stored in UTC and rendered in the business timezone. "Today"
  comes from the server, so a phone set to the wrong date still reports the
  right day.
- The demo data is deterministic for a given day: re-seeding on the same date
  produces the same numbers.
