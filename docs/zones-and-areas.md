# Zone and area mowing

This page documents selected-area mowing and zone-related protocol concepts for ECOVACS GOAT mowers.

Last reviewed: **2026-08-24**

## Overview

GOAT lawn zones appear in several different protocol contexts.

It is important not to treat all "area" functionality as one command.

Current research distinguishes at least:

```text
1. starting a mowing job for selected zone(s)
2. identifying a zone
3. reading/writing settings for a zone
4. retrieving zone names/metadata
5. map/geometry data
```

The O1200 area-parameter work improves our understanding of items 2 and 3.

It does **not** automatically solve items 1, 4 or 5.

---

# Generic selected-area mowing capability

The shared client exposes selected-area start through:

```text
Capabilities.clean.action.area
```

using an optional area command:

```python
CapabilityCleanAction(
    command=...,
    area=...,
)
```

Conceptually:

```text
CapabilityCleanAction
        │
        ├── command → START / PAUSE / RESUME / STOP
        └── area    → selected-area start
```

Once a selected-area job has started, normal lifecycle control still applies.

---

# `CleanAreaV2`

The generic V2 area implementation is:

```text
CleanAreaV2
```

It extends:

```text
CleanV2
```

and uses the same wire command family:

```text
clean_V2
```

General selected-area structure:

```json
{
  "act": "start",
  "content": {
    "type": "...",
    "value": "..."
  }
}
```

The client supports:

```text
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

with protocol values:

| Client mode | Protocol value |
| --- | --- |
| `SPOT_AREA` | `spotArea` |
| `CUSTOM_AREA` | `customArea` |
| `FREE_CLEAN` | `freeClean` |

These names are generic ECOVACS/DEEBOT terminology.

They should not automatically be treated as official GOAT app terminology.

---

# `spotArea`

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

The generic client can therefore encode multiple target identifiers.

### Physically verified O1200 area mowing — PR #1791

Physical tests against the **GOAT O1200 LiDAR (`2i0fns`)** in [`PR #1791`](https://github.com/DeebotUniverse/client.py/pull/1791) confirm:

1. **Single-area mowing:**
   ```json
   {
     "act": "start",
     "content": {
       "type": "spotArea",
       "value": 1
     }
   }
   ```
2. **Multi-area mowing:**
   ```json
   {
     "act": "start",
     "content": {
       "type": "spotArea",
       "value": "1,2"
     }
   }
   ```
   The area ID order is strictly preserved during serialization.
3. **Active mode retention:**
   When paused, resumed, or stopped during an area mowing job, the `content` dictionary must explicitly retain `{"type": "spotArea"}`:
   ```json
   {"act": "pause", "content": {"type": "spotArea"}}
   ```
4. **Unsupported modes:**
   The O1200 rejects vacuum modes like `customArea` and `freeClean`. Non-integer area IDs and empty area lists fail closed.

---

# `customArea`

Generic example:

```json
{
  "act": "start",
  "content": {
    "type": "customArea",
    "value": "1580.0,-4087.0,3833.0,-7525.0"
  }
}
```

The common client treats these as coordinate-style values.

This does not prove that arbitrary coordinate mowing works on every GOAT.

---

# `freeClean`

Generic example:

```json
{
  "act": "start",
  "content": {
    "type": "freeClean",
    "value": "1,5,8"
  }
}
```

The first value represents the generic:

```text
cleanings
```

count.

A test such as:

```text
2,0
```

means two operations for target `0` in the shared client test context.

The exact mower-specific meaning should remain evidence-based.

---

# Selected-zone mowing observed on a physical GOAT

A named lawn zone was selected through the ECOVACS app and used as its own mowing job.

The active job was then:

```text
started
paused
resumed
stopped
```

This confirms that the physical/app concept exists.

Evidence:

```text
APP + DEVICE + PROTOCOL
```

However, protocol research must distinguish:

```text
selected-zone start
```

from:

```text
zone settings
```

They are related through zone identity but are not the same operation.

---

# Upstream area capability by GOAT model

Reviewed upstream profiles expose `CleanAreaV2` as follows:

| Model | `CleanAreaV2` |
| --- | :---: |
| GOAT G1 | ✓ |
| GOAT A1600 RTK | ✓ |
| GOAT A3000 LiDAR Pro | ✓ |
| GOAT O500 Panorama | ✓ |
| GOAT O1200 LiDAR | — |

The O1200 profile exposes general:

```text
CleanV2
```

but no upstream:

```text
CapabilityCleanAction.area
```

This remains an implementation/research gap.

---

# O1200 area parameters: a different zone protocol family

O1200 protocol investigation identified:

```text
getAreaParameter
setAreaParameter
onAreaParameter
```

These commands/messages do not start mowing.

They read and change settings associated with known areas.

Each record contains:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

Python representation:

```python
AreaParameter(
    area_id=...,
    mow_height_level=...,
    cut_mode=...,
    obstacle_height=...,
    angle=...,
)
```

Multiple zone records are represented by:

```text
AreaParameterEvent
```

Detailed reference:

[O1200 area parameters](area-parameters.md)

---

# What `areaID` now establishes

The O1200 area-parameter protocol provides direct evidence that ECOVACS has a zone/area identifier:

```text
areaID
```

Example:

```text
"2"
```

This is stronger than the earlier generic hypothesis that "some numeric field probably identifies the zone".

We can now safely say:

> O1200 area-parameter state is keyed by an ECOVACS `areaID`.

However, this does not yet prove that:

```text
CleanAreaV2 spotArea value
```

uses the same exact ID format on O1200.

That relationship should be explicitly correlated before the client wires selected-zone mowing to the same identifier.

---

# Zone name versus `areaID`

PR #1774 substantially resolves the O1200 area-name metadata question.

The development capability uses:

```text
GetAreaSet
```

with wire command:

```text
getAreaSet
```

to decode area IDs and names into:

```text
RoomsEvent
```

Real O1200 validation produced:

```text
4 → Østkanten
1 → Sentrum
2 → Vestkanten
```

This provides a confirmed tested-device relationship:

```text
area ID → display name
```

for the O1200.

The same zone identity can therefore be represented conceptually as:

```text
display name
    │
    ▼
area ID
    │
    ├── RoomsEvent / metadata
    └── AreaParameterEvent / settings
```

The remaining open question is not the name mapping itself, but whether the selected-zone mowing **start command** consumes the same identifier directly.

See:

[O1200 area names](area-names.md)

---

# Per-zone cutting height

O1200 area parameters include:

```text
mowHeightLevel
```

This demonstrates that cutting height is zone-specific in this protocol family.

The remaining work is not command discovery.

It is value semantics:

```text
mowHeightLevel
       │
       ▼
app-selected / physical cutting height
```

Do not assume raw `10` means `10 mm`.

---

# Per-zone cut mode

O1200 area parameters include:

```text
cutMode
```

This is a known zone-specific raw field.

Open questions:

```text
Which app option changes it?
What does each integer mean?
Does it control pattern, efficiency, passes, or another concept?
```

Do not automatically equate it with generic `efficiency_mode`.

---

# Per-zone obstacle-height parameter

O1200 area parameters include:

```text
obstacleHeight
```

This establishes a zone-specific raw parameter.

Its exact physical unit and app meaning remain unresolved.

This parameter should be kept separate from global AI/avoidance toggles.

---

# Per-zone angle

O1200 area parameters include:

```text
angle
```

Observed/test values include:

```text
0
136
180
```

The original protocol investigation associates this with zone-specific mowing/clipping angle.

The relationship with global:

```text
settings.cut_direction
```

is not yet fully established.

---

# Complete-tuple writes

The setter:

```text
setAreaParameter
```

writes all values for one area:

```json
{
  "areaID": "2",
  "mowHeightLevel": 10,
  "cutMode": 7,
  "obstacleHeight": 1,
  "angle": 136
}
```

This matters for integrations.

Changing only one visible zone setting should preserve the current values of the others.

Recommended flow:

```text
read AreaParameterEvent
        │
        ▼
find target areaID
        │
        ▼
copy complete area record
        │
        ▼
modify one field
        │
        ▼
SetAreaParameter
        │
        ▼
onAreaParameter confirms state
```

---

# Getter and push schemas

Getter/push state is list-based:

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

This allows multiple zones to be represented in one event.

The setter is different: it writes one area using a flat object.

This asymmetry is intentional and should be preserved.

