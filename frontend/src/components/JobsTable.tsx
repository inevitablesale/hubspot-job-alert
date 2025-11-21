import { Job } from '../types'

interface Props {
  jobs: Job[]
}

const JobsTable = ({ jobs }: Props) => {
  return (
    <div className="card">
      <h3>Jobs ({jobs.length})</h3>
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
              <td>{job.location || 'Unknown'}</td>
              <td>{job.remote_flag ? 'Yes' : 'No'}</td>
              <td>{job.tags?.join(', ')}</td>
              <td>{job.score.toFixed(1)}</td>
              <td><a href={job.job_url} target="_blank" rel="noreferrer">View</a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default JobsTable
