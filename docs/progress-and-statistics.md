# Mowing progress and statistics

This page documents mowing statistics and job-progress information for ECOVACS GOAT mowers in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py).

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* development branch `feature/mower-stats-progress`

Date: **2026-08-23**

## Overview

There are two related but different concepts:

1. **statistics** describing mowing activity
2. **progress** describing how far the current mowing job has advanced

The upstream client already supports several statistics events.

Additional GOAT protocol observations show that the statistics payload can also contain:

```text
mowedArea
```

which can be used to represent the part of the current target area that has already been mowed.

Support for this field has been implemented in the development branch:

```text
feature/mower-stats-progress
```

but is not part of the reviewed upstream `dev` baseline.

---

# Capability architecture

Mower statistics are exposed through:

```text
Capabilities.stats
```

using:

```python
CapabilityStats(
    clean=...,
    report=...,
    total=...,
)
```

The generic names originate from the shared DEEBOT client.

For GOAT devices they should be interpreted approximately as:

| Generic capability | GOAT interpretation              |
| ------------------ | -------------------------------- |
| `stats.clean`      | Current/recent mowing statistics |
| `stats.report`     | Pushed job statistics/status     |
| `stats.total`      | Cumulative mower statistics      |

The reviewed GOAT hardware profiles expose all three categories.

---

# Statistics events

The common capability system uses three statistics event types:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

They serve different purposes.

---

# `StatsEvent`

In current upstream `dev`, `StatsEvent` contains:

```python
area: int | None
time: int | None
type: str | None
```

Conceptually:

```text
StatsEvent
├── area
├── time
└── type
```

The values are populated by the ECOVACS:

```text
getStats
```

response and by statistics messages where applicable.

## Important unit warning

The raw protocol fields should not automatically be assigned human-readable units solely from their names.

For example:

```text
area
time
```

are protocol values.

Their physical units and exact mower-specific semantics should be established from protocol observations and device behaviour before being presented as square metres, seconds, minutes, or another unit.

This documentation therefore preserves raw field names unless the unit is independently confirmed.

---

# `GetStats`

Current upstream implements:

```text
GetStats
```

with ECOVACS command name:

```text
getStats
```

The response parser creates:

```text
StatsEvent
```

from:

```text
area
time
type
```

Conceptually:

```text
getStats
   │
   ▼
ECOVACS response
   │
   ├── area
   ├── time
   └── type
        │
        ▼
    StatsEvent
```

---

# GOAT `mowedArea`

During GOAT protocol investigation, an additional statistics field was identified:

```text
mowedArea
```

This field is not currently represented by the reviewed upstream `StatsEvent`.

A development implementation adds:

```python
mowed_area: int | None
```

as an optional keyword field.

The extended event therefore becomes conceptually:

```text
StatsEvent
├── area
├── time
├── type
└── mowed_area
```

The Python name follows normal snake-case conventions:

```text
mowedArea   → protocol
mowed_area  → Python
```

Status:

**Fork implemented**

---

# Development implementation

In:

```text
feature/mower-stats-progress
```

the event is extended with:

```python
mowed_area: int | None = field(
    default=None,
    kw_only=True,
)
```

Making the field optional is important for backwards compatibility.

Existing devices and messages that do not provide:

```text
mowedArea
```

can still produce a normal `StatsEvent`.

Conceptually:

```text
Device without mowedArea
       │
       ▼
mowed_area = None
```

while a GOAT payload containing the field can produce:

```text
mowed_area = <raw protocol value>
```

---

# Parsing `mowedArea`

The development branch extends both relevant statistics paths.

## `GetStats` response

The parser adds:

```python
mowed_area=data.get("mowedArea")
```

to the generated `StatsEvent`.

## `onStats` message

The mower may also provide statistics through:

```text
onStats
```

The development parser likewise extracts:

```text
mowedArea
```

from this message.

This means the field can be represented whether statistics arrive as:

```text
explicit getStats response
```

or:

```text
onStats message
```

Conceptually:

```text
getStats response ─────┐
                       │
                       ▼
                   StatsEvent
                       ▲
                       │
onStats message ───────┘
```

---

