# Home Assistant integration

This page documents how ECOVACS GOAT mower functionality maps to Home Assistant and how mower-specific `deebot_client` capabilities can be represented safely.

Last reviewed against:

- `DeebotUniverse/client.py`
- Home Assistant branch `feature/ecovacs-mower-progress`
- mower development branches
- O1200 area-parameter work in PR #1767/#1768

Date: **2026-08-24**

## Architecture

The intended architecture is:

```text
ECOVACS mower
      │
      ▼
ECOVACS protocol
      │
      ▼
deebot_client
      │
      ├── commands
      ├── messages
      ├── events
      └── capabilities
             │
             ▼
Home Assistant Ecovacs integration
             │
             ▼
Home Assistant entities/actions
```

Home Assistant should consume normalised `deebot_client` capabilities rather than parse raw ECOVACS payloads directly.

---

# Current mower entity

GOAT devices are identified by:

```text
DeviceType.MOWER
```

and represented as:

```text
lawn_mower
```

The development implementation creates:

```text
EcovacsMower
```

for mower-capable devices.

---

# Current `lawn_mower` features

The reviewed development implementation exposes:

```text
START_MOWING
PAUSE
DOCK
```

Underlying client operations:

| Home Assistant action | `deebot_client` |
| --- | --- |
| Start mowing | `CleanV2(CleanAction.START)` |
| Pause | `CleanV2(CleanAction.PAUSE)` |
| Dock | `Charge()` |

These are covered by automated Home Assistant tests.

---

# Mower activity mapping

| `deebot_client` | Home Assistant |
| --- | --- |
| `State.CLEANING` | `MOWING` |
| `State.RETURNING` | `RETURNING` |
| `State.DOCKED` | `DOCKED` |
| `State.ERROR` | `ERROR` |
| `State.PAUSED` | `PAUSED` |
| `State.IDLE` | `PAUSED` |

`IDLE → PAUSED` is an integration compromise, not a physical semantic claim.

---

# Stop mowing

The client supports:

```text
CleanAction.STOP
```

and physical GOAT stop behaviour has been observed.

The reviewed Home Assistant mower entity does not expose stop as a current lawn-mower feature.

Therefore:

```text
client/protocol STOP
      │
      └── supported

Home Assistant mower
      │
      └── not currently exposed
```

---

# Start versus resume

Home Assistant uses:

```text
CleanAction.START
```

The shared client contains state-aware START/RESUME handling.

When current state is:

```text
PAUSED
```

a START request can be translated into:

```text
RESUME
```

This avoids needing a separate Home Assistant resume feature.

---

# Current mower statistics

Mower-oriented labels include:

```text
Area mowed
Mowing duration
Total area mowed
Total mowing duration
Total mowings
```

rather than vacuum-oriented terminology.

This is the preferred UI pattern.

---

# O1200 mowing progress

Development pair:

```text
client:
feature/mower-stats-progress

Home Assistant:
feature/ecovacs-mower-progress
```

The client adds:

```text
CapabilityStats.mowing_job_progress
```

and enables it for the researched O1200 profile.

Home Assistant uses the flag before applying mower-specific progress semantics.

---

# Current area mowed

For the progress path:

```text
StatsEvent.mowed_area
```

becomes:

```text
Area mowed
```

The current HA implementation uses square centimetres natively for this path and suggests square metres for display.

A test verifies:

```text
28699 cm² → 2.8699 m²
```

---

# Progress percentage

Home Assistant derives:

```python
mowed_area / area * 100
```

when both values are usable.

Missing input yields unknown, not an incorrect zero.

Status:

```text
Derived / HA implemented / HA tested
```

---

# Estimated mowing duration

For:

```text
mowing_job_progress=True
```

Home Assistant interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

with native seconds and suggested display in minutes.

Example test:

```text
2304 seconds → 38.4 minutes
```

This interpretation is model-gated.

It is not a universal statement about `StatsEvent.time`.

---

# Current O1200 progress entities

The development tests cover entities equivalent to:

```text
sensor.goat_o1200_lidar_area_mowed
sensor.goat_o1200_lidar_mowing_progress
sensor.goat_o1200_lidar_estimated_mowing_duration
```

---

# Common settings already fit generic HA platforms

Several common GOAT capabilities naturally map to existing Home Assistant entity patterns.

Examples:

| Capability | Representation |
| --- | --- |
| `advanced_mode` | switch |
| `true_detect` | switch |
| `border_switch` | switch |
| `child_lock` | switch |
| `moveup_warning` | switch |
| `cross_map_border_warning` | switch |
| `safe_protect` | switch |
| `cut_direction` | number |
| `volume` | number |

