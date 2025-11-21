import { CrawlStatus } from '../types'

interface Props {
  status: CrawlStatus
}

const StatusPanel = ({ status }: Props) => {
  const progress = status.domainsTotal ? Math.round((status.domainsCompleted / status.domainsTotal) * 100) : 0
  return (
    <div className="card">
      <h3>Crawl Status</h3>
      <p>Status: {status.status}</p>
      <p>Domains: {status.domainsCompleted} / {status.domainsTotal}</p>
      <p>Jobs found: {status.jobsFound}</p>
      <p>Errors: {status.errorCount}</p>
      {status.currentDomain && <p>Scanning: {status.currentDomain}</p>}
      <div className="progress">
        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
      </div>
    </div>
  )
}

export default StatusPanel
