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
      <header>
        <h1>Job Discovery Dashboard</h1>
        <p>Crawl curated HubSpot-related companies and surface relevant roles.</p>
      </header>

      <RunControls onRun={startRun} />
      <StatusPanel status={status} />
      <DomainsPanel domains={domains} />

      <div className="filters">
        <label>
          Min Score: {minScore}
          <input type="range" min="0" max="10" value={minScore} onChange={e => setMinScore(Number(e.target.value))} />
        </label>
        <label>
          Remote only
          <input type="checkbox" checked={remoteOnly} onChange={e => setRemoteOnly(e.target.checked)} />
        </label>
        <input placeholder="Search company or title" value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      <JobsTable jobs={filteredJobs} />
      <LogsPanel />
    </div>
  )
}

export default App
