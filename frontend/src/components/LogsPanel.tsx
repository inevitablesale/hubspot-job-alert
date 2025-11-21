import { useEffect, useState } from 'react'
import axios from 'axios'

const LogsPanel = () => {
  const [logs, setLogs] = useState('')

  useEffect(() => {
    axios.get('/api/logs?lines=50').then(res => setLogs(res.data.logs)).catch(console.error)
    const timer = setInterval(() => {
      axios.get('/api/logs?lines=50').then(res => setLogs(res.data.logs)).catch(console.error)
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="card">
      <h3>Live crawl logs</h3>
      <pre className="logs">{logs || 'No logs yet'}</pre>
    </div>
  )
}

export default LogsPanel
