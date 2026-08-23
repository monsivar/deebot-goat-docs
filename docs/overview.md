# ECOVACS GOAT support overview

This page provides a high-level overview of ECOVACS GOAT mower support in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py), the protocol research documented in this repository, and the relationship with Home Assistant.

Last reviewed: **2026-08-23**

## Purpose

This repository documents three related layers:

```text
ECOVACS GOAT mower
        │
        ▼
ECOVACS protocol
        │
        ▼
deebot_client
        │
        ▼
Home Assistant
```

The goal is to keep these layers clearly separated.

A feature available in the ECOVACS app is not automatically available in `deebot_client`.

Likewise, a capability implemented in `deebot_client` is not automatically exposed in Home Assistant.

---

# Architecture

The typical data path is:

```text
Physical mower
     │
     ▼
ECOVACS firmware
     │
     ▼
ECOVACS cloud / MQTT / P2P protocol
     │
     ▼
commands and messages
     │
     ▼
deebot_client events
     │
     ▼
capability model
     │
     ▼
consumer integration
     │
     ▼
Home Assistant entities
```

For example:

```text
Mower reports statistics
        │
        ▼
onStats
        │
        ▼
StatsEvent
        │
        ▼
CapabilityStats
        │
        ▼
Home Assistant sensor
```

or:

```text
Home Assistant Start mowing
        │
        ▼
deebot_client CleanV2
        │
        ▼
clean_V2
        │
        ▼
GOAT starts mowing
```

---

# What `deebot_client` provides

`deebot_client` is responsible for understanding ECOVACS communication and exposing device functionality through a common Python API.

The main building blocks are:

```text
Commands
Messages
Events
Capabilities
Hardware profiles
```

## Commands

Commands send requests to ECOVACS devices.

Examples:

```text
CleanV2
Charge
GetStats
SetTrueDetect
SetRainDelay
```

## Messages

Messages handle device/cloud updates.

Examples include:

```text
onStats
onRainDelay
onProtectState
onRecognization
```

## Events

Protocol information is converted into normalised Python events.

Examples:

```text
StateEvent
StatsEvent
RainDelayEvent
ProtectStateEvent
AiRecognitionEvent
```

## Capabilities

Capabilities describe which functionality is supported by a particular hardware profile.

For example:

```text
capabilities.clean
capabilities.stats
capabilities.settings
capabilities.charge
```

## Hardware profiles

Each supported ECOVACS model has a hardware profile describing its exposed capabilities.

For GOAT devices, the profile identifies the device as:

```python
DeviceType.MOWER
```

---

# Why hardware profiles matter

A command existing in the library does not automatically mean that every mower can use it.

The hardware profile determines which capabilities are enabled.

Conceptually:

```text
Command implementation exists
          │
          ▼
Hardware profile enables it?
       ┌──┴──┐
       │     │
      no    yes
       │     │
       ▼     ▼
 unavailable exposed capability
```

This is particularly important for GOAT models because hardware and firmware capabilities can differ.

---

# Supported GOAT models

The reviewed upstream client contains dedicated mower profiles for:

| Model                | Hardware ID |
| -------------------- | ----------- |
| GOAT G1              | `5xu9h3`    |
| GOAT A1600 RTK       | `xmp9ds`    |
| GOAT A3000 LiDAR Pro | `51rcxt`    |
| GOAT O500 Panorama   | `300lc5`    |
| GOAT O1200 LiDAR     | `2i0fns`    |

All are represented as:

```text
DeviceType.MOWER
```

Detailed capability differences are documented in:

[Supported models](supported-models.md)

---

# Generic DEEBOT terminology

`deebot_client` originally supported robotic vacuum cleaners and still uses shared terminology such as:

```text
clean
cleaning
cleanings
room
CleanAction
CleanMode
State.CLEANING
```

For a GOAT mower these normally correspond conceptually to:

| Shared client term | GOAT meaning      |
| ------------------ | ----------------- |
| clean              | mow               |
| cleaning           | mowing            |
| cleanings          | mowing operations |
| room/area          | lawn zone/area    |
| `CleanAction`      | mowing action     |
| `CleanMode`        | mowing/area mode  |
| `State.CLEANING`   | mower is mowing   |

The shared Python/protocol names should normally remain unchanged.

User-facing integrations should translate them into mower terminology.

---

# Current core mowing support

