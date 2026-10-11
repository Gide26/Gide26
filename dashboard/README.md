# Money Tracker

A personal revenue dashboard that runs in your browser and installs on your phone like an app. Works offline. No build step, no dependencies — three files and some icons.

## Your numbers (privacy)

**No real income figures are in this repo.** The committed code ships with made-up demo numbers.

Your actual figures go in **`config.js`**, which is gitignored:

```bash
cp config.example.js config.js   # then edit it
```

- `config.js` seeds a **fresh** browser. Once you've used the app, `localStorage` wins over it.
- Settings → **Reset all data** wipes localStorage and re-seeds from `config.js`.
- Don't want a config file at all? Just edit the rates in **⚙ Settings** — they persist in that browser.
- Money you log never leaves your device. It lives in `localStorage` until you Export it.

## What the demo numbers look like

| Stream | Month 1 | Growth | Scales? | 6-month plan |
| --- | --- | --- | --- | --- |
| Clothes sales | 1,000,000 | +10%/mo | yes | 7,720,000 |
| Writing gigs | 500,000 | 0% | yes | 3,000,000 |
| Job income | 500,000 | 0% | no | 3,000,000 |
| Investing | 100,000 | 0% | no | 600,000 |
| **Total** | **2,100,000** | | | **14,320,000** |

Against a 24M goal, the **Reality check** panel says: 14.32M delivered, 9.68M short, needing 4M/month (1.7× the plan's average) or +32.6% growth every month on the scalable streams — or 11 months instead of 6, landing August 2027.

Swap in your own rates and those numbers recompute on the spot.

## Run it

From **this folder**:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Prefer Node? `npx serve`.

## Publish your own copy

```bash
bash publish.sh https://github.com/<you>/<repo>.git
```

It copies this folder into a clean repo, **leaves your private `config.js` behind**, and pushes.
Create the target repo empty first (no README), then turn on Pages: Settings → Pages → *Deploy from a branch* → `main` / `/ (root)`.

## Install it (phone or laptop)

It's a PWA — installs like a normal app and works with **no internet** once installed.

| Where | How |
| --- | --- |
| **Desktop Chrome / Edge** | ⬇ install icon at the right of the address bar, or ⋮ → *Install app* |
| **Android Chrome** | ⋮ → **Install app** (or *Add to Home Screen*) |
| **iPhone / iPad Safari** | Share ⤴ → **Add to Home Screen** |
| **In-app** | The **⬇ Install app** button appears in the top bar on browsers that support it |

Must be served over `http://localhost` or `https://` — a double-clicked `index.html` (`file://`) won't install or cache properly.

## What it shows

- **Pace** — what you should have banked by today (past months in full + current month prorated by day), ahead or behind *your own plan*
- **Needed / day** split two ways: to hit the **goal**, and just to stay **on plan**
- **Run-rate projection** — where you land if the rest looks like the start
- **Reality check** — plan vs goal, shortfall, months to goal, growth required, with three one-click ways out: lower the goal, stretch the months, or model the growth
- **Cumulative chart** — actual vs planned curve with a "today" marker
- **Monthly scorecard** — hit / miss per month, split by stream
- **Stream breakdown** — progress per stream against its own plan
- **Milestones** — the non-money things that move the money

## Editing the plan

**⚙ Settings** lets you change:

- Total goal, start month, number of months (1–36)
- Each stream: name, colour, **month-1 amount**, **growth % per month** (compounding), and **Scales?**
- **Scales?** marks a stream that can genuinely grow. The growth solver only pushes growth onto ticked streams — salary and fixed returns stay flat, which is the only honest way to model this.
- Per-month overrides for real seasonality (December rush, slow January). *Reset to stream rates* undoes them.

## Notes

- Data is saved in this browser (`localStorage`) — it doesn't sync across devices.
- **↓ Export** for a JSON backup, **↑ Import** to restore. Do it monthly.
- **⎙ Print** gives a clean one-page summary.
- Ships with 4 demo entries — hit *Clear sample data* to start for real.
