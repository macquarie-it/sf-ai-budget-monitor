# Snowflake AI Credit Control

A lightweight DBA dashboard prototype for monitoring Snowflake AI credit consumption. The UI is React-first, all displayed data is synthetic, and the Streamlit layer is only a thin host for the compiled frontend.

## What is included

- Four headline metrics: consumed credits, projected monthly usage, active identities, and growth signals.
- AI credit trend, service mix, and top-agent views.
- Employee-level attribution and growth alerts, including large mock spikes such as `+1,008%`.
- Exactly nine primary dashboard surfaces: four metrics and five analysis panels.
- No database connection, API, secrets, Snowpark session, or Snowflake query.

## Architecture

```text
React source (src/)
  ├─ npm start              → Vite local development server
  └─ npm run build:streamlit
       └─ single HTML file  → Streamlit components.html() thin host
                                └─ Snowflake warehouse runtime
```

The production bundle contains its JavaScript and CSS inline. This matters because Streamlit in Snowflake warehouse runtime supports Components v1 inline HTML, while its content security policy blocks custom-component scripts loaded from external domains.

Runtime dependencies stay deliberately small:

- Browser: React and React DOM only.
- Build time: Vite, the React Vite plugin, and a single-file bundler plugin.
- Snowflake runtime: Python and Streamlit only.

Node.js is needed only on the developer or CI machine that builds the committed HTML bundle. DBAs deploying an already-built checkout do not need Node.js on Snowflake.

## Prerequisites

### 1. Node.js

Install Node.js 22 LTS. Node 20.19 or newer also works.

With `nvm`:

```bash
nvm install 22
nvm use 22
```

On macOS with Homebrew:

```bash
brew install node@22
```

Verify the installation:

```bash
node --version
npm --version
```

### 2. Python for local Streamlit preview

Python 3.11 is recommended. Create a virtual environment and install Streamlit:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install "streamlit==1.50.0"
```

### 3. Snowflake CLI for deployment

Install and configure the Snowflake CLI if it is not already available:

```bash
pipx install snowflake-cli
snow connection add
snow connection test
```

The deployment role needs `USAGE` on the target database and warehouse, plus `USAGE` and `CREATE STREAMLIT` on the target schema.

## Local React development

Install the JavaScript dependencies once:

```bash
npm install
```

Start the fast local React development mode:

```bash
npm start
```

Open the URL printed by Vite, normally `http://localhost:5173`.

## Local Streamlit preview

Build the single-file React bundle and start the thin Streamlit host:

```bash
npm run streamlit
```

Or run the two steps separately:

```bash
npm run build:streamlit
python3 -m streamlit run streamlit_app.py
```

## Build commands

```bash
npm run build             # Standard static build in dist/
npm run build:streamlit   # Single-file bundle for Streamlit warehouse runtime
npm run check             # Verify both production builds
```

`npm run build:streamlit` also verifies that the output is self-contained. The deployable frontend is written to `streamlit_app/frontend/index.html`.

## Deploy to Streamlit in Snowflake

1. Edit `query_warehouse` in `snowflake.yml`; it is set to `COMPUTE_WH` as a placeholder.
2. Build the deployable frontend.
3. Deploy with your configured Snowflake CLI connection.

```bash
npm ci
npm run build:streamlit
snow streamlit deploy sf_ai_credit_watch --replace --open
```

The project explicitly selects `SYSTEM$WAREHOUSE_RUNTIME`; it does not require a compute pool or container runtime. The `artifacts` list uploads only the Python host, compiled React page, and minimal environment file.

## Replacing mock data later

All prototype data currently lives in `src/App.jsx`. A later iteration can inject data into the React page from the Streamlit host, or replace individual panels with Snowflake-backed queries. Until that work is intentionally added, the app never connects to Snowflake and is safe to use as a visual prototype.

