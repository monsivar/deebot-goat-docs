# ECOVACS GOAT support overview

This page provides a high-level overview of ECOVACS GOAT mower support in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py), the protocol research documented in this repository, and the relationship with Home Assistant.

Last reviewed: **2026-08-24**

## Purpose

This repository documents several related layers:

```text
ECOVACS GOAT mower
        │
        ▼
ECOVACS app / firmware
        │
        ▼
ECOVACS cloud / MQTT / P2P protocol
        │
        ▼
deebot_client
        │
        ▼
consumer integrations
        │
        ▼
Home Assistant
```

The goal is to keep these layers clearly separated.

A feature available in the ECOVACS app is not automatically available in `deebot_client`.

Likewise, a capability implemented in `deebot_client` is not automatically exposed in Home Assistant.

---

# Evidence-driven architecture

The preferred development flow is:

```text
Observe app/device behaviour
          │
          ▼
Capture protocol traffic
          │
          ▼
Identify command/message and fields
          │
          ▼
Implement command/event in deebot_client
          │
          ▼
Add hardware capability
          │
          ▼
Add automated tests
          │
          ▼
Verify physical behaviour
          │
          ▼
Expose through integrations
```

Not every feature reaches all stages at the same time.

This documentation therefore distinguishes:

```text
Upstream implemented
Fork implemented
Python tested
Protocol observed
Device tested
App observed
Derived
Unverified
```

---

# Main `deebot_client` building blocks

`deebot_client` represents ECOVACS functionality using:

```text
Commands
Messages
Events
Capabilities
Device-specific command routing
Hardware profiles
```

## Commands

Commands request state changes or actions.

Examples:

```text
CleanV2
Charge
GetStats
GetAreaParameter
SetAreaParameter
SetRainDelay
```

## Messages

Messages handle device/cloud updates.

Examples:

```text
onStats
onAreaParameter
onRainDelay
onProtectState
onRecognization
```

## Events

Wire data is normalised into Python events.

Examples:

```text
StateEvent
StatsEvent
AreaParameterEvent
RainDelayEvent
ProtectStateEvent
AiRecognitionEvent
```

## Capabilities

Capabilities describe what a hardware profile exposes.

Examples:

```text
capabilities.clean
capabilities.stats
capabilities.settings
capabilities.charge
```

## Hardware profiles

Each supported model has a hardware profile.

GOAT devices are identified as:

```python
DeviceType.MOWER
```

---


# Device-specific command routing

An important architecture limitation appears when ECOVACS reuses the same wire command name across device families but the devices require different Python implementations.

PR #1772 introduces:

```text
Capabilities.get_command(name)
```

and a per-device command lookup derived from the hardware capability tree.

Conceptually:

```text
wire name
   │
   ▼
device capabilities
   │
   ▼
device-specific command class
   │
   └── fallback to global registry when appropriate
```

This is relevant to GOAT mower work such as same-name `clean` implementations without making the command name globally unique.

The PR also makes MQTT P2P routing device-aware:

```text
request (q)  → receiver device
response (p) → sender device
```

PR #1772 is still development work and does not itself change which mowing command a GOAT hardware profile uses.

See:

[Device-specific command routing](command-routing.md)

---

# Supported GOAT models

The reviewed upstream client contains dedicated profiles for:

| Model | Hardware ID |
| --- | --- |
| GOAT G1 | `5xu9h3` |
| GOAT A1600 RTK | `xmp9ds` |
| GOAT A3000 LiDAR Pro | `51rcxt` |
| GOAT O500 Panorama | `300lc5` |
| GOAT O1200 LiDAR | `2i0fns` |

All are represented as:

```text
DeviceType.MOWER
```

Detailed capability differences:

[Supported models](supported-models.md)

---

# Shared DEEBOT terminology

The client was originally designed around vacuum robots and still uses terms such as:

```text
clean
cleaning
cleanings
room
CleanAction
CleanMode
State.CLEANING
```

For GOAT these normally correspond conceptually to:

| Shared term | GOAT interpretation |
| --- | --- |
| clean | mow |
| cleaning | mowing |
| cleanings | mowing operations |
| room / area | lawn zone / area |
| `CleanAction` | mowing action |
| `CleanMode` | mowing/area mode |
| `State.CLEANING` | mowing |

Protocol and Python names should generally remain stable.

User-facing integrations should use mower terminology.

---

# Core mowing lifecycle

The strongest-supported mower lifecycle includes:

```text
START
PAUSE
RESUME
STOP
RETURN TO DOCK
```

General mowing uses:

```text
CleanV2
```

Return to station uses:

```text
Charge
```

The shared state model includes:

```text
IDLE
CLEANING
PAUSED
RETURNING
DOCKED
ERROR
```

For a mower:

```text
State.CLEANING
```

should be displayed as:

```text
MOWING
```

See:

[Mowing control](mowing-control.md)

---

# Zone mowing and zone settings are separate concepts

GOAT zone functionality contains at least two distinct areas of protocol work.

