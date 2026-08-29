import { useMemo, useState } from "react";

const rangeData = {
  "7D": [42, 54, 49, 73, 68, 96, 112],
  "30D": [28, 33, 31, 39, 46, 44, 52, 61, 58, 69, 72, 68, 75, 81, 79, 86, 92, 89, 98, 103, 96, 108, 115, 111, 119, 126, 122, 139, 147, 156],
  "90D": [19, 23, 21, 26, 30, 28, 34, 39, 37, 42, 47, 44, 52, 49, 57, 63, 60, 68, 74, 71, 80, 88, 84, 94, 101, 97, 109, 118, 126, 139],
};

const services = [
  { name: "Cortex Analyst", value: 41, credits: 536, color: "#6757d9" },
  { name: "Cortex Search", value: 27, credits: 353, color: "#2f8f83" },
  { name: "Document AI", value: 19, credits: 248, color: "#ec6a4c" },
  { name: "Snowflake Copilot", value: 13, credits: 170, color: "#e4b94f" },
];

const agents = [
  { name: "FINANCE_RECON_AGENT", owner: "Finance Ops", credits: 286, delta: 38 },
  { name: "SUPPORT_SEARCH_AGENT", owner: "Customer Care", credits: 219, delta: 16 },
  { name: "LEGAL_DOC_REVIEW", owner: "Legal", credits: 164, delta: 203 },
  { name: "SALES_BRIEF_AGENT", owner: "Revenue", credits: 122, delta: -8 },
  { name: "HR_POLICY_ASSIST", owner: "People", credits: 83, delta: 11 },
];

const employees = [
  { id: "E-10428", team: "Finance Ops", service: "Cortex Analyst", credits: 184.2, delta: 42, risk: "Watch" },
  { id: "E-11807", team: "Legal", service: "Document AI", credits: 147.8, delta: 1008, risk: "High" },
  { id: "E-09331", team: "Customer Care", service: "Cortex Search", credits: 126.5, delta: 18, risk: "Normal" },
  { id: "E-12142", team: "Revenue", service: "Snowflake Copilot", credits: 98.1, delta: 204, risk: "High" },
  { id: "E-08774", team: "Data Platform", service: "Cortex Analyst", credits: 84.6, delta: -6, risk: "Normal" },
];

const alerts = [
  { level: "critical", value: "+1,008%", title: "Document AI spike", detail: "E-11807 · 14:32 UTC" },
  { level: "warning", value: "+203%", title: "Legal agent acceleration", detail: "LEGAL_DOC_REVIEW · 13:48 UTC" },
  { level: "info", value: "81%", title: "Monthly budget pace", detail: "12 days remaining" },
];

function formatCredits(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
}

