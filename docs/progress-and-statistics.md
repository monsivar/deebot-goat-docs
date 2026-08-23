# Mowing progress and statistics

This page documents mowing statistics and current-job progress information for ECOVACS GOAT mowers in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py), together with the mower-specific interpretation used by the Home Assistant development work.

Last reviewed against:

- upstream `DeebotUniverse/client.py` `dev`
- `monsivar/client.py` branch `feature/mower-stats-progress`
- `monsivar/core` branch `feature/ecovacs-mower-progress`

Date: **2026-08-23**

## Overview

There are several related but distinct concepts:

1. raw statistics reported by ECOVACS
2. current-job progress derived from those statistics
3. cumulative mower statistics
4. an estimated mowing duration shown by the ECOVACS app
5. the model-specific duration interpretation used by the Home Assistant development branch

These should not be collapsed into one concept.

The reviewed upstream client already exposes general statistics. Development work adds the GOAT-specific:

```text
mowedArea
```

field as:

```text
StatsEvent.mowed_area
```

and adds a model capability flag:

```text
mowing_job_progress
```

which allows a consumer such as Home Assistant to apply mower-job-specific semantics only on hardware profiles for which those semantics have been explicitly enabled.

---

# Evidence terminology

This page uses the following status terms.

| Status | Meaning |
| --- | --- |
| **Upstream implemented** | Present in reviewed upstream `DeebotUniverse/client.py` |
| **Fork implemented** | Present in a development branch but not the reviewed upstream baseline |
| **Python tested** | Covered by automated client tests |
| **HA implemented** | Implemented in the Home Assistant development branch |
| **HA tested** | Covered by Home Assistant automated tests |
| **Protocol observed** | Relevant field/message observed in real GOAT communication |
| **App observed** | Behaviour/value observed in the official ECOVACS app |
| **Derived** | Calculated from other values rather than directly supplied as a dedicated protocol field |
| **Unverified** | Some important semantics still require confirmation |

---

# Statistics capability

Mower statistics are exposed through:

```text
Capabilities.stats
```

using the shared capability model.

The reviewed upstream shape is conceptually:

```python
CapabilityStats(
    clean=...,
    report=...,
    total=...,
)
```

The progress development branch extends this concept with:

```python
mowing_job_progress: bool = False
```

This flag is not itself protocol data.

It describes whether the hardware profile is known to use the common statistics event with mower-job-progress semantics.

Conceptually:

```text
StatsEvent exists
      │
      ▼
mowing_job_progress?
   ┌──┴──┐
   │     │
  no    yes
   │     │
   ▼     ▼
generic  mower-progress
stats    interpretation
```

The researched O1200 development profile sets:

```python
mowing_job_progress=True
```

Status:

**Fork implemented**

---

# `StatsEvent`

The reviewed upstream event contains:

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

The values can be populated from:

```text
getStats
```

and relevant pushed statistics messages.

The field names are shared with other ECOVACS device types and should not automatically be assigned mower-specific semantics without model evidence.

---

# `getStats`

Python command:

```text
GetStats
```

ECOVACS command:

```text
getStats
```

The upstream parser exposes:

```text
area
time
type
```

through `StatsEvent`.

Status:

**Upstream implemented**

---

# GOAT `mowedArea`

GOAT protocol investigation identified an additional statistics field:

```text
mowedArea
```

The development branch:

```text
feature/mower-stats-progress
```

extends `StatsEvent` with:

```python
mowed_area: int | None = field(
    default=None,
    kw_only=True,
)
```

The wire-to-Python mapping is:

```text
mowedArea
    │
    ▼
mowed_area
```

Making the field optional preserves compatibility with devices that do not report it.

Status:

**Fork implemented / Protocol observed / Python tested**

Strongest current model evidence:

```text
GOAT O1200 LiDAR
```

---

# Parsing `mowedArea`

The development implementation parses the field from both:

```text
getStats
```

and:

```text
onStats
```

Conceptually:

```text
getStats response ─────┐
                       │
                       ▼
                   StatsEvent
                       ▲
                       │
onStats push ──────────┘
```

with:

```text
mowedArea → StatsEvent.mowed_area
```

A parser test uses a payload equivalent to:

```json
{
  "area": 2889500,
  "time": 11269,
  "mowedArea": 1005475
}
```

and expects the value to be preserved in the normalised event.

The raw example should be treated as a parser fixture rather than a universal protocol-unit specification.

---

# Current-job area

For hardware profiles declaring:

```text
mowing_job_progress=True
```

the Home Assistant development branch uses:

```text
StatsEvent.mowed_area
```

as the current:

```text
Area mowed
```

value.

This is intentionally different from the generic statistics path, where:

```text
StatsEvent.area
```

is normally used as the operation area.

Conceptually, for the researched mower-progress path:

```text
area
    │
    └── total target area used for progress calculation

mowed_area
    │
    └── completed area exposed as "Area mowed"
```

