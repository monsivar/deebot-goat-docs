# GOAT protocol observations

This file is the working research log for ECOVACS GOAT protocol investigation.

Unlike the files under `docs/`, entries here may contain incomplete interpretations, open questions and hypotheses.

The purpose is to preserve evidence before it is promoted into the main documentation.

Last updated: **2026-08-23**

## Research principles

Each observation should distinguish between:

```text
What was done
What the app showed
What the mower physically did
What protocol traffic was observed
What the client currently implements
What is still inferred
```

A protocol field name alone is not considered proof of its physical meaning.

---

# Evidence labels

Use the following labels.

| Label        | Meaning                                     |
| ------------ | ------------------------------------------- |
| `APP`        | Observed in the official ECOVACS app        |
| `DEVICE`     | Physical mower behaviour observed           |
| `PROTOCOL`   | Real mower/cloud protocol traffic observed  |
| `CLIENT`     | Implemented in `deebot_client`              |
| `TEST`       | Covered by automated Python tests           |
| `HYPOTHESIS` | Plausible interpretation, not yet confirmed |
| `OPEN`       | Requires further investigation              |

An observation may have several labels.

Example:

```text
Evidence: APP + DEVICE + PROTOCOL
```

---

# Observation template

Use this template for future captures.

````markdown
## YYYY-MM-DD — Short observation title

### Context

Model:
Hardware ID:
Firmware:
App version:
Client branch:
Home Assistant branch:

### User action

Describe exactly what was changed or triggered.

### App observation

Describe what the ECOVACS app displayed.

### Physical mower behaviour

Describe what the mower actually did.

### Protocol observation

Direction:
Wire name:
Payload/message:

```json
{
}
````

### Client mapping

Command:
Message:
Event:
Capability:

### Interpretation

What can safely be concluded?

### Confidence

Evidence:

### Open questions

* ...

````

---

# Sanitisation rules

Do not commit complete raw logs to this public repository.

Remove or replace:

```text
account IDs
device IDs
serial numbers
authentication tokens
cloud credentials
Wi-Fi information
precise property location
private map data
personally identifying information
````

Keep only the fields required to explain the behaviour.

For example, prefer:

```json
{
  "enable": 1,
  "delay": 180
}
```

over an entire MQTT message envelope.

---

# 2026 — Basic mowing lifecycle

## Context

Model:

```text
Physical GOAT test mower
```

Client implementation:

```text
CleanV2
GetCleanInfoV2
```

Evidence:

```text
APP + DEVICE + PROTOCOL + CLIENT
```

## User actions

The following sequence was performed through the ECOVACS app:

```text
Start mowing
Pause
Resume
Stop
Confirm stop
```

## Physical mower behaviour

Observed sequence:

```text
Start
  │
  ▼
Mowing
  │
  ▼
Pause
  │
  ▼
Paused
  │
  ▼
Resume
  │
  ▼
Mowing
  │
  ▼
Stop
  │
  ▼
Job terminated
```

## Protocol/client mapping

The shared client represents these operations through:

```text
clean_V2
```

with:

```text
start
pause
resume
stop
```

## Interpretation

The physical mower lifecycle matches the control abstraction already implemented by `CleanV2`.

This confirms the behaviour and protocol flow.

It does not by itself mean every action was independently end-to-end invoked through every consumer integration.

---

# Return to charging station

## User action

The ECOVACS app's dock/return command was selected.

## Physical behaviour

The mower returned toward the charging station.

## Client mapping

```text
Charge
```

Wire command:

```text
charge
```

Conceptual payload:

```json
{
  "act": "go"
}
```

Expected client state:

```text
State.RETURNING
```

and once charging/docked:

```text
State.DOCKED
```

## Confidence

```text
APP + DEVICE + PROTOCOL + CLIENT
```

---

# Selected-zone mowing

## User action

A single named lawn zone was selected in the ECOVACS app.

One observed zone name during testing was:

```text
Sentrum
```

The selected zone was then started as a mowing job.

The job was subsequently:

```text
paused
resumed
stopped
```

## Physical behaviour

The mower operated as a selected-zone job rather than a generic whole-lawn operation.

## Client context

The generic client supports:

```text
CleanAreaV2
```

with numeric area/target values.

However, the reviewed upstream O1200 profile does not currently expose an area callable.

## Interpretation

Confirmed:

```text
named-zone mowing exists on the physical mower/app
```

Not yet confirmed:

```text
exact GOAT wire command
exact zone-ID field
exact mapping to SPOT_AREA
exact O1200 CleanAreaV2 compatibility
```

## Confidence

```text
APP + DEVICE + PROTOCOL
```

