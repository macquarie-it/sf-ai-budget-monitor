import { useMemo, useState } from "react";
import bundledDashboardData from "./generated/dashboard-data.json";

const dashboardData = window.__DASHBOARD_DATA__ ?? bundledDashboardData;
const components = dashboardData.components;
const shell = components.dashboard_shell.data;
const monitoringStatus = components.monitoring_status.data;
const metrics = [
  components.credits_consumed.data,
  components.projected_month.data,
  components.active_identities.data,
];
const chartMenu = components.chart_menu.data.toSorted((left, right) => left.displayOrder - right.displayOrder);
const barData = components.agent_bar_chart.data;
const lineData = components.credit_burn.data;
const scatterData = components.usage_scatter.data;
const pieData = components.service_pie_chart.data;
const heatmapData = components.activity_heatmap.data;
const footer = components.dashboard_footer.data;

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
}

function formatGeneratedAt(timestamp) {
  return new Intl.DateTimeFormat([], {
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(new Date(timestamp));
}

function panelCopy(rows) {
  return rows[0];
}

function PanelHeading({ data, aside }) {
  return (
    <div className="panel-heading">
      <div>
        <p className="panel-kicker">{data.kicker}</p>
        <h2>{data.title}</h2>
        <p className="panel-description">{data.description}</p>
      </div>
      {aside}
    </div>
  );
}

function Metric({ eyebrow, value, suffix, trend, tone = "default", note }) {
  return (
    <article className={`metric metric--${tone}`}>
      <div className="metric-topline"><span>{eyebrow}</span><span className="metric-spark" aria-hidden="true">↗</span></div>
      <p className="metric-value">{value}<small>{suffix}</small></p>
      <div className="metric-foot"><span className={`trend ${trend.startsWith("+") ? "trend--up" : ""}`}>{trend}</span><span>{note}</span></div>
    </article>
  );
}

function LineChart({ rows }) {
  const width = 720;
  const height = 230;
  const padding = 20;
  const values = rows.map(({ value }) => value);
  const safeValues = values.length > 1 ? values : [values[0] ?? 0, values[0] ?? 0];
  const rawMax = Math.max(...safeValues);
  const rawMin = Math.min(...safeValues);
  const max = rawMax === rawMin ? rawMax + 1 : rawMax * 1.08;
  const min = rawMax === rawMin ? rawMin - 1 : rawMin * 0.82;
  const points = safeValues.map((value, index) => {
    const x = padding + (index / (safeValues.length - 1)) * (width - padding * 2);
    const y = height - padding - ((value - min) / (max - min)) * (height - padding * 2);
    return [x, y];
  });
  const line = points.map(([x, y]) => `${x},${y}`).join(" ");
  const area = `${padding},${height - padding} ${line} ${width - padding},${height - padding}`;
  const finalPoint = points.at(-1);

  return (
    <div className="line-chart" aria-label="AI credit consumption line chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img">
        <defs>
          <linearGradient id="areaFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#6757d9" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#6757d9" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0.2, 0.5, 0.8].map((ratio) => (
          <line key={ratio} x1="18" x2="702" y1={height * ratio} y2={height * ratio} className="chart-grid" />
        ))}
        <polygon points={area} fill="url(#areaFill)" />
        <polyline points={line} className="chart-line-shadow" />
        <polyline points={line} className="chart-line" />
        <circle cx={finalPoint[0]} cy={finalPoint[1]} r="7" className="chart-dot-halo" />
        <circle cx={finalPoint[0]} cy={finalPoint[1]} r="3.5" className="chart-dot" />
      </svg>
      <div className="axis-labels"><span>Start</span><span>Mid-period</span><span>Today</span></div>
    </div>
  );
}

function BarChart({ rows }) {
  const maxValue = Math.max(...rows.map(({ value }) => value), 1);
  return (
    <div className="bar-list" aria-label="Agent credit consumption bar chart">
      {rows.map((item, index) => (
        <div className="bar-row" key={item.label}>
          <div className="bar-copy">
            <span><b>{index + 1}</b>{item.label}<small>{item.sublabel}</small></span>
            <span><strong>{formatNumber(item.value)}</strong> cr <em className={item.changePercent > 100 ? "hot" : item.changePercent < 0 ? "cool" : ""}>{item.changePercent > 0 ? "+" : ""}{item.changePercent}%</em></span>
          </div>
          <div className="bar-track"><i style={{ width: `${(item.value / maxValue) * 100}%` }} /></div>
        </div>
      ))}
    </div>
  );
}