Less common configuration can be disabled by default to avoid clutter.

---

# Global cutting direction

The generic setting:

```text
settings.cut_direction
```

is represented as a Home Assistant:

```text
number
```

with current design:

```text
0–180°
step 1°
```

This is a global/shared capability.

It should not automatically be conflated with the new O1200 zone-specific:

```text
AreaParameter.angle
```

---

# O1200 area-parameter capability

Development PRs #1767/#1768 introduce:

```text
settings.area_parameter
```

with state:

```text
AreaParameterEvent
```

Each zone contains:

```text
area_id
mow_height_level
cut_mode
obstacle_height
angle
```

Detailed protocol documentation:

[O1200 area parameters](area-parameters.md)

Status:

```text
Client fork implemented
Python tested
Protocol observed
Home Assistant not yet exposed
```

---

# Why area parameters are not simple independent settings

The low-level setter requires:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

together.

There is no independent low-level command documented here such as:

```text
setMowHeight(areaID, value)
```

Therefore exposing four independent writable HA entities without state-preserving write logic would be unsafe.

Bad conceptual implementation:

```text
user changes height
      │
      ▼
send areaID + height only
```

when the protocol expects the complete tuple.

Also unsafe:

```text
user changes height
      │
      ▼
send default cutMode / obstacleHeight / angle
```

because this may overwrite valid zone configuration.

---

# Safe area-parameter write pattern

Recommended architecture:

```text
AreaParameterEvent
      │
      ▼
cache latest state
      │
      ▼
user changes one field
      │
      ▼
find target area_id
      │
      ▼
copy full current AreaParameter
      │
      ▼
replace requested field only
      │
      ▼
SetAreaParameter(...)
      │
      ▼
wait for onAreaParameter confirmation
```

This is the same complete-state principle used for other structured settings.

---

# Cutting height in Home Assistant

The status has changed.

For O1200 the protocol is now mapped through:

```text
mow_height_level
```

So the limitation is no longer:

```text
cutting height command unknown
```

Instead, the remaining blocker for a polished Home Assistant entity is the mapping:

```text
raw mowHeightLevel
       │
       ▼
physical/app cutting height
```

A user-facing `number` entity should only be created once the integration knows:

```text
minimum
maximum
step
unit
level-to-height conversion
```

## Possible interim designs

A low-level developer action could expose the raw tuple.

A user-facing height entity should wait for validated physical semantics.

This keeps Home Assistant from displaying a misleading "mm" value.

---

# Zone cut mode in Home Assistant

Raw field:

```text
cut_mode
```

is mapped.

A future Home Assistant:

```text
select
```

would be appropriate **if** the valid enum values and labels are known.

Current blocker:

```text
integer value → confirmed app/user-facing meaning
```

Do not reuse generic `efficiency_mode` merely because the concepts sound similar.

---

# Zone obstacle-height parameter in Home Assistant

Raw field:

```text
obstacle_height
```

is mapped.

A future entity type depends on the semantics:

```text
number
```

if it is a physical stepped height, or potentially:

```text
select
```

if ECOVACS exposes discrete categories.

The app/protocol mapping should determine the entity type.

---

# Zone angle in Home Assistant

Raw area field:

```text
angle
```

is mapped.

It should not immediately become a second obvious "Cut direction" entity until its relationship with:

```text
settings.cut_direction
```

is understood.

Potential designs include:

```text
global cut direction
per-zone mowing angle
```

if evidence shows they are separate concepts.

---

# Area names and IDs in Home Assistant

The client area-name development adds:

```text
CapabilityClean.areas
    │
    ▼
RoomsEvent
```

and the Home Assistant branch:

```text
feature/ecovacs-mower-area-names
```

subscribes to that event for mower entities.

The current branch exposes an extra-state attribute:

```text
rooms
```

on the mower.

The automated O1200 test verifies:

```yaml
rooms:
  ostkanten: 4
  sentrum: 1
  vestkanten: 2
```

The original ECOVACS names are:

```text
Østkanten
Sentrum
Vestkanten
```

Home Assistant uses:

```text
slugify
```

for the attribute keys, so `Østkanten` becomes `ostkanten`.

The attribute is marked as unrecorded to avoid unnecessary recorder/history storage.

Status:

**Client fork implemented / Device validated / HA development implemented / HA tested**

## Duplicate names

The branch preserves multiple IDs if different areas produce the same slugified name.