The strongest-supported mower functionality currently includes:

```text
start mowing
pause
resume
stop
return to charging station
mower operational state
battery
statistics
maintenance lifespan
```

Basic mowing uses:

```text
CleanV2
```

with actions:

```text
START
PAUSE
RESUME
STOP
```

Return to the dock uses the separate:

```text
Charge
```

command.

See:

[Mowing control](mowing-control.md)

---

# State model

The shared `deebot_client` state model contains:

```text
IDLE
CLEANING
RETURNING
DOCKED
ERROR
PAUSED
```

For GOAT:

```text
CLEANING
```

means:

```text
MOWING
```

A mower-oriented integration should translate these states rather than displaying vacuum terminology.

---

# Zone and area mowing

The generic client implements:

```text
CleanAreaV2
```

and area modes including:

```text
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

Some upstream GOAT hardware profiles expose `CleanAreaV2`.

However, the exact relationship between these generic modes and GOAT lawn zones requires device-specific verification.

One particularly important case is the GOAT O1200.

The physical mower/app supports selected-zone mowing, while its reviewed upstream hardware profile currently does not expose an area command.

This is therefore a known implementation/research gap.

See:

[Zone and area mowing](zones-and-areas.md)

---

# Statistics and current-job progress

Upstream provides common statistics through:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

and commands such as:

```text
GetStats
GetTotalStats
```

GOAT research additionally identified:

```text
mowedArea
```

which is implemented in the progress development branch as:

```text
StatsEvent.mowed_area
```

This allows the consuming integration to calculate current mowing progress where the field semantics are known.

The Home Assistant development work uses:

```text
mowed_area / area × 100
```

for mowing progress on models explicitly declaring support for mowing-job progress.

See:

[Mowing progress and statistics](progress-and-statistics.md)

---

# Estimated mowing duration

The ECOVACS app can display an estimated mowing duration.

In the current O1200 progress implementation, the mower-specific Home Assistant branch interprets:

```text
StatsEvent.time
```

as estimated mowing duration when the hardware capability declares:

```text
mowing_job_progress=True
```

This is intentionally model-specific.

It should not be assumed that `StatsEvent.time` has that meaning for every GOAT or DEEBOT model.

Further cross-model verification is still required.

---

# Common upstream settings

Reviewed GOAT profiles already expose several settings upstream.

Examples include:

```text
advanced mode
border switch
cutting direction
child lock
move-up warning
cross-map border warning
safe protect
TrueDetect
volume
```

These use the shared `CapabilitySettings` model.

See:

[Mower settings](settings.md)

---

# Mower-specific settings under development

Protocol research has identified additional GOAT-specific settings, particularly on the O1200.

Development implementations include:

```text
AI recognition
smart mowing with avoidance / Humanoid AI
narrow passage adaptation
animal protection
rain configuration
lifted-alarm volume
runtime protection state
```

These are implemented in development branches rather than the reviewed upstream baseline.

This distinction is important.

Documentation should always indicate whether a feature is:

```text
Upstream implemented
Fork implemented
Protocol observed
Device tested
Unverified
```

---

# Rain and protection

GOAT rain handling illustrates why configuration and runtime state must remain separate.

Configuration:

```text
RainDelayEvent
├── enabled
└── delay
```

Runtime state:

```text
ProtectStateEvent
├── is_rain_protect
├── is_rain_delay
├── is_anim_protect
├── is_e_stop
├── is_locked
├── is_pin_code
└── is_prepare_data_success
```

Actual rain was observed with:

```text
isRainProtect = 1
isRainDelay   = 0
```

This gives strong evidence for active rain protection.

The exact meaning of every possible protection-state combination remains under investigation.

See:

[Rain and protection](rain-and-protection.md)

---

# AI and obstacle-related features

Several independent controls appear related to recognition, avoidance or navigation:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
Animal protection
```

These should not be merged into one generic "obstacle avoidance" setting.

They are separate ECOVACS protocol concepts.

For several of them, the protocol mapping is known but the exact physical effect and ECOVACS app wording still require systematic correlation.

See:

[Obstacle avoidance and AI](obstacle-and-ai.md)

---

# Home Assistant

GOAT devices can be represented as native Home Assistant:

```text
lawn_mower
```

entities.

The current mower development implementation supports:

```text
start mowing
pause
dock
```

and translates:

