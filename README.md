# ECOVACS GOAT mower documentation

Unofficial technical documentation for ECOVACS GOAT robotic lawn mower support in [DeebotUniverse/client.py](https://github.com/DeebotUniverse/client.py).

This repository collects information about mower capabilities, commands, events, settings, protocol behaviour, model differences, and integration considerations discovered through source-code analysis and testing with real ECOVACS GOAT devices.

> [!IMPORTANT]
> This is a community-maintained project and is **not affiliated with or endorsed by ECOVACS or DeebotUniverse**.
>
> ECOVACS firmware, cloud APIs and device protocols may change without notice. Behaviour can also differ between mower models, firmware versions and regions.

## Purpose

The goal of this repository is to make the GOAT mower support in `deebot_client` easier to understand, test and extend.

The documentation aims to answer questions such as:

* Which ECOVACS GOAT models are currently represented in `deebot_client`?
* Which capabilities are implemented for each model?
* Which mower commands and events have been identified?
* How do start, pause, resume, stop and return-to-station operations work?
* How is zone or area mowing represented?
* Which progress and statistics values are available?
* Which mower settings can be read or changed?
* How are rain protection, obstacle avoidance and AI-related settings represented?
* Which functionality has been confirmed on a real mower?
* Which functionality exists only in development branches or has only been observed in the protocol?
* How can these capabilities be exposed by integrations such as Home Assistant?

## Evidence levels

Information in this repository should clearly indicate how well a feature has been verified.

| Status                   | Meaning                                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **Upstream implemented** | The feature is present in the current `DeebotUniverse/client.py` source tree.                               |
| **Fork implemented**     | The feature has been implemented in a development branch or fork but is not necessarily available upstream. |
| **Device tested**        | The behaviour has been tested against a real ECOVACS GOAT mower.                                            |
| **Protocol observed**    | Relevant messages or fields have been observed in communication with the mower or ECOVACS app.              |
| **Unverified**           | The interpretation is incomplete or still requires testing.                                                 |

A feature can have more than one status. For example, a command may be both **Fork implemented** and **Device tested**.

## Mower models currently represented upstream

The current `DeebotUniverse/client.py` source contains dedicated mower hardware profiles for at least the following models:

| Model                        | Hardware identifier |
| ---------------------------- | ------------------- |
| ECOVACS GOAT G1              | `5xu9h3`            |
| ECOVACS GOAT A1600 RTK       | `xmp9ds`            |
| ECOVACS GOAT A3000 LiDAR Pro | `51rcxt`            |
| ECOVACS GOAT O500 Panorama   | `300lc5`            |
| ECOVACS GOAT O1200 LiDAR     | `2i0fns`            |

These hardware profiles should be treated as the primary source for determining which capabilities `deebot_client` currently exposes for each model.

Model support does **not** necessarily mean that every mower feature offered by the ECOVACS app is already supported.

## Documentation scope

The repository is intended to cover the following areas.

### Mower capabilities

Documentation of the mower-specific capability model in `deebot_client`, including:

* mower device type
* battery and availability
* charging and return to station
* mowing actions
* zone or area mowing
* mower state
* errors
* statistics
* consumable lifetime information
* network information
* mower settings

### Mowing control

Known behaviour for:

* start
* pause
* resume
* stop
* return to station
* whole-lawn mowing
* zone or area mowing

Where possible, the documentation will distinguish between the user-facing ECOVACS app action and the underlying `deebot_client` command or event.

### Progress and statistics

Known mower progress and statistics information, including where available:

* mowing progress
* current job information
* completed or remaining work
* estimated job duration
* mowing statistics
* total statistics

### Mower settings

Settings identified in source code or mower protocol traffic, including areas such as:

* border or edge behaviour
* cutting direction
* mowing efficiency and related mowing behaviour
* cutting height
* rain behaviour and rain delay
* obstacle avoidance
* AI or recognition features
* animal protection
* narrow-area adaptation
* safety and protection options
* sound and volume
* other global mower settings

Not every setting is available on every GOAT model.

### Protocol research

Where useful, the repository will document:

* ECOVACS command names
* request payloads
* response payloads
* push messages
* fields and value mappings
* observed differences between models or firmware versions

Protocol examples should be sanitised before publication.

## Planned documentation structure

```text
docs/
├── overview.md
├── supported-models.md
├── capabilities.md
├── mowing-control.md
├── zones-and-areas.md
├── progress-and-statistics.md
├── settings.md
├── rain-and-protection.md
├── obstacle-and-ai.md
├── protocol-reference.md
├── home-assistant.md
├── testing-status.md
└── known-limitations.md

research/
└── protocol-observations.md
```

The structure may evolve as more mower functionality is understood.

## Source of information

Documentation in this repository may be based on several sources:

1. The current source code in `DeebotUniverse/client.py`.
2. Development branches containing proposed mower support.
3. Tests included with mower-related implementations.
4. Behaviour observed on real ECOVACS GOAT devices.
5. Sanitised communication logs between the ECOVACS app, cloud services and mower.
6. Comparison of behaviour across mower models and firmware versions.

Where possible, documentation should reference the relevant `deebot_client` command, event, message parser or hardware profile.

## Upstream project

The Python client documented here is maintained by the DeebotUniverse project:

https://github.com/DeebotUniverse/client.py

This repository does not replace the upstream project's own documentation. Its purpose is to provide additional mower-specific technical documentation and research.

## Security and privacy

Raw logs should **not** be committed directly to this repository.

Before publishing protocol examples, remove or replace sensitive or device-specific information such as:

* account identifiers
* authentication tokens
* device serial numbers
* device IDs
* Wi-Fi information
* cloud credentials
* precise location information
* other personally identifiable data

Prefer small, sanitised examples containing only the fields required to explain the protocol.

## Contributions and corrections

GOAT functionality can vary by model, firmware and region.

Corrections, additional model observations and reproducible test results are therefore valuable. When documenting newly discovered behaviour, include enough context to distinguish confirmed behaviour from assumptions or incomplete protocol interpretation.
