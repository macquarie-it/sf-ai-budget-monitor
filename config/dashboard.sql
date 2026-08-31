-- ============================================================================
-- SNOWFLAKE AI CREDIT CONTROL
-- This is the only data file a DBA needs to edit.
--
-- LOCAL USE
--   npm run data:refresh -- --connection YOUR_CONNECTION
--
-- DEPLOYED USE
--   The Streamlit app reads this same file and runs each query in Snowflake.
--
-- SAFE EDITING RULES
--   1. Replace the SELECT statements with queries against your own views.
--   2. Keep the @component, @renderer and @end-component lines unchanged.
--   3. Keep the output column names shown in each example.
--   4. Every section includes one example result so you can see the shape.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- PAGE HEADER
-- Controls the dashboard name, environment badge and introduction.
--
-- RETURN DATA LIKE THIS (one summary result):
-- BRAND_TITLE   | BRAND_SUBTITLE             | ENVIRONMENT_LABEL | ACCOUNT_NAME
-- Credit Control| Snowflake AI observability | LIVE SQL          | ACME_PROD
--
-- Also return PAGE_OVERLINE, TITLE_LINE_1, TITLE_EMPHASIS and LEDE.
-- ----------------------------------------------------------------------------
-- @component dashboard_shell
-- @renderer shell
SELECT
    column1 AS brand_title,
    column2 AS brand_subtitle,
    column3 AS environment_label,
    column4 AS account_name,
    column5 AS page_overline,
    column6 AS title_line_1,
    column7 AS title_emphasis,
    column8 AS lede
FROM VALUES (
    'Credit Control',
    'Snowflake AI observability',
    'LIVE SQL',
    'ACME_PROD / ACCOUNTADMIN',
    'AI GOVERNANCE / COMMAND CENTER',
    'Every AI credit.',
    'Clearly accountable.',
    'Three numbers and five visual perspectives—maintained entirely through SQL.'
);
-- @end-component


-- ----------------------------------------------------------------------------
-- MONITORING MESSAGE
-- Appears directly above the three number cards.
--
-- EXAMPLE RESULT:
-- MESSAGE
-- Monitoring 4 AI services across 38 identities
-- ----------------------------------------------------------------------------
-- @component monitoring_status
-- @renderer status
SELECT column1 AS message
FROM VALUES ('Monitoring 4 AI services across 38 identities');
-- @end-component


-- ----------------------------------------------------------------------------
-- NUMBER CARD 1: CREDITS CONSUMED
--
-- RETURN DATA LIKE THIS:
-- EYEBROW          | VALUE   | SUFFIX | TREND | NOTE              | TONE
-- Credits consumed | 1,307.4 | cr     | +24.8%| vs prior period   | default
--
-- TONE can be: default, violet, mint or coral.
-- ----------------------------------------------------------------------------
-- @component credits_consumed
-- @renderer metric
SELECT column1 AS eyebrow, column2 AS value, column3 AS suffix,
       column4 AS trend, column5 AS note, column6 AS tone
FROM VALUES ('Credits consumed', '1,307.4', ' cr', '+24.8%', 'vs prior period', 'default');
-- @end-component


-- ----------------------------------------------------------------------------
-- NUMBER CARD 2: PROJECTED MONTH
--
-- EXAMPLE RESULT:
-- EYEBROW        | VALUE | SUFFIX | TREND | NOTE            | TONE
-- Projected month| 1,941 | cr     | 81%   | of 2,400 budget | violet
-- ----------------------------------------------------------------------------
-- @component projected_month
-- @renderer metric
SELECT column1 AS eyebrow, column2 AS value, column3 AS suffix,
       column4 AS trend, column5 AS note, column6 AS tone
FROM VALUES ('Projected month', '1,941', ' cr', '81%', 'of 2,400 budget', 'violet');
-- @end-component


-- ----------------------------------------------------------------------------
-- NUMBER CARD 3: ACTIVE IDENTITIES
--
-- EXAMPLE RESULT:
-- EYEBROW         | VALUE | SUFFIX | TREND | NOTE               | TONE
-- Active identities| 38   |        | +6    | employees & agents | mint
-- ----------------------------------------------------------------------------
-- @component active_identities
-- @renderer metric
SELECT column1 AS eyebrow, column2 AS value, column3 AS suffix,
       column4 AS trend, column5 AS note, column6 AS tone
FROM VALUES ('Active identities', '38', '', '+6', 'employees & agents', 'mint');
-- @end-component


-- ----------------------------------------------------------------------------
-- CHART PICKER
-- Creates the five radio-button choices above the charts.
-- CHART_ID must match one of the five chart component names below.
--
-- EXAMPLE RESULT:
-- CHART_ID        | LABEL      | DESCRIPTION                          | DISPLAY_ORDER
-- agent_bar_chart | Bar chart  | Compare services side by side        | 1
-- ----------------------------------------------------------------------------
-- @component chart_menu
-- @renderer radio_group
SELECT column1 AS chart_id, column2 AS label, column3 AS description,
       column4 AS display_order
