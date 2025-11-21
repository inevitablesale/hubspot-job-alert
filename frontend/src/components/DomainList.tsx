import { Domain } from "../api";

type Props = {
  domains: Domain[];
  selectedDomainId: string | null;
  onSelect: (id: string | null) => void;
  onPreview: (id: string) => void;
};

function DomainList({ domains, selectedDomainId, onSelect, onPreview }: Props) {
  return (
    <div className="card">
      <h3>Domains</h3>
      <p>{domains.length} companies monitored</p>
      <ul className="domain-list">
        <li
          className={!selectedDomainId ? "active" : ""}
          onClick={() => onSelect(null)}
        >
          All domains
        </li>
        {domains.map((domain) => (
          <li
            key={domain.id}
            className={selectedDomainId === domain.id ? "active" : ""}
            onClick={() => onSelect(domain.id)}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span
                className="status-dot"
                style={{
                  background: domain.lastOkFetchAt ? "#16a34a" : "#f59e0b",
                }}
              />
              <div>
                <div>{domain.name}</div>
                <small>{domain.website}</small>
                <small>
                  Last OK fetch: {domain.lastOkFetchAt ? new Date(domain.lastOkFetchAt).toLocaleString() : "never"}
                </small>
              </div>
            </div>
            <button
              className="button secondary"
              onClick={(e) => {
                e.stopPropagation();
                onPreview(domain.id);
              }}
            >
              Preview careers page
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DomainList;
