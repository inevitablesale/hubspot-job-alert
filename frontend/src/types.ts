export interface Domain {
  id?: number
  title: string
  totalScore?: number
  reviewsCount?: number
  street?: string
  city?: string
  state?: string
  countryCode?: string
  website?: string
  phone?: string
  categoryName?: string
  url?: string
  internal_lastScannedAt?: string
  internal_careersUrl?: string
  jobsFoundLastRun?: number
}

export interface Job {
  id?: number
  domain_id: number
  domain_title: string
  domain_website: string
  title: string
  location?: string
  remote_flag?: boolean
  department?: string
  job_url: string
  apply_url?: string
  posted_at?: string
  discovered_at: string
  score: number
  tags: string[]
  snippet?: string
}

export interface CrawlStatus {
  runId?: number
  status: string
  startedAt?: string
  finishedAt?: string
  domainsTotal: number
  domainsCompleted: number
  jobsFound: number
  currentDomain?: string
  lastLogMessage?: string
  errorCount: number
}
