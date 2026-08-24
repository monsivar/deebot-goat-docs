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
- merged upstream pull requests
- recent commits on the upstream `dev` branch

New items are written to [the upstream change log](../research/upstream-change-log.md).
The workflow opens or updates a pull request in this repository for review.

## Evidence boundary

The job records upstream metadata only. It does not infer protocol semantics,
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