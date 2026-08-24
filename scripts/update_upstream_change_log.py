"""Record new upstream client releases, commits and merged pull requests."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


UPSTREAM = "DeebotUniverse/client.py"
BRANCH = "dev"
API_ROOT = "https://api.github.com"
STATE_PATH = Path(".automation/upstream-state.json")
LOG_PATH = Path("research/upstream-change-log.md")


def github_get(path: str) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "deebot-goat-docs-upstream-sync",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"GitHub API request failed for {path}: {error}") from error

    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected GitHub API response for {path}")
    return payload


def load_state() -> dict[str, list[str]]:
    if not STATE_PATH.exists():
        return {"commits": [], "releases": [], "pull_requests": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, list[str]]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )


def date_part(value: str | None) -> str:
    return (value or "unknown")[:10]


def main() -> int:
    state = load_state()
    commits = github_get(
        f"/repos/{UPSTREAM}/commits?sha={BRANCH}&per_page=30"
    )
    releases = github_get(f"/repos/{UPSTREAM}/releases?per_page=20")
    pull_requests = [
        pull_request
        for pull_request in github_get(
            f"/repos/{UPSTREAM}/pulls?state=closed&sort=updated&direction=desc&per_page=50"
        )
        if pull_request.get("merged_at")
    ]

    new_commits = [
        commit for commit in commits if commit["sha"] not in state["commits"]
    ]
    new_releases = [
        release
        for release in releases
        if release.get("tag_name") not in state["releases"]
    ]
    new_pull_requests = [
        pull_request
        for pull_request in pull_requests
        if str(pull_request["number"]) not in state["pull_requests"]
    ]

    if not any((new_commits, new_releases, new_pull_requests)):
        print("No new upstream changes found.")
        return 0

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists():
        existing = LOG_PATH.read_text(encoding="utf-8").rstrip()
    else:
        existing = "# Upstream change log\n\nAutomatically collected from `DeebotUniverse/client.py`.\n"

    sections = [f"## {datetime.now(timezone.utc).date().isoformat()}"]
    if new_releases:
        sections.append("### Releases")
        sections.extend(
            f"- [{release.get('name') or release['tag_name']}]({release['html_url']})"
            for release in new_releases
        )
    if new_pull_requests:
        sections.append("### Merged pull requests")
        sections.extend(
            f"- [#{pull_request['number']} - {pull_request['title']}]({pull_request['html_url']}) "
            f"(merged {date_part(pull_request.get('merged_at'))})"
            for pull_request in new_pull_requests
        )
    if new_commits:
        sections.append(f"### Commits on `{BRANCH}`")
        sections.extend(
            f"- [`{commit['sha'][:7]}`]({commit['html_url']}) - "
            f"{commit['commit']['message'].splitlines()[0]} "
            f"({date_part(commit['commit']['author'].get('date'))})"
            for commit in new_commits
        )

    LOG_PATH.write_text(existing + "\n".join(sections).rstrip() + "\n", encoding="utf-8")
    state["commits"] = [commit["sha"] for commit in commits]
    state["releases"] = [release["tag_name"] for release in releases]
    state["pull_requests"] = [str(pull_request["number"]) for pull_request in pull_requests]
    save_state(state)
    print(
        f"Recorded {len(new_releases)} releases, {len(new_pull_requests)} merged PRs "
        f"and {len(new_commits)} commits."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())