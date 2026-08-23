# GOAT protocol reference

This page is a compact developer reference for ECOVACS GOAT mower commands, messages, payload fields and normalised `deebot_client` events.

Last reviewed against:

- upstream `DeebotUniverse/client.py` `dev`
- mower development branches
- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)

Date: **2026-08-24**

## Scope

This is not a complete ECOVACS protocol specification.

It focuses on elements currently relevant to GOAT mower support and protocol research.

---

# Status legend

| Status | Meaning |
| --- | --- |
| **Upstream** | Implemented in reviewed upstream `dev` |
| **Fork** | Implemented in a development branch/PR |
| **Observed** | Seen in real GOAT communication |
| **Tested** | Covered by automated Python tests |
| **HA** | Exposed in reviewed Home Assistant development work |
| **Unverified** | Interpretation/model scope still incomplete |

---

# Direction legend

| Direction | Meaning |
| --- | --- |
| **GET** | Request current state |
| **SET** | Change configuration |
| **EXECUTE** | Request an action |
| **PUSH** | Device/cloud reports state |
| **REPORT** | Job/statistical report |

---

# Mowing control

## `clean_V2`

Python:

```text
CleanV2
```

Direction:

```text
EXECUTE
```

Status:

**Upstream**

Supported actions:

```text
start
pause
resume
stop
```

Start example:

```json
{
  "act": "start",
  "content": {
    "type": "auto"
  }
}
```

Pause:

```json
{
  "act": "pause",
  "content": {
    "type": ""
  }
}
```

Resume:

```json
{
  "act": "resume",
  "content": {}
}
```

Stop:

```json
{
  "act": "stop",
  "content": {
    "type": ""
  }
}
```

---

# `getCleanInfo_V2`

Python:

```text
GetCleanInfoV2
```

Direction:

```text
GET
```

Status:

**Upstream**

Relevant state mappings include:

```text
motionState = working
    → State.CLEANING

motionState = pause
    → State.PAUSED

motionState = goCharging
    → State.RETURNING

state = goCharging
    → State.RETURNING

state = idle
    → State.IDLE

trigger = alert
    → State.ERROR
```

For mower UI:

```text
State.CLEANING = MOWING
```

---

# Return to charging station

## `charge`

Python:

```text
Charge
```

Direction:

```text
EXECUTE
```

Status:

**Upstream**

Payload:

```json
{
  "act": "go"
}
```

Normal result:

```text
State.RETURNING
```

Known response code:

```text
30007
```

is handled as already charging/docked and produces:

```text
State.DOCKED
```

## `getChargeState`

Python:

```text
GetChargeState
```

Direction:

```text
GET
```

Important field:

```text
isCharging
```

Known mapping:

```text
isCharging = 1
    → State.DOCKED
```

Status:

**Upstream**

---

# Selected-area mowing

## `CleanAreaV2`

Python:

```text
CleanAreaV2
```

Wire:

```text
clean_V2
```

Direction:

```text
EXECUTE
```

Status:

**Upstream generic command**

Selected target is encoded in:

```text
content.type
content.value
```

Example `spotArea`:

```json
{
  "act": "start",
  "content": {
    "type": "spotArea",
    "value": "5,8"
  }
}
```

Other generic types include:

```text
customArea
freeClean
```

Four reviewed upstream GOAT profiles expose the area command.

The reviewed O1200 upstream profile does not.

---

# O1200 area-name metadata

## `getAreaSet`

Python:

```text
GetAreaSet
```

Wire:

```text
getAreaSet
```

Direction:

```text
GET
```

Request:

```json
{
  "mid": "1",
  "aid": "0",
  "type": "ar"
}
```

The response carries compressed:

```text
subsets
```

data.

The development parser uses:

```text
decompress_base64_data
```

then decodes the JSON into:

```text
RoomsEvent
```

with:

```text
Room.id
Room.name
```

Real O1200 validation on firmware `1.13.10` produced:

```text
4 → Østkanten
1 → Sentrum
2 → Vestkanten
```

Status:

**Fork / Observed / Tested / Device validated**

Development capability:

```python
CapabilityClean(
    ...,
    areas=CapabilityEvent(
        RoomsEvent,
        [GetAreaSet()],
    ),
)
```