FROM VALUES
    ('agent_bar_chart', 'Bar chart', 'Compare categories or groups side by side', 1),
    ('credit_burn', 'Line chart', 'Show trends over time or continuous data', 2),
    ('usage_scatter', 'Scatter plot', 'Show relationships between two numeric values', 3),
    ('service_pie_chart', 'Pie chart', 'Show proportions of a whole', 4),
    ('activity_heatmap', 'Heatmap', 'Show intensity across two dimensions', 5)
ORDER BY column4;
-- @end-component


-- ----------------------------------------------------------------------------
-- CHART 1 OF 5: BAR CHART
-- Shows which autonomous agents consumed the most credits.
-- Return one result for every bar you want to display.
--
-- EXAMPLE RESULT:
-- LABEL               | SUBLABEL   | VALUE | CHANGE_PERCENT
-- FINANCE_RECON_AGENT | Finance Ops| 286   | 38
--
-- Also return KICKER, TITLE and DESCRIPTION for the chart heading.
-- ----------------------------------------------------------------------------
-- @component agent_bar_chart
-- @renderer bar_chart
SELECT column1 AS label, column2 AS sublabel, column3 AS value,
       column4 AS change_percent, 'BAR CHART' AS kicker,
       'Top autonomous consumers' AS title,
       'Credits consumed by each agent during the selected period.' AS description
FROM VALUES
    ('FINANCE_RECON_AGENT', 'Finance Ops', 286, 38),
    ('SUPPORT_SEARCH_AGENT', 'Customer Care', 219, 16),
    ('LEGAL_DOC_REVIEW', 'Legal', 164, 203),
    ('SALES_BRIEF_AGENT', 'Revenue', 122, -8),
    ('HR_POLICY_ASSIST', 'People', 83, 11)
ORDER BY column3 DESC;
-- @end-component


-- ----------------------------------------------------------------------------
-- CHART 2 OF 5: LINE CHART
-- Shows credit usage over time. Return the points in POSITION order.
-- RANGE_LABEL creates the 7D, 30D and 90D buttons.
--
-- EXAMPLE RESULT:
-- RANGE_LABEL | POSITION | VALUE
-- 7D          | 0        | 42
--
-- Also return KICKER, TITLE and DESCRIPTION for the chart heading.
-- ----------------------------------------------------------------------------
-- @component credit_burn
-- @renderer line_chart
SELECT column1 AS range_label, column2 AS position, column3 AS value,
       'LINE CHART' AS kicker, 'AI credit burn' AS title,
       'Daily AI credit consumption across the selected reporting window.' AS description
FROM VALUES
    ('7D', 0, 42), ('7D', 1, 54), ('7D', 2, 49), ('7D', 3, 73),
    ('7D', 4, 68), ('7D', 5, 96), ('7D', 6, 112),
    ('30D', 0, 28), ('30D', 1, 33), ('30D', 2, 31), ('30D', 3, 39),
    ('30D', 4, 46), ('30D', 5, 44), ('30D', 6, 52), ('30D', 7, 61),
    ('30D', 8, 58), ('30D', 9, 69), ('30D', 10, 72), ('30D', 11, 68),
    ('30D', 12, 75), ('30D', 13, 81), ('30D', 14, 79), ('30D', 15, 86),
    ('30D', 16, 92), ('30D', 17, 89), ('30D', 18, 98), ('30D', 19, 103),
    ('30D', 20, 96), ('30D', 21, 108), ('30D', 22, 115), ('30D', 23, 111),
    ('30D', 24, 119), ('30D', 25, 126), ('30D', 26, 122), ('30D', 27, 139),
    ('30D', 28, 147), ('30D', 29, 156),
    ('90D', 0, 19), ('90D', 1, 23), ('90D', 2, 21), ('90D', 3, 26),
    ('90D', 4, 30), ('90D', 5, 28), ('90D', 6, 34), ('90D', 7, 39),
    ('90D', 8, 37), ('90D', 9, 42), ('90D', 10, 47), ('90D', 11, 44),
    ('90D', 12, 52), ('90D', 13, 49), ('90D', 14, 57), ('90D', 15, 63),
    ('90D', 16, 60), ('90D', 17, 68), ('90D', 18, 74), ('90D', 19, 71),
    ('90D', 20, 80), ('90D', 21, 88), ('90D', 22, 84), ('90D', 23, 94),
    ('90D', 24, 101), ('90D', 25, 97), ('90D', 26, 109), ('90D', 27, 118),
    ('90D', 28, 126), ('90D', 29, 139);
-- @end-component


