export type Domain = {
  id: string;
  name: string;
  website: string;
  city?: string | null;
  state?: string | null;
  countryCode?: string | null;
  categoryName?: string | null;
  sourceUrl: string;
  totalScore?: number | null;
  reviewsCount?: number | null;
  lastOkFetchAt?: string | null;
};

export type JobPosting = {
  id: string;
  domainId: string;
  domainName: string;
  companyWebsite: string;
  sourceUrl: string;
  title: string;
  location?: string | null;
  department?: string | null;
  employmentType?: string | null;
  remote?: boolean | null;
  descriptionSnippet: string;
  isHubspotRole: boolean;
  matchedKeywords: string[];
  scrapedAt: string;
};

export type CrawlStatus = {
  running: boolean;
  lastRunStartedAt?: string | null;
  lastRunCompletedAt?: string | null;
  currentDomainId?: string | null;
  currentDomainName?: string | null;
  totalDomains: number;
  completedDomains: number;
  jobsFoundThisRun: number;
  errorCount: number;
};

export type LogEntry = {
  timestamp: string;
  level: string;
  message: string;
  context: Record<string, unknown>;
};

export type RunResponse = {
  started: boolean;
  scope: "single" | "full";
  domainId?: string | null;
};

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });
  if (!resp.ok) {
    throw new Error(`Request failed: ${resp.status}`);
  }
  return resp.json();
}

export async function fetchDomains(): Promise<Domain[]> {
  return request<Domain[]>("/domains");
}

export async function runCrawl(domainId?: string): Promise<RunResponse> {
  const params = domainId ? `?domainId=${encodeURIComponent(domainId)}` : "";
  return request<RunResponse>(`/run${params}`, { method: "POST" });
}

export async function fetchStatus(): Promise<CrawlStatus> {
  return request<CrawlStatus>("/status");
}

export async function fetchJobs(
  hubspotOnly = true,
  limit = 200
): Promise<JobPosting[]> {
  const params = new URLSearchParams();
  params.append("limit", String(limit));
  params.append("hubspotOnly", hubspotOnly ? "true" : "false");
  return request<JobPosting[]>(`/results?${params.toString()}`);
}

export async function fetchLogs(): Promise<LogEntry[]> {
  return request<LogEntry[]>("/logs");
}

export async function previewCareers(domainId: string): Promise<string[]> {
  return request<string[]>(`/domains/${domainId}/careers`);
}
