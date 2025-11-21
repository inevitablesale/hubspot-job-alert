import { CrawlStatus } from '../types'

interface Props {
  status: CrawlStatus
}

const StatusPanel = ({ status }: Props) => {
  const progress = status.domainsTotal ? Math.round((status.domainsCompleted / status.domainsTotal) * 100) : 0
  const pulses = status.domainsTotal || 12
  return (
    <div className="card status-card">
      <div className="status-header">
        <div>
          <p className="eyebrow">Live crawl</p>
          <h3>{status.status === 'running' ? 'Crawl in motion' : 'Crawler idle'}</h3>
          {status.currentDomain && <p className="muted">Scanning: {status.currentDomain}</p>}
        </div>
        <div className="status-ring" style={{ ['--progress' as string]: `${progress}%` }}>
          <div className="status-ring-inner">
            <strong>{progress}%</strong>
            <span>domains</span>
          </div>
        </div>
      </div>

      <div className="status-grid">
        <div className="metric">
          <p className="label">Domains complete</p>
          <strong>{status.domainsCompleted} / {status.domainsTotal}</strong>
        </div>
        <div className="metric">
          <p className="label">Jobs surfaced</p>
          <strong>{status.jobsFound}</strong>
        </div>
        <div className="metric">
          <p className="label">Errors</p>
          <strong className={status.errorCount ? 'warn' : ''}>{status.errorCount}</strong>
        </div>
        <div className="metric">
          <p className="label">Run ID</p>
          <strong>{status.runId ?? '—'}</strong>
        </div>
      </div>

      <div className="domain-stream" aria-label="domain progress visualization">
        {Array.from({ length: pulses }).map((_, idx) => (
          <span key={idx} className={`node ${idx < status.domainsCompleted ? 'node-complete' : 'node-waiting'}`}></span>
        ))}
      </div>

      <div className="timeline">
        <span>Waiting</span>
        <div className="timeline-bar">
          <div className="timeline-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <span>Complete</span>
      </div>
    </div>
  )
}

export default StatusPanel