Client mapping:

```text
OPEN
```

---

# Zone display name versus protocol identifier

## Observation

The ECOVACS app uses human-readable names for zones.

Low-level client area commands use numeric values.

## Hypothesis

The architecture is likely:

```text
human-readable zone name
          │
          ▼
internal zone ID
          │
          ▼
mowing command
```

## Status

```text
HYPOTHESIS + OPEN
```

## Required next evidence

Capture a controlled test where:

```text
zone A is started
zone B is started
```

and compare only the differing protocol fields.

This should reveal the zone identifier.

---

# Current mowing statistics — `mowedArea`

## Context

Research branch:

```text
feature/mower-stats-progress
```

Strongest current model evidence:

```text
GOAT O1200 LiDAR
```

## Protocol field

```text
mowedArea
```

## Client mapping

```text
StatsEvent.mowed_area
```

The field is parsed from:

```text
getStats
onStats
```

## Example sanitised fixture

```json
{
  "area": 2889500,
  "time": 11269,
  "mowedArea": 1005475
}
```

## Interpretation

Strong evidence exists that:

```text
mowedArea
```

is useful as current-job progress information.

The current progress implementation preserves the raw value.

## Confidence

```text
PROTOCOL + CLIENT + TEST
```

---

# Mowing percentage

## Derived interpretation

Where:

```text
area
```

and:

```text
mowedArea
```

describe total and completed area for the same operation, Home Assistant can calculate:

```text
mowedArea / area × 100
```

## Status

```text
DERIVED
```

This percentage is not currently treated as a separate ECOVACS protocol field.

---

# Estimated mowing duration

## App observation

When a mowing job is started, the ECOVACS app presents an estimated job duration.

## Development interpretation

For the researched mower-progress capability, Home Assistant currently interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

when:

```text
mowing_job_progress = True
```

## Important distinction

This interpretation is model-gated.

Do not generalise:

```text
StatsEvent.time = ETA
```

to every ECOVACS device.

## Open question

Determine whether:

```text
time
```

is itself the ECOVACS app's estimate, or whether another explicit duration/ETA field exists.

## Confidence

```text
APP + CLIENT + TEST
```

Protocol semantics:

```text
OPEN
```

---

# Rain configuration

## Strongest current model evidence

```text
GOAT O1200 LiDAR
```

## Wire command

```text
setRainDelay
```

## Known fields

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

## Known delay values

Accepted by the current implementation:

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

## Client mapping

```text
SetRainDelay
RainDelayEvent
OnRainDelay
```

## Confidence

```text
PROTOCOL + CLIENT + TEST + DEVICE
```

---

# Rain configuration update

## Wire message

```text
onRainDelay
```

Example:

```json
{
  "enable": 1,
  "delay": 180
}
```

## Client event

```python
RainDelayEvent(
    enabled=True,
    delay=180,
)
```

## Interpretation

This message represents rain configuration.

It should not be interpreted as evidence that rain is currently falling.

---

# Active rain protection

## Test condition

Actual rain was correlated with a protection-state message.

## Wire message

```text
onProtectState
```

## Relevant observed values

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

## Client event

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

## Safe conclusion

During the observed rain condition:

```text
isRainProtect = 1
```

was associated with active rain protection.

## Confidence

```text
DEVICE + PROTOCOL + CLIENT + TEST
```

---

# `isRainDelay`

## Observation

During actual rain:

```text
isRainDelay = 0
```

## Hypothesis

A possible interpretation is:

```text
isRainDelay = 1
```

during the post-rain waiting period.

## Status

```text
HYPOTHESIS + OPEN
```

This must not be promoted to confirmed documentation until directly observed.

---

# Required rain lifecycle experiment

Capture the complete sequence:

```text
dry
 │
 ▼
rain starts
 │
 ▼
active rain protection
 │
 ▼
rain stops
 │
 ▼
post-rain wait
 │
 ▼
delay expires
 │
 ▼
ready/resume
```

At every transition record:

```text
timestamp
mower state
onRainDelay
onProtectState
ECOVACS app status
physical mower behaviour
```

Primary question:

```text
When and why does isRainDelay become 1?
```

---

# Animal protection configuration

## Wire commands

```text
getAnimProtect
setAnimProtect
```

## Fields

```text
enable
start
end
```

Example:

```json
{
  "enable": 1,
  "start": "23:45",
  "end": "06:30"
}
```

## Client mapping

```text
GetAnimalProtection
SetAnimalProtection
AnimalProtectionEvent
OnAnimalProtection
```

## Interpretation

Animal protection is a scheduled configuration rather than a simple boolean toggle.

## Confidence

