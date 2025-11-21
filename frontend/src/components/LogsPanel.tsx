import { LogEntry } from "../api";

type Props = {
  logs: LogEntry[];
  expanded?: boolean;
  onToggle?: () => void;
};

function LogsPanel({ logs, expanded = true, onToggle }: Props) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Logs</h3>
        <button className="button secondary" onClick={onToggle}>
          {expanded ? "Hide" : "Show"}
        </button>
      </div>
      {expanded && (
        <div className="logs">
          {logs.map((log) => (
            <div key={`${log.timestamp}-${log.message}`}>
              <strong>[{log.level}]</strong> {log.timestamp}: {log.message}
            </div>
          ))}
          {!logs.length && <div>No logs yet.</div>}
        </div>
      )}
    </div>
  );
}

export default LogsPanel;