Important:

```text
CapabilityClean.areas
```

provides area metadata.

It does **not** imply:

```text
capabilities.map
```

and PR #1774 intentionally leaves full map support unset.

See:

[O1200 area names](area-names.md)

---

# O1200 area-parameter protocol

This is a **separate protocol family from selected-zone start**.

It configures settings associated with known areas/zones.

Development sources:

- PR #1767
- PR #1768
- issue #1610 protocol observations

## Data model

Wire fields:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

Python:

```text
area_id
mow_height_level
cut_mode
obstacle_height
angle
```

Normalised record:

```python
AreaParameter(
    area_id=...,
    mow_height_level=...,
    cut_mode=...,
    obstacle_height=...,
    angle=...,
)
```

Event:

```text
AreaParameterEvent
```

containing:

```text
list[AreaParameter]
```

Status:

**Fork / Observed / Tested**

Strongest model scope:

```text
GOAT O1200 LiDAR (2i0fns)
```

---

# `getAreaParameter`

Python:

```text
GetAreaParameter
```

Wire:

```text
getAreaParameter
```

Direction:

```text
GET
```

Response schema:

```json
{
  "areaParameters": [
    {
      "areaID": "2",
      "mowHeightLevel": 10,
      "cutMode": 7,
      "obstacleHeight": 1,
      "angle": 180
    },
    {
      "areaID": "3",
      "mowHeightLevel": 9,
      "cutMode": 4,
      "obstacleHeight": 2,
      "angle": 0
    }
  ]
}
```

Result:

```text
AreaParameterEvent
```

Status:

**Fork / Tested**

---

# `setAreaParameter`

Python:

```text
SetAreaParameter
```

Wire:

```text
setAreaParameter
```

Direction:

```text
SET / EXECUTE-style command handling
```

Payload is a flat single-area object:

```json
{
  "areaID": "2",
  "mowHeightLevel": 10,
  "cutMode": 7,
  "obstacleHeight": 1,
  "angle": 136
}
```

Status:

**Fork / Observed / Tested**

## Full-tuple semantics

The setter includes all four configurable values.

It is not a set of independent low-level setters.

Integrations should preserve unchanged sibling fields.

---

# `onAreaParameter`

Direction:

```text
PUSH
```

Wire:

```text
onAreaParameter
```

Schema:

```json
{
  "areaParameters": [
    {
      "areaID": "2",
      "mowHeightLevel": 10,
      "cutMode": 7,
      "obstacleHeight": 1,
      "angle": 136
    }
  ]
}
```

Result:

```text
AreaParameterEvent
```

Status:

**Fork / Observed / Tested**

The mower publishes this after successful area-parameter changes, allowing state to be confirmed from device reporting.

---

# `mowHeightLevel`

Protocol field:

```text
mowHeightLevel
```

Python:

```text
mow_height_level
```

Meaning:

```text
zone-specific mower cutting-height level
```

Status:

**Observed / Fork / Tested**

Still unresolved:

```text
raw level → physical unit/height
full range
step
cross-model mapping
```

Do not interpret a raw value such as `10` as `10 mm` without evidence.

---

# `cutMode`

Protocol:

```text
cutMode
```

Python:

```text
cut_mode
```

Meaning:

```text
zone-specific raw cut-mode value
```

Status:

**Observed / Fork / Tested**

Unresolved:

```text
integer → official app label/behaviour
```

Do not automatically map it to generic `efficiency_mode`.

---

# `obstacleHeight`

Protocol:

```text
obstacleHeight
```

Python:

```text
obstacle_height
```

Status:

**Observed / Fork / Tested**

The name suggests obstacle-height-related zone configuration, but exact unit/range/physical semantics remain unverified.

---

# Area `angle`

Protocol:

```text
angle
```

Python:

```text
angle
```

Status:

**Observed / Fork / Tested**

Associated with:

```text
areaID
```

and therefore zone-specific in this protocol family.

Its exact relationship with global:

```text
GetCutDirection / SetCutDirection
```

remains open.

---

# O1200 area-parameter capability

Development capability:

```python
area_parameter=CapabilitySet(
    AreaParameterEvent,
    [GetAreaParameter()],
    SetAreaParameter,
)
```

Conceptually:

