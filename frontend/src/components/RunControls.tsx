import { useState } from "react";
import { Domain } from "../api";

type Props = {
  domains: Domain[];
  onRunFull: () => void;
  onRunDomain: (id: string) => void;
  running: boolean;
};

function RunControls({ domains, onRunFull, onRunDomain, running }: Props) {
  const [selected, setSelected] = useState<string>("");

  return (
    <div className="card">
      <h3>Run Crawl</h3>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <button
          className="button primary"
          onClick={onRunFull}
          disabled={running}
        >
          Run full crawl
        </button>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          style={{ flex: 1, padding: 8, borderRadius: 6 }}
          disabled={running}
        >
          <option value="">Select domain</option>
          {domains.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
        <button
          className="button secondary"
          onClick={() => selected && onRunDomain(selected)}
          disabled={!selected || running}
        >
          Run selected
        </button>
      </div>
      {running && <small>Crawl running…</small>}
    </div>
  );
}

export default RunControls;
