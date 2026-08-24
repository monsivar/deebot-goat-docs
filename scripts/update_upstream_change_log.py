"""Record new upstream client releases, commits and merged pull requests."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


UPSTREAM = "DeebotUniverse/client.py"
BRANCH = "dev"
API_ROOT = "https://api.github.com"

# Base directory is the docs repository root ('docs/')
BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / ".automation" / "upstream-state.json"
LOG_PATH = BASE_DIR / "research" / "upstream-change-log.md"


def github_get(path: str) -> Any:
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
            return json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"GitHub API request failed for {path}: {error}") from error


def get_pr_files(pr_number: int) -> list[str]:
    """Fetch the list of changed filenames for a pull request."""
    try:
        payload = github_get(f"/repos/{UPSTREAM}/pulls/{pr_number}/files?per_page=100")
        if isinstance(payload, list):
            return [f.get("filename", "") for f in payload if f.get("filename")]
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: Could not fetch files for PR #{pr_number}: {exc}")
    return []

def suggest_affected_docs(
    title: str,
    labels: list[str],
    files: list[str],
) -> list[tuple[str, str]]:
    """Suggest likely affected documentation pages based on PR metadata and changed files."""
    suggestions: dict[str, str] = {}
    combined_text = f"{title} {' '.join(labels)} {' '.join(files)}".lower()

    def has_word(pattern: str, text: str) -> bool:
        return bool(re.search(rf"\b({pattern})\b", text, re.IGNORECASE))

    # Map rules
    if (
        any("map" in f.lower() for f in files)
        or any(f.startswith("src/map") for f in files)
        or has_word("map|maps|svg|onmi|onari|onmaptrace|onmaptrack", combined_text)
    ):
        suggestions["map.md"] = "../docs/map.md"

    # Capability rules
    if (
        any("capabilities.py" in f for f in files)
        or has_word("capability|capabilities", combined_text)
    ):
        suggestions["capabilities.md"] = "../docs/capabilities.md"

    # Model / Hardware rules
    if (
        any(f.startswith("deebot_client/hardware") for f in files)
        or any(f.startswith("deebot_client/models") for f in files)
        or has_word("model|models|hardware|2i0fns|5xu9h3|xmp9ds|51rcxt|300lc5", combined_text)
        or "support for" in combined_text
    ):
        suggestions["supported-models.md"] = "../docs/supported-models.md"

    # Command routing
    if (
        any("commands/" in f for f in files)
        or any("p2p" in f for f in files)
        or any("mqtt" in f for f in files)
        or has_word("routing|p2p|mqtt|command_routing", combined_text)
    ):
        suggestions["command-routing.md"] = "../docs/command-routing.md"

    # Mowing control
    if (
        has_word("clean|cleanaction|cleanmode|mow|mowing|dock|pause|resume", combined_text)
        and not any(f.startswith("src/map") for f in files)
        and not has_word("map|maps", title)
    ):
        suggestions["mowing-control.md"] = "../docs/mowing-control.md"

    # Zones and area settings
    if has_word("area|areas|room|rooms|zone|zones", combined_text):
        if has_word("height|cutmode|cut_mode|obstacle_height|angle", combined_text):
            suggestions["area-parameters.md"] = "../docs/area-parameters.md"
        if has_word("name|names|roomsevent|getareaset", combined_text):
            suggestions["area-names.md"] = "../docs/area-names.md"
        if not suggestions.get("area-parameters.md") and not suggestions.get("area-names.md"):
            suggestions["zones-and-areas.md"] = "../docs/zones-and-areas.md"

    # Rain & Protection
    if has_word("rain|weather|precipitation", combined_text):
        suggestions["rain-and-protection.md"] = "../docs/rain-and-protection.md"

    # Obstacle & AI
    if has_word("obstacle|obstacles|ai|animal|avoidance|vision", combined_text):
        suggestions["obstacle-and-ai.md"] = "../docs/obstacle-and-ai.md"

    # Settings
    if has_word("setting|settings|preference|preferences|volume", combined_text):
        suggestions["settings.md"] = "../docs/settings.md"

    # Progress & Statistics
    if has_word("stat|stats|statistics|progress|history|clean_log|lifespan|report", combined_text):
        suggestions["progress-and-statistics.md"] = "../docs/progress-and-statistics.md"

    # General protocol reference
    if (
        any(f.startswith("deebot_client/messages") for f in files)
        or any(f.startswith("deebot_client/events") for f in files)
    ):
        suggestions["protocol-reference.md"] = "../docs/protocol-reference.md"

    # Home Assistant
    if has_word("homeassistant|home-assistant|hass", combined_text):
        suggestions["home-assistant.md"] = "../docs/home-assistant.md"

    return [(k, v) for k, v in sorted(suggestions.items())]


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


def format_pr_entry(pr: dict[str, Any]) -> str:
    """Format a merged pull request with labels, changed files, and suggested doc pages."""
    pr_number = pr["number"]
    title = pr.get("title", "")
    html_url = pr.get("html_url", "")
    merged_at = date_part(pr.get("merged_at"))

    labels = [
        label["name"]
        for label in pr.get("labels", [])
        if isinstance(label, dict) and "name" in label
    ]
    files = get_pr_files(pr_number)
    suggested_docs = suggest_affected_docs(title, labels, files)

    lines = [f"- [#{pr_number} — {title}]({html_url}) (merged {merged_at})"]
    if labels:
        labels_str = ", ".join(f"`{label}`" for label in labels)
        lines.append(f"  - **Labels:** {labels_str}")

    if files:
        if len(files) <= 5:
            files_str = ", ".join(f"`{Path(f).name}`" for f in files)
            lines.append(f"  - **Changed files ({len(files)}):** {files_str}")
        else:
            files_sample = ", ".join(f"`{Path(f).name}`" for f in files[:5])
            lines.append(f"  - **Changed files ({len(files)}):** {files_sample}, ...")

    if suggested_docs:
        docs_str = ", ".join(f"[{name}]({path})" for name, path in suggested_docs)
        lines.append(f"  - **Likely affected docs:** {docs_str}")

    return "\n".join(lines)


def main() -> int:
    state = load_state()
    commits = github_get(f"/repos/{UPSTREAM}/commits?sha={BRANCH}&per_page=30")
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

    sections = [f"\n\n## {datetime.now(timezone.utc).date().isoformat()}"]
    if new_releases:
        sections.append("\n### Releases\n")
        sections.extend(
            f"- [{release.get('name') or release['tag_name']}]({release['html_url']})\n"
            for release in new_releases
        )
    if new_pull_requests:
        sections.append("\n### Merged pull requests\n")
        sections.extend(
            f"{format_pr_entry(pull_request)}\n"
            for pull_request in new_pull_requests
        )
    if new_commits:
        sections.append(f"\n### Commits on `{BRANCH}`\n")
        sections.extend(
            f"- [`{commit['sha'][:7]}`]({commit['html_url']}) — "
            f"{commit['commit']['message'].splitlines()[0]} "
            f"({date_part(commit['commit']['author'].get('date'))})\n"
            for commit in new_commits
        )

    LOG_PATH.write_text(existing + "".join(sections).rstrip() + "\n", encoding="utf-8")
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