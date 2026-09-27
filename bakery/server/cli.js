/**
 * Maintenance commands — for when you are at the computer rather than
 * in the app.
 *
 *   node server/cli.js seed-demo
 *   node server/cli.js create-owner "Name" 079000000 password
 *   node server/cli.js reset-password 079000000 newpassword
 *   node server/cli.js list-users
 *   node server/cli.js backup [destination-file]
 *   node server/cli.js stats
 *   node server/cli.js wipe --yes
 */
import { copyFileSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { db, DB_PATH, DATA_DIR, hashPassword, tableCounts, tx, now } from './db.js';
import { seedDemo, seedOwner, clearAll } from './seed.js';
import { num, str } from './util.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const [, , command, ...args] = process.argv;

const usage = () => {
  console.log(`
Bakery Tracker — maintenance commands

  seed-demo                              Load 60 days of demo data (empty database only)
  create-owner <name> <phone> <password> Create an owner login
  reset-password <phone> <new-password>  Set a new password for a login
  list-users                             Show all logins
  backup [file]                          Copy the database to a .bak file
  stats                                  Print record counts and totals
  wipe --yes                             Delete ALL data (irreversible)
  clear-history --yes                    Delete sales/expenses/stock only, keep the catalogue
`);
};

function listUsers() {
  const rows = db.prepare(
    `SELECT id, name, phone, role, active, created_at,
            (SELECT COUNT(*) FROM sales s WHERE s.user_id = users.id) AS sales
       FROM users ORDER BY role DESC, name`).all();
  if (!rows.length) return console.log('No users yet.');
  console.table(rows.map((u) => ({
    id: u.id, name: u.name, phone: u.phone, role: u.role,
    active: u.active ? 'yes' : 'no', sales: u.sales, created: u.created_at?.slice(0, 10),
  })));
}

function stats() {
  const c = tableCounts();
  const money = (sql) => num(db.prepare(sql).get().v ?? 0);
  console.log('\nRecords:');
  console.table(c);
  console.log('\nTotals:');
  console.table({
    revenue: money("SELECT SUM(total) v FROM sales WHERE status <> 'void'"),
    cost_of_goods: money("SELECT SUM(line_cost) v FROM sale_items si JOIN sales s ON s.id=si.sale_id WHERE s.status <> 'void'"),
    expenses: money('SELECT SUM(amount) v FROM expenses'),
    outstanding_credit: money("SELECT SUM(total - paid) v FROM sales WHERE status IN ('partial','unpaid')"),
    stock_value: money('SELECT SUM(stock * cost_per_unit) v FROM ingredients WHERE active = 1'),
  });
  console.log(`\nDatabase: ${DB_PATH}`);
}

function backup(dest) {
  if (!existsSync(DB_PATH)) return console.error('No database file to back up yet.');
  mkdirSync(join(DATA_DIR, 'backups'), { recursive: true });
  const stamp = now().replace(/[: ]/g, '-');
  const target = dest ? resolve(dest) : join(DATA_DIR, 'backups', `bakery-${stamp}.bak.sqlite`);
  mkdirSync(dirname(target), { recursive: true });
  // Checkpoint WAL first so the copy is complete and consistent.
  try { db.exec('PRAGMA wal_checkpoint(TRUNCATE)'); } catch { /* ignore */ }
  copyFileSync(DB_PATH, target);
  console.log(`Backed up to ${target}`);
}

function wipe() {
  if (!args.includes('--yes')) {
    return console.error('Refusing to wipe: re-run with --yes to confirm you understand this is permanent.');
  }
  tx(() => clearAll());
  console.log('All business data deleted. Restart the server to re-initialise.');
}

/**
 * Erase the example TRADING history — sales, expenses, stock movements — while
 * keeping the catalogue (products, ingredients, recipes), customers, users and
 * settings.
 *
 * Going live usually means "my reports must start at zero", not "my product
 * list must start at zero": renaming nineteen seeded products to the real menu
 * is far quicker than re-typing them. This is the command for that middle path.
 */
function clearHistory() {
  if (!args.includes('--yes')) {
    return console.error('Refusing to clear history: re-run with --yes to confirm.\n'
      + 'This deletes sales, expenses and stock movements. Products, customers and users stay.');
  }
  const before = tableCounts();
  tx(() => {
    for (const t of ['sale_items', 'sales', 'stock_moves', 'expenses', 'sync_log', 'sessions']) {
      db.prepare(`DELETE FROM ${t}`).run();
    }
    db.prepare("DELETE FROM sqlite_sequence WHERE name IN ('sales','sale_items','stock_moves','expenses')").run();
    // Let invoice numbering restart at 1 with the new, real first sale.
    db.prepare("DELETE FROM settings WHERE key = 'next_invoice'").run();
  });
  const after = tableCounts();
  console.log('Trading history cleared. Reports now start from zero.');
  console.log(`  sales: ${before.sales ?? 0} -> ${after.sales ?? 0}, expenses -> 0, stock movements -> 0`);
  console.log('  Kept: products, ingredients, recipes, categories, customers, users, settings.');
  console.log('  Everyone is signed out; sign in again to continue.');
}

function resetPassword() {
  const [phone, password] = args;
  if (!phone || !password) return usage();
  const norm = (v) => str(v).replace(/[\s\-()]/g, '').toLowerCase();
  const users = db.prepare('SELECT * FROM users').all();
  const user = users.find((u) => norm(u.phone) === norm(phone));
  if (!user) return console.error(`No user with phone "${phone}". Try: node server/cli.js list-users`);
  if (str(password).length < 6) return console.error('Password must be at least 6 characters.');
  const { salt, hash } = hashPassword(password);
  db.prepare('UPDATE users SET pass_hash=?, pass_salt=?, must_change=0, active=1 WHERE id=?').run(hash, salt, user.id);
  db.prepare('DELETE FROM sessions WHERE user_id=?').run(user.id);
  console.log(`Password updated for ${user.name} (${user.phone}). They have been signed out everywhere.`);
}

function createOwner() {
  const [name, phone, password] = args;
  if (!name || !phone || !password) return usage();
  if (str(password).length < 6) return console.error('Password must be at least 6 characters.');
  if (num(db.prepare("SELECT COUNT(*) n FROM users").get().n) === 0) {
    const { ownerId } = seedOwner({ name, phone, password });
    db.prepare('UPDATE users SET must_change = 0 WHERE id = ?').run(ownerId);
    return console.log(`Owner "${name}" created (${phone}).`);
  }
  const { salt, hash } = hashPassword(password);
  const id = Number(db.prepare(
    `INSERT INTO users (name, phone, role, pass_hash, pass_salt, must_change, active, created_at)
     VALUES (?,?, 'owner', ?,?,0,1,?)`).run(name, phone, hash, salt, now()).lastInsertRowid);
  console.log(`Owner "${name}" created with id ${id} (${phone}).`);
}

switch (str(command)) {
  case 'seed-demo': {
    const out = seedDemo({ force: args.includes('--force') });
    console.log(out.skipped ? `Skipped: ${out.reason}` : `Seeded: ${JSON.stringify(out, null, 2)}`);
    break;
  }
  case 'create-owner': createOwner(); break;
  case 'reset-password': resetPassword(); break;
  case 'list-users': listUsers(); break;
  case 'backup': backup(args[0]); break;
  case 'stats': stats(); break;
  case 'wipe': wipe(); break;
  case 'clear-history': clearHistory(); break;
  case undefined:
  case 'help':
  default: usage();
}

try { db.close(); } catch { /* ignore */ }
process.exit(0);
