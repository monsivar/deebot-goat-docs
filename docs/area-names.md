# O1200 area names and zone metadata

This page documents the ECOVACS GOAT O1200 area-name capability implemented in [`DeebotUniverse/client.py` PR #1774](https://github.com/DeebotUniverse/client.py/pull/1774) and the related Home Assistant development branch.

Last reviewed: **2026-08-24**

> [!IMPORTANT]
> PR #1774 is still open and is therefore development/fork functionality, not part of the reviewed upstream `dev` baseline.
>
> The Home Assistant area-name branch is also development work.

## Overview

The GOAT O1200 exposes human-readable lawn-area names through:

```text
getAreaSet
```

The command returns a compressed:

```text
subsets
```

payload.

The development parser decodes this data and emits the existing shared:

```text
RoomsEvent
```

with normalised:

```text
Room
```

objects.

Conceptually:

```text
getAreaSet
    │
    ▼
compressed subsets
    │
    ▼
decompress + JSON decode
    │
    ▼
RoomsEvent
    │
    ├── Room(id=4, name="Østkanten")
    ├── Room(id=1, name="Sentrum")
    └── Room(id=2, name="Vestkanten")
```

This provides a concrete O1200 mapping between protocol area identifiers and human-readable names.

## Evidence status

| Item | Status |
| --- | --- |
| `getAreaSet` request | Protocol observed / Fork implemented / Python tested |
| compressed `subsets` parsing | Fork implemented / Python tested |
| `RoomsEvent` output | Fork implemented / Python tested |
| O1200 `CapabilityClean.areas` | Fork implemented / Python tested |
| Real O1200 area IDs and names | Device/protocol validated |
| Live refresh without ECOVACS app open | Device tested |
| Home Assistant `rooms` attribute | HA development implemented / tested |
| Full mower map support | Not implied / not implemented by this PR |
| Selected-zone start command | Separate research/implementation topic |
| Cross-model area-name support | Unverified |

---

# Client capability

PR #1774 extends:

```text
CapabilityClean
```

with optional:

```python
areas: CapabilityEvent[RoomsEvent] | None
```

For the researched O1200 profile:

```python
areas=CapabilityEvent(
    RoomsEvent,
    [GetAreaSet()],
)
```

Conceptually:

```text
capabilities.clean
    │
    ├── action → mowing lifecycle
    └── areas  → area names / IDs
```

This is important because area metadata belongs to the mower operation domain without requiring full map support.

---

# `getAreaSet`

Python command:

```text
GetAreaSet
```

Wire command:

```text
getAreaSet
```

Request payload:

```json
{
  "mid": "1",
  "aid": "0",
  "type": "ar"
}
```

The development parser only handles data where:

```text
type = "ar"
```

and:

```text
subsets
```

is present.

Status:

**Protocol observed / Fork implemented / Python tested**

---

# Compressed `subsets`

The response contains area information in a compressed:

```text
subsets
```

value.

The implementation uses the existing client helper:

```text
decompress_base64_data
```

and then decodes the resulting JSON.

The parser intentionally reuses existing shared map/room infrastructure rather than introducing a mower-only name model.

---

# Normalised `RoomsEvent`

The decoded data becomes:

```text
RoomsEvent
```

with:

```text
Room
```

objects.

The relevant mapping is conceptually:

```text
subset[0]
    → map_id context

subset[1]
    → Room.id

subset[2]
    → Room.name
```

The current implementation does not use the area-name capability to claim zone geometry.

`Room.coordinates` is empty in this path.

---

# Real O1200 validation

PR #1774 documents a real-device capture from:

```text
GOAT O1200 LiDAR
hardware ID: 2i0fns
firmware: 1.13.10
```

The decoded areas were:

| Area ID | Name |
| ---: | --- |
| `4` | `Østkanten` |
| `1` | `Sentrum` |
| `2` | `Vestkanten` |

This is direct evidence for:

```text
area identifier → display name
```

on the tested O1200.

---

# Live refresh validation

The area-name capability was also tested end to end without the ECOVACS app open.

Observed flow:

```text
subscribe to RoomsEvent
        │
        ▼
capability refresh is triggered
        │
        ▼
GetAreaSet()
        │
        ▼
mower returns compressed area data
        │
        ▼
parser emits RoomsEvent
        │
        ▼
three expected names/IDs are available
```

This is stronger evidence than an isolated parser fixture because it confirms the refresh path against the physical mower.

---

# `areaID` and `Room.id`

The earlier area-parameter research established:

```text
areaID
```

as the identifier used by:

```text
getAreaParameter
setAreaParameter
onAreaParameter
```

The area-name work now provides normalised area IDs through:

```text
Room.id
```

with the same real-world zone identities.

This gives the project a concrete metadata relationship:

```text
area ID
   │
   ├── human-readable name via RoomsEvent
   └── area settings via AreaParameterEvent
```

For example:

```text
2
├── name: Vestkanten
└── area-parameter record: areaID = "2"
```

The Python types differ slightly:

```text
Room.id        → int
AreaParameter.area_id → str
```

so integrations should compare them using an intentional normalisation rather than relying on implicit type equality.

---

# Area names do not prove selected-zone start semantics

PR #1774 resolves:

```text
area ID → human-readable name
```

for the tested O1200.

It does **not** by itself resolve:

```text
which selected-zone mowing command consumes that ID
```

The reviewed upstream O1200 profile still lacks:

```text
CapabilityCleanAction.area
```

Therefore the following remain separate:

```text
Area metadata
    → getAreaSet

Area settings
    → get/set/onAreaParameter

Selected-zone mowing start
    → separate command/capability question
```

This distinction should be preserved in both client and Home Assistant design.

---

# Not full map support

PR #1774 deliberately leaves:

```text
capabilities.map
```

unset for the O1200.

This is correct.

Area names and IDs are metadata; they do not establish:

```text
boundary geometry
zone polygons
mower position
station position
route
mowing trace
```

Conceptually:

```text
area names support
      ≠
full mower map support
```

Map research remains separate.

---

# Home Assistant development

The Home Assistant branch:

```text
feature/ecovacs-mower-area-names
```

subscribes to:

```text
RoomsEvent
```

when:

```text
capabilities.clean.areas
```

is available.

It exposes the data as the mower entity extra-state attribute:

```text
rooms
```

Example from the automated test:

```yaml
rooms:
  ostkanten: 4
  sentrum: 1
  vestkanten: 2
```

Names are passed through Home Assistant:

```text
slugify
```

so:

```text
Østkanten
```

becomes:

```text
ostkanten
```

The attribute is marked unrecorded to avoid unnecessary recorder/history storage.

Status:

**HA development implemented / HA tested**

---

# Duplicate names

The Home Assistant branch handles duplicate slugified names.

Conceptually:

```text
same name once
    → name: ID

same name multiple times
    → name: [ID1, ID2, ...]
```

This avoids silently dropping an area when names collide.

A mature user-facing design may eventually prefer a structure that preserves both the original display name and ID explicitly.

---

# Integration design

The area-name capability enables user interfaces to display:

```text
Sentrum
Vestkanten
Østkanten
```

instead of raw IDs.

A long-term architecture could use:

```text
RoomsEvent
    │
    ▼
area metadata registry
    │
    ├── display name
    └── area ID
         │
         ├── AreaParameterEvent
         └── selected-zone mowing action
```

The final selected-zone action still depends on the separate mowing-start protocol.

---

# Relationship to `Room`

The development intentionally reuses the existing:

```text
Room
```

model.

For mower UI/documentation, this should be interpreted as:

```text
lawn area / zone
```

rather than an indoor vacuum room.

This is another example of shared DEEBOT terminology being reused at the client layer while the integration translates it into mower language.

---

# What PR #1774 resolves

The following former research gap is substantially resolved for the tested O1200:

```text
area ID → human-readable area name
```

Specifically:

```text
GetAreaSet
    → RoomsEvent
    → Room.id + Room.name
```

with real-device validation.

The following remain open:

```text
selected-zone start command/capability
multi-zone start encoding/order
zone geometry
full map support
cross-model area-name support
```

---

# Recommended next research

Now that IDs and names are known, selected-zone research can become more precise.

Recommended test:

```text
1. GetAreaSet
2. record known name/ID mapping
3. start one named zone
4. capture start payload
5. compare target with known area ID
6. repeat another zone
```

Goal:

```text
prove or disprove selected-zone target == GetAreaSet/areaID
```

This is higher value than searching blindly for zone identifiers.

---

# Related development

Client:

- [`PR #1774`](https://github.com/DeebotUniverse/client.py/pull/1774)
- earlier superseded zone-name work: PR #1626

Related area settings:

- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)

Home Assistant:

```text
feature/ecovacs-mower-area-names
```

---


# Relationship to the mower map stack

PR #1774 models O1200 area names as:

```text
GetAreaSet
   │
   ▼
RoomsEvent
   │
   ▼
CapabilityClean.areas
```

The newer stacked map draft #1788 reuses the same underlying:

```text
getAreaSet type="ar"
```

metadata directly inside the map pipeline.

It combines area IDs/names with:

```text
onArI geometry
```

to create:

```text
MowerWorkAreasEvent
```

with registered polygons.

PR #1788 explicitly describes this as superseding the **map-zone parsing direction** of #1774 if the new stack is accepted.

This does not invalidate the #1774 protocol observation or its Home Assistant area-name prototype.

It means the final client architecture should avoid independently decoding the same AreaSet data twice for one hardware profile unless there is a deliberate reason to expose both abstractions.

See:

[GOAT mower map support](map.md)

---

# Related documentation

- [Overview](overview.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Zones and areas](zones-and-areas.md)
- [GOAT mower map support](map.md)
- [O1200 area parameters](area-parameters.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
- [Protocol observations](../research/protocol-observations.md)