```text
GET ──────► AreaParameterEvent ◄────── PUSH
                 ▲
                 │
                SET
```

This should be treated as O1200 development support until merged/verified elsewhere.

---

# Statistics

## `getStats`

Python:

```text
GetStats
```

Direction:

```text
GET
```

Status:

**Upstream**

Upstream fields:

```text
area
time
type
```

Event:

```text
StatsEvent
```

## `mowedArea`

Wire:

```text
mowedArea
```

Python development field:

```text
mowed_area
```

Status:

**Fork / Observed / Tested**

Example:

```json
{
  "area": 2889500,
  "time": 11269,
  "mowedArea": 1005475
}
```

## `onStats`

Direction:

```text
PUSH
```

Development parsing includes:

```text
area
time
type
mowedArea
```

## `getTotalStats`

Direction:

```text
GET
```

Mapping:

```text
area  → TotalStatsEvent.area
time  → TotalStatsEvent.time
count → TotalStatsEvent.cleanings
```

Status:

**Upstream**

## `reportStats`

Direction:

```text
REPORT / PUSH
```

Event:

```text
ReportStatsEvent
```

Relevant shared fields:

```text
area
time
type
cid
content
stop
stopReason
```

Known statuses include:

```text
NO_STATUS
CLEANING
FINISHED
MANUALLY_STOPPED
FINISHED_WITH_WARNINGS
```

---

# Progress semantics

For the researched O1200 progress path:

```text
mowed_area / area × 100
```

is derived by Home Assistant.

`StatsEvent.time` is model-gated as:

```text
Estimated mowing duration
```

when:

```text
mowing_job_progress=True
```

This does not create a universal ETA protocol rule.

---

# Common upstream mower settings

| Capability | GET | SET | Event |
| --- | --- | --- | --- |
| Advanced mode | `GetAdvancedMode` | `SetAdvancedMode` | `AdvancedModeEvent` |
| Border switch | `GetBorderSwitch` | `SetBorderSwitch` | `BorderSwitchEvent` |
| Cutting direction | `GetCutDirection` | `SetCutDirection` | `CutDirectionEvent` |
| Child lock | `GetChildLock` | `SetChildLock` | `ChildLockEvent` |
| Move-up warning | `GetMoveUpWarning` | `SetMoveUpWarning` | `MoveUpWarningEvent` |
| Cross-map border warning | `GetCrossMapBorderWarning` | `SetCrossMapBorderWarning` | `CrossMapBorderWarningEvent` |
| Safe protect | `GetSafeProtect` | `SetSafeProtect` | `SafeProtectEvent` |
| TrueDetect | `GetTrueDetect` | `SetTrueDetect` | `TrueDetectEvent` |
| Volume | `GetVolume` | `SetVolume` | `VolumeEvent` |

Status:

**Upstream**

---

# AI recognition

Wire:

```text
getRecognization
setRecognization
onRecognization
```

Field:

```text
state
```

Event:

```text
AiRecognitionEvent
```

Status:

**Fork / Tested**

---

# Humanoid AI / smart avoidance

Wire:

```text
getHumanoidAI
setHumanoidAI
onHumanoidAI
```

Field:

```text
enable
```

Event:

```text
HumanoidAiEvent
```

Implementation description:

```text
Smart mowing with avoidance
```

Status:

**Fork / Tested**

---

# Narrow passage adaptation

Wire:

```text
getNarrowAdapt
setNarrowAdapt
onNarrowAdapt
```

Field:

```text
state
```

Event:

```text
NarrowAdaptEvent
```

Status:

**Fork / Tested**

---

# Animal protection

Wire:

```text
getAnimProtect
setAnimProtect
onAnimProtect
```

Fields:

```text
enable
start
end
```

Event:

```text
AnimalProtectionEvent
```

Time strings are normalised to:

```text
HH:MM
```

Status:

**Fork / Tested**

---

# Rain configuration

## `setRainDelay`

Fields:

```text
enable
delay
```

Example:

```json
{
  "enable": 1,
  "delay": 180
}
```

Allowed development values:

```text
0–300 minutes
step 30 minutes
```

Status:

**Fork / Observed / Tested**

## `onRainDelay`

Direction:

```text
PUSH
```

