import { JobPosting } from "../api";

type Props = {
  jobs: JobPosting[];
  hubspotOnly: boolean;
  onToggleHubspot: () => void;
};

function JobsTable({ jobs, hubspotOnly, onToggleHubspot }: Props) {
  const exportCsv = () => {
    const headers = [
      "Company",
      "Title",
      "Location",
      "HubSpot",
      "Keywords",
      "ScrapedAt",
      "URL",
    ];
    const rows = jobs.map((job) => [
      job.domainName,
      job.title,
      job.location || "",
      job.isHubspotRole ? "Yes" : "No",
      job.matchedKeywords.join(";"),
      job.scrapedAt,
      job.sourceUrl,
    ]);
    const csv = [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", "hubspot-jobs.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Jobs</h3>
        <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={hubspotOnly}
            onChange={onToggleHubspot}
          />
          HubSpot roles only
        </label>
        <button className="button secondary" onClick={exportCsv} disabled={!jobs.length}>
          Export CSV
        </button>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Company</th>
            <th>Title</th>
            <th>Location</th>
            <th>HubSpot</th>
            <th>Keywords</th>
            <th>Scraped</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id} style={{ opacity: job.isHubspotRole ? 1 : 0.6 }}>
              <td>{job.domainName}</td>
              <td>{job.title}</td>
              <td>{job.location || "-"}</td>
              <td>
                <span className={`badge ${job.isHubspotRole ? "green" : "gray"}`}>
                  {job.isHubspotRole ? "Yes" : "No"}
                </span>
              </td>
              <td>{job.matchedKeywords.join(", ")}</td>
              <td>{new Date(job.scrapedAt).toLocaleString()}</td>
              <td>
                <a href={job.sourceUrl} target="_blank" rel="noreferrer">
                  View
                </a>
              </td>
            </tr>
          ))}
          {!jobs.length && (
            <tr>
              <td colSpan={7}>No jobs found yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default JobsTable;
