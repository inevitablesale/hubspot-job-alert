import { Job } from '../types'

interface Props {
  jobs: Job[]
}

const JobsTable = ({ jobs }: Props) => {
  return (
    <div className="table-wrapper">
      <div className="table-header">
        <div>
          <p className="eyebrow">Jobs feed</p>
          <h3>Fresh discoveries ({jobs.length})</h3>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Title</th>
            <th>Location</th>
            <th>Remote</th>
            <th>Tags</th>
            <th>Score</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map(job => (
            <tr key={`${job.job_url}-${job.domain_id}`}>
              <td>{job.domain_title}</td>
              <td>{job.title}</td>
              <td>{job.location || '—'}</td>
              <td>{job.remote_flag ? 'Yes' : 'No'}</td>
              <td>{job.tags?.join(', ')}</td>
              <td>{job.score.toFixed(1)}</td>
              <td><a href={job.job_url} target="_blank" rel="noreferrer">Open</a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default JobsTable
