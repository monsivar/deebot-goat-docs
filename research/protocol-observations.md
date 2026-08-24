# GOAT protocol observations

This file is the working research log for ECOVACS GOAT protocol investigation.

Unlike files under `docs/`, entries here may contain incomplete interpretations, hypotheses and open questions.

Last updated: **2026-08-24**

## Research principles

Each observation should distinguish:

```text
What was done
What the app showed
What the mower physically did
What protocol traffic was observed
What the client implements
What is still inferred
```

A protocol field name alone is not proof of complete physical semantics.

---

# Evidence labels

| Label | Meaning |
| --- | --- |
| `APP` | Observed in official ECOVACS app |
| `DEVICE` | Physical mower behaviour observed |
| `PROTOCOL` | Real mower/cloud traffic observed |
| `CLIENT` | Implemented in `deebot_client` development |
| `TEST` | Covered by automated tests |
| `HA` | Implemented/tested in Home Assistant development |
| `DERIVED` | Calculated from protocol/client fields |
| `HYPOTHESIS` | Plausible but unconfirmed interpretation |
| `OPEN` | Requires more research |

---

# Sanitisation rules

Do not publish complete raw logs.

Remove:

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
```

Prefer minimal payloads.

---

# Observation template

Use this structure for future captures:

````markdown
## YYYY-MM-DD — Title

### Context

Model:
Hardware ID:
Firmware:
App version:
Client branch:
Home Assistant branch:

### User action

...

### App observation

...

### Physical mower behaviour

...

### Protocol observation

Direction:
Wire name:

```json
{}
```

### Client mapping

Command:
Message:
Event:
Capability:

### Interpretation

...

### Confidence

Evidence:

### Open questions

- ...
````

---

# Basic mowing lifecycle

## Observation

Actions performed through the app:

```text
Start
Pause
Resume
Stop
Confirm stop
```

Physical behaviour followed the expected lifecycle.

Client/protocol representation:

```text
clean_V2
start
pause
resume
stop
```

Evidence:

```text
APP + DEVICE + PROTOCOL + CLIENT
```

---

# Return to charging station

App dock/return action caused the mower to return toward the station.

Client:

```text
Charge
```

Wire:

```text
charge
```

Payload:

```json
{
  "act": "go"
}
```

Expected normalised states:

```text
RETURNING
DOCKED
```

Evidence:

```text
APP + DEVICE + PROTOCOL + CLIENT
```

---

# Selected-zone mowing

A named zone was selected in the ECOVACS app.

One observed name:

```text
Sentrum
```

The job was:

```text
started
paused
resumed
stopped
```

Physical behaviour confirmed a zone-scoped mowing job.

Evidence:

```text
APP + DEVICE + PROTOCOL
```

Important:

```text
selected-zone start
```

and:

```text
area-parameter configuration
```

are separate protocol questions.

The area-parameter work described below establishes a concrete `areaID`, but the selected-zone start path should still be explicitly correlated to that ID before being considered solved.

---

# O1200 `areaID` and area parameters

## Context

Related development:

```text
PR #1767
PR #1768
Issue #1610
```

Model:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

## Protocol family

```text
getAreaParameter
setAreaParameter
onAreaParameter
```

## Area record

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

Example setter:

```json
{
  "areaID": "2",
  "mowHeightLevel": 10,
  "cutMode": 7,
  "obstacleHeight": 1,
  "angle": 136
}
```

Example reported state:

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

## Client mapping

```text
AreaParameter
AreaParameterEvent
GetAreaParameter
SetAreaParameter
OnAreaParameter
settings.area_parameter
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

## Safe conclusion

The O1200 has an ECOVACS area/zone identifier called:

```text
areaID
```

for this settings protocol family.

This is stronger than the earlier generic assumption that a numeric target probably identifies a zone.

## Open question

Confirm whether the selected-zone mowing start command uses the same `areaID` directly.

Status:

```text
OPEN
```

---

# `setAreaParameter` complete-tuple behaviour

The setter sends:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

together.

This means higher-level integrations should preserve sibling values when changing one field.

Recommended safe write:

```text
read latest AreaParameterEvent
        │
        ▼
find areaID
        │
        ▼
copy all values
        │
        ▼
change one requested field
        │
        ▼
SetAreaParameter
        │
        ▼
wait for onAreaParameter
```

Evidence:

```text
PROTOCOL + CLIENT
```

---

# Cutting height — semantic mapping implemented in HA development

## Protocol layer

Known O1200 field:

```text
mowHeightLevel
```

Python:

```text
mow_height_level
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

## HA semantic layer

Branch:

```text
monsivar/core
feature/ecovacs-area-parameter
```

implements:

```python
height_cm = (17 - level) / 2
level = 17 - height_cm * 2
```

with:

```text
minimum = 3.0 cm
maximum = 8.0 cm
step    = 0.5 cm
```

and automated helper tests covering all implemented levels:

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

Evidence:

```text
HA + TEST
```

## What is now known

```text
zone-specific cutting-height raw field exists
GET state exists
SET command exists
PUSH state exists
software conversion to centimetres exists
implemented range is 3.0–8.0 cm
implemented step is 0.5 cm
```

## What is still open

```text
independent physical/app verification of every level
confirmation that raw 1..11 is the complete protocol-valid range
firmware/region differences
cross-model mapping
```

The research target is now **validation of an implemented semantic table**, not discovery of the O1200 height formula.

# Zone cut mode / mowing speed — semantic mapping implemented in HA development

Known raw field:

```text
cutMode
```

Python:

```text
cut_mode
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

The HA development branch maps:

```text
7 → Gentle / 0.35 m/s
4 → Efficient / 0.5 m/s
```

and tests both directions.

Evidence:

```text
HA + TEST
```

## Safe current conclusion

The researched O1200 has a software semantic mapping for **zone mowing speed through `cutMode`**.

Therefore:

```text
mowing speed completely unmapped
```

is no longer an accurate statement.

## Still open

```text
independent official-app correlation
independent physical speed validation
additional possible cutMode/speed values
cross-model applicability
relationship to generic efficiency_mode
whether a separate/global speed command also exists
```

# Zone obstacle/environment mode — semantic mapping implemented in HA development

Known raw field:

```text
obstacleHeight
```

Python:

```text
obstacle_height
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

The HA development branch maps:

```text
1 → flat terrain / short grass <10 cm
2 → normal environment <15 cm
3 → high grass environment <20 cm
```

and tests both directions.

Evidence:

```text
HA + TEST
```

## Safe current conclusion

The O1200 raw field is no longer semantically unmapped in software.

The branch interprets it as an environment/obstacle-avoidance mode with three height-threshold labels.

## Still open

```text
exact official app wording
physical behavioural effect
whether the threshold refers to grass/environment height or a sensor obstacle-height threshold
cross-model applicability
```

It remains separate from TrueDetect, Recognization, HumanoidAI and other avoidance settings.

# Zone mowing angle — conversion implemented in HA development

Known raw field:

```text
angle
```

associated with:

```text
areaID
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

The HA development branch implements:

```python
user_degrees = (270 - raw_angle) % 360
raw_angle = (270 - user_degrees) % 360
```

with helper tests including:

```text
180 → 90°
145 → 125°
216 → 54°
0   → 270°
```

Evidence:

```text
HA + TEST
```

## What remains open

Reviewed upstream also exposes global:

```text
GetCutDirection
SetCutDirection
CutDirectionEvent.angle
```

The remaining research question is the relationship:

```text
AreaParameter.angle
          ?
          │
          ▼
global cut_direction
```

Possible hypotheses remain:

```text
global default vs zone override
model-generation difference
separate app controls
```

The raw-to-user angle conversion itself should no longer be listed as unresolved.

# Area ID versus zone display name — resolved for tested O1200

## Development

PR:

```text
#1774
```

Client capability:

```text
CapabilityClean.areas
```

Command:

```text
GetAreaSet
```

Wire:

```text
getAreaSet
```

Request:

```json
{
  "mid": "1",
  "aid": "0",
  "type": "ar"
}
```

The response contains compressed:

```text
subsets
```

which are decoded into:

```text
RoomsEvent
```

## Real-device result