Event:

```text
RainDelayEvent
```

Important:

```text
configuration state ≠ current rain condition
```

---

# Runtime protection

## `onProtectState`

Direction:

```text
PUSH
```

Event:

```text
ProtectStateEvent
```

Mapping:

| Wire | Python |
| --- | --- |
| `isAnimProtect` | `is_anim_protect` |
| `isRainProtect` | `is_rain_protect` |
| `isRainDelay` | `is_rain_delay` |
| `isEStop` | `is_e_stop` |
| `isLocked` | `is_locked` |
| `isPinCode` | `is_pin_code` |
| `isPrepareDataSuccess` | `is_prepare_data_success` |

Real-rain observation:

```text
isRainProtect = 1
isRainDelay   = 0
```

The exact physical meaning of:

```text
isRainDelay = 1
```

remains open.

---

# Volume

## System

Wire:

```text
getVolume
setVolume
```

Example:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 6
}
```

## Lifted/fall channel

Wire:

```text
setVolume
```

Python:

```text
SetFallVolume
```

Example:

```json
{
  "type": "fall",
  "total": 10,
  "volume": 6
}
```

Event:

```text
FallVolumeEvent
```

Push:

```text
onVolume
```

---

# Move-up warning push

Wire:

```text
onMoveupWarning
```

Python:

```text
OnMoveUpWarning
```

Event:

```text
MoveUpWarningEvent
```

This is separate from fall/lifted alarm volume.

---

# Compact command reference

| Wire name | Python | Direction | Event/result | Status |
| --- | --- | --- | --- | --- |
| `clean_V2` | `CleanV2` | EXECUTE | `StateEvent` | Upstream |
| `getCleanInfo_V2` | `GetCleanInfoV2` | GET | `StateEvent` | Upstream |
| `charge` | `Charge` | EXECUTE | `StateEvent` | Upstream |
| `getChargeState` | `GetChargeState` | GET | `StateEvent` | Upstream |
| `getAreaSet` | `GetAreaSet` | GET | `RoomsEvent` | Fork |
| `getAreaParameter` | `GetAreaParameter` | GET | `AreaParameterEvent` | Fork |
| `setAreaParameter` | `SetAreaParameter` | SET | later `AreaParameterEvent` | Fork |
| `onAreaParameter` | `OnAreaParameter` | PUSH | `AreaParameterEvent` | Fork |
| `getStats` | `GetStats` | GET | `StatsEvent` | Upstream |
| `onStats` | `OnStats` | PUSH | `StatsEvent` | Upstream/Fork |
| `getTotalStats` | `GetTotalStats` | GET | `TotalStatsEvent` | Upstream |
| `reportStats` | `ReportStats` | REPORT | `ReportStatsEvent` | Upstream |
| `getTrueDetect` | `GetTrueDetect` | GET | `TrueDetectEvent` | Upstream |
| `setTrueDetect` | `SetTrueDetect` | SET | `TrueDetectEvent` | Upstream |
| `getBorderSwitch` | `GetBorderSwitch` | GET | `BorderSwitchEvent` | Upstream |
| `setBorderSwitch` | `SetBorderSwitch` | SET | `BorderSwitchEvent` | Upstream |
| `getRecognization` | `GetRecognization` | GET | `AiRecognitionEvent` | Fork |
| `setRecognization` | `SetRecognization` | SET | `AiRecognitionEvent` | Fork |
| `onRecognization` | `OnRecognization` | PUSH | `AiRecognitionEvent` | Fork |
| `getHumanoidAI` | `GetHumanoidAi` | GET | `HumanoidAiEvent` | Fork |
| `setHumanoidAI` | `SetHumanoidAi` | SET | `HumanoidAiEvent` | Fork |
| `onHumanoidAI` | `OnHumanoidAi` | PUSH | `HumanoidAiEvent` | Fork |
| `getNarrowAdapt` | `GetNarrowAdapt` | GET | `NarrowAdaptEvent` | Fork |
| `setNarrowAdapt` | `SetNarrowAdapt` | SET | `NarrowAdaptEvent` | Fork |
| `onNarrowAdapt` | `OnNarrowAdapt` | PUSH | `NarrowAdaptEvent` | Fork |
| `getAnimProtect` | `GetAnimalProtection` | GET | `AnimalProtectionEvent` | Fork |
| `setAnimProtect` | `SetAnimalProtection` | SET | `AnimalProtectionEvent` | Fork |
| `onAnimProtect` | `OnAnimalProtection` | PUSH | `AnimalProtectionEvent` | Fork |
| `setRainDelay` | `SetRainDelay` | SET | later `RainDelayEvent` | Fork |
| `onRainDelay` | `OnRainDelay` | PUSH | `RainDelayEvent` | Fork |
| `onProtectState` | `OnProtectState` | PUSH | `ProtectStateEvent` | Fork |
| `getVolume` | `GetVolume` | GET | `VolumeEvent` / `FallVolumeEvent` | Upstream/Fork |
| `setVolume` | `SetVolume` / `SetFallVolume` | SET | volume state | Upstream/Fork |
| `onVolume` | `OnVolume` | PUSH | volume events | Fork |
| `onMoveupWarning` | `OnMoveUpWarning` | PUSH | `MoveUpWarningEvent` | Fork |

---

# GET / SET / PUSH pattern

Many settings follow:

```text
GET current state
      │
      ▼
