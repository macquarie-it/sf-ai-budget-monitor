# Operations Runbook

## Daily Checks

- Confirm the application opens with the DBA application role.
- Confirm the latest source timestamp is within the expected latency window.
- Review partial and unattributed cost.
- Review exceeded and critical budget states.

## Deployment

1. Apply ordered SQL migrations with `scripts/apply_migrations.py`.
2. Deploy the application with `snow streamlit deploy`.
3. Run `scripts/validate_deployment.py`.
4. Run `scripts/reconcile_costs.py`.
5. Validate access with an administrator role and a restricted owner role.

## Failure Triage

- Query failures: verify the query warehouse, imported Snowflake privileges, and schema grants.
- Empty Agent data: confirm Cortex Agent activity exists and Account Usage latency has elapsed.
- Missing compute attribution: allow for the documented SQL attribution delay and confirm the
  request did not use an Adaptive Warehouse.
- Package failures: verify `environment.yml` versions are available in the selected warehouse
  runtime.
