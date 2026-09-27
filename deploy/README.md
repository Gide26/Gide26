# Running the Bakery Tracker in the cloud

The server is one Node process with zero npm dependencies, and the whole
business lives in one data folder. That makes it cheap and simple to host
anywhere that runs Linux or Docker.

**One rule that matters:** the phone's offline features (and installing it as an
app) require a *secure* connection — `https://`, or `localhost`. A bare
`http://<ip>:3000` on the public internet will load, but the browser will refuse
to cache the app or queue offline sales. So pick a host that gives you HTTPS:
Fly.io and Render do it automatically; on a plain VPS you add Caddy (below) and
a domain name.

The data folder is chosen by `BAKERY_DATA_DIR`. Everything the bakery owns —
database, backups — is inside it. Back that folder up and you can move hosts
any time.

---

## Option A — Fly.io (recommended: fastest, HTTPS included, ~$2–5/month)

Needs a Fly account (email + card; you are billed only for what you use).

```bash
# 1. One-time: install the Fly CLI
curl -L https://fly.io/docs/install.sh | sh

# 2. From the ROOT of this repository (the folder containing deploy/)
fly launch --copy-config          # accepts the Dockerfile in deploy/
                                  # choose a region near you; say No to postgres

# 3. A persistent disk for the database — without this, data dies on redeploy
fly volumes create bakery_data --size 1

# 4. Tell the app to mount it (fly.toml was created by fly launch)
cat >> fly.toml <<'TOML'

[mounts]
  source = "bakery_data"
  destination = "/data"
TOML

# 5. Ship it
fly deploy
fly open                          # prints your https://….fly.dev address
```

Your phones and computers use that `https://` address from anywhere — home
Wi‑Fi, mobile data, another town. Updates later are just `git pull` then
`fly deploy`.

For a real bakery, create the volume **before** the first deploy and run once
with the setup wizard instead of demo data:

```bash
fly secrets set BAKERY_SEED=empty
```

---

## Option B — A small VPS (Hetzner, DigitalOcean, Linode: $4–6/month)

Full control, persistent disk, and you own everything. Ubuntu 24.04.

```bash
# On the VPS, as root:
adduser --disabled-password --gecos "" bakery
mkdir -p /opt/bakery-data && chown bakery:bakery /opt/bakery-data

# Node 22 (the distro's own Node is too old)
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs git

# The code, on the branch that has the app
sudo -u bakery git clone -b arena/01a0e191-gide26 \
  https://github.com/Gide26/Gide26.git /opt/bakery

# Run it as a service: starts at boot, restarts on crash
cp /opt/bakery/deploy/bakery.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now bakery
systemctl status bakery           # should say active (running)
```

Then HTTPS with Caddy and a domain you own (a `.com` is ~$10/year):

```bash
apt-get install -y caddy
cat > /etc/caddy/Caddyfile <<'CADDY'
bakery.yourdomain.com {
    reverse_proxy localhost:3000
}
CADDY
systemctl reload caddy            # Caddy fetches and renews the certificate
```

Point the domain's DNS `A` record at the VPS address first. Your app is then at
`https://bakery.yourdomain.com`, offline features included.

---

## Option C — Oracle Cloud "Always Free" (free forever, more setup)

Oracle's free tier includes a small VM that never expires and never sleeps —
genuinely free hosting, at the cost of a fiddlier sign-up (account verification
can take a day). Once you have the VM, the steps are **exactly Option B's**
from `adduser` onwards, plus Caddy for HTTPS. Choose the Ubuntu 24.04 image and
open port 80/443 in the Oracle console's firewall rules as well as the VM's.

---

## Backups, whichever host you choose

```bash
npm run backup          # inside the bakery folder: copies the database
```

The copies land in the data folder's `backups/` directory. Download that
directory occasionally (or sync it to Drive/Dropbox) and no cloud accident can
cost you the business's history.
