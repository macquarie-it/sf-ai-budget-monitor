# Snowflake AI Credit Control

React dashboard to monitor AI credit usage. Its data and visible copy are controlled by a documented SQL component registry, so a DBA can maintain the dashboard without editing React.

## SQL controls the dashboard

The DBA edits one file: [`config/dashboard.sql`](config/dashboard.sql).

Each block has a stable component name, a chart renderer, a plain-English explanation, an example result, and one replaceable SQL statement:

```sql
-- @component credits_consumed
-- @renderer metric
-- EXAMPLE RESULT:
-- EYEBROW          | VALUE   | SUFFIX | TREND | NOTE
-- Credits consumed | 1,307.4 | cr     | +24.8%| vs prior period
SELECT ...;
-- @end-component
```

The checked-in queries use `VALUES` to provide safe demo data. Replace the `SELECT` inside any block with a query against your Snowflake views, but keep its markers and documented output columns.

Refresh the generated React data with Snowflake CLI:

```bash
npm run data:refresh -- --connection sf-ai-monitor
```

Then run or build the application normally:

```bash
npm start
# or
npm run build:streamlit
```

The local data flow is:

```text
config/dashboard.sql
  -> snow sql --format JSON
  -> contract validation
  -> src/generated/dashboard-data.json
  -> React
  -> single-file Streamlit bundle
```

After deployment, the same file is read again inside Snowflake:

```text
deployed config/dashboard.sql
  -> Streamlit active Snowflake session
  -> each component query runs in Snowflake
  -> live data is injected into the React bundle
  -> the five charts render
```

The browser never launches a local CLI. Locally, the CLI generates the snapshot before the page starts. In deployed Streamlit, the active Snowflake session executes `config/dashboard.sql` whenever the app runs or reloads.

### SQL configuration rules

- Keep every query between `@component` and `@end-component` comments.
- Return exactly the columns listed in that block's data contract.
- Use the example result directly above the query as the expected data shape.
- Column names are case-insensitive and become camel-case JSON properties.
- Do not put credentials, HTML, JavaScript, or React code in the SQL file.

Validate the config and generated snapshot without connecting to Snowflake:

```bash
npm run data:check
```

Pass Snowflake CLI template variables when your queries need them:

```bash
npm run data:refresh -- \
  --connection sf-ai-monitor \
  --variable PERIOD_START=2026-08-01
```

## Install / do not install

Install on your Mac:

- Homebrew
- Node.js 22 — includes npm
- Python 3.11 — only for local Streamlit
- Snowflake CLI — for local data refresh and deployment

Do not install:

- Full Xcode
- Docker or a container runtime
- Conda
- A charting library
- Snowflake Python drivers

Homebrew might ask for Apple Command Line Tools. Let Homebrew install them if required; full Xcode is unnecessary.

## Quick start on macOS

### 1. Install Homebrew if `brew` is missing

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Run the PATH command printed by the installer, then reopen Terminal.

### 2. Install the required tools

```bash
brew install node@22 python@3.11 snowflake-cli
```

Add Node.js 22 to `zsh`:

```bash
echo 'export PATH="$(brew --prefix node@22)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Check everything:

```bash
git --version
node --version
npm --version
python3.11 --version
snow --version
```

### 3. Download and set up the project

```bash
git clone https://github.com/macquarie-it/sf-ai-budget-monitor.git
cd sf-ai-budget-monitor
npm ci
```

### 4. Run the React app

```bash
npm start
```

Open `http://localhost:5173`.

That is enough for frontend work. Python and Snowflake CLI are not used by this command.

## Run through Streamlit locally

Run once:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install "streamlit==1.50.0"
```

Then start the app:

```bash
npm run data:refresh -- --connection sf-ai-monitor
npm run streamlit
```

Open `http://localhost:8501`.

Next time, run only:

```bash
source .venv/bin/activate
npm run streamlit
```

## Build

```bash
npm run build
npm run build:streamlit
npm run check
```

| Command | Output |
| --- | --- |
| `npm run data:refresh -- --connection NAME` | Executes every component query and generates React data |
| `npm run data:check` | Validates SQL markers, component contracts, and checked-in data |
| `npm run build` | Normal web build in `dist/` |
| `npm run build:streamlit` | Single-file build in `streamlit_app/frontend/index.html` |
| `npm run check` | Runs and verifies both builds |

## Deploy to Snowflake

### 1. Change the warehouse

Edit `snowflake.yml`:

```yaml
query_warehouse: YOUR_WAREHOUSE
```

The app uses `SYSTEM$WAREHOUSE_RUNTIME`; no container or compute pool is needed.

### 2. Configure and test Snowflake CLI

```bash
snow connection add --connection-name sf-ai-monitor --default
snow connection test --connection sf-ai-monitor
```

For browser-based SSO:

```bash
snow connection add \
  --connection-name sf-ai-monitor \
  --authenticator EXTERNALBROWSER \
  --default
```

### 3. Build and deploy

```bash
npm ci
npm run build:streamlit
snow streamlit deploy sf_ai_credit_watch \
  --connection sf-ai-monitor \
  --replace \
  --open
```

The deployed artifacts include `config/dashboard.sql`. A DBA can replace its demo `VALUES` queries before deployment; the deployed Streamlit app reads and executes that file with its active Snowflake session.

The deployment role needs:

- `USAGE` on the database and warehouse
- `USAGE`, `CREATE STREAMLIT`, and `CREATE STAGE` on the schema

## Packages

Installed by `npm ci`:

- `react`
- `react-dom`
- `vite`
- `@vitejs/plugin-react`
- `vite-plugin-singlefile`

Installed in `.venv`:

- `streamlit==1.50.0`

Installed in the Snowflake warehouse runtime from `environment.yml`:

- `python=3.11`
- `streamlit=1.50.0`
- `snowflake-snowpark-python`

## Useful commands

```bash
npm start                 # React development
npm run data:refresh -- --connection sf-ai-monitor
npm run data:check        # Validate SQL config and generated data
npm run streamlit         # Local Streamlit
npm run build:streamlit   # Build for Snowflake
npm run check             # Verify builds
```

## Common fixes

Node is not found:

```bash
echo 'export PATH="$(brew --prefix node@22)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Streamlit is not found:

```bash
source .venv/bin/activate
python -m pip install "streamlit==1.50.0"
```

The React bundle is missing:

```bash
npm run build:streamlit
```

## Project structure

```text
config/dashboard.sql              DBA-owned SQL component registry
scripts/refresh-dashboard-data.mjs Snowflake CLI query runner and materializer
dashboard_runtime.py               Deployed Snowflake SQL reader and executor
src/                              React source
src/generated/dashboard-data.json Generated, validated component data
streamlit_app.py                  Runtime data injection and React host
streamlit_app/frontend/index.html Compiled React bundle
package.json                      Local and build commands
environment.yml                   Snowflake Python environment
snowflake.yml                     Snowflake deployment settings
```

Official references: [Homebrew installation](https://docs.brew.sh/Installation) · [Snowflake CLI installation](https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation) · [Streamlit deployment](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/streamlit-commands/deploy)
