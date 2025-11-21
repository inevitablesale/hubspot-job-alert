import { Domain } from '../types'

interface Props {
  domains: Domain[]
}

const DomainsPanel = ({ domains }: Props) => {
  return (
    <div className="card">
      <h3>Domains ({domains.length})</h3>
      <div className="domain-grid">
        {domains.map(domain => (
          <div key={domain.website} className="domain-pill">
            <strong>{domain.title}</strong>
            <div>{domain.website}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DomainsPanel
