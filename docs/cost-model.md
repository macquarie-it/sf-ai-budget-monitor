# Cost Model

## Agent Requests

Agent rows originate from `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY`.

- Token credits come from `TOKEN_CREDITS` and include token-based Agent orchestration and tools,
  including Analyst calls orchestrated by the Agent.
- AI Function credits come from `METADATA:ai_functions_credits`.
- Attributed SQL compute comes from `METADATA:sql_query_credits`.
- Total attributed cost is the sum of these distinct components.

Agent usage can lag by approximately one hour. SQL credit attribution can lag by approximately
eight hours and excludes Adaptive Warehouse queries. A missing SQL credit value is therefore
classified as partial attribution rather than silently estimated.

## Standalone Analyst Requests

Standalone Analyst rows originate from
`SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY`. The source is aggregated hourly and
contains message count, username, and billed credits. It does not contain request IDs, semantic
model names, generated query IDs, or attributed warehouse cost.

The application labels these records as partial attribution. Request-level semantic model and SQL
lineage require an additional approved request-logging source.

## Currency

Snowflake credits remain the source financial unit. Currency values are estimates calculated from
the contract-specific `CORTEX_CREDIT_PRICE` setting and must not be presented as invoice totals.