```text
PROTOCOL + CLIENT + TEST
```

Physical behaviour during the active schedule:

```text
OPEN
```

---

# Animal protection runtime state

## Protection field

```text
isAnimProtect
```

Client mapping:

```text
ProtectStateEvent.is_anim_protect
```

## Open question

Determine exactly when this becomes true relative to:

```text
configured start time
configured end time
active mowing job
```

and what physical behaviour changes when active.

---

# AI recognition

## Wire commands

```text
getRecognization
setRecognization
```

Push:

```text
onRecognization
```

## Field

```text
state
```

Example enabled value:

```json
{
  "state": 1
}
```

## Client mapping

```text
AiRecognitionEvent
```

## Confidence

```text
PROTOCOL + CLIENT + TEST
```

Exact ECOVACS app label:

```text
OPEN
```

Physical behavioural effect:

```text
OPEN
```

---

# Humanoid AI

## Wire commands

```text
getHumanoidAI
setHumanoidAI
```

Push:

```text
onHumanoidAI
```

## Field

```text
enable
```

Example:

```json
{
  "enable": 1
}
```

## Client mapping

```text
HumanoidAiEvent
```

Current implementation description:

```text
Smart mowing with avoidance
```

## Confidence

```text
PROTOCOL + CLIENT + TEST
```

## Open questions

Determine:

```text
official app label
whether this specifically relates to people
whether it changes general obstacle avoidance
interaction with AI recognition
interaction with TrueDetect
```

---

# Narrow passage adaptation

## Wire commands

```text
getNarrowAdapt
setNarrowAdapt
```

Push:

```text
onNarrowAdapt
```

## Field

```text
state
```

## Client mapping

```text
NarrowAdaptEvent
```

## Current interpretation

```text
Narrow passage adaptation
```

## Confidence

```text
PROTOCOL + CLIENT + TEST
```

Physical navigation effect:

```text
OPEN
```

---

# Recommended narrow-passage experiment

Use the same mapped narrow passage and run controlled tests with:

```text
NarrowAdapt OFF
NarrowAdapt ON
```

Keep other settings unchanged.

Record:

```text
whether mower enters passage
whether it mows inside passage
route chosen
number of retries
minimum clearance
app warnings/errors
relevant protocol messages
```

---

# TrueDetect

## Wire commands

```text
getTrueDetect
setTrueDetect
```

## Client status

```text
Upstream implemented
```

## Open issue

The exact relationship between:

```text
TrueDetect
Recognization
HumanoidAI
```

on GOAT mowers remains unclear.

A systematic app correlation test is required.

---

# AI/app-setting correlation experiment

For each ECOVACS app option:

```text
1. record current values
2. start protocol capture
3. change exactly one app setting
4. stop capture
5. identify changed command
6. restore original setting
7. repeat
```

The target result is a table such as:

| App label | Wire command       | Field    | Confirmed |
| --------- | ------------------ | -------- | :-------: |
| unknown   | `setRecognization` | `state`  |  pending  |
| unknown   | `setHumanoidAI`    | `enable` |  pending  |
| unknown   | `setNarrowAdapt`   | `state`  |  pending  |
| unknown   | `setTrueDetect`    | boolean  |  pending  |

Do not fill the app-label column from guesswork.

---

# Volume channels

## System volume

Protocol family:

```text
getVolume
setVolume
```

Known channel:

```text
sys
```

