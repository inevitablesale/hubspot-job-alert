interface Props {
  onRun: () => void
}

const RunControls = ({ onRun }: Props) => {
  return (
    <div className="card">
      <h3>Run Crawl</h3>
      <p>Trigger a fresh crawl across the configured domains.</p>
      <button onClick={onRun}>Run Scan</button>
    </div>
  )
}

export default RunControls
