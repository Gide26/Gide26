# Northstar — Market Intelligence

A local, browser-based market scanner with equities, ETFs, crypto, forex, commodities, and major index instruments. It calculates transparent trend/momentum signals and can connect to Twelve Data for live intraday prices plus daily technical history.

> **Coverage note:** The included `universe.json` is a starter list of 60 representative instruments across those asset classes—not every security, exchange, pair, or contract worldwide. Edit that file to add supported Twelve Data symbols and exchange identifiers. Actual coverage, real-time entitlements, and API quotas depend on your provider plan. Signals are educational analysis, not investment advice.

## Run it on your PC

1. Install Python 3.
2. Create a `.env` file from the template (`Copy-Item .env.example .env` in PowerShell, or `cp .env.example .env` on Mac/Linux). Open `.env`, replace `your_api_key_here` with your Twelve Data API key, and save it. **Do not paste the key into chat or commit `.env`.**
3. In a terminal opened in this folder, run:

   **Windows**
   ```powershell
   py server.py
   ```

   **Mac / Linux**
   ```bash
   python3 server.py
   ```

4. Open [http://localhost:4173](http://localhost:4173), then select **Start live scan**. The dashboard polls at the configured cache interval (default five minutes) while it remains open. It shows an in-dashboard toast when an asset's Bullish / Watch / Bearish classification changes.
5. Press **Ctrl+C** in the terminal to stop the local server.

The Twelve Data key is used only by the local Python server; the browser never receives it. The dashboard-only alert option does not send notifications when the browser is closed.

## Data and limits

The server requests a batch of 60 daily bars and a batch of latest one-minute bars from Twelve Data, computes RSI, MACD, 20/50-day trend, and relative volume locally, then caches the result. If one-minute data is not enabled for your account/market, it falls back to the latest daily bar and displays a warning. Provider rate limits, real-time access, and coverage vary by plan. If symbols are missing, verify their Twelve Data spelling and exchange in `universe.json`.

To scan more instruments, add entries to `universe.json` using this format:

```json
{"ticker":"EXAMPLE","name":"Example Security","asset":"stock","providerSymbol":"EXAMPLE","exchange":"NASDAQ"}
```

Supported `asset` categories: `stock`, `crypto`, `forex`, `commodity`, and `index`. Crypto and FX symbols often use pair format such as `BTC/USD` and `EUR/USD`. Consult your provider's symbol directory for exact identifiers. Larger scans may require a higher API plan or a smaller cache refresh cadence.

Without a configured key, Northstar stays in demo mode with illustrative sample values. CSV import is a separate, local snapshot workflow; it is not a live feed.

## Signal methodology

The 0–100 momentum score combines moving-average trend (35%), RSI and MACD momentum (30%), relative volume (20%), and recent price change (15%). Scores of 67+ are labelled **Bullish**, 40–66 **Watch**, and lower scores **Bearish**. Classifications summarize indicators only; they do not predict returns or recommend trades.
