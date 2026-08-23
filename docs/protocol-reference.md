# GOAT protocol reference

This page is a compact developer reference for ECOVACS GOAT mower commands, messages, payload fields and normalised `deebot_client` events.

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* development branches used for GOAT mower research

Date: **2026-08-23**

## Scope

This is not intended to document the complete ECOVACS protocol.

It focuses on protocol elements currently relevant to GOAT mower support and research.

Detailed behavioural explanations are available in the topic-specific documentation.

---

# Status legend

| Status         | Meaning                                           |
| -------------- | ------------------------------------------------- |
| **Upstream**   | Implemented in current upstream `dev`             |
| **Fork**       | Implemented in a development branch/fork          |
| **Observed**   | Seen in GOAT protocol traffic                     |
| **Tested**     | Covered by Python tests                           |
| **Unverified** | Interpretation or model support remains uncertain |

A protocol item may have more than one status.

---

# Direction legend

| Direction   | Meaning                                            |
| ----------- | -------------------------------------------------- |
| **GET**     | Client requests current state                      |
| **SET**     | Client changes configuration                       |
| **EXECUTE** | Client requests an action                          |
| **PUSH**    | Device/cloud reports state without an explicit GET |
| **REPORT**  | Device reports job/statistical information         |

---

# Mowing control

## `clean_V2`

Python command:

```text
CleanV2
```

Direction:

```text
EXECUTE
```

Status:

**Upstream**

Purpose:

```text
Control the mowing lifecycle.
```

Supported actions:

```text
start
pause
resume
stop
```

### Start

Conceptual payload:

```json
{
  "act": "start",
  "content": {
    "type": "auto"
  }
}
```

### Pause

Conceptual payload:

```json
{
  "act": "pause",
  "content": {
    "type": ""
  }
}
```

### Resume

Conceptual payload:

```json
{
  "act": "resume",
  "content": {}
}
```

### Stop

Conceptual payload:

```json
{
  "act": "stop",
  "content": {
    "type": ""
  }
}
```

Related events:

```text
StateEvent
```

Possible normalised states include:

```text
CLEANING
PAUSED
IDLE
RETURNING
ERROR
```

For GOAT devices:

```text
CLEANING = mowing
```

---

# `getCleanInfo_V2`

Python command:

```text
GetCleanInfoV2
```

Direction:

```text
GET
```

Status:

**Upstream**

Purpose:

```text
Retrieve current operation/mowing information.
```

Relevant observed/shared protocol values include:

```text
state
trigger
cleanState
motionState
content
```

Known state mappings include:

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

---

# Return to charging station

## `charge`

Python command:

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

Normal successful result:

```text
State.RETURNING
```

Known response code:

```text
30007
```

is handled as:

```text
already charging
```

and produces:

```text
State.DOCKED
```

---

# `getChargeState`

Python command:

```text
GetChargeState
```

Direction:

```text
GET
```

Status:

**Upstream**

Important field:

```text
isCharging
```

Known mapping:

```text
isCharging = 1
    → State.DOCKED
```

---

# Area and zone mowing

## `CleanAreaV2`

Python command:

```text
CleanAreaV2
```

Wire command:

```text
clean_V2
```

Direction:

```text
EXECUTE
```

Status:

**Upstream**

The selected area is encoded in:

```text
content.type
content.value
```

General structure:

```json
{
  "act": "start",
  "content": {
    "type": "...",
    "value": "..."
  }
}
```

---

# `spotArea`

Client mode:

```text
CleanMode.SPOT_AREA
```

Protocol type:

```text
spotArea
```

Example:

```python
CleanAreaV2(
    CleanMode.SPOT_AREA,
    [5, 8],
)
```

produces:

```json
{
  "act": "start",
  "content": {
    "type": "spotArea",
    "value": "5,8"
  }
}
```

For GOAT devices, the numeric values may represent lawn-zone identifiers.

The exact mower-specific mapping should be verified per model/protocol.

---

# `customArea`

Client mode:

```text
CleanMode.CUSTOM_AREA
```

Protocol type:

```text
customArea
```

Example:

```json
{
  "act": "start",
  "content": {
    "type": "customArea",
    "value": "1580.0,-4087.0,3833.0,-7525.0"
  }
}
```

The generic client treats these as coordinate values.

