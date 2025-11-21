import { useEffect, useMemo, useState } from "react";
import {
  CrawlStatus,
  Domain,
  JobPosting,
  LogEntry,
  fetchDomains,
  fetchJobs,
  fetchLogs,
  fetchStatus,
  previewCareers,
  runCrawl,
} from "../api";
import DomainList from "./DomainList";
import JobsTable from "./JobsTable";
import LogsPanel from "./LogsPanel";
import RunControls from "./RunControls";
import StatusPanel from "./StatusPanel";

const POLL_INTERVAL_MS = 8000;

function Dashboard() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<CrawlStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [hubspotOnly, setHubspotOnly] = useState(true);
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(true);

  const refreshAll = async () => {
    const [domainsData, statusData, jobsData, logsData] = await Promise.all([
      fetchDomains(),
      fetchStatus(),
      fetchJobs(hubspotOnly),
      fetchLogs(),
    ]);
    setDomains(domainsData);
    setStatus(statusData);
    setJobs(jobsData);
    setLogs(logsData);
  };

  useEffect(() => {
    refreshAll();
    const timer = setInterval(() => {
      refreshAll();
    }, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [hubspotOnly]);

  const handleRun = async (domainId?: string) => {
    setLoading(true);
    try {
      await runCrawl(domainId);
      await refreshAll();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredJobs = useMemo(() => {
    if (!selectedDomainId) return jobs;
    return jobs.filter((job) => job.domainId === selectedDomainId);
  }, [jobs, selectedDomainId]);

  const filteredLogs = useMemo(() => {
    if (!selectedDomainId) return logs;
    return logs.filter((log) => log.context?.domainId === selectedDomainId);
  }, [logs, selectedDomainId]);

  return (
    <div className="grid grid-two">
      <div className="grid" style={{ alignSelf: "start" }}>
        <RunControls
          domains={domains}
          onRunFull={() => handleRun()}
          onRunDomain={(id) => handleRun(id)}
          running={!!status?.running || loading}
        />
        <StatusPanel status={status} />
        <JobsTable
          jobs={filteredJobs}
          hubspotOnly={hubspotOnly}
          onToggleHubspot={() => setHubspotOnly((v) => !v)}
        />
      </div>
      <div className="grid">
        <DomainList
          domains={domains}
          selectedDomainId={selectedDomainId}
          onSelect={setSelectedDomainId}
          onPreview={async (domainId) => {
            try {
              const urls = await previewCareers(domainId);
              if (!urls.length) {
                alert("No careers pages detected yet for this domain.");
                return;
              }
              window.open(urls[0], "_blank");
            } catch (err) {
              console.error(err);
              alert("Preview failed. Check logs for details.");
            }
          }}
        />
        <LogsPanel logs={filteredLogs} expanded={showLogs} onToggle={() => setShowLogs((v) => !v)} />
      </div>
    </div>
  );
}

export default Dashboard;