Example:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 5
}
```

## Lifted-alarm volume

Known channel:

```text
fall
```

Example:

```json
{
  "type": "fall",
  "total": 10,
  "volume": 5
}
```

Client event:

```text
FallVolumeEvent
```

## Interpretation

System audio volume and lifted-mower alarm volume are separate logical settings using the same command family.

## Confidence

```text
PROTOCOL + CLIENT + TEST
```

---

# Move-up/lift warning

Push name:

```text
onMoveupWarning
```

Client event:

```text
MoveUpWarningEvent
```

This should be kept conceptually separate from:

```text
fall volume
```

One controls warning behaviour/state.

The other controls the associated alarm-volume channel.

---

# Protection-state unresolved fields

The following fields are mapped but not yet fully understood.

## `isEStop`

Likely emergency-stop-related.

Status:

```text
OPEN
```

Required test:

Trigger and reset emergency stop while capturing `onProtectState`.

---

## `isLocked`

Lock-related.

Do not assume it is identical to:

```text
ChildLockEvent
```

Status:

```text
OPEN
```

Required test:

Toggle child lock while observing `isLocked`.

---

## `isPinCode`

PIN/security-related.

Possible meanings are currently unknown.

Status:

```text
OPEN
```

Do not publish a user-facing interpretation until correlated.

---

## `isPrepareDataSuccess`

Observed field with unclear user-facing purpose.

Status:

```text
OPEN
```

Likely best retained for diagnostics/research unless future evidence shows a meaningful feature.

---

# Cutting height research target

## Current status

```text
NOT MAPPED
```

## Goal

Identify:

```text
GET command
SET command
push message
raw value
unit
minimum
maximum
step
model support
```

## Recommended experiment

1. Record current cutting height in the ECOVACS app.
2. Start a clean protocol capture.
3. Change only cutting height by one step.
4. Stop capture.
5. Compare new messages/commands with baseline.
6. Change height again.
7. Compare which field changes consistently.
8. Restore original value.

Avoid changing other mower settings during the capture.

---

# Mowing speed research target

## Current status

```text
NOT MAPPED
```

## Goal

Determine whether mower speed is:

```text
discrete enum
numeric value
part of another mowing-mode object
```

## Recommended capture

Change only the speed option in the app and compare outgoing protocol values.

If several levels exist, capture every level.

---

# Mowing efficiency/mode research target

## Current status

```text
NOT MAPPED FOR GOAT
```

Do not assume the generic DEEBOT:

```text
efficiency_mode
```

capability is applicable.

## Required evidence

Map every app option individually to:

```text
wire command
field
raw value
push message
```

---

# Zone-ID research target

## Priority

```text
HIGH
```

## Goal

Identify the exact command and zone identifier used by the O1200.

## Recommended experiment

Create or use two already-defined zones with clearly different names.

Run separate captures:

```text
start zone A
stop

start zone B
stop
```

Compare the outgoing start commands.

Any field whose value consistently changes with the selected zone is a candidate identifier.

Then repeat zone A to verify the same value returns.

---

# Multi-zone research target

Once the single-zone identifier is known, test:

```text
zone A
zone B
zone A + B
zone B + A
```

Questions:

```text
Does one command contain multiple IDs?
Does order affect the payload?
Does order affect physical mowing?
Does the mower choose its own route?
```

---

# Zone-name research target

After identifying zone IDs, determine where human-readable names originate.

Search protocol traffic for:

```text
zone ID
known app zone name
map metadata
area metadata
```

The desired result is a mapping:

```text
zone_id → display_name
```

without depending on manually configured Home Assistant names.

---

# Scheduling research target

## Current status

```text
NOT MAPPED
```

Capture operations for:

```text
create schedule
edit schedule
disable schedule
enable schedule
delete schedule
change weekday
change start time
change selected zone
```

Important fields to identify:

```text
schedule ID
weekdays
time
enabled
zone selection
mowing mode
timezone
```

---

# Map research target

GOAT map support remains a separate research area.

Potential objects include:

```text
lawn boundary
zones
no-go areas
station position
mower position
navigation route
mowing trace
```

Before implementing map support, establish:

```text
coordinate system
origin
scale
orientation
object IDs
map revision behaviour
```

Do not assume DEEBOT vacuum-map semantics apply unchanged.

---

# Promotion from research to documentation

An observation should normally move from this file into `docs/` when:

```text
wire name is known
relevant fields are known
model scope is known
interpretation is sufficiently supported
```

Ideal evidence also includes:

```text
client implementation
automated tests
physical-device verification
```

After promotion, this research entry can remain as historical evidence but should link to the corresponding documentation page.

---

# Current research priorities

Recommended next investigation order:

```text
1. cutting height
2. mowing mode / efficiency
3. mowing speed
4. O1200 zone-ID command
5. exact AI app-setting mapping
6. post-rain delay lifecycle
7. animal-protection runtime behaviour
8. zone names/metadata
9. scheduling
10. map semantics
```

The order may change as new protocol evidence appears.

---

# Related documentation

* [`docs/overview.md`](../docs/overview.md)
* [`docs/supported-models.md`](../docs/supported-models.md)
* [`docs/mowing-control.md`](../docs/mowing-control.md)
* [`docs/zones-and-areas.md`](../docs/zones-and-areas.md)
* [`docs/progress-and-statistics.md`](../docs/progress-and-statistics.md)
* [`docs/settings.md`](../docs/settings.md)
* [`docs/rain-and-protection.md`](../docs/rain-and-protection.md)
* [`docs/obstacle-and-ai.md`](../docs/obstacle-and-ai.md)
* [`docs/protocol-reference.md`](../docs/protocol-reference.md)
* [`docs/testing-status.md`](../docs/testing-status.md)
* [`docs/known-limitations.md`](../docs/known-limitations.md)
* [`docs/home-assistant.md`](../docs/home-assistant.md)