function LineChart({ values }) {
  const width = 720;
  const height = 220;
  const padding = 18;
  const max = Math.max(...values) * 1.08;
  const min = Math.min(...values) * 0.82;
  const points = values.map((value, index) => {
    const x = padding + (index / (values.length - 1)) * (width - padding * 2);
    const y = height - padding - ((value - min) / (max - min)) * (height - padding * 2);
    return [x, y];
  });
  const line = points.map(([x, y]) => `${x},${y}`).join(" ");
  const area = `${padding},${height - padding} ${line} ${width - padding},${height - padding}`;

  return (
    <div className="line-chart" aria-label="AI credit consumption trend">
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
        <circle cx={points.at(-1)[0]} cy={points.at(-1)[1]} r="7" className="chart-dot-halo" />
        <circle cx={points.at(-1)[0]} cy={points.at(-1)[1]} r="3.5" className="chart-dot" />
      </svg>
      <div className="axis-labels"><span>Start</span><span>Mid-period</span><span>Today</span></div>
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

function App() {
  const [range, setRange] = useState("30D");
  const [service, setService] = useState("All AI services");
  const [updatedAt, setUpdatedAt] = useState("14:35 UTC");
  const trend = useMemo(() => rangeData[range], [range]);

  const refresh = () => {
    setUpdatedAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Snowflake AI Credit Control home">
          <span className="brand-mark"><i /><i /><i /></span>
          <span><b>Credit Control</b><small>Snowflake AI observability</small></span>
        </a>
        <div className="topbar-meta">
          <span className="demo-pill"><i /> DEMO DATA</span>
          <span className="account-name">ACME_PROD / ACCOUNTADMIN</span>
          <button className="icon-button" onClick={refresh} aria-label="Refresh mock data">↻</button>
          <span className="avatar" aria-label="Signed in as database administrator">DB</span>
        </div>
      </header>

      <section className="workspace" id="top">
        <div className="page-heading">
          <div>
            <p className="overline">AI GOVERNANCE / COMMAND CENTER</p>
            <h1>Every AI credit.<br /><em>Clearly accountable.</em></h1>
            <p className="lede">A focused view of Snowflake AI consumption, ownership, and unusual growth—built for the DBA on call.</p>
          </div>
          <div className="heading-actions">
            <label className="select-wrap">
              <span>Service</span>
              <select value={service} onChange={(event) => setService(event.target.value)}>
                <option>All AI services</option>
                {services.map((item) => <option key={item.name}>{item.name}</option>)}
              </select>
            </label>
            <div className="range-control" aria-label="Reporting period">
              {Object.keys(rangeData).map((item) => (
                <button key={item} className={range === item ? "active" : ""} onClick={() => setRange(item)}>{item}</button>
              ))}
            </div>
          </div>
        </div>

        <div className="status-line">
          <span><i className="status-dot" /> Monitoring 4 AI services across 38 identities</span>
          <span>Mock snapshot · Updated {updatedAt}</span>
        </div>

        <section className="metric-grid" aria-label="Key AI credit metrics">
          <Metric eyebrow="Credits consumed" value="1,307.4" suffix=" cr" trend="+24.8%" note="vs prior period" />
          <Metric eyebrow="Projected month" value="1,941" suffix=" cr" trend="81%" note="of 2,400 budget" tone="violet" />
          <Metric eyebrow="Active identities" value="38" suffix="" trend="+6" note="employees & agents" tone="mint" />
          <Metric eyebrow="Growth signals" value="3" suffix="" trend="+2 new" note="need DBA review" tone="coral" />
        </section>

        <section className="dashboard-grid">
          <article className="panel panel--trend">
            <div className="panel-heading">
              <div><p className="panel-kicker">CONSUMPTION PULSE</p><h2>AI credit burn</h2></div>
              <div className="current-reading"><b>{range === "7D" ? "112" : range === "30D" ? "156" : "139"}</b><span>credits today</span></div>
            </div>
            <LineChart values={trend} />
            <div className="insight-strip"><span>↗</span><p><b>Acceleration detected.</b> Daily use is 2.1× the period baseline, led by Document AI.</p></div>
          </article>

          <article className="panel panel--mix">
            <div className="panel-heading"><div><p className="panel-kicker">SERVICE MIX</p><h2>Where credits go</h2></div><span className="quiet-label">1,307 total</span></div>
            <div className="donut-layout">
              <div className="donut" role="img" aria-label="Service usage donut chart">
                <div><b>41%</b><span>Analyst</span></div>
              </div>
              <div className="legend">
                {services.map((item) => (
                  <div className="legend-row" key={item.name}>
                    <span className="legend-name"><i style={{ background: item.color }} />{item.name}</span>
                    <span><b>{item.value}%</b><small>{item.credits} cr</small></span>
                  </div>
                ))}
              </div>
            </div>
          </article>

          <article className="panel panel--agents">
            <div className="panel-heading"><div><p className="panel-kicker">AGENT METER</p><h2>Top autonomous consumers</h2></div><span className="quiet-label">by credits</span></div>
            <div className="bar-list">
              {agents.map((agent, index) => (
                <div className="bar-row" key={agent.name}>
                  <div className="bar-copy"><span><b>{index + 1}</b>{agent.name}<small>{agent.owner}</small></span><span><strong>{agent.credits}</strong> cr <em className={agent.delta > 100 ? "hot" : agent.delta < 0 ? "cool" : ""}>{agent.delta > 0 ? "+" : ""}{agent.delta}%</em></span></div>
                  <div className="bar-track"><i style={{ width: `${(agent.credits / agents[0].credits) * 100}%` }} /></div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel panel--employees">
            <div className="panel-heading"><div><p className="panel-kicker">IDENTITY ATTRIBUTION</p><h2>Employee consumption</h2></div><button className="text-button">View all 38 <span>→</span></button></div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Employee</th><th>Team</th><th>Primary service</th><th>Credits</th><th>Growth</th><th>Status</th></tr></thead>
                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.id}>
                      <td><span className="employee-id">{employee.id}</span></td>
                      <td>{employee.team}</td><td>{employee.service}</td><td><b>{formatCredits(employee.credits)}</b></td>
                      <td><span className={employee.delta > 200 ? "growth growth--hot" : employee.delta < 0 ? "growth growth--down" : "growth"}>{employee.delta > 0 ? "+" : ""}{employee.delta}%</span></td>
                      <td><span className={`risk risk--${employee.risk.toLowerCase()}`}>{employee.risk}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <article className="panel panel--alerts">
            <div className="panel-heading"><div><p className="panel-kicker">DBA ATTENTION</p><h2>Growth signals</h2></div><span className="signal-count">3 open</span></div>
            <div className="alert-list">
              {alerts.map((alert) => (
                <div className={`alert alert--${alert.level}`} key={alert.title}>
                  <span className="alert-value">{alert.value}</span>
                  <span><b>{alert.title}</b><small>{alert.detail}</small></span>
                  <button aria-label={`Inspect ${alert.title}`}>→</button>
                </div>
              ))}
            </div>
            <div className="budget-block">
              <div><span>Monthly budget pace</span><b>1,941 / 2,400 credits</b></div>
              <div className="budget-track"><i /></div>
              <p>At the current rate, the account will remain <b>459 credits under budget.</b></p>
            </div>
          </article>
        </section>

        <footer><span>Snowflake AI Credit Control · Prototype 0.1</span><span>All values are synthetic · No warehouse queries executed</span></footer>
      </section>
    </main>
  );
}

export default App;