# Test coverage

The development branch includes a test using the following example statistics payload:

```json
{
  "area": 2889500,
  "time": 11269,
  "mowedArea": 1005475
}
```

The expected client event is:

```python
StatsEvent(
    area=2889500,
    time=11269,
    type=None,
    mowed_area=1005475,
)
```

This verifies that:

```text
mowedArea
```

is preserved by the parser and exposed through:

```text
StatsEvent.mowed_area
```

The example should be treated as a parser test fixture.

Raw numeric values should not be converted into physical units without separate unit verification.

---

# Deriving mowing progress

If:

```text
area
```

represents the complete target area of the current job and:

```text
mowedArea
```

represents the already completed part of that same target in the same unit, a progress percentage can conceptually be calculated as:

```text
mowed_area
────────── × 100
   area
```

However, this calculation should only be exposed when those assumptions are verified.

The client development branch currently exposes the raw data rather than adding a new calculated percentage field.

This is deliberate.

It keeps protocol parsing separate from higher-level interpretation.

Conceptually:

```text
ECOVACS protocol
      │
      ▼
 area + mowedArea
      │
      ▼
deebot_client raw event
      │
      ▼
integration may derive %
```

This allows a consuming integration such as Home Assistant to calculate progress if appropriate.

---

# Why raw progress data is preferable

There are several advantages to exposing:

```text
area
mowed_area
```

rather than immediately converting them to a percentage inside the protocol parser.

## Protocol fidelity

The client preserves what the mower actually reported.

## Future interpretation changes

If later research shows that:

```text
area
```

or:

```text
mowedArea
```

has model-specific semantics, the raw data remains available.

## Integration flexibility

Different consumers may want:

* percentage
* completed area
* remaining area
* progress bars
* historical graphs

These can all be derived from the same raw values once their units are known.

---

# Remaining area

If the semantics and units are confirmed to match, another possible derived value is:

```text
remaining_area = area - mowed_area
```

This is not currently a dedicated upstream or development event field.

It should therefore be considered:

**Derived data**

rather than protocol data.

---

# Estimated job duration

The ECOVACS app displays an estimated duration when a mowing job is started.

This is distinct from the elapsed:

```text
time
```

value found in statistics.

Three concepts should therefore remain separate:

```text
Elapsed time
Estimated total duration
Estimated remaining time
```

They should not be treated as interchangeable.

## App observation

During physical GOAT testing, the ECOVACS application presented an estimate of how long the selected mowing operation was expected to take.

This indicates that ECOVACS has enough information to estimate job duration at the application, cloud, mower, or protocol level.

Status:

**Device/app observed**

## Current client status

The reviewed:

```text
feature/mower-stats-progress
```

implementation does **not** introduce a dedicated field for:

```text
estimated_duration
```

or:

```text
remaining_time
```

It currently focuses on exposing:

```text
mowedArea
```

through `StatsEvent`.

Therefore the existence of the app estimate should not be documented as an implemented `deebot_client` feature.

---

# Possible duration derivation

If progress and elapsed time are both reliable, an integration could theoretically estimate total duration from:

```text
elapsed time
progress fraction
```

and calculate remaining duration.

For example, conceptually:

```text
estimated total duration
          =
elapsed time / progress fraction
```

followed by:

```text
estimated remaining
          =
estimated total - elapsed
```

However, this would be a client/integration-side estimate.

It is not necessarily the same estimate displayed by the ECOVACS app.

The app may use additional information such as:

* mower speed
* route planning
* zone geometry
* obstacle history
* cutting pattern
* planned path length
* mower settings
* battery requirements
* charging interruptions
* terrain or navigation data

For that reason, a locally calculated estimate should be labelled clearly as derived.

---

# Protocol-supplied estimate versus calculated estimate

Future investigation should distinguish between:

```text
A: ECOVACS supplies an explicit ETA/duration value
```

and:

```text
B: ECOVACS app calculates the estimate itself
```

These lead to different implementations.

## Protocol-supplied

If an explicit field is found:

```text
protocol field
     │
     ▼
normalised event
     │
     ▼
integration
```

This would be preferable because it preserves ECOVACS' own estimate.