GOAT support for arbitrary coordinate mowing remains model/behaviour dependent.

---

# `freeClean`

Client mode:

```text
CleanMode.FREE_CLEAN
```

Protocol type:

```text
freeClean
```

Example:

```json
{
  "act": "start",
  "content": {
    "type": "freeClean",
    "value": "1,5,8"
  }
}
```

The first value represents:

```text
cleanings
```

in the generic client.

Example:

```text
2,0
```

represents two operations for target `0` in the upstream tests.

GOAT-specific interpretation remains to be fully established.

---

# Statistics

## `getStats`

Python command:

```text
GetStats
```

Direction:

```text
GET
```

Status:

**Upstream**

Known upstream fields:

```text
area
time
type
```

Normalised event:

```text
StatsEvent
```

Current upstream event:

```python
StatsEvent(
    area=...,
    time=...,
    type=...,
)
```

---

# `mowedArea`

Protocol field:

```text
mowedArea
```

Python field in development branch:

```text
mowed_area
```

Status:

**Fork / Observed / Tested**

Development event:

```python
StatsEvent(
    area=...,
    time=...,
    type=...,
    mowed_area=...,
)
```

Example test payload:

```json
{
  "area": 2889500,
  "time": 11269,
  "mowedArea": 1005475
}
```

The raw units should not be inferred without separate verification.

---

# `onStats`

Direction:

```text
PUSH
```

Status:

**Upstream, extended in fork**

Purpose:

```text
Report statistics without requiring an explicit getStats request.
```

Development parsing includes:

```text
area
time
type
mowedArea
```

Normalised event:

```text
StatsEvent
```

---

# `getTotalStats`

Python command:

```text
GetTotalStats
```

Direction:

```text
GET
```

Status:

**Upstream**

Known response mapping:

```text
area  → TotalStatsEvent.area
time  → TotalStatsEvent.time
count → TotalStatsEvent.cleanings
```

Normalised event:

```text
TotalStatsEvent
```

---

# `reportStats`

Direction:

```text
REPORT / PUSH
```

Status:

**Upstream**

Normalised event:

```text
ReportStatsEvent
```

Relevant fields include:

```text
area
time
type
cid
content
stop
stopReason
```

Client mapping:

```text
cid
    → cleaning_id

content
    → list[int]

stop / stopReason
    → CleanJobStatus
```

Known normalised statuses include:

```text
NO_STATUS
CLEANING
FINISHED
MANUALLY_STOPPED
FINISHED_WITH_WARNINGS
```

For GOAT:

```text
CLEANING
```

should normally be interpreted as:

```text
MOWING
```

in a user-facing interface.

---

# TrueDetect

## `getTrueDetect`

Python command:

```text
GetTrueDetect
```

Direction:

```text
GET
```

Status:

**Upstream**

Event:

```text
TrueDetectEvent
```

---

# `setTrueDetect`

Python command:

```text
SetTrueDetect
```

Direction:

```text
SET
```

Status:

**Upstream**

Type:

```text
boolean
```

The exact user-facing GOAT meaning of TrueDetect should be correlated with the ECOVACS app.

---

# Border switch

## `getBorderSwitch`

Python command:

```text
GetBorderSwitch
```

Direction:

```text
GET
```

Status:

**Upstream**

Event:

```text
BorderSwitchEvent
```

---

# `setBorderSwitch`

Python command:

```text
SetBorderSwitch
```

Direction:

```text
SET
```

Status:

**Upstream**

Type:

```text
boolean
```

The upstream source explicitly defines the wire names as:

```text
getBorderSwitch
setBorderSwitch
```

---

# Other upstream mower settings

The reviewed GOAT profiles also expose the following command/event pairs.

| Capability               | GET class                  | SET class                  | Event                        |
| ------------------------ | -------------------------- | -------------------------- | ---------------------------- |
| Advanced mode            | `GetAdvancedMode`          | `SetAdvancedMode`          | `AdvancedModeEvent`          |
| Cutting direction        | `GetCutDirection`          | `SetCutDirection`          | `CutDirectionEvent`          |
| Child lock               | `GetChildLock`             | `SetChildLock`             | `ChildLockEvent`             |
| Move-up warning          | `GetMoveUpWarning`         | `SetMoveUpWarning`         | `MoveUpWarningEvent`         |
| Cross-map border warning | `GetCrossMapBorderWarning` | `SetCrossMapBorderWarning` | `CrossMapBorderWarningEvent` |
| Safe protect             | `GetSafeProtect`           | `SetSafeProtect`           | `SafeProtectEvent`           |
| TrueDetect               | `GetTrueDetect`            | `SetTrueDetect`            | `TrueDetectEvent`            |
| Volume                   | `GetVolume`                | `SetVolume`                | `VolumeEvent`                |

