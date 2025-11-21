import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import RunControls from './components/RunControls'
import StatusPanel from './components/StatusPanel'
import JobsTable from './components/JobsTable'
import DomainsPanel from './components/DomainsPanel'
import LogsPanel from './components/LogsPanel'
import { CrawlStatus, Domain, Job } from './types'

const API_BASE = '/api'

function App() {
  const [domains, setDomains] = useState<Domain[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [status, setStatus] = useState<CrawlStatus>({ status: 'idle', domainsTotal: 0, domainsCompleted: 0, jobsFound: 0, errorCount: 0 })
  const [activeRunId, setActiveRunId] = useState<number | undefined>()
  const [minScore, setMinScore] = useState(0)
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [search, setSearch] = useState('')

  useEffect(() => {
    axios.get(`${API_BASE}/domains`).then(res => setDomains(res.data)).catch(console.error)
    fetchResults()
    fetchStatus()
  }, [])

  useEffect(() => {
    if (status.status === 'running' && status.runId) {
      const timer = setInterval(() => fetchStatus(status.runId), 2000)
      return () => clearInterval(timer)
    }
  }, [status.status, status.runId])

  const fetchStatus = (runId?: number) => {
    axios.get(`${API_BASE}/status`, { params: { run_id: runId } })
      .then(res => setStatus(res.data))
      .catch(console.error)
  }

  const fetchResults = (runId?: number) => {
    axios.get(`${API_BASE}/results`, { params: { run_id: runId } })
      .then(res => setJobs(res.data))
      .catch(console.error)
  }

  const startRun = () => {
    axios.post(`${API_BASE}/run`, {})
      .then(res => {
        setActiveRunId(res.data.run_id)
        fetchStatus(res.data.run_id)
      })
      .catch(err => alert(err.response?.data?.detail || 'Failed to start crawl'))
  }

  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      if (minScore && job.score < minScore) return false
      if (remoteOnly && !job.remote_flag) return false
      if (search) {
        const text = `${job.title} ${job.domain_title}`.toLowerCase()
        if (!text.includes(search.toLowerCase())) return false
      }
      return true
    })
  }, [jobs, minScore, remoteOnly, search])

  return (
    <div className="container">
      <div className="hero">
        <div>
          <p className="eyebrow">Render-ready telemetry</p>
          <h1>Orbiting HubSpot job signals</h1>
          <p className="lede">Watch domains light up as the crawler resolves careers pages, scores roles, and streams them into the dashboard in real time.</p>
          <div className="hero-metrics">
            <span className="pill">Domains tracked: {domains.length}</span>
            <span className="pill pill-soft">Active run: {status.runId ?? '—'}</span>
            <span className="pill pill-soft">Latest score floor: {minScore}</span>
          </div>
        </div>
        <div className="hero-visual" aria-hidden>
          <div className="orb">
            <div className="orb-ring" style={{ ['--progress' as string]: `${status.domainsTotal ? (status.domainsCompleted / status.domainsTotal) * 100 : 0}%` }}></div>
            <div className="orb-core">{status.jobsFound || 0}<span>jobs</span></div>
          </div>
          <p className="orb-caption">Crawl pulse updates as domains complete</p>
        </div>
      </div>

      <div className="grid">
        <div className="panel">
          <RunControls onRun={startRun} domains={domains.length} />
        </div>
        <div className="panel">
          <StatusPanel status={status} />
        </div>
      </div>

      <div className="panel">
        <DomainsPanel domains={domains} />
      </div>

      <div className="panel filters">
        <div>
          <p className="eyebrow">Fine-tune stream</p>
          <h3>Focus the jobs feed</h3>
        </div>
        <div className="filter-controls">
          <label className="slider-label">
            Min Score: <strong>{minScore}</strong>
            <input type="range" min="0" max="10" value={minScore} onChange={e => setMinScore(Number(e.target.value))} />
          </label>
          <label className="toggle">
            <input type="checkbox" checked={remoteOnly} onChange={e => setRemoteOnly(e.target.checked)} />
            <span>Remote only</span>
          </label>
          <input className="search" placeholder="Search company or title" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      <div className="panel">
        <JobsTable jobs={filteredJobs} />
      </div>
      <div className="panel">
        <LogsPanel />
      </div>
    </div>
  )
}

export default App
