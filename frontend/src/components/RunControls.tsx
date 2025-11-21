interface Props {
  onRun: () => void
  domains: number
  isRunning?: boolean
}

const RunControls = ({ onRun, domains, isRunning }: Props) => {
  return (
    <div className="card run-card">
      <div>
        <p className="eyebrow">Control center</p>
        <h3>Launch a new crawl</h3>
        <p>Pulse through {domains || 'all'} domains from the curated list and stream live discoveries.</p>
      </div>
      <div className="run-actions">
        <button className="primary" onClick={onRun} disabled={isRunning}>{isRunning ? 'Running…' : 'Start live scan'}</button>
        <div className="legend">
          <span className="dot dot-ready"></span>Ready to dispatch
          <span className="dot dot-progress"></span>In-flight
          <span className="dot dot-complete"></span>Completed
        </div>
      </div>
    </div>
  )
}

export default RunControls