```text
State.CLEANING
```

into:

```text
LawnMowerActivity.MOWING
```

The progress branch additionally implements model-gated entities for:

```text
Area mowed
Mowing progress
Estimated mowing duration
```

Other client capabilities can naturally map to Home Assistant platforms such as:

```text
switch
number
select
sensor
binary_sensor
time
```

See:

[Home Assistant integration](home-assistant.md)

---

# Current Home Assistant architecture

A desirable long-term architecture is:

```text
lawn_mower
    │
    ├── start
    ├── pause
    └── dock

sensors
    │
    ├── battery
    ├── area mowed
    ├── progress
    ├── estimated duration
    └── maintenance

configuration
    │
    ├── obstacle/AI settings
    ├── cutting direction
    ├── rain protection
    ├── animal protection
    └── mower-specific settings

runtime status
    │
    ├── rain protection active
    ├── animal protection active
    ├── emergency stop
    └── other mower protection states
```

Only verified capabilities should be exposed.

---

# Current major research gaps

Important areas still requiring protocol or physical-device work include:

```text
O1200 zone command
zone names and metadata
cutting height
mowing speed
mowing efficiency/mode
AI/app-setting correlation
physical effects of AI settings
complete rain-delay lifecycle
animal-protection behaviour
mower scheduling
GOAT map support
cross-model verification
```

These gaps are documented in:

[Known limitations](known-limitations.md)

---

# Evidence-driven development

This project follows an evidence-based approach.

The preferred workflow is:

```text
Observe ECOVACS app behaviour
          │
          ▼
Capture protocol traffic
          │
          ▼
Identify command/message
          │
          ▼
Understand payload
          │
          ▼
Implement event/command
          │
          ▼
Add capability
          │
          ▼
Add automated tests
          │
          ▼
Verify physical mower
          │
          ▼
Expose in integration
```

The exact order may vary, but implementation should not rely solely on guessing from command names.

---

# Evidence categories

Documentation uses several evidence categories.

## Upstream implemented

The feature exists in the current upstream `DeebotUniverse/client.py`.

## Fork implemented

The feature exists in a development branch but is not yet part of reviewed upstream.

## Python tested

Automated tests verify parser, command or capability behaviour.

## Protocol observed

The relevant payload or message has been seen in real GOAT communication.

## Device tested

Physical mower behaviour has been exercised.

## App observed

The ECOVACS app exposes or reports the feature.

## Unverified

Some important part of the interpretation remains unknown.

A feature can have multiple evidence categories.

---

# Why this distinction matters

Consider a hypothetical field:

```text
isSomething
```

Finding it in a protocol payload proves:

```text
field exists
```

It does not necessarily prove:

```text
what physical condition it means
```

Likewise:

```text
SetSomething(True)
```

passing a unit test proves:

```text
client creates expected payload
```

but not necessarily:

```text
physical mower behaves correctly
```

The documentation therefore tries to keep implementation confidence separate from semantic confidence.

---

# Recommended reading paths

## I want to know which GOAT models are represented

Read:

[Supported models](supported-models.md)

---

## I want to understand the Python capability architecture

Read:

[Capability architecture](capabilities.md)

---

## I want to start, pause or dock a mower

Read:

[Mowing control](mowing-control.md)

---

## I want to understand lawn zones

Read:

[Zone and area mowing](zones-and-areas.md)

---

## I want mowing progress or statistics

Read:

[Mowing progress and statistics](progress-and-statistics.md)

---

## I want to understand mower settings

Start with:

[Mower settings](settings.md)

Then use:

[Obstacle avoidance and AI](obstacle-and-ai.md)

and:

[Rain and protection](rain-and-protection.md)

for detailed behaviour.

---

## I am analysing ECOVACS traffic

Use:

[Protocol reference](protocol-reference.md)

---

## I need to know how confident a feature is

Use:

[Testing status](testing-status.md)

---

## I need to know what is missing

Use:

[Known limitations](known-limitations.md)

---

## I am working on Home Assistant

Use:

[Home Assistant integration](home-assistant.md)

---

# Documentation map

The current documentation is organised approximately as follows:

```text
README.md
│
└── docs/
    │
    ├── overview.md
    │
    ├── supported-models.md
    │
    ├── capabilities.md
    │
    ├── mowing-control.md
    │
    ├── zones-and-areas.md
    │
    ├── progress-and-statistics.md
    │
    ├── settings.md
    │
    ├── rain-and-protection.md
    │
    ├── obstacle-and-ai.md
    │
    ├── protocol-reference.md
    │
    ├── home-assistant.md
    │
    ├── testing-status.md
    │
    └── known-limitations.md
```

---

# Documentation roles

| File                         | Main purpose                             |
| ---------------------------- | ---------------------------------------- |
| `overview.md`                | Architecture and reading guide           |
| `supported-models.md`        | GOAT model and hardware-profile coverage |
| `capabilities.md`            | `deebot_client` capability architecture  |
| `mowing-control.md`          | Start, pause, resume, stop and dock      |
| `zones-and-areas.md`         | Selected-zone/area mowing                |
| `progress-and-statistics.md` | Current and cumulative mowing data       |
| `settings.md`                | Master mower settings reference          |
| `rain-and-protection.md`     | Rain and runtime protection behaviour    |
| `obstacle-and-ai.md`         | AI, recognition and avoidance settings   |
| `protocol-reference.md`      | Wire/Python command reference            |
| `home-assistant.md`          | Home Assistant entity design             |
| `testing-status.md`          | Evidence and verification matrix         |
| `known-limitations.md`       | Current gaps and unresolved behaviour    |

---

# Protocol research

Protocol research should generally preserve:

```text
exact wire name
exact field name
model
firmware
direction
relevant values
observed behaviour
```

For example:

```text
wire: onProtectState
model: O1200
condition: actual rain
isRainProtect: 1
isRainDelay: 0
```

This is substantially more useful than documenting only:

```text
rain works
```

because it allows other developers to reproduce and extend the implementation.

---

# Security and privacy

Do not commit raw ECOVACS logs without sanitisation.

Protocol logs may contain sensitive information such as:

```text
account IDs
device IDs
serial numbers
authentication data
cloud identifiers
Wi-Fi information
location information
map data
```

Documentation examples should contain only the minimum fields required to explain the protocol behaviour.

Prefer:

```json
{
  "enable": 1,
  "delay": 180
}
```

rather than a complete raw ECOVACS message envelope.

---

# Model-specific findings

A finding made on one mower should be labelled with that mower.

For example:

```text
Verified on GOAT O1200 LiDAR
```

is preferable to:

```text
GOAT behaves this way
```

unless multiple models have been verified.

This is especially important for mower-specific functionality such as:

```text
AI features
navigation options
rain behaviour
zone handling
accessories
```

---

# Firmware-specific findings

Where practical, protocol captures should also record firmware version.

Firmware changes may alter:

```text
command support
field names
payload structure
allowed values
state transitions
cloud requirements
```

A previously verified observation should not automatically be considered permanent across all firmware releases.

---

# Upstream contributions

A well-prepared GOAT feature contribution to `deebot_client` should ideally include:

```text
protocol evidence
        │
        ▼
normalised event
        │
        ▼
GET / SET / execute command
        │
        ▼
capability wiring
        │
        ▼
hardware-profile scope
        │
        ▼
tests
```

The feature should only be enabled for hardware profiles supported by available evidence.

---

# Home Assistant contributions

Once the `deebot_client` capability is stable, Home Assistant work should generally include:

```text
entity description
entity type
translation
icon where appropriate
tests
model/capability gating
```

Home Assistant should normally avoid embedding ECOVACS-specific payload parsing.

That logic belongs in `deebot_client`.

---

# Current project direction

The current documentation and development effort has established a strong baseline for:

```text
GOAT mower identification
mowing lifecycle
return-to-dock
statistics
job progress
rain handling
protection state
several AI/navigation settings
Home Assistant mower representation
```

The next major gains are expected from systematically mapping the remaining mower-specific app settings and zone/map behaviour.

The most useful future captures are likely to focus on one unknown feature at a time.

---

# Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mowing control](mowing-control.md)
* [Zone and area mowing](zones-and-areas.md)
* [Mowing progress and statistics](progress-and-statistics.md)
* [Mower settings](settings.md)
* [Rain and protection](rain-and-protection.md)
* [Obstacle avoidance and AI](obstacle-and-ai.md)
* [Protocol reference](protocol-reference.md)
* [Home Assistant integration](home-assistant.md)
* [Testing status](testing-status.md)
* [Known limitations](known-limitations.md)