Exact wire-name spelling should be taken from the corresponding command implementation rather than derived from the Python class name when building protocol tooling.

---

# AI recognition

## `getRecognization`

Python command:

```text
GetRecognization
```

Direction:

```text
GET
```

Status:

**Fork / Tested**

Protocol field:

```text
state
```

Normalised event:

```text
AiRecognitionEvent
```

---

# `setRecognization`

Python command:

```text
SetRecognization
```

Direction:

```text
SET
```

Status:

**Fork / Tested**

Payload concept:

```json
{
  "state": 1
}
```

or:

```json
{
  "state": 0
}
```

---

# `onRecognization`

Direction:

```text
PUSH
```

Status:

**Fork**

Purpose:

```text
AI recognition state update
```

Parser behaviour is shared with:

```text
GetRecognization
```

Normalised event:

```text
AiRecognitionEvent
```

---

# Smart mowing / Humanoid AI

## `getHumanoidAI`

Python command:

```text
GetHumanoidAi
```

Direction:

```text
GET
```

Status:

**Fork / Tested**

Protocol field:

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

---

# `setHumanoidAI`

Python command:

```text
SetHumanoidAi
```

Direction:

```text
SET
```

Status:

**Fork / Tested**

Example:

```json
{
  "enable": 1
}
```

---

# `onHumanoidAI`

Direction:

```text
PUSH
```

Status:

**Fork**

Normalised event:

```text
HumanoidAiEvent
```

The push handler reuses the GET parser.

---

# Narrow passage adaptation

## `getNarrowAdapt`

Python command:

```text
GetNarrowAdapt
```

Direction:

```text
GET
```

Status:

**Fork / Tested**

Protocol field:

```text
state
```

Event:

```text
NarrowAdaptEvent
```

---

# `setNarrowAdapt`

Python command:

```text
SetNarrowAdapt
```

Direction:

```text
SET
```

Status:

**Fork / Tested**

Example:

```json
{
  "state": 1
}
```

---

# `onNarrowAdapt`

Direction:

```text
PUSH
```

Status:

**Fork**

Normalised event:

```text
NarrowAdaptEvent
```

---

# Animal protection

## `getAnimProtect`

Python command:

```text
GetAnimalProtection
```

Direction:

```text
GET
```

Status:

**Fork / Tested**

Known response fields:

```text
enable
start
end
```

Normalised event:

```text
AnimalProtectionEvent
```

Example response:

```json
{
  "enable": 1,
  "start": "23:45",
  "end": "6:30"
}
```

Normalised event times:

```text
23:45
06:30
```

---

# `setAnimProtect`

Python command:

```text
SetAnimalProtection
```

Direction:

```text
SET
```

Status:

**Fork / Tested**

Payload:

```json
{
  "enable": 1,
  "start": "23:45",
  "end": "06:30"
}
```

Time strings are normalised to:

```text
HH:MM
```

---

# `onAnimProtect`

Direction:

```text
PUSH
```

Status:

**Fork**

Purpose:

```text
Animal protection configuration update
```

Normalised event:

```text
AnimalProtectionEvent
```

---

# Rain configuration

## `setRainDelay`

Python command:

```text
SetRainDelay
```

Direction:

```text
SET
```

Status:

**Fork / Observed / Tested**

Payload fields:

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

Supported delay values:

```text
0
30
60
90
120
150
180
210
240
270
300
```

Unit:

```text
minutes
```

Invalid values are rejected by the implementation.

---

# `onRainDelay`

Direction:

```text
PUSH
```

Status:

**Fork / Observed / Tested**

Payload:

```json
{
  "enable": 1,
  "delay": 180
}
```

Normalised event:

```python
RainDelayEvent(
    enabled=True,
    delay=180,
)
```

Important:

