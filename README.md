# Snowflake AI Credit Control

React dashboard prototype for Snowflake DBAs to monitor AI credit usage. All data is fake; this version does not query Snowflake.

## Install / do not install

Install on your Mac:

- Homebrew
- Node.js 22 — includes npm
- Python 3.11 — only for local Streamlit
- Snowflake CLI — only for deployment

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

## Useful commands

```bash
npm start                 # React development
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
src/                              React source and fake data
streamlit_app.py                  Thin Streamlit wrapper
streamlit_app/frontend/index.html Compiled React bundle
package.json                      Local and build commands
environment.yml                   Snowflake Python environment
snowflake.yml                     Snowflake deployment settings
```

Official references: [Homebrew installation](https://docs.brew.sh/Installation) · [Snowflake CLI installation](https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation) · [Streamlit deployment](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/streamlit-commands/deploy)