## Locally calculated

If no explicit protocol value exists:

```text
elapsed time + mowing progress
             │
             ▼
 integration calculation
             │
             ▼
          local ETA
```

That value should not be presented as an ECOVACS-reported ETA.

---

# `ReportStatsEvent`

Statistics can also arrive through:

```text
reportStats
```

messages.

These are represented by:

```text
ReportStatsEvent
```

which extends the normal statistics event with job-specific information.

The event contains:

```text
cleaning_id
status
content
```

in addition to the normal statistics fields.

Again, `cleaning_id` is generic naming inherited from DEEBOT support.

For GOAT documentation it can conceptually be understood as a mowing-job identifier.

---

# Job status

`ReportStatsEvent` uses:

```text
CleanJobStatus
```

The shared enum currently contains:

| Value                    | Meaning                     |
| ------------------------ | --------------------------- |
| `NO_STATUS`              | No explicit status          |
| `CLEANING`               | Job currently active        |
| `FINISHED`               | Job finished                |
| `MANUALLY_STOPPED`       | Job stopped manually        |
| `FINISHED_WITH_WARNINGS` | Job completed with warnings |

For GOAT use:

```text
CLEANING
```

should normally be interpreted as:

```text
MOWING
```

at the user-interface level.

---

# `reportStats` status parsing

The parser starts from:

```text
CLEANING
```

for an active report.

If no:

```text
stop
```

field exists, the parser uses:

```text
NO_STATUS
```

If the report contains a non-zero stop indication, the parser uses:

```text
stopReason
```

to determine the final `CleanJobStatus`.

Conceptually:

```text
reportStats
     │
     ├── active
     │      └── CLEANING
     │
     ├── no stop information
     │      └── NO_STATUS
     │
     └── stopped
            │
            ▼
        stopReason
```

This allows the client to distinguish normal completion from manual termination and some warning states.

---

# `content`

`ReportStatsEvent` also contains:

```text
content
```

represented as:

```python
list[int]
```

The parser converts comma-separated protocol content values into integers.

Because the field is shared across ECOVACS device types, its exact mower-specific meaning should be documented only after GOAT protocol correlation.

Possible relationships with zone or area identifiers should be confirmed from actual messages rather than inferred solely from the data type.

---

# Total statistics

Cumulative statistics are represented by:

```text
TotalStatsEvent
```

with:

```python
area: int
time: int
cleanings: int
```

The associated command is:

```text
GetTotalStats
```

with protocol command name:

```text
getTotalStats
```

The response parser maps:

```text
area  → area
time  → time
count → cleanings
```

For GOAT use, the generic:

```text
cleanings
```

name should be interpreted as a count of mowing/operation activity according to the protocol semantics.

---

# Current versus total statistics

It is useful to distinguish:

```text
StatsEvent
```

from:

```text
TotalStatsEvent
```

Conceptually:

```text
StatsEvent
   │
   └── current/recent job information

TotalStatsEvent
   │
   └── cumulative device information
```

An integration should not use cumulative values when calculating the progress of the active job.

---

# Model support

All five reviewed upstream GOAT hardware profiles currently expose:

```text
CapabilityStats
```

including:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

The reviewed profiles are:

* GOAT G1
* GOAT A1600 RTK
* GOAT A3000 LiDAR Pro
* GOAT O500 Panorama
* GOAT O1200 LiDAR

This confirms common statistics capability wiring.

It does not prove that every model sends every optional statistics field such as:

```text
mowedArea
```

The additional field should be considered model/protocol dependent until tested more broadly.

---

# O1200 development support

The:

```text
feature/mower-stats-progress
```

work explicitly connects the progress-related statistics change to the O1200 development profile used during investigation.

Therefore the strongest current evidence for:

```text
mowedArea
```

should be recorded as:

**GOAT O1200: protocol observed / fork implemented**

Support on other models should not be assumed solely because they share the generic statistics capability.

---

# Integration recommendations

A mower-oriented integration can potentially expose several useful values.

## Raw values

When available:

```text
area
mowed_area
time
type
```

These most closely represent the client event.

## Derived values

After confirming semantics:

