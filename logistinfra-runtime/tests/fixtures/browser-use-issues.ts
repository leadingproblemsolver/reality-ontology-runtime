import type { RawGithubIssue } from "../../src/adapters/github.js";

function daysAgo(days: number): string {
  return new Date(Date.now() - days * 86_400_000).toISOString();
}

const GOOD_BODY =
  "Steps to reproduce:\n1. Launch the agent against a page with a hidden iframe target.\n" +
  "2. Call `page.click` on a selector inside that iframe.\n" +
  "Expected: ActionResult.error is returned.\nActual: the process hangs indefinitely.";

/** A small, deliberately mixed set of issues: some should pass the deterministic filter, most should not. */
export function buildFixtureIssues(): RawGithubIssue[] {
  return [
    {
      id: 1001,
      number: 501,
      title: "Agent hangs when clicking a selector inside a hidden iframe",
      body: GOOD_BODY,
      html_url: "https://github.com/browser-use/browser-use/issues/501",
      state: "open",
      labels: ["bug"],
      created_at: daysAgo(10),
      updated_at: daysAgo(2),
      comments: 3,
      user: { login: "reporter-a" },
    },
    {
      id: 1002,
      number: 502,
      title: "Support custom viewport presets",
      body: GOOD_BODY,
      html_url: "https://github.com/browser-use/browser-use/issues/502",
      state: "open",
      labels: ["enhancement"],
      created_at: daysAgo(20),
      updated_at: daysAgo(5),
      comments: 1,
      user: { login: "reporter-b" },
    },
    {
      id: 1003,
      number: 503,
      title: "Fixed in v0.9",
      body: GOOD_BODY,
      html_url: "https://github.com/browser-use/browser-use/issues/503",
      state: "closed",
      labels: ["bug"],
      created_at: daysAgo(60),
      updated_at: daysAgo(50),
      comments: 8,
      user: { login: "reporter-c" },
    },
    {
      id: 1004,
      number: 504,
      title: "Doesn't work",
      body: "help",
      html_url: "https://github.com/browser-use/browser-use/issues/504",
      state: "open",
      labels: ["bug"],
      created_at: daysAgo(3),
      updated_at: daysAgo(1),
      comments: 0,
      user: { login: "reporter-d" },
    },
    {
      id: 1005,
      number: 505,
      title: "Timeout not respected under heavy DOM mutation",
      body: GOOD_BODY,
      html_url: "https://github.com/browser-use/browser-use/issues/505",
      state: "open",
      labels: ["bug", "reliability"],
      created_at: daysAgo(400),
      updated_at: daysAgo(400),
      comments: 2,
      user: { login: "reporter-e" },
    },
    {
      id: 1006,
      number: 506,
      title: "Bump dependency versions",
      body: GOOD_BODY,
      html_url: "https://github.com/browser-use/browser-use/pull/506",
      state: "open",
      labels: [],
      created_at: daysAgo(4),
      updated_at: daysAgo(1),
      comments: 0,
      user: { login: "reporter-f" },
      pull_request: { url: "https://api.github.com/repos/browser-use/browser-use/pulls/506" },
    },
  ];
}

/** Only the issues that should survive the deterministic filter for the fixture above. */
export const EXPECTED_PASSING_ISSUE_NUMBERS = [501];
