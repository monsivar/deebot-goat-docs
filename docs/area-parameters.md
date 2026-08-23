# O1200 area parameters

This page documents the zone-specific area-parameter protocol identified for the ECOVACS GOAT O1200 LiDAR and implemented in the development work associated with:

- [`DeebotUniverse/client.py` PR #1767](https://github.com/DeebotUniverse/client.py/pull/1767) — `setAreaParameter` and combined area-parameter capability
- [`DeebotUniverse/client.py` PR #1768](https://github.com/DeebotUniverse/client.py/pull/1768) — `getAreaParameter`, `onAreaParameter` and `AreaParameterEvent`
- [`DeebotUniverse/client.py` issue #1610](https://github.com/DeebotUniverse/client.py/issues/1610) — original O1200 protocol observations

Last reviewed: **2026-08-23**

> [!IMPORTANT]
> Both PRs were still open at the time of this review.
>
> The functionality described here is therefore **development/fork support**, not part of the reviewed upstream `dev` baseline.

## Overview

The GOAT O1200 exposes several mowing parameters on a **per-zone** basis.

The identified protocol fields are:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

These fields are grouped together as one area-parameter record.

Conceptually:

```text
Lawn zone
   │
   └── areaID
        │
        ├── mowHeightLevel
        ├── cutMode
        ├── obstacleHeight
        └── angle
```

This is important because these values are not merely global mower settings.

They belong to a specific mower area/zone.

## Evidence status

| Item | Status |
| --- | --- |
| `setAreaParameter` command | Protocol observed / Fork implemented / Python tested |
| `getAreaParameter` command | Fork implemented / Python tested |
| `onAreaParameter` push | Protocol observed / Fork implemented / Python tested |
| `AreaParameterEvent` | Fork implemented / Python tested |
| O1200 capability wiring | Fork implemented |
| Zone-specific `areaID` | Protocol observed |
| `mowHeightLevel` field | Protocol observed / implemented |
| `cutMode` field | Protocol observed / implemented |
| `obstacleHeight` field | Protocol observed / implemented |
| `angle` field | Protocol observed / implemented |
| Exact `mowHeightLevel` → physical height mapping | Not fully documented |
| Exact `cutMode` enum/app-label mapping | Not fully documented |
| Exact `obstacleHeight` physical semantics/unit | Not fully documented |
| Relationship between `angle` and global `cut_direction` | Requires clarification |
| Home Assistant entity/action representation | Not yet implemented in reviewed HA branch |
| Other GOAT model support | Unverified |

## Python representation

The development implementation introduces:

```python
@dataclass(frozen=True)
class AreaParameter:
    area_id: str
    mow_height_level: int
    cut_mode: int
    obstacle_height: int
    angle: int
```

Multiple zones are reported through:

```python
@dataclass(frozen=True)
class AreaParameterEvent(Event):
    area_parameters: list[AreaParameter]
```

The wire-to-Python mapping is:

| ECOVACS field | Python field |
| --- | --- |
| `areaID` | `area_id` |
| `mowHeightLevel` | `mow_height_level` |
| `cutMode` | `cut_mode` |
| `obstacleHeight` | `obstacle_height` |
| `angle` | `angle` |

## Capability

The current combined development implementation exposes the O1200 setting through:

```python
area_parameter=CapabilitySet(
    AreaParameterEvent,
    [GetAreaParameter()],
    SetAreaParameter,
)
```

This gives the capability three important parts:

```text
GET current state
      │
      ▼
AreaParameterEvent
      ▲
      │
PUSH state updates

and

SET one area's parameter tuple
```

The capability is currently connected to the researched:

```text
GOAT O1200 LiDAR
hardware ID: 2i0fns
```

Support on other GOAT models should not be assumed.

---

# `setAreaParameter`

Python command:

```text
SetAreaParameter
```

Wire command:

```text
setAreaParameter
```

The setter uses a **flat payload** for one area.

Example:

```json
{
  "areaID": "2",
  "mowHeightLevel": 10,
  "cutMode": 7,
  "obstacleHeight": 1,
  "angle": 136
}
```

The Python constructor is conceptually:

```python
SetAreaParameter(
    area_id="2",
    mow_height_level=10,
    cut_mode=7,
    obstacle_height=1,
    angle=136,
)
```

Status:

**Protocol observed / Fork implemented / Python tested**

## Important: the setter writes the complete parameter tuple

`setAreaParameter` does not currently expose independent setters such as:

```text
setMowHeight
setCutMode
setObstacleHeight
setAreaAngle
```

Instead, the request contains all four configurable values together with the zone ID.

Conceptually:

```text
Set parameter for area 2
        │
        ▼
areaID = 2
mowHeightLevel = ...
cutMode = ...
obstacleHeight = ...
angle = ...
```

This has an important integration consequence:

> When changing only one user-facing value, a consumer should preserve the latest known values of the other fields rather than inventing defaults.

For example, changing only cutting height should conceptually follow:

```text
Latest AreaParameterEvent
        │
        ▼
find areaID = "2"
        │
        ▼
copy current:
  cutMode
  obstacleHeight
  angle
        │
        ▼
replace only:
  mowHeightLevel
        │
        ▼
SetAreaParameter(...)
```

This reduces the risk of unintentionally overwriting other zone settings.

---

# `getAreaParameter`

Python command:

```text
GetAreaParameter
```

Wire command:

```text
getAreaParameter
```

The response contains:

```text
areaParameters
```

which is a list of parameter records.

Example structure:

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

The parser creates:

```text
AreaParameterEvent
```

containing one:

```text
AreaParameter
```

object per reported zone.

Status:

**Fork implemented / Python tested**

---

# `onAreaParameter`

Push message:

```text
onAreaParameter
```

The mower has been observed publishing this state after area-parameter changes.

The push uses the same list-style state schema as the getter:

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

Conceptually:

```text
setAreaParameter
       │
       ▼
mower accepts change
       │
       ▼
onAreaParameter
       │
       ▼
AreaParameterEvent
```

This allows integrations to use reported mower state rather than assuming that a successful command acknowledgement is the final state.

Status:

**Protocol observed / Fork implemented / Python tested**

---

# `areaID`

The field:

```text
areaID
```

identifies which mower area/zone the parameter record belongs to.

It is represented as:

```python
area_id: str
```

Example:

```text
"2"
```

The protocol evidence establishes that area parameters are associated with area IDs.

PR #1774 adds the complementary area-name capability using:

```text
GetAreaSet → RoomsEvent
```

Real O1200 validation provides mappings such as:

```text
1 → Sentrum
2 → Vestkanten
4 → Østkanten
```

This means the tested O1200 now has a concrete metadata path:

```text
Room.id / area ID
      │
      ├── Room.name
      └── AreaParameter.area_id
```

The client types differ (`Room.id` is numeric while `AreaParameter.area_id` is a string), so integrations should normalise intentionally when joining the two data sets.

See:

[O1200 area names](area-names.md)

---

# Cutting height: `mowHeightLevel`

The O1200 area-parameter protocol exposes:

```text
mowHeightLevel
```

represented in Python as:

```text
mow_height_level
```

This establishes that **cutting/mowing height is protocol-mapped for the O1200 development implementation**.

It should therefore no longer be described as:

```text
cutting height protocol unknown
```

or:

```text
cutting height not mapped
```

for the researched O1200.

The correct current status is:

**Protocol observed / Fork implemented / Python tested**

## What remains unknown

The current PR/test evidence does not by itself fully document:

- physical unit
- complete valid-value range
- minimum level
- maximum level
- level step
- whether each level maps linearly to millimetres
- whether the same mapping applies to other GOAT models

For example:

```text
mowHeightLevel = 10
```

is a known raw protocol value.

It should not automatically be converted into:

```text
10 mm
```

or another physical height without independent evidence.

A useful next experiment is therefore no longer:

```text
find the cutting-height command
```

but:

```text
map app/physical height selections
        │
        ▼
mowHeightLevel values
        │
        ▼
physical height/unit mapping
```

---

# Cut mode: `cutMode`

The area-parameter protocol exposes:

```text
cutMode
```

represented as:

```text
cut_mode
```

This establishes a raw O1200 **zone-specific cut-mode parameter**.

Status:

**Protocol observed / Fork implemented / Python tested**

## Important semantic limitation

The existence of:

```text
cutMode
```

does not yet establish the complete mapping between its integer values and:

- official ECOVACS app labels
- mowing efficiency options
- path/pattern choices
- speed behaviour
- number of passes
- another user-facing mowing mode

For example, observed/test values include integers such as:

```text
4
7
```

The exact meaning of each value should be determined from controlled app changes and protocol correlation.

Therefore the correct research question is:

```text
What does each cutMode value mean?
```

rather than:

```text
Does a cut-mode protocol field exist?
```

---

# Obstacle height: `obstacleHeight`

The O1200 area-parameter record includes:

```text
obstacleHeight
```

represented as:

```text
obstacle_height
```

Status:

**Protocol observed / Fork implemented / Python tested**

This should be treated as a separate parameter from global/AI-related settings such as:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
AnimalProtection
```

The field name suggests an obstacle-height-related zone parameter, but the exact user-facing meaning, unit and physical effect should be established through app/device correlation.

Do not automatically interpret:

```text
obstacleHeight = 1
```

as a physical height in centimetres or millimetres without evidence.

---

# Area angle: `angle`

The area-parameter protocol includes:

```text
angle
```

represented directly as:

```text
angle
```

Observed/test values include examples such as:

```text
0
136
180
```

The original protocol investigation associated this field with a zone-specific clipping/mowing angle.

Status:

**Protocol observed / Fork implemented / Python tested**

## Relationship to global `cut_direction`

The reviewed upstream GOAT profiles also expose:

```text
settings.cut_direction
```

through the generic:

```text
GetCutDirection
SetCutDirection
```

capability.

The new:

```text
AreaParameter.angle
```

is explicitly tied to an:

```text
areaID
```

and is therefore a zone-specific value in this protocol family.

The relationship between the two mechanisms should be documented carefully.

Possible interpretations include:

- older/global protocol versus newer zone-specific protocol
- a global default versus per-zone override
- model-generation differences
- different app functions

The current evidence is insufficient to declare them identical.

---

# Setter schema versus getter/push schema

This difference is technically important.

## Setter

One area, flat object:

```json
{
  "areaID": "2",
  "mowHeightLevel": 10,
  "cutMode": 7,
  "obstacleHeight": 1,
  "angle": 136
}
```

## Getter/push

Multiple areas, wrapped list:

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

The implementation deliberately preserves this protocol asymmetry.

A generic JSON setting helper should not assume that read and write schemas are identical.

---

# Test coverage

The PR family contains automated tests for:

## SET

Verifies generation of the flat `setAreaParameter` payload.

## GET

Verifies parsing of multiple `areaParameters` records into:

```text
AreaParameterEvent
```

## PUSH

Verifies parsing of:

```text
onAreaParameter
```

into the same event model.

Automated coverage reports for the PRs indicate that the added coverable lines are exercised by tests.

This provides strong software-level confidence.

It does not by itself establish every physical interpretation of each numeric value.

---

# Home Assistant implications

The reviewed Home Assistant mower work does not yet expose these area parameters as native entities/actions.

Several possible designs exist.

## Composite action/service

A low-level action could accept:

```text
area_id
mow_height_level
cut_mode
obstacle_height
angle
```

This closely matches the protocol.

## Selected-zone entities

A richer design could expose values for a selected/current zone.

The O1200 development work now has area-name metadata through:

```text
GetAreaSet → RoomsEvent
```

so the remaining Home Assistant questions are primarily UI architecture, state-preserving writes and selected-zone start control rather than name discovery.

## Individual parameter entities per zone

This could be convenient for automation but may create many entities and requires careful state-preserving writes.

### Important implementation rule

Because the setter writes the complete tuple, any UI that exposes individual controls should:

1. read/cache the current `AreaParameterEvent`
2. identify the selected `area_id`
3. preserve unchanged sibling parameters
4. change only the intended field
5. call `SetAreaParameter` with the complete tuple
6. wait for `onAreaParameter` to confirm state

This is safer than using arbitrary defaults.

---

# Cross-model scope

Current strongest evidence is:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

The field names may appear on other GOAT models, but support should not be enabled merely because the models are similar.

Before enabling another profile, confirm at least:

- getter/push availability
- setter availability
- field set
- valid values
- area-ID semantics
- physical behaviour

---

# What PR #1767/#1768 resolves

The PR family resolves or substantially changes the status of several previous research gaps.

## No longer "protocol unknown" for O1200

```text
cutting height
    → mowHeightLevel

zone-specific cut mode
    → cutMode

zone-specific obstacle-height parameter
    → obstacleHeight

zone-specific mowing angle
    → angle
```

## Still open

```text
mowHeightLevel → physical height/unit mapping
cutMode value → app/user meaning
obstacleHeight value → app/user meaning/unit
angle relationship to global cut_direction
Home Assistant representation
cross-model support
area ID → human-readable zone metadata
```

---

# Recommended next experiments

For this protocol family, the highest-value tests are now semantic mapping rather than command discovery.

## Cutting height

Change exactly one app height level at a time and record:

```text
app value
mowHeightLevel
physical/displayed height
```

## Cut mode

Change one app mode at a time and record:

```text
app label
cutMode
other fields unchanged?
```

## Obstacle height

Change only the relevant app option and record:

```text
app label/value
obstacleHeight
physical unit if shown
```

## Angle

Change only zone mowing direction and record:

```text
app angle
AreaParameter.angle
global cut_direction
```

This will determine whether the global and zone-specific direction mechanisms overlap.

---

# Related documentation

- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Zones and areas](zones-and-areas.md)
- [O1200 area names](area-names.md)
- [Settings](settings.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
- [Protocol observations](../research/protocol-observations.md)
