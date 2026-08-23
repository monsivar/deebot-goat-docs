# Supported GOAT mower models

This page documents ECOVACS GOAT mower models with dedicated hardware profiles in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py), together with model-specific capabilities currently implemented in GOAT development work.

Last reviewed:

- upstream `DeebotUniverse/client.py` `dev`
- O1200 area-name development in [`PR #1774`](https://github.com/DeebotUniverse/client.py/pull/1774)

Date: **2026-08-24**

## What "supported" means here

A model being listed means that `deebot_client` contains a dedicated hardware profile and identifies the device as a mower.

It does **not** mean every physical/app feature is implemented.

Support has several layers:

```text
hardware profile exists
      │
      ▼
commands implemented
      │
      ▼
events parsed
      │
      ▼
capabilities exposed
      │
      ▼
physical semantics verified
      │
      ▼
consumer integration support
```

This page therefore separates:

```text
reviewed upstream support
```

from:

```text
development/fork support
```

---

# Reviewed upstream mower profiles

| Model | Hardware ID | Hardware profile |
| --- | --- | --- |
| ECOVACS GOAT G1 | `5xu9h3` | `deebot_client/hardware/5xu9h3.py` |
| ECOVACS GOAT A1600 RTK | `xmp9ds` | `deebot_client/hardware/xmp9ds.py` |
| ECOVACS GOAT A3000 LiDAR Pro | `51rcxt` | `deebot_client/hardware/51rcxt.py` |
| ECOVACS GOAT O500 Panorama | `300lc5` | `deebot_client/hardware/300lc5.py` |
| ECOVACS GOAT O1200 LiDAR | `2i0fns` | `deebot_client/hardware/2i0fns.py` |

All use:

```python
device_type=DeviceType.MOWER
```

---

# Reviewed upstream capability comparison

A check mark means the capability is connected in the reviewed upstream hardware profile.

| Capability | G1 | A1600 RTK | A3000 LiDAR Pro | O500 Panorama | O1200 LiDAR |
| --- | :---: | :---: | :---: | :---: | :---: |
| Availability | ✓ | ✓ | ✓ | ✓ | ✓ |
| Battery | ✓ | ✓ | ✓ | ✓ | ✓ |
| Return to / charge at station | ✓ | ✓ | ✓ | ✓ | ✓ |
| General mowing action | ✓ | ✓ | ✓ | ✓ | ✓ |
| Area mowing via `CleanAreaV2` | ✓ | ✓ | ✓ | ✓ | — |
| Custom command support | ✓ | ✓ | ✓ | ✓ | ✓ |
| Error reporting | ✓ | ✓ | ✓ | ✓ | ✓ |
| Network information | ✓ | ✓ | ✓ | ✓ | ✓ |
| Play sound | ✓ | ✓ | ✓ | ✓ | ✓ |
| Current mower state | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mowing statistics | ✓ | ✓ | ✓ | ✓ | ✓ |
| Total statistics | ✓ | ✓ | ✓ | ✓ | ✓ |
| Consumable lifetime | ✓ | ✓ | ✓ | ✓ | ✓ |

This table describes only the reviewed upstream baseline.

Development capabilities are documented separately below.

---

# Common upstream mowing actions

All five profiles use:

```text
CleanV2
```

for general mowing control.

The shared action set includes:

```text
START
PAUSE
RESUME
STOP
```

G1, A1600 RTK, A3000 LiDAR Pro and O500 Panorama additionally expose:

```text
CleanAreaV2
```

through:

```text
CapabilityCleanAction.area
```

The reviewed upstream O1200 profile does **not**.

This means:

> Selected-area mowing is not currently exposed through the O1200 upstream hardware capability.

It does **not** mean the physical O1200 lacks selected-zone mowing.

Physical/app testing has demonstrated selected-zone behaviour.

---

# O1200 development capability picture

The researched O1200 currently has several development capabilities that go beyond the reviewed upstream baseline.

## Area names — PR #1774

PR #1774 adds:

```text
CapabilityClean.areas
```

using:

```text
CapabilityEvent(
    RoomsEvent,
    [GetAreaSet()],
)
```

for:

```text
2i0fns
```

This makes named area metadata available without adding full map support.

Status:

```text
Fork implemented
Python tested
Protocol observed
Live-device end-to-end verified
```

## Area parameters — PR #1767/#1768

Development work exposes:

```text
settings.area_parameter
```

with:

```text
AreaParameterEvent
GetAreaParameter
SetAreaParameter
onAreaParameter
```

Fields:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

Status:

```text
Fork implemented
Python tested
Protocol observed
```

## Mowing job progress — PR #1771

Development work exposes:

```text
StatsEvent.mowed_area
CapabilityStats.mowing_job_progress
```

for the researched O1200 progress semantics.

Status:

```text
Fork implemented
Python tested
Protocol/device observed
```

## Additional mower settings — development

O1200-focused development also includes:

```text
rain_delay
ai_recognition
humanoid_ai
narrow_adapt
animal_protection
fall_volume
protect_state
```

These should not be described as reviewed upstream features until merged.

---

# O1200 area names

PR #1774 uses:

```text
getAreaSet
```

to retrieve compressed area metadata.

Request:

```json
{
  "mid": "1",
  "aid": "0",
  "type": "ar"
}
```

The decoded result is normalised into:

```text
RoomsEvent
```

containing existing:

```text
Room
```

objects.

A live O1200 capture on firmware:

```text
1.13.10
```

decoded:

| Area ID | Name |
| ---: | --- |
| 4 | `Østkanten` |
| 1 | `Sentrum` |
| 2 | `Vestkanten` |

An end-to-end test was also performed without the ECOVACS app open:

```text
subscribe to RoomsEvent
      │
      ▼
capability refresh triggers
      │
      ▼
GetAreaSet
      │
      ▼
mower response
      │
      ▼
decode compressed subsets
      │
      ▼
RoomsEvent with names and IDs
```

This gives high confidence in the O1200 area-name capability.

---

# Area names do not equal map support

PR #1774 explicitly keeps:

```text
capabilities.map
```

unset for O1200.

Therefore:

```text
area names supported
```

does **not** imply:

```text
full mower map supported
```

This is an intentional architectural distinction.

The O1200 development profile can have:

```text
clean.areas
```

while:

```text
map is None
```

Full map parsing/rendering remains separate work.

---

# Area names do not equal selected-zone start

Another important distinction:

```text
clean.areas
```

provides:

```text
area metadata
```

while:

```text
clean.action.area
```

would provide:

```text
selected-area mowing action
```

The O1200 development evidence currently supports:

```text
area ID/name retrieval
```

but the reviewed upstream hardware profile still does not expose:

```text
CleanAreaV2
```

for O1200.

Therefore:

```text
O1200 area names: implemented in development
O1200 selected-zone client action: still unresolved
```

---

# O1200 ID-to-name mapping

The area-name work resolves an important previous gap.

For the tested mower:

```text
areaID / area number
        │
        ▼
human-readable display name
```

can now be obtained from the mower.

Example:

```text
1 → Sentrum
2 → Vestkanten
4 → Østkanten
```

This is useful when combined with the separate area-parameter work, which also identifies zones using:

```text
areaID
```

The next protocol question is no longer:

```text
Can we retrieve zone names?
```

but:

```text
Does the selected-zone start command use the same IDs?
```

---


# GOAT map development status

The current map stack should not yet be represented as an enabled O1200 `map` capability in the model matrix.

The stacked drafts implement:

```text
#1567 — shared mower grouped geometry / onMapTrace
#1782 — O1200 static onMI boundary
#1788 — O1200 work areas + names + registration
#1789 — shared Map capability + static SVG rendering
```

but #1789 explicitly does **not** wire:

```text
CapabilityMap.mower
```

into:

```text
2i0fns
```

yet.

Therefore the correct current O1200 status is:

```text
protocol/parser evidence: high
software static-map stack: implemented in drafts
hardware capability enabled: no
upstream merged: no
Home Assistant map: no
```

PR #1567 has direct `onMapTrace` evidence from the A1600 RTK firmware 1.15.13, but the O1200 static-map parser/registration fixtures must not automatically be enabled for A1600 or other GOAT models.

See:

[GOAT mower map support](map.md)

---

# Common state handling

All five reviewed upstream mower profiles use state retrieval including:

```text
GetChargeState
GetCleanInfoV2
```

This contributes to:

```text
StateEvent
```

with mower states such as:

```text
CLEANING
PAUSED
RETURNING
DOCKED
IDLE
ERROR
```

At the UI layer:

```text
CLEANING → MOWING
```

---

# Common upstream settings

The reviewed upstream profiles expose a common set including:

```text
advanced_mode
border_switch
cut_direction
child_lock
moveup_warning
cross_map_border_warning
safe_protect
true_detect
volume
```

These are common client capabilities.

The exact wording/physical semantics may still differ from app labels.

---

# Cutting direction

Reviewed upstream exposes:

```text
GetCutDirection
SetCutDirection
```

through:

```text
settings.cut_direction
```

This is separate from the O1200 development area parameter:

```text
AreaParameter.angle
```

until their relationship is conclusively established.

---

# O1200 cutting height

The reviewed upstream baseline does not expose a dedicated cutting-height setting.

However, O1200 development work maps:

```text
mowHeightLevel
```

inside:

```text
AreaParameter
```

Therefore the correct O1200 development status is:

```text
raw protocol field mapped
GET/SET/PUSH implemented
physical height mapping incomplete
```

It should not be described as completely "not mapped".

---

# O1200 cut mode

The raw zone field:

```text
cutMode
```

is implemented in development.

Its integer-to-app-label semantics remain incomplete.

It should not automatically be equated with a generic:

```text
efficiency_mode
```

capability.

---

# O1200 obstacle-height parameter

Development area parameters include:

```text
obstacleHeight
```

The raw field is known.

Its exact unit, valid range and physical meaning remain under research.

---

# Mowing speed

A dedicated mower-speed protocol/capability remains unmapped in the documented work.

Status:

```text
Open research
```

---

# Common consumable lifetime

G1, A1600 RTK, A3000 LiDAR Pro and O500 Panorama expose:

```text
BLADE
LENS_BRUSH
```

The O1200 additionally exposes:

```text
WEED_ROPE
TRIMMER_BRUSH
```

Its full reviewed upstream lifetime set is therefore:

```text
BLADE
LENS_BRUSH
WEED_ROPE
TRIMMER_BRUSH
```

This model-specific support originated from earlier O1200 work and was merged upstream.

The presence of a lifespan type does not necessarily prove that every retail configuration includes the physical accessory.

---

# Statistics

All five reviewed upstream profiles expose:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

with refresh commands including:

```text
GetStats
GetTotalStats
```

Mower-specific progress semantics are documented separately.

For O1200 development:

```text
area
mowedArea
time
```

have been correlated with planned area, mowed area and estimated total mowing duration.

---

# Home Assistant development status

Current Home Assistant mower development provides native:

```text
lawn_mower
```

representation.

Additional O1200 development work includes:

```text
mowing progress
estimated mowing duration
area names
```

The area-name branch subscribes to:

```text
RoomsEvent
```

and exposes a mower attribute equivalent to:

```yaml
rooms:
  ostkanten: 4
  sentrum: 1
  vestkanten: 2
```

This is development-branch support, not reviewed upstream Home Assistant support.

---

# Development capability matrix

The following table summarises major O1200 capabilities added in the documented development work.

| O1200 feature | Client capability/event | Status |
| --- | --- | --- |
| Area names | `clean.areas` / `RoomsEvent` | PR #1774 / tested / live verified |
| Area parameters | `settings.area_parameter` / `AreaParameterEvent` | PR #1767/#1768 / tested |
| Cutting-height raw level | `AreaParameter.mow_height_level` | mapped; physical conversion incomplete |
| Zone cut mode | `AreaParameter.cut_mode` | mapped; enum semantics incomplete |
| Zone obstacle-height | `AreaParameter.obstacle_height` | mapped; semantics incomplete |
| Zone angle | `AreaParameter.angle` | mapped; global relationship incomplete |
| Mowing progress | `StatsEvent.mowed_area` + flag | PR #1771 / tested |
| Rain configuration | `rain_delay` | development / tested |
| Runtime protection | `ProtectStateEvent` | development / tested |
| AI recognition | `ai_recognition` | development / tested |
| Smart avoidance | `humanoid_ai` | development / tested |
| Narrow adaptation | `narrow_adapt` | development / tested |
| Animal protection | `animal_protection` | development / tested |
| Lifted-alarm volume | `fall_volume` | development / tested |

These rows should not be interpreted as merged upstream unless their PR status changes.

---

# Capabilities still incomplete

After the recent O1200 work, several earlier gaps have narrowed.

## No longer fully unknown for O1200

```text
area IDs/names
cutting-height raw field
zone cut-mode raw field
zone obstacle-height field
zone mowing angle
current mowing progress
rain configuration
several AI/protection settings
```

## Still incomplete

```text
selected-zone start capability
multi-zone start/order
mowHeightLevel → physical height
cutMode → app labels/behaviour
obstacleHeight → physical meaning/unit
AreaParameter.angle ↔ global cut_direction
mowing speed
cross-model verification
scheduling
full mower map capability
```

---

# Model differences should be evidence-based

Do not infer protocol support from marketing similarity.

Prefer evidence from:

1. hardware profile
2. command/event implementation
3. real protocol payload
4. automated tests
5. reproducible app/device behaviour

For development features, enable additional models only after comparable evidence exists.

---

# Current reviewed upstream summary

At the reviewed upstream baseline:

- five dedicated GOAT mower profiles are present
- all five are `DeviceType.MOWER`
- all five expose `CleanV2`
- four expose `CleanAreaV2`
- O1200 does not expose upstream `CleanAreaV2`
- all five expose the common settings group
- all five expose statistics and total statistics
- all five expose blade and lens-brush lifetime
- O1200 additionally exposes weed-rope and trimmer-brush lifetime

---

# Current O1200 development summary

With the documented open development PRs/branches, the O1200 picture is broader:

```text
general mowing
    ✓

area names and IDs
    ✓ PR #1774

zone-specific settings
    ✓ PR #1767/#1768

mowing progress
    ✓ PR #1771

rain/AI/protection settings
    ✓ development branches

selected-zone start capability
    still incomplete

static map hardware wiring + live map layers
    separate/incomplete
```

---

# Related documentation

- [Overview](overview.md)
- [Capability architecture](capabilities.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [GOAT mower map support](map.md)
- [O1200 area names](area-names.md)
- [O1200 area parameters](area-parameters.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