function PieChart({ rows }) {
  const total = rows.reduce((sum, item) => sum + item.value, 0) || 1;
  let cursor = 0;
  const gradient = `conic-gradient(${rows.map((item) => {
    const start = cursor;
    cursor += (item.value / total) * 100;
    return `${item.color} ${start}% ${cursor}%`;
  }).join(", ")})`;
  const totalCredits = rows.reduce((sum, item) => sum + item.credits, 0);

  return (
    <div className="donut-layout">
      <div className="donut" style={{ background: gradient }} role="img" aria-label="Service credit share pie chart">
        <div><b>{rows[0].value}%</b><span>{rows[0].label}</span></div>
      </div>
      <div className="legend">
        {rows.map((item) => (
          <div className="legend-row" key={item.label}>
            <span className="legend-name"><i style={{ background: item.color }} />{item.label}</span>
            <span><b>{item.value}%</b><small>{formatNumber(item.credits)} cr</small></span>
          </div>
        ))}
        <div className="legend-total"><span>Total</span><b>{formatNumber(totalCredits)} cr</b></div>
      </div>
    </div>
  );
}

function ScatterPlot({ rows }) {
  const width = 620;
  const height = 290;
  const padding = 44;
  const maxX = Math.max(...rows.map(({ xValue }) => xValue), 1);
  const maxY = Math.max(...rows.map(({ yValue }) => yValue), 1);

  return (
    <div className="scatter-chart" aria-label="Request volume versus credits scatter plot">
      <svg viewBox={`0 0 ${width} ${height}`} role="img">
        {[0.25, 0.5, 0.75].map((ratio) => (
          <g key={ratio}>
            <line x1={padding} x2={width - padding} y1={height * ratio} y2={height * ratio} className="chart-grid" />
            <line y1={padding} y2={height - padding} x1={width * ratio} x2={width * ratio} className="chart-grid" />
          </g>
        ))}
        <line x1={padding} x2={padding} y1={padding} y2={height - padding} className="scatter-axis" />
        <line x1={padding} x2={width - padding} y1={height - padding} y2={height - padding} className="scatter-axis" />
        {rows.map((item) => {
          const x = padding + (item.xValue / maxX) * (width - padding * 2);
          const y = height - padding - (item.yValue / maxY) * (height - padding * 2);
          const radius = 8 + Math.sqrt(item.size) * 1.7;
          return (
            <g key={item.label}>
              <circle cx={x} cy={y} r={radius} fill={item.color} fillOpacity="0.78" />
              <text x={x} y={y - radius - 7} textAnchor="middle" className="scatter-label">{item.label}</text>
            </g>
          );
        })}
        <text x={width / 2} y={height - 4} textAnchor="middle" className="axis-title">Request volume</text>
        <text x="12" y={height / 2} textAnchor="middle" transform={`rotate(-90 12 ${height / 2})`} className="axis-title">Credits</text>
      </svg>
    </div>
  );
}

function Heatmap({ rows }) {
  const rowLabels = [...new Set(rows.map(({ rowLabel }) => rowLabel))];
  const columnLabels = [...new Set(rows.map(({ columnLabel }) => columnLabel))];
  const maxValue = Math.max(...rows.map(({ value }) => value), 1);
  const lookup = new Map(rows.map((item) => [`${item.rowLabel}:${item.columnLabel}`, item.value]));

  return (
    <div className="heatmap" style={{ "--heat-columns": columnLabels.length }} aria-label="AI workload activity heatmap">
      <span className="heatmap-corner" />
      {columnLabels.map((label) => <span className="heatmap-column" key={label}>{label}</span>)}
      {rowLabels.flatMap((rowLabel) => [
        <span className="heatmap-row" key={`${rowLabel}-label`}>{rowLabel}</span>,
        ...columnLabels.map((columnLabel) => {
          const value = lookup.get(`${rowLabel}:${columnLabel}`) ?? 0;
          const intensity = 0.1 + (value / maxValue) * 0.9;
          return <span className="heat-cell" style={{ "--intensity": intensity, color: intensity > 0.58 ? "#fff" : "#17223b" }} title={`${rowLabel} ${columnLabel}: ${value}`} key={`${rowLabel}-${columnLabel}`}>{value}</span>;
        }),
      ])}
      <div className="heat-legend"><span>Quiet</span><i /><i /><i /><i /><span>Busy</span></div>
    </div>
  );
}