```text
progress percentage
remaining area
```

These should be clearly understood as calculated values.

## Job status

From:

```text
ReportStatsEvent.status
```

an integration may expose:

* mowing
* finished
* manually stopped
* finished with warnings

## Total statistics

Cumulative values can be exposed independently for historical usage:

* total area
* total time
* total operation count

---

# Suggested Home Assistant representation

Once units and semantics are confirmed, possible entities include:

```text
sensor.goat_mowing_progress
sensor.goat_mowed_area
sensor.goat_mowing_time
sensor.goat_total_mowed_area
sensor.goat_total_mowing_time
sensor.goat_total_mowing_jobs
```

A duration/ETA sensor should only be added once its source is clearly defined.

For example:

```text
sensor.goat_estimated_remaining_time
```

should specify whether it represents:

```text
ECOVACS-reported estimate
```

or:

```text
locally calculated estimate
```

Those should not silently be treated as equivalent.

---

# Recommended progress logic

Once field semantics have been confirmed, consuming integrations could use logic conceptually equivalent to:

```text
if area is known
and area > 0
and mowed_area is known:

    progress =
        mowed_area / area
```

The integration should also handle:

* missing `mowedArea`
* zero target area
* values temporarily resetting between jobs
* stale statistics after job completion
* new jobs replacing old job data
* model/firmware differences

A progress sensor should not assume that a missing value means zero progress.

Missing data and zero are different states.

---

# Job lifecycle considerations

Progress data should be interpreted together with mower state.

For example:

```text
State.CLEANING
      +
StatsEvent
      │
      ▼
active mowing progress
```

while:

```text
State.PAUSED
      +
StatsEvent
      │
      ▼
paused job with retained progress
```

and:

```text
job stopped
      +
new statistics report
      │
      ▼
completed/terminated job data
```

Care should be taken not to continue presenting an old percentage as the progress of a newly started job.

Where possible, job identifiers from report messages can help correlate statistics to a specific operation.

---

# Evidence summary

## Upstream implemented

Current upstream provides:

* `CapabilityStats`
* `StatsEvent`
* `ReportStatsEvent`
* `TotalStatsEvent`
* `GetStats`
* `GetTotalStats`
* `reportStats`
* `onStats`
* common job status handling
* statistics capability wiring for the reviewed GOAT profiles

## Fork implemented

`feature/mower-stats-progress` adds:

```text
StatsEvent.mowed_area
```

and parses:

```text
mowedArea
```

from:

* `getStats`
* `onStats`

The branch also contains test coverage for the additional field.

## Device/protocol observed

GOAT investigation has identified:

```text
mowedArea
```

in mower statistics communication.

The ECOVACS application also displays an estimated job duration when a mowing job is started.

## Not yet upstream

At the reviewed baseline:

```text
mowed_area
```

is not part of upstream `dev`.

## Still requiring investigation

The following should remain open until further verified:

* physical unit of `area`
* physical unit of `mowedArea`
* physical unit/semantics of `time` for GOAT
* whether all GOAT models provide `mowedArea`
* when progress values reset
* behaviour across pause/resume
* behaviour across charging interruptions
* explicit ECOVACS ETA/duration protocol field, if any
* source of the app's estimated job duration
* multi-zone progress semantics
* whether progress is based on geometric area, planned route, or another internal metric

---

# Relevant source files

## Upstream

* [`deebot_client/capabilities.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/capabilities.py)
* [`deebot_client/events/__init__.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/events/__init__.py)
* [`deebot_client/commands/json/stats.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/stats.py)
* [`deebot_client/messages/json/stats.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/messages/json/stats.py)

## Development branch

* [`deebot_client/events/__init__.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/events/__init__.py)
* [`deebot_client/commands/json/stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/commands/json/stats.py)
* [`deebot_client/messages/json/stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/messages/json/stats.py)
* [`tests/commands/json/test_stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/tests/commands/json/test_stats.py)

## Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mowing control](mowing-control.md)
* [Zone and area mowing](zones-and-areas.md)
* Mower settings *(planned)*
* Protocol reference *(planned)*
* Home Assistant integration *(planned)*