## 1. Starting a selected-zone mowing job

The generic client supports:

```text
CleanAreaV2
```

with modes including:

```text
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

Four reviewed upstream GOAT profiles expose `CleanAreaV2`.

The reviewed upstream O1200 profile does not.

Physical/app selected-zone mowing exists on the O1200, so this remains a client/protocol integration gap.

## 2. Configuring parameters for a known zone

O1200 protocol research identified a separate area-parameter family:

```text
getAreaParameter
setAreaParameter
onAreaParameter
```

with one record per:

```text
areaID
```

containing:

```text
mowHeightLevel
cutMode
obstacleHeight
angle
```

These zone settings are implemented in the development work represented by:

- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)

Conceptually:

```text
Zone identity
   │
   └── areaID
        │
        ├── mowing height
        ├── cut mode
        ├── obstacle-height parameter
        └── mowing angle
```

This is important:

> Mapping `areaID` and area parameters does not by itself prove that the same API is the selected-zone start command.

The two functions should be documented separately.

See:

- [Zone and area mowing](zones-and-areas.md)
- [O1200 area parameters](area-parameters.md)

---

# O1200 area names and IDs

PR #1774 adds a dedicated mower-area metadata capability:

```text
CapabilityClean.areas
```

using:

```text
GetAreaSet
RoomsEvent
Room
```

The command:

```text
getAreaSet
```

requests:

```json
{"mid": "1", "aid": "0", "type": "ar"}
```

and decodes the compressed `subsets` response into area IDs and names.

Real O1200 validation on firmware `1.13.10` produced:

```text
4 → Østkanten
1 → Sentrum
2 → Vestkanten
```

This resolves the O1200-specific:

```text
area ID → display name
```

metadata relationship for the tested device.

It does **not** imply full map support, and it does not by itself establish the selected-zone start command.

See:

[O1200 area names](area-names.md)

---

# O1200 cutting height is protocol-mapped

The O1200 development implementation maps cutting-height state through:

```text
mowHeightLevel
```

normalised as:

```text
mow_height_level
```

inside:

```text
AreaParameter
```

Therefore the correct current status is:

```text
protocol field known
fork implemented
Python tested
zone-specific
```

The remaining question is the mapping:

```text
mowHeightLevel
      │
      ▼
actual app/physical cutting height
```

Unknowns include:

```text
physical unit
complete valid range
level-to-height mapping
cross-model compatibility
```

So research has moved from:

```text
find the command
```

to:

```text
decode the values
```

---

# O1200 cut mode is protocol-mapped at the raw level

The same area-parameter record contains:

```text
cutMode
```

normalised as:

```text
cut_mode
```

This proves that a zone-specific raw cut-mode field exists.

It does **not** yet establish the complete mapping between integer values and:

```text
official ECOVACS app labels
mowing behaviour
efficiency/pattern terminology
```

It should not automatically be equated with the generic:

```text
efficiency_mode
```

capability.

---

# O1200 obstacle-height parameter

The zone record also contains:

```text
obstacleHeight
```

normalised as:

```text
obstacle_height
```

This is a known protocol field.

Its exact:

```text
app label
unit
valid range
physical effect
```

remain under investigation.

It should be kept separate from the boolean/AI settings:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
Animal protection
```

---

# O1200 zone angle

The area record contains:

```text
angle
```

for a specific:

```text
areaID
```

This appears to represent a zone-specific mowing direction/angle.

Reviewed upstream also has global:

```text
settings.cut_direction
```

The relationship between:

```text
AreaParameter.angle
```

and:

```text
CutDirectionEvent.angle
```

is not yet fully established.

Possible explanations include:

```text
global default vs zone override
older/global protocol vs newer zone-specific protocol
model-generation difference
different app functions
```

---

# O1200 area-parameter state flow

The development design is:

```text
GetAreaParameter
       │
       ▼
getAreaParameter
       │
       ▼
AreaParameterEvent
       ▲
       │
onAreaParameter
```

Writes use:

```text
SetAreaParameter
       │
       ▼
setAreaParameter
```

and the mower publishes:

```text
onAreaParameter
```

after successful changes.

This means state can be refreshed and synchronised rather than inferred only from command acknowledgements.

---

# Structured write behaviour

`setAreaParameter` writes the complete tuple:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

in one request.

Therefore a higher-level integration that allows changing only one value should preserve all unchanged sibling fields.

Recommended pattern:

```text
latest AreaParameterEvent
        │
        ▼
find areaID
        │
        ▼
copy complete tuple
        │
        ▼
replace one requested field
        │
        ▼
SetAreaParameter(...)
        │
        ▼
wait for onAreaParameter
```

This same design principle is relevant to other structured settings such as animal protection and rain configuration.

---

# Statistics and mowing progress

The common client exposes:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

Development work additionally preserves:

```text
mowedArea
```

as:

```text
StatsEvent.mowed_area
```

for the mower-progress path.

Home Assistant can then derive:

```text
mowed_area / area × 100
```

when the model declares:

```text
mowing_job_progress=True
```

See:

[Mowing progress and statistics](progress-and-statistics.md)

---

# Estimated mowing duration

For the researched O1200 progress path, Home Assistant interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

only when:

```text
mowing_job_progress=True
```

This is model-gated.

A separate explicit ECOVACS field such as:

```text
eta
estimated_remaining_time
```

has not been identified.

---

# Common upstream settings

Reviewed upstream GOAT profiles expose settings including:

```text
advanced mode
border switch
cut direction
child lock
move-up warning
cross-map border warning
safe protect
TrueDetect
volume
```

See:

[Mower settings](settings.md)

---

# O1200 mower settings under development

O1200-focused development work now includes:

```text
area_parameter
AI recognition
Humanoid AI / smart avoidance
narrow passage adaptation
animal protection
rain configuration
lifted-alarm volume
runtime protection state
```

The area-parameter capability is especially significant because it groups several formerly "unmapped" mower settings into one zone-specific protocol object.

---

# Rain and protection

Rain configuration:

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

A real-rain observation included:

```text
isRainProtect = 1
isRainDelay   = 0
```

The meaning of:

```text
isRainDelay = 1
```

remains unconfirmed.

See:

[Rain and protection](rain-and-protection.md)

---

# AI and obstacle-related controls

Known separate controls include:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
Animal protection
AreaParameter.obstacle_height
```

These should not be collapsed into one generic obstacle-avoidance setting.

For several controls, protocol mapping is stronger than user-facing semantic mapping.

See:

[Obstacle avoidance and AI](obstacle-and-ai.md)

---

# Home Assistant

GOAT devices can be represented as native:

```text
lawn_mower
```

entities.

Current mower development work supports:

```text
start mowing
pause
dock
mower-aware activity mapping
```

Progress development adds:

```text
Area mowed
Mowing progress
Estimated mowing duration
```

Area-parameter support is not yet exposed in the reviewed Home Assistant branch.

A future implementation must account for the structured per-zone write behaviour rather than treating `mow_height_level`, `cut_mode`, `obstacle_height` and `angle` as independent low-level setters.

See:

[Home Assistant integration](home-assistant.md)

---

# Current major research gaps

After the area-parameter PRs, the research priorities have changed.

The following are **no longer protocol-discovery gaps for O1200**:

```text
cutting-height field
zone cut-mode field
zone obstacle-height field
zone angle field
```

Remaining high-value work includes:

```text
mowHeightLevel → physical/app height mapping
cutMode → app labels and behaviour
obstacleHeight → exact meaning/unit
area angle ↔ global cut_direction relationship
mowing speed
selected-zone start command/capability for O1200
multi-zone behaviour
cross-model area-name support
AI/app-setting correlation
rain-delay lifecycle
animal-protection runtime behaviour
scheduling
GOAT map semantics
cross-model verification
```

See:

[Known limitations](known-limitations.md)

---

# Recommended reading paths

## Model support

[Supported models](supported-models.md)

## Capability architecture

[Capabilities](capabilities.md)

## Command routing

[Device-specific command routing](command-routing.md)

## Basic mowing

[Mowing control](mowing-control.md)

## Zones and selected-zone mowing

[Zones and areas](zones-and-areas.md)

## O1200 zone settings / cutting height / cut mode

[O1200 area parameters](area-parameters.md)

## O1200 area IDs and zone names

[O1200 area names](area-names.md)

## Progress

[Progress and statistics](progress-and-statistics.md)

## Settings

[Settings](settings.md)

## Rain/protection

[Rain and protection](rain-and-protection.md)

## AI/obstacle settings

[Obstacle and AI](obstacle-and-ai.md)

## Protocol commands/messages

[Protocol reference](protocol-reference.md)

## Home Assistant

[Home Assistant](home-assistant.md)

## Confidence/status

[Testing status](testing-status.md)

## Gaps

[Known limitations](known-limitations.md)

---

# Documentation map

```text
README.md
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
│   ├── area-names.md
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

---

# Model and firmware specificity

Protocol findings should be recorded with model and firmware context where practical.

Current strongest evidence for the newly mapped area-parameter family is:

```text
GOAT O1200 LiDAR
hardware ID: 2i0fns
```

Do not enable the same capability on other models solely because they have similar marketing names or app controls.

---

# Security and sanitisation

Public examples should remove:

```text
account IDs
device identifiers
serial numbers
authentication tokens
Wi-Fi data
precise location
private map data
```

Small sanitised protocol examples are preferred over raw MQTT/cloud messages.

---

# Related source work

Area-parameter development:

- [`PR #1767 — Add setAreaParameter support for GOAT O1200`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768 — Add onAreaParameter event support`](https://github.com/DeebotUniverse/client.py/pull/1768)
- [`Issue #1610 — O1200 zone-specific settings`](https://github.com/DeebotUniverse/client.py/issues/1610)