function App() {
  const groupedLineData = useMemo(() => lineData
    .toSorted((left, right) => left.position - right.position)
    .reduce((groups, item) => {
      groups[item.rangeLabel] = [...(groups[item.rangeLabel] ?? []), item];
      return groups;
    }, {}), []);
  const availableRanges = Object.keys(groupedLineData);
  const [range, setRange] = useState(availableRanges.includes("30D") ? "30D" : availableRanges[0]);
  const [activeChart, setActiveChart] = useState(chartMenu[0].chartId);
  const activeLineRows = groupedLineData[range] ?? [];
  const generatedAt = formatGeneratedAt(dashboardData.generatedAt);

  const selectChart = (chartId) => {
    setActiveChart(chartId);
    document.getElementById(chartId)?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Snowflake AI Credit Control home">
          <span className="brand-mark"><i /><i /><i /></span>
          <span><b>{shell.brandTitle}</b><small>{shell.brandSubtitle}</small></span>
        </a>
        <div className="topbar-meta">
          <span className="demo-pill"><i /> {shell.environmentLabel}</span>
          <span className="account-name">{shell.accountName}</span>
          <button className="icon-button" onClick={() => window.location.reload()} aria-label="Reload SQL dashboard data">↻</button>
          <span className="avatar" aria-label="Signed in as database administrator">DB</span>
        </div>
      </header>

      <section className="workspace" id="top">
        <div className="page-heading">
          <div>
            <p className="overline">{shell.pageOverline}</p>
            <h1>{shell.titleLine1}<br /><em>{shell.titleEmphasis}</em></h1>
            <p className="lede">{shell.lede}</p>
          </div>
          <div className="data-source-card"><span>DATA SOURCE</span><b>config/dashboard.sql</b><small>Generated {generatedAt}</small></div>
        </div>

        <div className="status-line">
          <span><i className="status-dot" /> {monitoringStatus.message}</span>
          <span>SQL-driven dashboard · 3 numbers + 5 charts</span>
        </div>

        <section className="metric-grid" aria-label="Three key AI credit metrics">
          {metrics.map((metric) => <Metric key={metric.eyebrow} {...metric} />)}
        </section>

        <fieldset className="chart-picker">
          <legend>Chart type: What chart type do you prefer?</legend>
          <div className="chart-options">
            {chartMenu.map((option) => (
              <label className={activeChart === option.chartId ? "selected" : ""} key={option.chartId}>
                <input type="radio" name="chart-type" value={option.chartId} checked={activeChart === option.chartId} onChange={() => selectChart(option.chartId)} />
                <span><b>{option.label}</b><small>{option.description}</small></span>
              </label>
            ))}
          </div>
        </fieldset>

        <section className="chart-grid-layout" aria-label="Five SQL-powered chart components">
          <article id="agent_bar_chart" className={`panel panel--bar ${activeChart === "agent_bar_chart" ? "panel--selected" : ""}`}>
            <PanelHeading data={panelCopy(barData)} aside={<span className="chart-number">01</span>} />
            <BarChart rows={barData} />
          </article>

          <article id="credit_burn" className={`panel panel--line ${activeChart === "credit_burn" ? "panel--selected" : ""}`}>
            <PanelHeading data={panelCopy(activeLineRows)} aside={
              <div className="range-control" aria-label="Line chart reporting period">
                {availableRanges.map((item) => <button key={item} className={range === item ? "active" : ""} onClick={() => setRange(item)}>{item}</button>)}
              </div>
            } />
            <LineChart rows={activeLineRows} />
          </article>

          <article id="usage_scatter" className={`panel panel--scatter ${activeChart === "usage_scatter" ? "panel--selected" : ""}`}>
            <PanelHeading data={panelCopy(scatterData)} aside={<span className="chart-number">03</span>} />
            <ScatterPlot rows={scatterData} />
          </article>

          <article id="service_pie_chart" className={`panel panel--pie ${activeChart === "service_pie_chart" ? "panel--selected" : ""}`}>
            <PanelHeading data={panelCopy(pieData)} aside={<span className="chart-number">04</span>} />
            <PieChart rows={pieData} />
          </article>

          <article id="activity_heatmap" className={`panel panel--heatmap ${activeChart === "activity_heatmap" ? "panel--selected" : ""}`}>
            <PanelHeading data={panelCopy(heatmapData)} aside={<span className="chart-number">05</span>} />
            <Heatmap rows={heatmapData} />
          </article>
        </section>

        <footer><span>{footer.leftText}</span><span>{footer.rightText}</span></footer>
      </section>
    </main>
  );
}

export default App;
