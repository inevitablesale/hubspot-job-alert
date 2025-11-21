import { CrawlStatus } from "../api";

type Props = {
  status: CrawlStatus | null;
};

function StatusPanel({ status }: Props) {
  if (!status) {
    return (
      <div className="card">
        <h3>Status</h3>
        <p>Loading status…</p>
      </div>
    );
  }

  const progress = status.totalDomains
    ? Math.round((status.completedDomains / status.totalDomains) * 100)
    : 0;

  const indicatorColor = status.running
    ? "#f59e0b"
    : status.errorCount > 0
    ? "#dc2626"
    : "#16a34a";

  return (
    <div className="card">
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span className="status-dot" style={{ background: indicatorColor }} />
        <h3>Status</h3>
      </div>
      <p>{status.running ? "Running" : "Idle"}</p>
      <div style={{ height: 8, background: "#e5e7eb", borderRadius: 8 }}>
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: "#ff7a59",
            borderRadius: 8,
          }}
        />
      </div>
      <p>
        {status.completedDomains}/{status.totalDomains} domains · Jobs this run: {" "}
        {status.jobsFoundThisRun}
      </p>
      <p>Current domain: {status.currentDomainName || "-"}</p>
      <p>Errors: {status.errorCount}</p>
      <small>
        Last started: {status.lastRunStartedAt || "-"} | Last completed: {" "}
        {status.lastRunCompletedAt || "-"}
      </small>
    </div>
  );
}

export default StatusPanel;