```text
onRainDelay
```

represents configuration.

It does not by itself indicate that rain is currently falling.

---

# Runtime protection state

## `onProtectState`

Direction:

```text
PUSH
```

Status:

**Fork / Observed / Tested**

Normalised event:

```text
ProtectStateEvent
```

Known payload fields:

```text
isAnimProtect
isRainProtect
isRainDelay
isEStop
isLocked
isPinCode
isPrepareDataSuccess
```

Python mapping:

| Protocol               | Python                    |
| ---------------------- | ------------------------- |
| `isAnimProtect`        | `is_anim_protect`         |
| `isRainProtect`        | `is_rain_protect`         |
| `isRainDelay`          | `is_rain_delay`           |
| `isEStop`              | `is_e_stop`               |
| `isLocked`             | `is_locked`               |
| `isPinCode`            | `is_pin_code`             |
| `isPrepareDataSuccess` | `is_prepare_data_success` |

---

# Observed rain protection payload

A real-rain observation produced the equivalent state:

```json
{
  "isAnimProtect": 0,
  "isRainProtect": 1,
  "isRainDelay": 0,
  "isEStop": 0,
  "isLocked": 0,
  "isPinCode": 0,
  "isPrepareDataSuccess": 1
}
```

Normalised:

```python
ProtectStateEvent(
    is_anim_protect=False,
    is_rain_protect=True,
    is_rain_delay=False,
    is_e_stop=False,
    is_locked=False,
    is_pin_code=False,
    is_prepare_data_success=True,
)
```

The confirmed interpretation is:

```text
isRainProtect = 1
```

can occur while actual rain protection is active.

The exact meaning of:

```text
isRainDelay = 1
```

remains to be established through direct observation.

---

# Volume

## `getVolume`

Python command:

```text
GetVolume
```

Direction:

```text
GET
```

Status:

**Upstream / extended mower parsing in fork**

Known fields include:

```text
volume
total
type
fallVolume
```

Normalised events can include:

```text
VolumeEvent
FallVolumeEvent
```

---

# `setVolume` — system channel

Python command:

```text
SetVolume
```

Direction:

```text
SET
```

Status:

**Upstream, refined for O1200 in fork**

