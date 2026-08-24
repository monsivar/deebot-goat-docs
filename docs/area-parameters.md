# O1200 area parameters

This page documents the zone-specific area-parameter protocol identified for the ECOVACS GOAT O1200 LiDAR and implemented in the development work associated with:

- [`DeebotUniverse/client.py` PR #1767](https://github.com/DeebotUniverse/client.py/pull/1767) — `setAreaParameter` and combined area-parameter capability
- [`DeebotUniverse/client.py` PR #1768](https://github.com/DeebotUniverse/client.py/pull/1768) — `getAreaParameter`, `onAreaParameter` and `AreaParameterEvent`
- [`DeebotUniverse/client.py` issue #1610](https://github.com/DeebotUniverse/client.py/issues/1610) — original O1200 protocol observations
- [`monsivar/core` branch `feature/ecovacs-area-parameter`](https://github.com/monsivar/core/tree/feature/ecovacs-area-parameter) — Home Assistant semantic conversion/mapping work

Last reviewed: **2026-08-24**

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
| `mowHeightLevel` → HA height mapping | Implemented/tested in HA development: 3.0–8.0 cm, 0.5 cm step |
| `cutMode` semantic mapping | Implemented/tested in HA development: 7 = Gentle/0.35 m/s, 4 = Efficient/0.5 m/s |
| `obstacleHeight` semantic mapping | Implemented/tested in HA development: 1/2/3 environment thresholds |
| Raw area `angle` → user degrees | Implemented/tested in HA development |
| Relationship between area `angle` and global `cut_direction` | Requires clarification |
| Home Assistant support | Semantic helpers + raw set service implemented; native per-area entity wiring incomplete |
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

PR #1767/#1768 establishes the raw protocol field and GET/SET/PUSH state flow.

The Home Assistant branch:

```text
feature/ecovacs-area-parameter
```

adds the user-facing semantic conversion:

```python
mow_height_level_to_cm(level) = (17 - level) / 2
mow_height_cm_to_level(height) = 17 - height * 2
```

and defines:

```text
minimum = 3.0 cm
maximum = 8.0 cm
step    = 0.5 cm
unit    = centimetres
```

The helper tests cover every mapped level:

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

Example:

```text
mowHeightLevel = 10
        │
        ▼
3.5 cm
```

This means the documentation should no longer list:

```text
unit
minimum
maximum
step
level-to-height conversion
```

as undiscovered for the researched O1200 HA development.

Status:

```text
Protocol observed
Client fork implemented
Client Python tested
HA semantic mapping implemented
HA helper mapping tested
```

## What still requires verification

The HA tests prove that the software conversion is internally consistent.

They do **not by themselves** prove that every one of the eleven levels was independently measured at the blade or physically verified against the mower.

Remaining evidence gaps are therefore narrower:

- independent app/physical verification of the complete 11-level table
- confirmation that levels `1..11` are the complete valid protocol range rather than the range currently exposed by the researched O1200 UI
- cross-model applicability
- firmware/region differences, if any

The correct research task is now **validation of an implemented semantic mapping**, not discovery of the conversion formula.

# Cut mode / zone mowing speed: `cutMode`

The area-parameter protocol exposes:

```text
cutMode
```

represented as:

```text
cut_mode
```

PR #1767/#1768 maps the raw field.

The Home Assistant development branch adds a concrete semantic interpretation:

| `cutMode` | HA option | Interpreted mowing speed |
| ---: | --- | ---: |
| 7 | Gentle | 0.35 m/s |
| 4 | Efficient | 0.5 m/s |

Both directions of the mapping are covered by the HA helper tests.

The branch also defines the prospective user-facing control as:

```text
Area {area_id} mowing speed
```

This means the previous statement:

```text
mowing speed is not mapped
```

is too broad for the researched O1200.

A more accurate statement is:

> O1200 **zone mowing speed has an implemented/tested HA semantic mapping through `cutMode`**, while no separate standalone speed command/capability has been identified.

Status:

```text
Protocol observed
Client fork implemented/tested
HA semantic mapping implemented/tested
```

## Remaining limitation

The mapping should still be independently correlated with:

```text
official ECOVACS app option
physical mower speed
```

and verified across firmware/models before being generalized.

Do not automatically equate `cutMode` with the generic client:

```text
efficiency_mode
```

capability.

# Obstacle/environment mode: `obstacleHeight`

The O1200 area-parameter record includes:

```text
obstacleHeight
```

represented as:

```text
obstacle_height
```

The Home Assistant development branch maps the raw values as:

| `obstacleHeight` | HA semantic option |
| ---: | --- |
| 1 | Flat terrain / short grass `<10 cm` |
| 2 | Normal environment `<15 cm` |
| 3 | High-grass environment `<20 cm` |

Both directions of this mapping are covered by the HA helper tests.

This is more precise than treating `obstacleHeight` as a raw integer with completely unknown semantics.

However, these values should be understood as **HA development semantic labels/environment thresholds**, not as proof that the raw number itself is a direct centimetre measurement.

Status:

```text
Protocol observed
Client fork implemented/tested
HA semantic mapping implemented/tested
```

## Remaining limitation

Still worth independently validating:

```text
exact ECOVACS app wording
physical behavioural effect
whether the threshold describes grass/obstacle environment rather than sensor detection height
cross-model applicability
```

The setting remains distinct from:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
AnimalProtection
```

# Area angle: `angle`

The area-parameter protocol includes:

```text
angle
```

for a specific:

```text
areaID
```

PR #1767/#1768 maps the raw field.

The Home Assistant development branch implements the conversion:

```python
area_angle_to_degrees(raw) = (270 - raw) % 360
degrees_to_area_angle(degrees) = (270 - degrees) % 360
```

and tests examples including:

| Raw `angle` | User-facing angle |
| ---: | ---: |
| 180 | 90° |
| 145 | 125° |
| 216 | 54° |
| 0 | 270° |

Status:

```text
Protocol observed
Client fork implemented/tested
HA semantic conversion implemented/tested
```

## Relationship to global `cut_direction`

The reviewed upstream GOAT profiles also expose:

```text
settings.cut_direction
```

through:

```text
GetCutDirection
SetCutDirection
```

The zone-specific `AreaParameter.angle` conversion is now known at the HA semantic layer.

What remains unresolved is **not** how to convert the raw angle, but how this per-area setting relates architecturally/behaviourally to the global `cut_direction` setting.

Possible interpretations include:

- global default versus per-zone override
- older/global protocol versus newer zone-specific protocol
- model-generation differences
- separate app functions

That relationship still requires direct correlation.

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

The Home Assistant development branch:

```text
feature/ecovacs-area-parameter
```

contains more than a raw protocol experiment.

It currently provides:

```text
tested height conversion helpers
tested cutMode/speed mapping helpers
tested obstacle-mode mapping helpers
tested area-angle conversion helpers
a raw set_area_parameter service path
translations/descriptions for planned per-area controls
```

The raw lawn-mower service accepts the full tuple:

```text
area_id
mow_height_level
cut_mode
obstacle_height
angle
```

and calls the client's area-parameter capability.

## Important current limitation

The semantic helper mappings are implemented/tested, but the reviewed branch does not yet represent a complete finished native per-area entity implementation.

In particular, the presence of entity descriptions/translations should not be confused with every proposed `number`/`select` already being dynamically instantiated for all mower areas.

The accurate status is therefore:

```text
HA semantic mapping: implemented/tested
raw area-parameter service path: implemented
native per-area entity UX: incomplete/development
```

## Safe write rule remains unchanged

Because `setAreaParameter` writes the complete tuple, any higher-level UI exposing individual controls must:

1. read/cache the latest `AreaParameterEvent`
2. identify the selected `area_id`
3. preserve unchanged sibling parameters
4. convert the intended user-facing value to the raw protocol value
5. call `SetAreaParameter` with the complete tuple
6. use `onAreaParameter` to confirm resulting state

The semantic mappings documented above make steps 4 and the user-facing presentation much clearer, but they do not remove the complete-tuple requirement.

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
