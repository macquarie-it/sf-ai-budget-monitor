# Application Architecture

The application uses a lightweight layered architecture:

1. Streamlit page modules render data and collect user input.
2. Shared components provide filters, metrics, charts, tables, and state handling.
3. Application services calculate dashboard-specific summaries.
4. Domain modules contain cost, attribution, and budget rules without Streamlit dependencies.
5. Repository implementations expose a stable data contract for Snowflake and demo data.
6. Curated Snowflake views normalize Account Usage records before they reach the application.

The Snowflake repository queries `V_COST_EVENTS`. It does not query raw Account Usage views from
page code. This keeps source-schema changes and accounting decisions isolated in versioned SQL.

Local execution uses deterministic demo records when no Snowflake session is available. The UI
always displays a warning in demo mode. Setting `CORTEX_COST_DATA_MODE=snowflake` disables the
fallback and fails fast when no Snowflake session can be created.