Mower system-volume usage:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 6
}
```

---

# `setVolume` — lifted-alarm channel

Python command:

```text
SetFallVolume
```

Wire command:

```text
setVolume
```

Direction:

```text
SET
```

Status:

**Fork**

Example:

```json
{
  "type": "fall",
  "total": 10,
  "volume": 6
}
```

Normalised event:

```text
FallVolumeEvent
```

---

# `onVolume`

Direction:

```text
PUSH
```

Status:

**Fork**

Purpose:

```text
Mower volume configuration update
```

The push handler reuses:

```text
GetVolume
```

parsing.

---

# Lift/move-up warning

The mower settings branch also registers:

```text
onMoveupWarning
```

Python message:

```text
OnMoveUpWarning
```

Direction:

```text
PUSH
```

Normalised event:

```text
MoveUpWarningEvent
```

This is separate from the dedicated lifted-alarm volume channel.

Conceptually:

```text
move-up warning enabled/state
```

and:

```text
fall alarm volume
```

are two different protocol concepts.

---

# Compact command reference

| Wire name          | Python                        | Direction | Event/result                      | Status                  |
| ------------------ | ----------------------------- | --------- | --------------------------------- | ----------------------- |
| `clean_V2`         | `CleanV2`                     | EXECUTE   | `StateEvent`                      | Upstream                |
| `getCleanInfo_V2`  | `GetCleanInfoV2`              | GET       | `StateEvent`                      | Upstream                |
| `charge`           | `Charge`                      | EXECUTE   | `StateEvent`                      | Upstream                |
| `getChargeState`   | `GetChargeState`              | GET       | `StateEvent`                      | Upstream                |
| `getStats`         | `GetStats`                    | GET       | `StatsEvent`                      | Upstream                |
| `onStats`          | `OnStats`                     | PUSH      | `StatsEvent`                      | Upstream/Fork extension |
| `getTotalStats`    | `GetTotalStats`               | GET       | `TotalStatsEvent`                 | Upstream                |
| `reportStats`      | `ReportStats`                 | REPORT    | `ReportStatsEvent`                | Upstream                |
| `getTrueDetect`    | `GetTrueDetect`               | GET       | `TrueDetectEvent`                 | Upstream                |
| `setTrueDetect`    | `SetTrueDetect`               | SET       | `TrueDetectEvent`                 | Upstream                |
| `getBorderSwitch`  | `GetBorderSwitch`             | GET       | `BorderSwitchEvent`               | Upstream                |
| `setBorderSwitch`  | `SetBorderSwitch`             | SET       | `BorderSwitchEvent`               | Upstream                |
| `getRecognization` | `GetRecognization`            | GET       | `AiRecognitionEvent`              | Fork                    |
| `setRecognization` | `SetRecognization`            | SET       | `AiRecognitionEvent`              | Fork                    |
| `onRecognization`  | `OnRecognization`             | PUSH      | `AiRecognitionEvent`              | Fork                    |
| `getHumanoidAI`    | `GetHumanoidAi`               | GET       | `HumanoidAiEvent`                 | Fork                    |
| `setHumanoidAI`    | `SetHumanoidAi`               | SET       | `HumanoidAiEvent`                 | Fork                    |
| `onHumanoidAI`     | `OnHumanoidAi`                | PUSH      | `HumanoidAiEvent`                 | Fork                    |
| `getNarrowAdapt`   | `GetNarrowAdapt`              | GET       | `NarrowAdaptEvent`                | Fork                    |
| `setNarrowAdapt`   | `SetNarrowAdapt`              | SET       | `NarrowAdaptEvent`                | Fork                    |
| `onNarrowAdapt`    | `OnNarrowAdapt`               | PUSH      | `NarrowAdaptEvent`                | Fork                    |
| `getAnimProtect`   | `GetAnimalProtection`         | GET       | `AnimalProtectionEvent`           | Fork                    |
| `setAnimProtect`   | `SetAnimalProtection`         | SET       | `AnimalProtectionEvent`           | Fork                    |
| `onAnimProtect`    | `OnAnimalProtection`          | PUSH      | `AnimalProtectionEvent`           | Fork                    |
| `setRainDelay`     | `SetRainDelay`                | SET       | later `RainDelayEvent`            | Fork                    |
| `onRainDelay`      | `OnRainDelay`                 | PUSH      | `RainDelayEvent`                  | Fork                    |
| `onProtectState`   | `OnProtectState`              | PUSH      | `ProtectStateEvent`               | Fork                    |
| `getVolume`        | `GetVolume`                   | GET       | `VolumeEvent` / `FallVolumeEvent` | Upstream/Fork           |
| `setVolume`        | `SetVolume` / `SetFallVolume` | SET       | volume state                      | Upstream/Fork           |
| `onVolume`         | `OnVolume`                    | PUSH      | volume events                     | Fork                    |
| `onMoveupWarning`  | `OnMoveUpWarning`             | PUSH      | `MoveUpWarningEvent`              | Fork                    |

---

# GET/SET/PUSH pattern

Many mower settings follow a consistent three-message pattern:

```text
GET current value
       │
       ▼
normalised Event
       ▲
       │
SET new value

and optionally:

external/app/device change
       │
       ▼
PUSH on...
       │
       ▼
same Event
```

Example:

```text
getNarrowAdapt
      │
      ▼
NarrowAdaptEvent
      ▲
      │
setNarrowAdapt

onNarrowAdapt
      │
      └──────► NarrowAdaptEvent
```

This design allows a consuming integration to stay synchronised when settings are changed through the official ECOVACS app.

---

# Protocol names versus client names

The ECOVACS protocol and Python client do not always use identical naming conventions.

Examples:

```text
Protocol             Python

mowedArea         →  mowed_area
getAnimProtect    →  GetAnimalProtection
setAnimProtect    →  SetAnimalProtection
getHumanoidAI     →  GetHumanoidAi
getRecognization  →  GetRecognization
isRainProtect     →  is_rain_protect
```

The documentation should preserve both names.

Protocol names are useful when analysing logs.

Python names are useful when working with `deebot_client`.

---

# Command acknowledgement versus state update

A successful command acknowledgement does not always mean that the corresponding state event is generated from the acknowledgement itself.

Rain configuration is an important example.

```text
setRainDelay
      │
      ▼
ACK: code = 0
      │
      ▼