Status:

**HA implemented / HA tested**

---

# Mowing progress percentage

There is no dedicated ECOVACS field or `deebot_client` event field named:

```text
progress_percent
```

The Home Assistant development branch calculates progress as:

```python
mowed_area / area * 100
```

when:

```text
area is present
area != 0
mowed_area is present
```

Otherwise the result is unknown.

Conceptually:

```text
completed area
────────────── × 100
 total area
```

This value is therefore:

**Derived**

rather than a direct protocol field.

The calculation belongs in the consuming integration rather than the low-level protocol parser.

Status:

**HA implemented / HA tested / Derived**

---

# Unknown progress is not zero progress

The Home Assistant implementation distinguishes:

```text
mowed_area = 0
```

from:

```text
mowed_area = None
```

and rejects the calculation when:

```text
area = 0
```

or:

```text
area = None
```

This prevents unavailable statistics from being presented as:

```text
0%
```

when the correct state is:

```text
unknown
```

---

# Estimated mowing duration

The ECOVACS app has been observed displaying an estimated duration when a mowing job is started.

During the O1200 progress work, the existing:

```text
StatsEvent.time
```

field was given a mower-specific integration interpretation.

For models declaring:

```text
mowing_job_progress=True
```

the Home Assistant development branch exposes:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

rather than the generic:

```text
Mowing duration
```

Status:

**HA implemented / HA tested / App observed**

---

# Why the duration interpretation is model-gated

The implementation does **not** claim:

```text
StatsEvent.time = estimated duration
```

for every ECOVACS device.

Instead:

```text
normal statistics path
        │
        ▼
time → operation duration

mowing-job-progress path
        │
        ▼
time → estimated mowing duration
```

The distinction is enabled by:

```text
CapabilityStats.mowing_job_progress
```

This is important because the same generic event type can carry different model-specific semantics.

Strongest current evidence:

```text
GOAT O1200
```

Cross-model verification is still required before enabling the same interpretation elsewhere.

---

# No dedicated ETA field identified

The current work has **not** identified a separate normalised field such as:

```text
eta
estimated_duration
estimated_remaining_time
remaining_time
```

Therefore the following two statements can both be true:

> The O1200 Home Assistant progress branch currently presents `StatsEvent.time` as estimated mowing duration.

and:

> No separate explicit ECOVACS ETA protocol field has been identified.

The second point remains an open protocol-research question.

---

# Estimated duration is not necessarily remaining time

The current integration label is:

```text
Estimated mowing duration
```

It should not automatically be described as:

```text
Estimated remaining time
```

These concepts are different:

```text
elapsed duration
estimated total duration
estimated remaining duration
```

Future captures should establish how `StatsEvent.time` changes while a mowing job progresses.

Useful questions include:

- Does the value remain constant during the job?
- Does it decrease?
- Does it change when route planning changes?
- Does it represent planned total duration?
- Does it represent another mower-specific time concept?

---

# Units and scaling

Raw protocol units should be documented carefully.

The Home Assistant O1200 progress implementation currently uses:

```text
mowed_area / area → square centimetres
time              → seconds
```

for the mower-progress sensor path.

Home Assistant then converts these values for presentation.

Its automated tests verify, for example:

```text
mowed_area = 28699
```

being presented as:

```text
2.8699 m²
```

and:

```text
time = 2304
```

being presented as:

```text
38.4 minutes
```

This mapping is **implemented and tested for the model-specific progress path**.

It should not automatically be promoted to a universal ECOVACS statistics rule for every GOAT model or every statistics event.

---

# Protocol fidelity versus integration semantics

The preferred architecture is:

```text
ECOVACS protocol
      │
      ▼
raw/normalised event values
      │
      ▼
hardware capability describes semantics
      │
      ▼
consumer integration presentation
```

For example:

```text
mowedArea
    │
    ▼
StatsEvent.mowed_area
    │
    ▼
Area mowed
```

and:

```text
area + mowed_area
        │
        ▼
derived mowing progress %
```

This keeps protocol parsing separate from user-interface interpretation.

---

# Remaining area

If `area` and `mowed_area` represent the same job in the same unit, an integration could also calculate:

```text
remaining_area = area - mowed_area
```

This is not currently a dedicated client field.

Status:

**Derived / not currently exposed**

---

# `ReportStatsEvent`

Statistics can also arrive through:

```text
reportStats
```

and are represented by:

```text
ReportStatsEvent
```

The event extends common statistics with job-related information such as:

```text
cleaning_id
status
content
```

The generic name:

```text
cleaning_id
```

comes from the shared DEEBOT abstraction.

For GOAT, it can conceptually represent a mowing-job identifier.

---

# Job status

`ReportStatsEvent` uses the shared:

```text
CleanJobStatus
```

model.

Relevant values include:

| Value | Mower-oriented interpretation |
| --- | --- |
| `NO_STATUS` | No explicit job status |
| `CLEANING` | Active mowing job |
| `FINISHED` | Job finished |
| `MANUALLY_STOPPED` | Job stopped manually |
| `FINISHED_WITH_WARNINGS` | Job completed with warnings |

At a mower user-interface layer:

```text
CLEANING
```

should normally be displayed as:

```text
MOWING
```

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

The exact GOAT-specific relationship between these numeric values and lawn zones should be established from protocol correlation rather than inferred solely from the type.

Possible zone/area relationships remain a research topic.

---

# Total statistics

Cumulative device statistics are represented by:

```text
TotalStatsEvent
```

with shared fields:

```python
area: int
time: int
cleanings: int
```

The corresponding command is:

```text
GetTotalStats
```

with wire name:

```text
getTotalStats
```

The protocol mapping includes:

```text
area  → TotalStatsEvent.area
time  → TotalStatsEvent.time
count → TotalStatsEvent.cleanings
```

For GOAT, user-facing wording should use mower terminology such as:

```text
Total area mowed
Total mowing duration
Total mowings
```

rather than vacuum-oriented wording.

Status:

**Upstream implemented**

---

# Current versus cumulative statistics

Do not use cumulative statistics to calculate active-job progress.

Conceptually:

```text
StatsEvent
    │
    └── current/recent operation data

TotalStatsEvent
    │
    └── lifetime/cumulative device data
```

The mowing-progress calculation uses current-job statistics.

---

# Model support

All five reviewed upstream GOAT profiles expose the common statistics capability:

- GOAT G1
- GOAT A1600 RTK
- GOAT A3000 LiDAR Pro
- GOAT O500 Panorama
- GOAT O1200 LiDAR

This confirms common support for the statistics architecture.

It does **not** prove that all optional mower-specific fields or semantics are shared by all models.

In particular:

```text
mowedArea
mowing_job_progress
estimated-duration interpretation
```

should remain model-evidence-based.

---

# O1200 development support

Current strongest evidence for mower-job-progress semantics is the:

```text
GOAT O1200 LiDAR
```

development profile.

The development pair is:

```text
client.py:
feature/mower-stats-progress

Home Assistant core:
feature/ecovacs-mower-progress
```

The client branch:

- preserves `mowedArea`
- adds `StatsEvent.mowed_area`
- adds `CapabilityStats.mowing_job_progress`
- enables `mowing_job_progress=True` for the researched O1200 profile

The Home Assistant branch:

- exposes current area mowed
- derives mowing progress percentage
- exposes `StatsEvent.time` as estimated mowing duration
- applies mower-specific units and presentation
- includes automated tests for the progress path

---

# Current Home Assistant entities

For the researched O1200 progress implementation, the tested entities are equivalent to:

```text
sensor.goat_o1200_lidar_area_mowed
sensor.goat_o1200_lidar_mowing_progress
sensor.goat_o1200_lidar_estimated_mowing_duration
```

These names belong to the Home Assistant integration layer rather than the ECOVACS protocol itself.

---

# Current status summary

| Feature | Status |
| --- | --- |
| Common `StatsEvent` | Upstream implemented |
| Common `ReportStatsEvent` | Upstream implemented |
| Common `TotalStatsEvent` | Upstream implemented |
| `mowedArea` parser | Fork implemented / Python tested / Protocol observed |
| `StatsEvent.mowed_area` | Fork implemented |
| `mowing_job_progress` capability flag | Fork implemented |
| Current area mowed in HA | HA implemented / HA tested |
| Progress percentage | Derived / HA implemented / HA tested |
| `StatsEvent.time` as estimated mowing duration | Model-gated / HA implemented / HA tested |
| Separate explicit ETA field | Not identified |
| Estimated remaining time | Not established |
| Cross-model progress semantics | Unverified |

---

# Recommended integration behaviour

Consumers should:

1. expose raw current-job statistics where useful
2. derive percentage only when the hardware profile explicitly declares appropriate semantics
3. keep derived percentage separate from protocol fields
4. treat the duration interpretation as model-specific
5. avoid calling the duration value "remaining time" without evidence
6. avoid enabling O1200-specific progress semantics on other GOAT models solely because they share `StatsEvent`
7. retain raw values so future interpretation changes do not require protocol-parser redesign

---

# Open research questions

The highest-value remaining questions are:

- Do other GOAT models send `mowedArea`?
- Do they use the same scaling?
- Does `StatsEvent.time` have the same mower-progress meaning on other models?
- How does `time` behave during an active O1200 job?
- Is there a separate explicit ETA field in another message?
- Does the ECOVACS app receive additional route-planning data for its estimate?
- How are statistics reported for multi-zone mowing?
- Does `ReportStatsEvent.content` correlate with mower zone IDs?
- Can remaining area be safely derived on all relevant job types?

---

# Related documentation

- [Overview](overview.md)
- [Supported models](supported-models.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant integration](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
- [Protocol observations](../research/protocol-observations.md)
