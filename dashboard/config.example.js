/* Money Tracker — personal numbers
 *
 * Copy this file to config.js and put your real figures in.
 * config.js is gitignored, so your income never gets committed.
 *
 *   cp config.example.js config.js
 *
 * This seeds a FRESH browser. Once you've used the app, your numbers live in
 * localStorage and win over this file — Settings → Reset all data re-seeds from here.
 */

window.TRACKER_CONFIG = {
  currency: 'UGX',
  goal: 24000000,          // total you're aiming for
  start: '2026-10',        // first month, YYYY-MM
  months: 6,               // how many months the plan runs

  // month-1 amount for each stream. growth compounds every month after that.
  // scalable: true  → the growth solver pushes growth onto this stream
  // scalable: false → stays flat (salaries, fixed returns)
  streams: [
    { id: 'clothes', name: 'Clothes sales', color: '#34d399', monthly: 1000000, growth: 10, scalable: true },
    { id: 'writing', name: 'Writing gigs',  color: '#38bdf8', monthly: 500000,  growth: 0,  scalable: true },
    { id: 'job',     name: 'Job income',    color: '#fbbf24', monthly: 500000,  growth: 0,  scalable: false },
    { id: 'invest',  name: 'Investing',     color: '#a78bfa', monthly: 100000,  growth: 0,  scalable: false }
  ],

  // optional — the non-money things that move the money
  milestones: [
    { title: 'Log every payment the day it lands', due: '2026-11-30' }
  ]

  // optional — seed entries so the charts aren't empty
  // entries: [
  //   { date: '2026-10-01', stream: 'job', amount: 500000, note: 'October salary' }
  // ]
};