Model:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
firmware 1.13.10
```

Observed/decoded mapping:

```text
4 → Østkanten
1 → Sentrum
2 → Vestkanten
```

## Live validation

A live test without the ECOVACS app open confirmed:

```text
subscribe RoomsEvent
      │
      ▼
refresh triggers GetAreaSet
      │
      ▼
mower returns data
      │
      ▼
RoomsEvent contains expected IDs/names
```

Evidence:

```text
APP + DEVICE + PROTOCOL + CLIENT + TEST
```

## Conclusion

For the tested O1200, the project now has a confirmed:

```text
area ID → human-readable display name
```

path.

This research item is promoted to:

```text
docs/area-names.md
```

## Still open

```text
selected-zone start target ↔ known area ID
cross-model area-name support
zone geometry/full map support
```

# Area ID versus selected-zone start target

This is now a more precise research target.

Instead of searching for "any possible zone ID", compare known:

```text
areaID
```

values with selected-zone start payloads.

Recommended experiment:

```text
getAreaParameter
    │
    └── record areaID A and B

start zone A
start zone B
    │
    ▼
compare start payload target values
```

Goal:

```text
prove selected-zone target == areaID
```

or show that another ID namespace is used.

Priority:

```text
HIGH
```

---

# Multi-zone start research

Once the single-zone relationship is confirmed, test:

```text
A
B
A + B
B + A
```

Questions:

```text
Does one command contain multiple area IDs?
What separator is used?
Does order matter?
Does physical mowing order match payload order?
```

---

# Current mowing statistics — `mowedArea`

Development branch:

```text
feature/mower-stats-progress
```

Field:

```text
mowedArea
```

Client:

```text
StatsEvent.mowed_area
```

Parsed from:

```text
getStats
onStats
```

Example:

```json
{
  "area": 2889500,
  "time": 11269,
  "mowedArea": 1005475
}
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

Strongest model:

```text
GOAT O1200
```

---

# Mowing percentage

Derived:

```text
mowedArea / area × 100
```

Status:

```text
DERIVED + HA
```

Not a separate ECOVACS protocol field.

---

# Estimated mowing duration

The app shows an estimated duration.

For:

```text
mowing_job_progress=True
```

Home Assistant currently interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

Evidence:

```text
APP + CLIENT + TEST + HA
```

Open protocol question:

```text
Is this exactly the app's estimate?
Is there another explicit ETA field?
How does time change during a job?
```

---

# Rain configuration

Wire:

```text
setRainDelay
onRainDelay
```

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

Known implementation values:

```text
0–300 minutes
step 30 minutes
```

Client:

```text
SetRainDelay
RainDelayEvent
OnRainDelay
```

Evidence:

```text
PROTOCOL + CLIENT + TEST + DEVICE
```

---

# Active rain protection

Wire:

```text
onProtectState
```

Observed during actual rain:

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

Safe conclusion:

```text
isRainProtect = 1
```

can represent active rain protection.

Evidence:

```text
DEVICE + PROTOCOL + CLIENT + TEST
```

---

# `isRainDelay`

Actual-rain observation:

```text
isRainDelay = 0
```

Hypothesis:

```text
isRainDelay = 1
```

may represent the post-rain waiting period.

Status:

```text
HYPOTHESIS + OPEN
```

Required experiment:

```text
dry
rain starts
rain protection
rain stops
delay period
ready/resume
```

Capture state at every transition.

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

Client:

```text
AnimalProtectionEvent
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

Runtime field:

```text
isAnimProtect
```

in:

```text
ProtectStateEvent
```

Physical schedule behaviour remains incomplete.

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

Client:

```text
AiRecognitionEvent
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

Official app label and complete physical effect remain open.

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

Client:

```text
HumanoidAiEvent
```

Implementation description:

```text
Smart mowing with avoidance
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

Open:

```text
official app label
human-specific vs general avoidance
interaction with Recognization/TrueDetect
```

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

Client:

```text
NarrowAdaptEvent
```

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

Physical navigation effect still needs A/B testing.

---

# TrueDetect

Wire:

```text
getTrueDetect
setTrueDetect
```

Status:

```text
Upstream implemented
```

Relationship with:

```text
Recognization
HumanoidAI
obstacleHeight
```

remains incomplete.

---

# AI/app correlation method

For each official app control:

```text
1. record baseline
2. start capture
3. change exactly one control
4. stop capture
5. identify changed command/field
6. restore
7. repeat
```

Do not infer app labels from protocol class names alone.

---

# Volume channels

System:

```text
type = sys
```

Lifted/fall warning:

```text
type = fall
```

Both use:

```text
getVolume / setVolume
```

but represent separate logical settings.

Evidence:

```text
PROTOCOL + CLIENT + TEST
```

---

# Protection-state unresolved fields

Mapped:

```text
isEStop
isLocked
isPinCode
isPrepareDataSuccess
```

Open questions remain for exact user-facing semantics.

Do not assume:

```text
isLocked == child lock
```

without correlation.

---

# Mowing speed research target

Status:

```text
NOT MAPPED
```

Goal:

```text
identify app option
wire command
raw field/value
valid range/options
physical effect
```

This is now the clearest remaining unmapped core mowing parameter after area-parameter discovery.

---

# Scheduling research target

Capture:

```text
create
edit
enable
disable
delete
weekday change
time change
zone change
```

Identify:

```text
schedule ID
weekdays
time
enabled
zone selection
mowing settings
timezone
```

Status:

```text
OPEN
```

---

# Map research target

Potential GOAT map objects:

```text
lawn boundary
zones
no-go areas
station
mower position
route
mowing trace
```

Need:

```text
coordinate system
origin
scale
orientation
area IDs
map revisions
geometry semantics
```

Now that `areaID` is known in area-parameter traffic, it should be used as a search key when analysing map/zone metadata.

---

# Updated research priorities

After reconciling PR #1767/#1768 with the Home Assistant branch `feature/ecovacs-area-parameter`, the O1200 area-parameter research priorities are now:

```text
1. independently validate the 3.0–8.0 cm / 0.5 cm cutting-height table
2. validate cutMode 7 = Gentle/0.35 m/s and 4 = Efficient/0.5 m/s against app/device behaviour
3. validate obstacleHeight 1/2/3 environment-threshold semantics physically
4. clarify AreaParameter.angle ↔ global cut_direction
5. confirm areaID ↔ selected-zone start target
6. determine whether any additional/standalone speed control exists
7. test multi-zone start/order
8. cross-model area-parameter semantic verification
9. exact AI app-setting mapping
10. post-rain delay lifecycle
11. animal-protection runtime behaviour
12. scheduling
13. remaining live-map semantics and production map lifecycle
14. cross-model progress semantics
```

The following are **no longer discovery gaps for the researched O1200 HA development**:

```text
mowHeightLevel unit/range/step/software conversion
cutMode 7/4 semantic speed mapping
obstacleHeight 1/2/3 software semantic mapping
raw area-angle ↔ user-degree conversion
```

They remain appropriate targets for independent physical/app validation and cross-model reproduction.

# Promotion from research to documentation

Move a finding into `docs/` when:

```text
wire name known
fields known
model scope known
interpretation sufficiently supported
```

Ideal evidence also includes:

```text
client implementation
automated tests
physical verification
```

Area-parameter protocol structure has now been promoted into:

```text
docs/area-parameters.md
```

while raw-value semantics remain active research topics.

---

# Related documentation

- [`docs/overview.md`](../docs/overview.md)
- [`docs/supported-models.md`](../docs/supported-models.md)
- [`docs/mowing-control.md`](../docs/mowing-control.md)
- [`docs/zones-and-areas.md`](../docs/zones-and-areas.md)
- [`docs/area-parameters.md`](../docs/area-parameters.md)
- [`docs/area-names.md`](../docs/area-names.md)
- [`docs/progress-and-statistics.md`](../docs/progress-and-statistics.md)
- [`docs/settings.md`](../docs/settings.md)
- [`docs/rain-and-protection.md`](../docs/rain-and-protection.md)
- [`docs/obstacle-and-ai.md`](../docs/obstacle-and-ai.md)
- [`docs/protocol-reference.md`](../docs/protocol-reference.md)
- [`docs/testing-status.md`](../docs/testing-status.md)
- [`docs/known-limitations.md`](../docs/known-limitations.md)
- [`docs/home-assistant.md`](../docs/home-assistant.md)


# GOAT map research — promoted findings

The detailed map-development research was performed as an evidence-first sequence before the current stacked map PRs.

This section records only the findings that materially explain the implementation.

It is not a replacement for the full diagnostic/research notebook.

## Transport / presence

Observed on the researched O1200:

```text
normal MQ
    carries onPos / onMapTrack / onMI / onArI