command accepted
```

The actual resulting configuration arrives separately through:

```text
onRainDelay
      │
      ▼
RainDelayEvent
```

When implementing new commands, always determine whether state comes from:

```text
command response
```

or:

```text
later push message
```

or both.

---

# Shared protocol abstractions

Some GOAT protocol support is implemented through code originally designed for DEEBOT vacuum robots.

This leads to generic terms such as:

```text
clean
cleaning
room
cleanings
CleanAction
CleanMode
```

For GOAT development these may correspond to:

```text
mow
mowing
zone
mowing passes/jobs
```

Do not rename protocol values themselves.

Instead, translate them only at the user-facing integration layer.

---

# Model scope

Current protocol evidence comes from several sources:

```text
upstream shared GOAT hardware profiles
```

and:

```text
O1200-specific development/protocol investigation
```

Commands already wired upstream to all reviewed GOAT profiles have stronger cross-model implementation evidence.

New mower settings discovered in the development branch should currently be treated as:

```text
O1200 verified implementation scope
```

unless separately observed on another model.

---

# Adding a protocol entry

When documenting a newly discovered command or message, record:

| Field        | Description                            |
| ------------ | -------------------------------------- |
| Wire name    | Exact ECOVACS `NAME`                   |
| Python class | `deebot_client` implementation         |
| Direction    | GET / SET / EXECUTE / PUSH / REPORT    |
| Payload      | Relevant fields                        |
| Event        | Normalised event                       |
| Model        | Device where observed                  |
| Firmware     | Firmware where captured                |
| Branch       | Upstream or development implementation |
| Tests        | Relevant test coverage                 |
| Behaviour    | Physical/app correlation               |
| Unknowns     | Anything still inferred                |

Avoid publishing credentials or device-specific identifiers.

---

# Sanitised protocol examples

Protocol examples should include only fields needed to explain behaviour.

Prefer:

```json
{
  "enable": 1,
  "delay": 180
}
```

over a complete raw cloud/MQTT message containing:

```text
account information
device identifiers
serial numbers
authentication tokens
cloud routing identifiers
precise map/location data
```

Raw logs should not be committed directly to the documentation repository.

---

# Known research gaps

Important GOAT protocol areas that are not yet fully mapped include:

```text
cutting height
mowing speed
mowing efficiency/mode
exact app mapping of AI controls
explicit estimated-duration/ETA field
zone-name retrieval
O1200 selected-zone command
multi-zone ordering
scheduling
map-specific mower commands
full rain-delay lifecycle
object-detection reports
```

These should be added to this reference as protocol evidence becomes available.

---

# Relevant upstream source files

* [`deebot_client/commands/json/clean.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/clean.py)
* [`deebot_client/commands/json/charge.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/charge.py)
* [`deebot_client/commands/json/charge_state.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/charge_state.py)
* [`deebot_client/commands/json/stats.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/stats.py)
* [`deebot_client/messages/json/stats.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/messages/json/stats.py)
* [`deebot_client/commands/json/true_detect.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/true_detect.py)
* [`deebot_client/commands/json/border_switch.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/border_switch.py)

# Relevant development source files

* [`deebot_client/commands/json/recognization.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/recognization.py)
* [`deebot_client/commands/json/humanoid_ai.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/humanoid_ai.py)
* [`deebot_client/commands/json/narrow_adapt.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/narrow_adapt.py)
* [`deebot_client/commands/json/animal_protection.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/animal_protection.py)
* [`deebot_client/commands/json/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/rain_delay.py)
* [`deebot_client/messages/json/mower_settings.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/mower_settings.py)
* [`deebot_client/messages/json/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/rain_delay.py)
* [`deebot_client/messages/json/protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/protect_state.py)
* [`deebot_client/commands/json/stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/commands/json/stats.py)
* [`deebot_client/messages/json/stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/messages/json/stats.py)

# Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mowing control](mowing-control.md)
* [Zone and area mowing](zones-and-areas.md)
* [Mowing progress and statistics](progress-and-statistics.md)
* [Mower settings](settings.md)
* [Rain and protection](rain-and-protection.md)
* [Obstacle avoidance and AI](obstacle-and-ai.md)
* Testing status *(planned)*
* Known limitations *(planned)*
* Home Assistant integration *(planned)*