Conceptually:

```text
one matching name
    → name: id

duplicate matching names
    → name: [id1, id2, ...]
```

## Design implication

The O1200-specific:

```text
area ID → display name
```

metadata problem is now substantially solved in development.

The remaining selected-zone problem is how to **start mowing the chosen ID**, not how to discover its name.

See:

[O1200 area names](area-names.md)

---

# Area parameters do not solve selected-zone start

The current upstream O1200 profile still does not expose:

```text
CapabilityCleanAction.area
```

Therefore:

```text
configure zone 2
```

and:

```text
start mowing zone 2
```

must remain separate integration tasks.

A future Home Assistant zone-mowing action should only be added after the selected-zone start protocol/capability is confidently mapped.

---

# Potential Home Assistant area-parameter designs

Several designs are possible.

## 1. Composite action

A Home Assistant action accepting:

```text
area
mow height
cut mode
obstacle height
angle
```

closely matches the protocol.

Advantages:

```text
clear tuple semantics
no hidden partial write
```

Disadvantage:

```text
less convenient for dashboards
```

## 2. Per-zone entities

Example concept:

```text
number.front_lawn_cutting_height
select.front_lawn_cut_mode
number.front_lawn_angle
```

Advantages:

```text
automation-friendly
```

Challenges:

```text
entity count
zone metadata dependency
state-preserving writes
dynamic zones
```

## 3. Selected-zone controls

A zone selector plus controls for the selected zone.

Advantages:

```text
fewer entities
```

Challenges:

```text
stateful UI
multi-user automation ambiguity
```

No design should be chosen solely because it is easy to implement.

It should follow Home Assistant architecture and confirmed GOAT semantics.

---

# O1200 global settings in Home Assistant

PR #1778 provides the client-side capability layer for several O1200 global settings.

Detailed client reference:

[O1200 global settings](o1200-global-settings.md)

These are not all exposed by the reviewed Home Assistant mower branch.

# AI recognition

Capability:

```text
settings.ai_recognition
```

Likely representation:

```text
switch
```

Status:

```text
Client fork implemented / HA not yet exposed
```

User-facing naming should wait for stronger app-label correlation.

---

# Humanoid AI / smart avoidance

Capability:

```text
settings.humanoid_ai
```

Likely representation:

```text
switch
```

Implementation description:

```text
Smart mowing with avoidance
```

Raw protocol name should not automatically be exposed as the UI label.

---

# Narrow passage adaptation

Capability:

```text
settings.narrow_adapt
```

Likely representation:

```text
switch
```

Status:

```text
Client fork implemented / HA not yet exposed
```

---

# System and lifted-alarm volume

O1200 client development distinguishes:

```text
settings.volume
settings.fall_volume
```

The O1200 setter wiring uses an observed:

```text
0–10
```

scale with:

```text
total = 10
```

and separate channels:

```text
sys
fall
```

Likely representation:

```text
number
```

The two channels should remain separate.

A third read payload field:

```text
searchVolume
```

should **not** be exposed as writable in Home Assistant because no setter protocol has been observed.

---

# Animal protection is structured state

Animal protection contains:

```text
enabled
start
end
```

A possible HA representation is:

```text
switch
time start
time end
```

But `SetAnimalProtection` writes all three fields together.

Every write must therefore preserve the latest other values.

Recommended pattern:

```text
latest AnimalProtectionEvent
       │
       ▼
replace one field
       │
       ▼
send complete enabled/start/end configuration
       │
       ▼
wait for onAnimProtect
```

---

# Rain configuration is structured state

Rain configuration contains:

```text
enabled
delay
```

Possible representation:

```text
switch
number/select for delay
```

Current development delay values:

```text
0–300 minutes
step 30
```

Writes should preserve the sibling field.

For example, disabling rain protection should preserve the configured delay unless explicitly changed.

There is currently no documented `getRainDelay` refresh command; state is reported through `onRainDelay`.

---

# Runtime protection state

`ProtectStateEvent` contains runtime booleans.

Recommended representation:

```text
binary_sensor
```

Potential fields:

```text
is_rain_protect
is_rain_delay
is_anim_protect
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

These are not writable settings.

Unclear fields should not receive confident user-facing names.

---

# Zone mowing

Selected-zone mowing is not exposed by the reviewed `EcovacsMower`.

A future architecture should separate:

```text
Zone metadata
    ├── area ID
    ├── name
    └── geometry

Zone configuration
    ├── height
    ├── mode
    ├── obstacle parameter
    └── angle