normalised Event
      ▲
      │
SET new state

external/app change
      │
      ▼
PUSH
      │
      ▼
same Event
```

O1200 area parameters are a clear example:

```text
getAreaParameter
      │
      ▼
AreaParameterEvent
      ▲
      │
onAreaParameter

setAreaParameter
      │
      └── writes one area's full tuple
```

---

# Setter schema can differ from getter schema

For area parameters:

## SET

```json
{
  "areaID": "2",
  "mowHeightLevel": 10,
  "cutMode": 7,
  "obstacleHeight": 1,
  "angle": 136
}
```

## GET/PUSH

```json
{
  "areaParameters": [
    {
      "areaID": "2",
      "mowHeightLevel": 10,
      "cutMode": 7,
      "obstacleHeight": 1,
      "angle": 136
    }
  ]
}
```

Protocol abstractions should preserve this difference instead of assuming symmetric schemas.

---

# Protocol names versus Python names

Examples:

```text
areaID             → area_id
mowHeightLevel     → mow_height_level
cutMode            → cut_mode
obstacleHeight     → obstacle_height
mowedArea          → mowed_area
getAnimProtect     → GetAnimalProtection
getHumanoidAI      → GetHumanoidAi
isRainProtect      → is_rain_protect
```

Both naming layers are useful:

```text
wire names → log/protocol analysis
Python names → client implementation
```

---

# Command acknowledgement versus reported state

A command acknowledgement does not always provide the final state.

Examples include:

```text
setRainDelay
   │
   ▼
ACK
   │
   ▼
onRainDelay
```

and area parameters:

```text
setAreaParameter
   │
   ▼
command accepted
   │
   ▼
onAreaParameter
   │
   ▼
AreaParameterEvent
```

Consumers should prefer reported state where available.

---

# Model scope

Strongest area-parameter evidence:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

Do not assume:

```text
same-looking app feature
    →
same protocol on every GOAT
```

Model capabilities should be enabled from evidence.

---

# Current protocol gaps

After PR #1767/#1768, these are no longer O1200 field-discovery gaps:

```text
cutting-height field
zone cut-mode field
zone obstacle-height field
zone angle
```

Remaining research includes:

```text
mowHeightLevel → physical/app height mapping
cutMode value semantics
obstacleHeight semantics/unit
zone angle ↔ global cut_direction
mowing speed
O1200 selected-zone start capability
areaID ↔ selected-zone start ID
cross-model area-name support
multi-zone semantics
AI app-label mapping
explicit separate ETA field
rain-delay lifecycle
scheduling
GOAT map semantics
```

---

# Sanitisation

Do not publish full raw ECOVACS traffic.

Remove:

```text
account IDs
device IDs
serial numbers
credentials
tokens
Wi-Fi details
precise location
private map data
```

Prefer minimal payload examples.

---

# Related development

- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)
- [`Issue #1610`](https://github.com/DeebotUniverse/client.py/issues/1610)

---

# Related documentation

- [Overview](overview.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [O1200 area parameters](area-parameters.md)
- [O1200 area names](area-names.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