---


# Zone geometry in the static map stack

PR #1788 adds a fourth zone concept beyond start action, metadata and settings:

```text
registered work-area geometry
```

The draft joins:

```text
onArI
    → local work-area contour

getAreaSet type="ar"
    → area ID + display name

onMI
    → static main-map frame
```

and emits:

```text
MowerWorkAreasEvent
```

Each:

```text
MowerWorkArea
```

contains the user-visible name plus a:

```text
MowerMapTraceGroup
```

whose `group_id` preserves the area ID.

The raw `onArI` geometry is local rather than already positioned on the main map.

PR #1788 therefore registers each area using the longest shared contiguous RLE direction sequence with the static main boundary and applies a translation only.

Ambiguous registrations are rejected.

This means the earlier category:

```text
map/geometry data
```

is now **partially mapped** for the researched O1200 static-map stack.

It still does not solve:

```text
selected-zone start
multi-zone ordering
live position
dock position
live mowing plan
map editing
```

See:

[GOAT mower map support](map.md)

---

# What the area-parameter PRs do not solve

Even with `areaID` and zone settings mapped, the following remain separate research topics:

```text
exact O1200 selected-zone start command in client architecture
multi-zone start semantics
zone ordering
selected-zone start target ↔ known area IDs
zone geometry
map object relationships
schedule → zone relationships
```

This distinction prevents the documentation from overstating the scope of PR #1767/#1768.

---

# Multi-zone mowing

The generic `CleanAreaV2` can encode more than one numeric target.

GOAT-specific questions remain:

```text
Does O1200 selected-zone start use one or multiple areaID values?
What separator/encoding is used?
Does order matter?
Does physical mowing order follow payload order?
Are per-zone parameters read at job start?
```

These require controlled captures.

---

# Human-readable zone metadata

A complete Home Assistant implementation ideally needs:

```text
areaID
display name
possibly geometry
possibly ordering
```

The current area-parameter work gives us `areaID`, but not the display-name source.

This is a meaningful advance because future metadata research can now search specifically for the known IDs.

---

# Integration design

A future mower integration should separate:

```text
Zone metadata
    ├── areaID
    ├── display name
    └── geometry

Zone settings
    ├── mowing height
    ├── cut mode
    ├── obstacle-height parameter
    └── angle

Mowing action
    ├── selected zone(s)
    ├── start
    ├── pause/resume
    └── stop
```

This is more accurate than treating "zone" as one scalar setting.

---

# Current evidence summary

## Upstream implemented

```text
CapabilityCleanAction.area
CleanAreaV2
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

on the four upstream GOAT profiles that expose the area capability.

## Device/app observed

```text
selected-zone mowing
pause/resume/stop during a selected-zone job
human-readable zone names
```

## O1200 development/protocol observed

```text
areaID
getAreaParameter
setAreaParameter
onAreaParameter
mowHeightLevel
cutMode
obstacleHeight
angle
```

## Still open

```text
O1200 selected-zone start capability
exact mapping between selected-zone start IDs and areaID
zone names/metadata source
multi-zone ordering
complete physical semantics of area-parameter values
```

---

# Recommended next experiments

## Confirm start-ID relationship

Capture:

```text
start area A
start area B
```

and compare the start payload with known `areaID` values from:

```text
getAreaParameter
```

Goal:

```text
prove or disprove selected-zone target == areaID
```

## Verify selected-zone target IDs

Use `GetAreaSet` to record the known area IDs and names, then compare those IDs with the outgoing selected-zone start payload.

Goal:

```text
prove or disprove selected-zone target == known area ID
```

## Map height levels

Change only cutting height for one area and record:

```text
app height
mowHeightLevel
```

## Decode cut mode

Change one app mowing-mode choice at a time and record:

```text
app label
cutMode
```

## Decode obstacle height

Change only the relevant app option and record:

```text
app label/value
obstacleHeight
```

## Compare angle systems

Change zone angle and compare:

```text
AreaParameter.angle
CutDirectionEvent.angle
```

---

# Related documentation

- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Mowing control](mowing-control.md)
- [O1200 area parameters](area-parameters.md)
- [GOAT mower map support](map.md)
- [O1200 area names](area-names.md)
- [Settings](settings.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
