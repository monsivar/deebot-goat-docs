# Upstream documentation automation

The repository includes a small GitHub Actions job for tracking changes in
[`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py).

## What runs automatically

The workflow in `.github/workflows/upstream-docs.yml` runs:

- once per day
- on manual dispatch
- on `repository_dispatch` events named `upstream-release` or `upstream-pr-merged`

It collects:

- releases from the upstream repository
- merged upstream pull requests (including PR labels, modified files, and heuristic mapping to likely affected documentation pages)
- recent commits on the upstream `dev` branch

New items are written to [the upstream change log](../research/upstream-change-log.md).
The workflow opens or updates a pull request in this repository for review.

## Enriched metadata and documentation mapping

For each merged pull request, the synchronization script collects:

1. **Pull request labels:** categorizing the type of change (e.g. `mower`, `map`, `model`, `dependencies`).
2. **Changed files:** summarizing key modified paths across Python, Rust, and test suites.
3. **Suggested documentation pages:** mapping modified code paths and keywords to the relevant pages in `docs/docs/`:
   - `src/map/*`, `deebot_client/map.py` $\rightarrow$ [`map.md`](map.md)
   - `deebot_client/capabilities.py` $\rightarrow$ [`capabilities.md`](capabilities.md)
   - `deebot_client/hardware/*` $\rightarrow$ [`supported-models.md`](supported-models.md)
   - `deebot_client/commands/*` $\rightarrow$ [`command-routing.md`](command-routing.md)
   - `rain` / `weather` $\rightarrow$ [`rain-and-protection.md`](rain-and-protection.md)
   - `area` / `room` / `zone` $\rightarrow$ [`zones-and-areas.md`](zones-and-areas.md), [`area-parameters.md`](area-parameters.md), [`area-names.md`](area-names.md)
   - `obstacle` / `ai` / `animal` $\rightarrow$ [`obstacle-and-ai.md`](obstacle-and-ai.md)
   - `settings` / `preference` $\rightarrow$ [`settings.md`](settings.md), [`o1200-global-settings.md`](o1200-global-settings.md)
   - `stat` / `progress` / `history` $\rightarrow$ [`progress-and-statistics.md`](progress-and-statistics.md)
   - `clean` / `mow` $\rightarrow$ [`mowing-control.md`](mowing-control.md)
   - `messages/`, `events/` $\rightarrow$ [`protocol-reference.md`](protocol-reference.md)
   - `homeassistant` $\rightarrow$ [`home-assistant.md`](home-assistant.md)

## Evidence boundary

The job records upstream metadata and suggestions only. It does not infer protocol semantics,
change evidence levels or silently modify the reference documentation. A human
must review each generated pull request and promote verified findings into the
appropriate page under `docs/`.

## Immediate upstream events

The daily schedule is sufficient for normal operation. Immediate processing of
an upstream release or merged pull request requires a small GitHub App or webhook
that sends a `repository_dispatch` event to this repository. The event payload is
optional because the collector queries the upstream API directly.

The target repository token must have permission to dispatch events, and the
workflow token must be allowed to create pull requests.