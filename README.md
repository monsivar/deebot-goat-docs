# ECOVACS GOAT mower documentation

Community-driven technical documentation and protocol research for ECOVACS GOAT robotic lawn mowers, with a focus on [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py), commonly used through the `deebot-client` Python library, and its integration with Home Assistant.

This repository exists because GOAT support, like much of the broader `deebot-client` ecosystem, is developed through community reverse engineering, testing, experimentation and contributions.

The goal is to collect that knowledge in one place so it can be reproduced, corrected and extended by others.

This repository documents:

- mower capabilities already implemented upstream
- GOAT-specific functionality implemented in development branches
- protocol behaviour observed from real mower communication
- physical-device testing
- Home Assistant integration work
- known limitations
- unresolved protocol questions
- planned areas for further community research

> [!IMPORTANT]
> This is an **unofficial, community-driven project**.
>
> It is **not affiliated with or endorsed by ECOVACS, DeebotUniverse or OpenAI**.
>
> ECOVACS does not provide an official public API or protocol specification for the functionality documented here. Much of the underlying work therefore depends on community reverse engineering and observation.
>
> Firmware, cloud APIs, app behaviour and device protocols may change without notice. Behaviour may also differ between mower models, firmware versions, app versions and regions.

> [!CAUTION]
> Parts of this documentation, protocol analysis and related development work have been created with assistance from **ChatGPT and Codex by OpenAI**.
>
> AI-assisted work can contain errors, incorrect assumptions, incomplete interpretations, hallucinations or misunderstandings of source code and ECOVACS protocol behaviour.
>
> This documentation should therefore **not be treated as an authoritative protocol specification**.
>
> Important findings should be verified against:
>
> - the actual `deebot-client` source code
> - automated tests
> - real ECOVACS protocol traffic
> - behaviour in the official ECOVACS app
> - physical mower behaviour
>
> Corrections and independently reproduced observations are very welcome.

## Community-driven development

The development model behind this documentation follows the same general spirit as the broader DeebotUniverse ecosystem:

```text
Someone discovers a problem or feature
              │
              ▼
Community investigates
              │
              ▼
Protocol behaviour is captured
              │
              ▼
Implementation is proposed
              │
              ▼
Tests and real devices provide evidence
              │
              ▼
Others review, correct and improve it
```

There is no official ECOVACS engineering support behind this work.

Progress depends on people contributing:

- time
- protocol observations
- logs
- access to different mower models
- testing
- code
- documentation
- review
- corrections

A feature being undocumented does not necessarily mean the mower does not support it.

Likewise, a feature being documented here does not guarantee that the interpretation is correct on every mower.

## Start here

For a high-level introduction to the architecture and documentation:

**[ECOVACS GOAT support overview](docs/overview.md)**

The overall stack documented here is:

```text
ECOVACS GOAT mower
        │
        ▼
Firmware / cloud / MQTT / P2P
        │
        ▼
ECOVACS protocol
        │
        ▼
deebot-client
        │
        ▼
Consumer integrations
        │
        ▼
Home Assistant
```

## Documentation

| Topic | Documentation |
| --- | --- |
| Architecture and reading guide | [Overview](docs/overview.md) |
| Supported GOAT models | [Supported models](docs/supported-models.md) |
| `deebot-client` capability architecture | [Capabilities](docs/capabilities.md) |
| Start, pause, resume, stop and dock | [Mowing control](docs/mowing-control.md) |
| Lawn zones and area mowing | [Zones and areas](docs/zones-and-areas.md) |
| Job progress and mowing statistics | [Progress and statistics](docs/progress-and-statistics.md) |
| Mower settings | [Settings](docs/settings.md) |
| O1200 zone-specific height, cut mode, obstacle height and angle | [O1200 area parameters](docs/area-parameters.md) |
| Rain behaviour and protection states | [Rain and protection](docs/rain-and-protection.md) |
| Obstacle avoidance and AI settings | [Obstacle and AI](docs/obstacle-and-ai.md) |
| Commands, messages and protocol fields | [Protocol reference](docs/protocol-reference.md) |
| Home Assistant representation | [Home Assistant](docs/home-assistant.md) |
| Verification and test status | [Testing status](docs/testing-status.md) |
| Unsupported and unresolved functionality | [Known limitations](docs/known-limitations.md) |

## Protocol research

New, incomplete or uncertain findings are recorded separately from the main reference documentation:

**[GOAT protocol observations](research/protocol-observations.md)**

The research log is intentionally allowed to contain:

- hypotheses
- incomplete mappings
- open questions
- planned experiments
- unresolved protocol fields
- device-specific observations
- possible interpretations that still need confirmation

This is deliberate.

We would rather document:

```text
Observed:
isRainProtect = 1
isRainDelay   = 0

Interpretation:
active rain protection confirmed

Unknown:
meaning of isRainDelay = 1
```

than silently turn an assumption into a supposed protocol fact.

Once a finding has sufficient evidence, it can be promoted into the relevant page under `docs/`.

## Evidence levels

