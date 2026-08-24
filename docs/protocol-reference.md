# GOAT protocol reference

This page is a compact developer reference for ECOVACS GOAT mower commands, messages, payload fields and normalised `deebot_client` events.

Last reviewed against:

- [`PR #1772`](https://github.com/DeebotUniverse/client.py/pull/1772) — device-specific command routing
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


# Command-name routing

Protocol command names are not necessarily globally unique in semantics.

PR #1772 introduces device-specific command resolution so the same wire name can map to different Python command classes for different hardware profiles.

Development resolution concept:

```text
wire command name
       │
       ▼
device capabilities
       │
   ┌───┴────┐
   │        │
 found   not found
   │        │
   ▼        ▼
device   global fallback
command
```

This is a client-routing concern rather than a new ECOVACS protocol field.

## Legacy messages

Legacy JSON message lookup prefers the command configured by the target device's capabilities and only then uses the global `COMMANDS` registry.

## MQTT P2P

Device-specific P2P lookup follows:

```text
q request  → receiver device
p response → sender device
```

An explicitly configured non-P2P command blocks substitution of a different global P2P implementation with the same name.

## Same-name command limitation inside one device

The per-device table contains one command class per command `NAME`.

When several directly discoverable commands in one device share a name, first-wins behaviour applies.

Commands hidden behind lambdas are not directly discovered.

This is relevant when combining PR #1772 with O1200 volume work in PR #1778, where multiple volume semantics share:

```text
setVolume
```

The combined routing should be explicitly integration-tested.

Detailed architecture:

[Device-specific command routing](command-routing.md)

---


# GOAT mower map protocol stack

The current mower map development uses several distinct wire families.

Do not collapse them into one generic "map message".

## `onMapTrace`

Source work:

```text
PR #1567
```

Purpose in the current architecture:

```text
typed mower trace/group geometry
```

Observed mower payloads can be chunked and LZMA-wrapped.

Normalised event:

```text
MowerMapTraceEvent
```

This is distinct from the O1200 live:

```text
onMapTrack
```

research family.

## `getMI`

Direction:

```text
GET / control request
```

Research shows both tested legacy and N-GIoT transports can solicit the O1200 static-map event family while presence is active.

The direct acknowledgement is not treated as the static geometry payload.

## `onMI`

Direction:

```text
PUSH
```

PR #1782 parses the supported O1200 request-associated geometry form into:

```text
MowerStaticMapEvent
```

The parser intentionally ignores the cadence-associated non-geometry form.

Observed O1200 static geometry:

```text
step_size = 50
2,336 points in the golden fixture
```

## `onArI`

Direction:

```text
PUSH
```

PR #1788 parses complete:

```text
type = 0
```

work-area geometry snapshots.

Persistent work-area geometry is carried in the observed:

```text
layer "1"
```

and uses the same eight-direction RLE representation as the static boundary.

Normalised output contributes to:

```text
MowerWorkAreasEvent
```

after metadata join and coordinate registration.

## `getAreaSet`

Direction:

```text
GET
```

PR #1788 uses:

```text
type = "ar"
```

for area metadata:

```text
map ID
area ID
display name
```

Important framing rule:

```text
AreaSet envelope infoSize
    ≠ decoded payload length
```

for the controlled O1200 corpus.

The parser instead validates the decompressed size retained in the trimmed LZMA-Alone header.

This rule is scoped to AreaSet and must not be applied blindly to `onMI`/`onArI`.

## `appping`

Research role:

```text
live-map presence trigger
```

Controlled O1200 tests observed an approximately:

```text
300-second
```

presence lease, reset by a later `appping`.

The current static map stack does not yet implement this as production Map lifecycle logic.

## `onPos`

Research role:

```text
live mower position
```

Raw position support is separate from the static-map rendering path because the live-to-static transform is not proven.

## `onMapTrack`

Research role:

```text
live mowing-plan/activity stream
```

Diagnostic decoding has established chunk/update structure, but no production Map event/rendering layer is included in #1789.

## Observed O1200 map-ID split

In the captured O1200 corpus:

```text
onPos / onMapTrack
    → map ID 0

onMI / onArI
    → map ID 1
```

Treat this as model/capture evidence, not a universal GOAT rule.

Detailed reference:

[GOAT mower map support](map.md)

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

Wire-level meaning:

```text
zone-specific mower cutting-height level
```

Status:

**Observed / Fork / Tested**

## HA semantic mapping

The Home Assistant development branch maps:

```python
height_cm = (17 - level) / 2
```

with:

```text
3.0–8.0 cm
0.5 cm step
```

| `mowHeightLevel` | HA semantic height |
| ---: | ---: |
| 11 | 3.0 cm |
| 10 | 3.5 cm |
| 9 | 4.0 cm |
| 8 | 4.5 cm |
| 7 | 5.0 cm |
| 6 | 5.5 cm |
| 5 | 6.0 cm |
| 4 | 6.5 cm |
| 3 | 7.0 cm |
| 2 | 7.5 cm |
| 1 | 8.0 cm |

Status:

**HA semantic mapping implemented/tested**

Still requiring evidence:

```text
complete independent physical validation
confirmation of protocol-valid range beyond UI assumptions
cross-model mapping
```

# `cutMode`

Protocol:

```text
cutMode
```

Python:

```text
cut_mode
```

Wire-level meaning:

```text
zone-specific raw cut-mode value
```

Status:

**Observed / Fork / Tested**

## HA semantic mapping

```text
7 → Gentle / 0.35 m/s
4 → Efficient / 0.5 m/s
```

The HA helper tests verify both mapping directions.

This is currently the known O1200 zone-speed representation.

Do not automatically map it to generic `efficiency_mode`, and do not infer that a separate standalone speed command exists.

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

## HA semantic mapping

```text
1 → short-grass / flat-terrain environment <10 cm
2 → normal environment <15 cm
3 → high-grass environment <20 cm
```

The mapping is tested in both directions.

Treat these as semantic environment/avoidance labels from the HA development branch, not as proof that the raw integer itself is a centimetre measurement.

# Area `angle`

Protocol:

```text
angle
```

Python:

```text
angle
```

Associated with:

```text
areaID
```

Status:

**Observed / Fork / Tested**

## HA semantic conversion

```python
user_degrees = (270 - raw_angle) % 360
raw_angle = (270 - user_degrees) % 360
```

Tested examples:

```text
180 → 90°
145 → 125°
216 → 54°
0   → 270°
```

The remaining open question is the relationship with global:

```text
GetCutDirection / SetCutDirection
```

—not conversion of the per-area raw value itself.

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

`setAnimProtect` writes the complete tuple:

```text
enable
start
end
```

rather than a partial field update.

Status:

**Fork / Observed / Tested**

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

No `getRainDelay` refresh command is introduced in PR #1776/#1778.

The setter acknowledgement does not itself emit `RainDelayEvent`; resulting state is reported by `onRainDelay`.

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

## Deliberately unmapped rain codes

PR #1776 explicitly leaves:

```text
event code 2052
rain-specific pause-reason values
```

without semantic mappings because their meanings are not sufficiently documented.

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

## Read payload

Wire:

```text
getVolume
onVolume
```

A complete O1200 payload can contain:

```json
{
  "total": 10,
  "volume": 5,
  "fallVolume": 2,
  "searchVolume": 10
}
```

Normalised mapping:

```text
volume
    → VolumeEvent

fallVolume
    → FallVolumeEvent
```

`searchVolume` is currently not exposed as a separate capability because no setter protocol has been observed.

## System

Wire:

```text
setVolume
```

O1200 channel:

```text
sys
```

Example:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 6
}
```

The generic `SetVolume(volume)` API remains backward compatible; `channel` and `total` are optional at the shared command level.

The O1200 capability explicitly supplies:

```text
channel = sys
total   = 10
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

The observed O1200 implementation uses `total=10` for both system and lifted-alarm volume.

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
- [Device-specific command routing](command-routing.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [GOAT mower map support](map.md)
- [O1200 area parameters](area-parameters.md)
- [O1200 global settings](o1200-global-settings.md)
- [O1200 area names](area-names.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
