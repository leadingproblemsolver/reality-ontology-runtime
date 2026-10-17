export interface RawGithubIssue {
  id: number;
  number: number;
  title: string;
  body: string | null;
  html_url: string;
  state: string;
  labels: Array<string | { name?: string }>;
  created_at: string;
  updated_at: string;
  comments: number;
  user: { login?: string } | null;
  pull_request?: unknown;
}

export interface GithubIssuesClient {
  listOpenIssues(target: { owner: string; repo: string }): Promise<RawGithubIssue[]>;
}

export class GithubApiError extends Error {
  status?: number;
  body?: unknown;

  constructor(message: string, status?: number, body?: unknown) {
    super(message);
    this.name = "GithubApiError";
    this.status = status;
    this.body = body;
  }
}

const GITHUB_API_BASE = "https://api.github.com";

export class GithubApiClient implements GithubIssuesClient {
  constructor(
    private readonly token?: string,
    private readonly fetchImpl: typeof fetch = fetch,
    private readonly perPage = 100,
  ) {}

  async listOpenIssues({ owner, repo }: { owner: string; repo: string }): Promise<RawGithubIssue[]> {
    const issues: RawGithubIssue[] = [];
    let page = 1;

    while (true) {
      const url = `${GITHUB_API_BASE}/repos/${owner}/${repo}/issues?state=open&sort=updated&direction=desc&per_page=${this.perPage}&page=${page}`;
      const headers: Record<string, string> = {
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      };
      if (this.token) headers.Authorization = `Bearer ${this.token}`;

      let response: Response;
      try {
        response = await this.fetchImpl(url, { headers });
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        throw new GithubApiError(`network error contacting GitHub: ${message}`);
      }

      if (!response.ok) {
        let body: unknown;
        try {
          body = await response.json();
        } catch {
          body = await response.text().catch(() => undefined);
        }
        throw new GithubApiError(
          `GitHub API returned ${response.status} for ${owner}/${repo} issues`,
          response.status,
          body,
        );
      }

      let payload: unknown;
      try {
        payload = await response.json();
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        throw new GithubApiError(`GitHub API returned non-JSON response: ${message}`);
      }

      if (!Array.isArray(payload)) {
        throw new GithubApiError("GitHub API response was not an array of issues", response.status, payload);
      }

      issues.push(...(payload as RawGithubIssue[]));

      if (payload.length < this.perPage) break;
      page += 1;
    }

    return issues;
  }
}