JMQ
    not required for map-stream activation in controlled runs

appping
    confirmed live-stream trigger

presence lease
    approximately 300 seconds

renewal around 240 seconds
    resets lease
```

Evidence:

```text
PROTOCOL + DEVICE/STATE CORRELATION + REPEATED CONTROLLED RUNS
```

The production map stack does not yet implement this lifecycle.

## `getMI`

Both legacy and N-GIoT `getMI` controls could solicit:

```text
onMI
onArI
```

while presence was active.

The direct acknowledgement did not contain the retained map-bearing value.

The pushed events carried the data.

## `onMI` timing forms

Two stable O1200 representations were isolated:

```text
876-character form
    request-associated

52-character form
    cadence-associated (~60 s)
```

A controlled repeatability run supported that explicit `getMI` produced the 876 form promptly and did not reset the independent short-form cadence.

These are timing labels only.

## `onMI` static geometry

The request-associated form was reduced to a narrow production parser proposal.

Evidence supports:

```text
canonical Base64
trimmed LZMA-Alone framing
infoSize validation
s1 geometry record
eight-direction RLE
50-unit step
2,336 points
known boundary bounds
known open gap preserved
```

The geometry matches the independent reference viewer point-for-point.

This research became PR #1782.

## `onArI`

Complete type-0 snapshots were shown to use:

```text
serial/index chunking
trimmed LZMA-Alone
grouped/layered JSON
layer 1 persistent work-area geometry
same eight-direction RLE family
```

Work-area geometry is local rather than already registered to the main-map frame.

## AreaSet framing correction

A read-only scan of:

```text
198 getAreaSet type="ar" responses
17 Phase 2 captures
```

showed:

```text
internal trimmed-LZMA decompressed-size field
    matched decoded length: 198/198

envelope infoSize
    matched decoded length: 0/198
```

This corrected an earlier diagnostic false negative.

The rule is now implemented in PR #1788 and is scoped specifically to AreaSet.

## Work-area registration

Research established an evidence-backed registration method:

```text
local area contour
      │
      ▼
longest shared contiguous direction sequence
with static main boundary
      │
      ▼
translation
      │
      ▼
exact matched-run verification
```

No fixed model-specific offset is required.

No scale or rotation is introduced for this static work-area registration.

Ambiguous translations are rejected.

This became PR #1788.

## Live-position transform remains unresolved

Static map geometry and registered work areas share one proven frame.

Live position does not.

The strongest tested rotation candidate is currently:

```text
135 degrees
```

but translation remains non-unique.

Therefore:

```text
no production live → static transform
```

is the current safe conclusion.

## `onMapTrack`

Diagnostic work can strictly reconstruct the observed chunk/update structure.

Observed diagnostic update behaviour includes:

```text
update 1
    replaces complete keyed state

update 2
    replaces individual keyed records
```

This has been useful for activity/timing research.

It has **not** been promoted into the production Map MVP.

## Map editing

Controlled reduced-avoidance-zone research identified the:

```text
SpecialContour
```

family as most tightly associated with creation/deletion.

The experiment did not create a true No-Entry Zone.

Static `onMI` remained stable through that controlled change and the tested AreaSet `ar`/`vw` values were also stable.

The results do not justify a complete SpecialContour geometry parser or general map-editing implementation.

## Promotion path

The map research has now been promoted into:

```text
#1567 → shared mower geometry
#1782 → static onMI boundary
#1788 → registered work areas
#1789 → shared Map/SVG static MVP
```

Remaining live/acquisition/editing findings stay research-level until their semantics are sufficiently proven.

See:

[`docs/map.md`](../docs/map.md)

---