Mowing action
    ├── selected zone(s)
    └── start
```

This reflects the protocol more accurately than a single "zone" scalar.

---


# GOAT map stack and Home Assistant

The client map stack in PR #1789 is designed to preserve the existing public:

```text
device.map
Map.get_svg_map()
```

path.

This is favourable for a future Home Assistant integration because HA should not need a separate GOAT-specific SVG renderer.

However, PR #1789 explicitly does **not** include Home Assistant compatibility changes and does not yet wire the mower map capability into the O1200 hardware profile.

Current status:

```text
static parser/events
    implemented in stacked client drafts

shared SVG renderer
    implemented in stacked client draft

O1200 map capability wiring
    not yet implemented

Home Assistant map entity/image integration
    not yet implemented
```

A future HA implementation should initially expose only the evidence-backed static layers:

```text
main lawn boundary
registered work-area polygons
```

It should **not** render:

```text
mower position
dock
onMapTrack
current area
```

until the live coordinate semantics are independently proven.

The static stack is documented in:

[GOAT mower map support](map.md)

---

# Mowing speed

A dedicated mower-speed protocol remains unmapped.

Do not create a speculative HA `number` or `select` until the protocol shape is known.

---

# Entity-type guidelines

| Capability shape | Home Assistant representation |
| --- | --- |
| Main mower lifecycle | `lawn_mower` |
| Boolean writable setting | `switch` |
| Numeric setting | `number` |
| Fixed enum/options | `select` |
| Measurement | `sensor` |
| Runtime boolean | `binary_sensor` |
| Scheduled time | `time` |
| Composite/structured write | action/service or carefully coordinated entities |
| Multi-zone selection/action | dedicated action/UI design based on semantics |

The semantic shape matters more than the Python type alone.

---

# Capability-driven creation

Home Assistant should continue to create entities based on capabilities:

```text
capability absent
     │
     ▼
no entity

capability present
     │
     ▼
entity/action available
```

This is preferable to hard-coding:

```python
if model == "O1200":
```

where the client can express the distinction in the hardware profile.

---

# Home Assistant should not parse raw ECOVACS fields

Raw names such as:

```text
mowHeightLevel
cutMode
obstacleHeight
mowedArea
isRainProtect
```

belong in `deebot_client`.

Home Assistant should ideally consume:

```text
AreaParameterEvent.mow_height_level
AreaParameterEvent.cut_mode
AreaParameterEvent.obstacle_height
StatsEvent.mowed_area
ProtectStateEvent.is_rain_protect
```

This keeps reverse-engineering logic in the protocol client.

---

# Current implementation summary

## Implemented in reviewed HA mower work

```text
lawn_mower entity
start
pause
dock
mower-aware state mapping
battery
maintenance sensors
mower-specific statistics labels
```

## Implemented in HA progress work

```text
current area mowed
mowing progress %
estimated mowing duration
```

## Client features requiring HA work

```text
area_parameter
area names / `RoomsEvent` metadata (separate HA area-name branch)
AI recognition
Humanoid AI / smart avoidance
narrow adaptation
animal protection
rain configuration
lifted-alarm volume
runtime protection state
```

## Protocol/client work still needed before HA

```text
mowing speed
O1200 selected-zone start capability
selected-zone start capability
unresolved security-state semantics
```

## Semantic mapping needed before polished HA entities

```text
mowHeightLevel → physical height
cutMode → labels/options
obstacleHeight → user meaning/unit
area angle ↔ global cut direction
```

---

# Recommended development order for area parameters

```text
1. Client GET/SET/PUSH implementation
       │
       ▼
2. Client tests
       │
       ▼
3. Hardware capability
       │
       ▼
4. Map raw values to app/physical semantics
       │
       ▼
5. Resolve areaID → display name
       │
       ▼
6. Choose HA entity/action architecture
       │
       ▼
7. Implement state-preserving writes
       │
       ▼
8. Add HA tests/translations
       │
       ▼
9. Physical end-to-end verification
```

Steps 1–3 are substantially represented by PR #1767/#1768.

---

# Relevant development work

Client:

- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)
- [`Issue #1610`](https://github.com/DeebotUniverse/client.py/issues/1610)

Home Assistant progress branch:

- `feature/ecovacs-mower-progress`

---

# Related documentation

- [Overview](overview.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [GOAT mower map support](map.md)
- [O1200 area parameters](area-parameters.md)
- [O1200 global settings](o1200-global-settings.md)
- [O1200 area names](area-names.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Protocol reference](protocol-reference.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