The documentation distinguishes between several types of evidence.

| Status | Meaning |
| --- | --- |
| **Upstream implemented** | Present in current `DeebotUniverse/client.py` |
| **Fork implemented** | Implemented in a development branch or fork |
| **Python tested** | Covered by automated tests |
| **Protocol observed** | Seen in real GOAT communication |
| **Device tested** | Physical mower behaviour verified |
| **App observed** | Behaviour or value observed in the ECOVACS app |
| **Unverified** | Interpretation still requires evidence |

A feature can have several statuses.

For example:

```text
Fork implemented
+
Python tested
+
Protocol observed
```

does **not** necessarily mean:

```text
physical behaviour completely understood
```

Likewise:

```text
field observed
```

does not necessarily mean:

```text
field semantics understood
```

See [Testing status](docs/testing-status.md) for the current evidence matrix.

## GOAT models represented upstream

The reviewed upstream client contains dedicated mower hardware profiles for:

| Model | Hardware ID |
| --- | --- |
| GOAT G1 | `5xu9h3` |
| GOAT A1600 RTK | `xmp9ds` |
| GOAT A3000 LiDAR Pro | `51rcxt` |
| GOAT O500 Panorama | `300lc5` |
| GOAT O1200 LiDAR | `2i0fns` |

All are represented by:

```python
DeviceType.MOWER
```

A hardware profile describes what `deebot-client` currently exposes for that model.

It is **not necessarily a complete specification of everything the physical mower can do**.

For example, a feature may:

1. exist on the physical mower,
2. be available in the official ECOVACS app,
3. exist in the protocol,
4. but not yet be represented by the client hardware profile.

See [Supported models](docs/supported-models.md).

## Current well-understood functionality

The strongest current implementation and test coverage includes:

- GOAT mower identification
- battery and availability
- start mowing
- pause
- resume
- stop
- return to charging station
- mower operational state
- mowing statistics
- total mowing statistics
- maintenance/lifespan information
- common mower settings
- O1200 zone-specific area-parameter protocol (`mowHeightLevel`, `cutMode`, `obstacleHeight`, `angle`)
- O1200 current-job progress
- O1200 rain configuration
- active rain-protection state

Several additional mower-specific settings have also been mapped in development branches.

See [Mower settings](docs/settings.md).

## Current research priorities

Important areas still requiring additional work include:

- mapping O1200 `mowHeightLevel` values to physical/app cutting heights
- decoding O1200 `cutMode` values and their app/user-facing meaning
- determining the exact meaning/unit of O1200 `obstacleHeight`
- clarifying the relationship between zone-specific `angle` and global `cut_direction`
- mowing speed
- O1200 selected-zone start command and zone metadata
- zone names and metadata
- multi-zone behaviour
- exact ECOVACS app mapping of AI settings
- physical effect of each avoidance/AI setting
- complete post-rain delay lifecycle
- animal-protection runtime behaviour
- mower scheduling
- GOAT-specific map semantics
- cross-model verification

See:

- [Known limitations](docs/known-limitations.md)
- [GOAT protocol observations](research/protocol-observations.md)

## Shared DEEBOT terminology

`deebot-client` uses a common abstraction for several ECOVACS product types.

Because much of the project historically revolves around robotic vacuum cleaners, mower support still contains generic names such as:

```text
clean
cleaning
cleanings
room
CleanAction
CleanMode
State.CLEANING
```

For GOAT devices these often mean:

| Shared term | GOAT interpretation |
| --- | --- |
| clean | mow |
| cleaning | mowing |
| cleanings | mowing operations |
| room / area | lawn zone / area |
| `CleanAction` | mowing action |
| `CleanMode` | mowing/area mode |
| `State.CLEANING` | mowing |

Protocol and Python names should normally remain unchanged where they are part of the shared client API.

User-facing integrations should use mower terminology.

For example:

```text
deebot-client:
State.CLEANING
       │
       ▼
Home Assistant:
MOWING
```

## Home Assistant

GOAT devices can be represented as native Home Assistant:

```text
lawn_mower
```

entities.

Current mower development work includes:

- start mowing
- pause
- dock
- mower-specific activity mapping
- mower-oriented statistics labels

O1200 progress development additionally includes:

- area mowed
- mowing progress percentage
- estimated mowing duration

Additional mower configuration and runtime state can eventually be exposed through appropriate Home Assistant entity types such as:

```text
switch
number
select
sensor
binary_sensor
time
```

once the corresponding `deebot-client` capability and semantics are sufficiently understood.

See [Home Assistant integration](docs/home-assistant.md).

## Development approach

New mower functionality should ideally follow an evidence-driven process:

```text
Observe app/device behaviour
          │
          ▼
Capture protocol traffic
          │
          ▼
Identify command/message
          │
          ▼
Understand fields and values
          │
          ▼
Implement in deebot-client
          │
          ▼
Add automated tests
          │
          ▼
Enable hardware capability
          │
          ▼
Verify physical mower
          │
          ▼
Expose in Home Assistant
          │
          ▼
Community review and correction
```