-- ----------------------------------------------------------------------------
-- CHART 3 OF 5: SCATTER PLOT
-- Compares request volume with credit usage. Bubble size shows growth.
-- Return one result for every bubble you want to display.
--
-- EXAMPLE RESULT:
-- LABEL          | X_VALUE | Y_VALUE | SIZE | COLOR
-- Cortex Analyst | 840     | 536     | 38   | #6757d9
--
-- Also return KICKER, TITLE and DESCRIPTION for the chart heading.
-- ----------------------------------------------------------------------------
-- @component usage_scatter
-- @renderer scatter_plot
SELECT column1 AS label, column2 AS x_value, column3 AS y_value,
       column4 AS size, column5 AS color, 'SCATTER PLOT' AS kicker,
       'Volume versus credit cost' AS title,
       'Each bubble compares request volume, credit usage and growth.' AS description
FROM VALUES
    ('Cortex Analyst', 840, 536, 38, '#6757d9'),
    ('Cortex Search', 1210, 353, 24, '#2f8f83'),
    ('Document AI', 310, 248, 52, '#ec6a4c'),
    ('Snowflake Copilot', 680, 170, 18, '#e4b94f'),
    ('AI Functions', 460, 132, 14, '#65748f');
-- @end-component


-- ----------------------------------------------------------------------------
-- CHART 4 OF 5: PIE CHART
-- Shows each service's share of total credits.
-- VALUE is the percentage shown by the pie slice.
--
-- EXAMPLE RESULT:
-- LABEL          | VALUE | CREDITS | COLOR
-- Cortex Analyst | 41    | 536     | #6757d9
--
-- Also return KICKER, TITLE and DESCRIPTION for the chart heading.
-- ----------------------------------------------------------------------------
-- @component service_pie_chart
-- @renderer pie_chart
SELECT column1 AS label, column2 AS value, column3 AS credits,
       column4 AS color, 'PIE CHART' AS kicker, 'Where credits go' AS title,
       'Share of total AI credits consumed by service.' AS description
FROM VALUES
    ('Cortex Analyst', 41, 536, '#6757d9'),
    ('Cortex Search', 27, 353, '#2f8f83'),
    ('Document AI', 19, 248, '#ec6a4c'),
    ('Snowflake Copilot', 13, 170, '#e4b94f')
ORDER BY column2 DESC;
-- @end-component


-- ----------------------------------------------------------------------------
-- CHART 5 OF 5: HEATMAP
-- Shows busy and quiet periods by weekday and time of day.
-- Return one result for every heatmap square.
-- VALUE controls the color intensity: higher value means a darker square.
--
-- EXAMPLE RESULT:
-- ROW_LABEL | COLUMN_LABEL | VALUE
-- Monday    | 08:00        | 32
--
-- Also return KICKER, TITLE and DESCRIPTION for the chart heading.
-- ----------------------------------------------------------------------------
-- @component activity_heatmap
-- @renderer heatmap
SELECT column1 AS row_label, column2 AS column_label, column3 AS value,
       'HEATMAP' AS kicker, 'When AI workloads run' AS title,
       'Credit intensity by weekday and four-hour window.' AS description
FROM VALUES
    ('Mon', '00:00', 8),  ('Mon', '04:00', 12), ('Mon', '08:00', 32), ('Mon', '12:00', 67), ('Mon', '16:00', 81), ('Mon', '20:00', 24),
    ('Tue', '00:00', 11), ('Tue', '04:00', 18), ('Tue', '08:00', 48), ('Tue', '12:00', 76), ('Tue', '16:00', 93), ('Tue', '20:00', 38),
    ('Wed', '00:00', 7),  ('Wed', '04:00', 15), ('Wed', '08:00', 42), ('Wed', '12:00', 58), ('Wed', '16:00', 88), ('Wed', '20:00', 31),
    ('Thu', '00:00', 14), ('Thu', '04:00', 21), ('Thu', '08:00', 55), ('Thu', '12:00', 83), ('Thu', '16:00', 97), ('Thu', '20:00', 44),
    ('Fri', '00:00', 9),  ('Fri', '04:00', 13), ('Fri', '08:00', 37), ('Fri', '12:00', 61), ('Fri', '16:00', 72), ('Fri', '20:00', 29);
-- @end-component


-- ----------------------------------------------------------------------------
-- PAGE FOOTER
--
-- EXAMPLE RESULT:
-- LEFT_TEXT                                        | RIGHT_TEXT
-- Snowflake AI Credit Control · SQL-driven         | Powered by dashboard.sql
-- ----------------------------------------------------------------------------
-- @component dashboard_footer
-- @renderer footer
SELECT column1 AS left_text, column2 AS right_text
FROM VALUES (
    'Snowflake AI Credit Control · SQL-driven',
    'Local: Snowflake CLI · Deployed: active Snowflake session'
);
-- @end-component