Not every feature will follow exactly this order.

The important part is that the documentation states which stages have actually been completed.

## Contributing observations

Protocol research is especially useful when only **one variable is changed at a time**.

For example, when mapping the physical meaning of an already identified field such as `mowHeightLevel`:

```text
record current app height + protocol state
              │
              ▼
change cutting height one step
              │
              ▼
capture onAreaParameter / getAreaParameter
              │
              ▼
record mowHeightLevel
              │
              ▼
repeat across available height choices
```

This distinction matters: the O1200 cutting-height **protocol field is already mapped**; the remaining task is to map its raw levels to the exact app/physical height semantics.

Useful contributions include:

- captures from mower models not currently available to other contributors
- firmware-specific observations
- ECOVACS app setting → wire-command mappings
- confirmation that an existing finding also applies to another model
- evidence disproving an existing assumption
- automated tests
- Home Assistant integration improvements

Discovering that something in this repository is **wrong** is a valuable contribution.

## Source projects

The primary Python client documented here is:

[`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py)

The client is a community-maintained reverse-engineering project and forms the technical foundation that makes the GOAT work documented here possible.

This documentation repository does not replace the upstream project and should not be considered an official fork of its documentation.

Instead, it provides additional mower-specific:

- technical documentation
- research notes
- protocol observations
- implementation experiments
- integration guidance

## Acknowledgements

This project would not exist without the work already done by the DeebotUniverse community.

A special thank you to **Robert Resch** and the maintainers and contributors of [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py) for maintaining and developing the `deebot-client` library.

The upstream project is maintained by volunteers in their spare time, and much of its functionality has been made possible through years of community reverse engineering, code contributions, device testing and user feedback.

The GOAT mower work documented here builds directly on that foundation.

Thank you also to:

- the wider **DeebotUniverse community**
- everyone who has contributed code to `deebot-client`
- users who have submitted useful protocol observations and logs
- people testing new ECOVACS models and firmware
- the developers of the projects on which the Deebot ecosystem historically builds
- Home Assistant contributors maintaining and reviewing the ECOVACS integration
- everyone willing to test incomplete features and report reproducible results

The upstream project itself also acknowledges earlier projects including:

- [`Deebotozmo`](https://github.com/And3rsL/Deebotozmo)
- [`sucks`](https://github.com/wpietri/sucks)

Open-source reverse engineering tends to be cumulative: each generation builds on discoveries made by the previous one.

This repository is another small part of that chain.

## AI assistance

AI tools are being used as assistants in parts of this project.

These include:

- **ChatGPT by OpenAI**
- **Codex by OpenAI**

They have been used for activities such as:

- source-code analysis
- comparing protocol observations with implementation
- drafting documentation
- suggesting tests
- assisting with code changes
- structuring research findings

AI output is **not considered evidence by itself**.

For example:

```text
ChatGPT says a field probably means X
```

is not sufficient evidence to document:

```text
field definitely means X
```

Evidence should instead come from sources such as:

```text
source code
tests
real protocol traffic
official app behaviour
physical mower behaviour
independent reproduction
```

This is particularly important for reverse-engineered protocols where incomplete context can make a plausible interpretation incorrect.

## Security and privacy

Raw ECOVACS logs should **not** be committed directly to this repository.

Before publishing protocol examples, remove or replace sensitive information including:

- account identifiers
- authentication tokens
- device IDs
- serial numbers
- Wi-Fi information
- cloud credentials
- precise location information
- private map data
- personally identifiable information

Prefer small sanitised examples containing only the fields required to explain the protocol.

For example:

```json
{
  "enable": 1,
  "delay": 180
}
```

is preferable to publishing a complete raw MQTT or cloud message.

## Repository structure

```text
deebot-goat-docs/
│
├── README.md
│
├── docs/
│   ├── overview.md
│   ├── supported-models.md
│   ├── capabilities.md
│   ├── mowing-control.md
│   ├── zones-and-areas.md
│   ├── progress-and-statistics.md
│   ├── settings.md
│   ├── area-parameters.md
│   ├── rain-and-protection.md
│   ├── obstacle-and-ai.md
│   ├── protocol-reference.md
│   ├── home-assistant.md
│   ├── testing-status.md
│   └── known-limitations.md
│
└── research/
    └── protocol-observations.md
```

## Corrections and contributions

GOAT functionality can vary by:

- model
- firmware
- region
- app version
- cloud-side ECOVACS changes

Corrections and reproducible observations are therefore particularly valuable.

When documenting new behaviour, include as much relevant context as practical:

- mower model
- hardware ID
- firmware version
- app version if relevant
- exact user action
- exact protocol command/message
- sanitised relevant fields
- physical mower behaviour
- implementation branch
- automated test coverage

Most importantly:

**distinguish confirmed observations from hypotheses.**

Because parts of this repository have been produced with AI assistance and reverse-engineered from undocumented behaviour, corrections to existing interpretations are not merely welcome — they are an expected and important part of the project.
