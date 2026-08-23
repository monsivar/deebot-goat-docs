# GOAT capability architecture

This page explains how ECOVACS GOAT mower functionality is represented by the capability architecture in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py).

Last reviewed:

- upstream `DeebotUniverse/client.py` `dev`
- device-specific command-routing development in [`PR #1772`](https://github.com/DeebotUniverse/client.py/pull/1772)
- O1200 area-name development in [`PR #1774`](https://github.com/DeebotUniverse/client.py/pull/1774)

Date: **2026-08-24**

> [!IMPORTANT]
> PR #1774 was still open at the time of this review.
>
> The `CapabilityClean.areas` / `GetAreaSet` functionality described as development support is therefore not part of the reviewed upstream `dev` baseline unless stated otherwise.

## Overview

`deebot_client` uses a capability model to describe what each supported device can do.

For GOAT devices, a hardware profile creates a:

```python
Capabilities(...)
```

object and identifies the device as:

```python
device_type=DeviceType.MOWER
```

The same capability framework is shared with DEEBOT vacuum robots.

As a result, common names such as:

```text
clean
cleaning
room
CleanAction
CleanMode
```

are still used internally even when the physical device is a robotic mower.

For GOAT documentation and integrations, these normally map conceptually to:

```text
mow
mowing
lawn area / zone
mowing action
mowing/area mode
```

---

# Architecture

At a high level:

```text
Hardware profile
      │
      ▼
Capabilities
      │
      ├── commands
      │     │
      │     ▼
      │  ECOVACS protocol
      │
      └── events
            │
            ▼
      normalised state
            │
            ▼
      consumer integration
```

A hardware profile therefore describes which normalised capabilities are enabled for a particular model.

---

# Commands, messages and events

## Command

A command requests information or asks the mower to perform/change something.

Examples:

```text
GetBattery
Charge
CleanV2
GetCleanInfoV2
GetStats
GetAreaSet
SetAreaParameter
SetRainDelay
```

Commands can be used to:

- request state
- start or control mowing
- return to the station
- read configuration
- change configuration

## Message

A message represents data returned or pushed through the ECOVACS protocol.

Examples include:

```text
onStats
onAreaParameter
onRainDelay
onProtectState
```

Message handlers parse protocol payloads and publish normalised events.

## Event

An event is the normalised state exposed internally by `deebot_client`.

Examples:

```text
BatteryEvent
StateEvent
StatsEvent
RoomsEvent
AreaParameterEvent
RainDelayEvent
ProtectStateEvent
```

Consumers should generally depend on these events rather than directly parse ECOVACS payloads.

---

# Common readable flow

A typical readable capability is:

```text
GET command
    │
    ▼
ECOVACS response
    │
    ▼
parser/message handling
    │
    ▼
Event
```

For example, in PR #1774:

```text
GetAreaSet
    │
    ▼
getAreaSet response
    │
    ▼
compressed subsets decoded
    │
    ▼
RoomsEvent
```

---

# Common writable flow

A typical writable setting follows:

```text
GET current state
      │
      ▼
Event
      ▲
      │
SET new state
```

Some settings additionally receive a push message:

```text
SET
 │
 ▼
device accepts command
 │
 ▼
on...
 │
 ▼
Event
```

The O1200 area-parameter capability is one example.

---

# Core capability types

## `CapabilityEvent`

`CapabilityEvent` represents state that can be refreshed and represented by an event.

Conceptually:

```python
CapabilityEvent(
    event=SomeEvent,
    get=[SomeGetCommand()],
)
```

It contains:

- an event type
- zero or more commands that can refresh that event

Example:

```python
battery=CapabilityEvent(
    BatteryEvent,
    [GetBattery()],
)
```

PR #1774 uses the same abstraction for O1200 area names:

```python
areas=CapabilityEvent(
    RoomsEvent,
    [GetAreaSet()],
)
```

This is significant because zone names become a normal capability-driven state source rather than a special-case map parser.

---

# `CapabilitySet`

`CapabilitySet` extends `CapabilityEvent` with a setter.

Conceptually:

```python
CapabilitySet(
    event=SomeEvent,
    get=[GetSomething()],
    set=SetSomething,
)
```

Pattern:

```text
GET
SET
EVENT
```

Examples in GOAT development include structured mower settings such as O1200 area parameters.

---

# `CapabilitySetEnable`

`CapabilitySetEnable` is a specialised boolean writable capability.

Its user-facing value is effectively:

```text
True / False
```

Common GOAT examples include:

```text
advanced_mode
border_switch
child_lock
moveup_warning
cross_map_border_warning
safe_protect
true_detect
```

Development-only O1200 examples include:

```text
ai_recognition
humanoid_ai
narrow_adapt
```

This capability shape maps naturally to a Home Assistant switch.

---

# `CapabilityExecute`

`CapabilityExecute` represents an action rather than a persistent configuration value.

Example:

```python
CapabilityExecute(Charge)
```

This is appropriate for actions such as:

```text
return to charging station
play sound
```

---

# `CapabilityTypes`

`CapabilityTypes` describes a known set of supported enum/type values.

This is useful when an integration needs to know which options are valid.

---

# `CapabilitySetTypes`

`CapabilitySetTypes` combines:

- readable state
- setter
- explicit supported options

It is useful for settings that behave like a select/list rather than a free numeric value.

---

# `CapabilityNumber`

`CapabilityNumber` represents a numeric writable setting with explicit bounds.

Conceptually:

```text
event
get
set
min
max
```

This is suitable when the physical semantics are known.

For example, a user-facing cutting-height number should only use this kind of abstraction once:

```text
minimum
maximum
step
unit
raw-value conversion
```

are established.

The O1200 raw `mowHeightLevel` field is mapped in development, but its complete physical-height mapping is still being researched.

---

# `CapabilityCleanAction`

Mowing lifecycle control is represented through:

```text
CapabilityCleanAction
```

The reviewed structure contains:

```python
command
area
```

where:

```text
command
```

is the main start/pause/resume/stop command and:

```text
area
```

is an optional selected-area start command.

Conceptually:

```python
CapabilityCleanAction(
    command=CleanV2,
    area=CleanAreaV2,
)
```

The area command is optional.

This allows a mower to support general mowing without exposing selected-area start through the same command family.

---

# `CapabilityClean`

`CapabilityClean` is the shared operation/mowing capability.

In the reviewed upstream baseline it contains the main:

```text
action
```

capability and optional shared fields used by different ECOVACS product families.

PR #1774 adds another optional field:

```python
areas: CapabilityEvent[RoomsEvent] | None = None
```

This is a major conceptual distinction.

The development structure becomes:

```text
CapabilityClean
├── action
│   ├── command
│   └── area
│
└── areas
    └── readable zone/area metadata
```

## `action.area` versus `areas`

These two fields serve different purposes.

### `clean.action.area`

Means:

```text
How can a selected area/zone mowing job be started?
```

For example:

```text
CleanAreaV2
```

### `clean.areas`

Means:

```text
Which named areas/zones does the device report?
```

PR #1774 uses:

```text
RoomsEvent
```

with:

```text
GetAreaSet()
```

for this metadata.

Therefore:

```text
clean.action.area
```

and:

```text
clean.areas
```

must not be treated as aliases.

A device can expose one without the other.

---

# O1200 area-name capability

PR #1774 wires the researched O1200 profile conceptually as:

```python
clean=CapabilityClean(
    action=CapabilityCleanAction(
        command=CleanV2,
    ),
    areas=CapabilityEvent(
        RoomsEvent,
        [GetAreaSet()],
    ),
)
```

This means the O1200 development profile can:

```text
start general mowing
```

and:

```text
read named lawn areas
```

while still not exposing:

```text
CleanAreaV2
```

through:

```text
clean.action.area
```

That separation accurately reflects the current evidence.

Status:

```text
area names: fork implemented / tested / live-device verified
selected-area start capability: still unresolved for O1200
```

---

# `RoomsEvent`

PR #1774 deliberately reuses the existing:

```text
RoomsEvent
```

and:

```text
Room
```

models.

For GOAT, the generic "room" abstraction represents a mower area/zone.

A decoded O1200 event can contain:

```python
RoomsEvent(
    map_id="1",
    rooms=[
        Room("Østkanten", 4, ""),
        Room("Sentrum", 1, ""),
        Room("Vestkanten", 2, ""),
    ],
)
```

This is useful because existing consumers already understand the event model.

At the user-facing layer:

```text
room
```

should normally be presented as:

```text
area
```

or:

```text
zone
```

for a mower.

---

# `GetAreaSet`

PR #1774 adds:

```text
GetAreaSet
```

with wire name:

```text
getAreaSet
```

Request arguments:

```json
{
  "mid": "1",
  "aid": "0",
  "type": "ar"
}
```

The command:

1. verifies the returned type is `ar`
2. reads the compressed `subsets` field
3. decompresses it using the existing helper
4. parses the decoded JSON structure
5. creates `Room` objects
6. publishes a `RoomsEvent`

Conceptually:

```text
compressed subsets
      │
      ▼
decompress
      │
      ▼
area records
      │
      ├── map ID
      ├── area ID
      └── area name
      │
      ▼
RoomsEvent
```

---

# Area names do not imply map support

PR #1774 explicitly leaves:

```text
capabilities.map
```

unset for O1200.

This is important.

The capability means:

```text
named area metadata is available
```

not:

```text
full map capability is implemented
```

A mower can therefore have:

```text
clean.areas != None
```

while:

```text
map == None
```

This is an intentional architecture decision.

---


# Device-specific command lookup

PR #1772 extends the capability architecture with a second derived lookup in addition to event refresh commands.

Existing capability derivation:

```text
Event type → GET command(s)
```

Development addition:

```text
wire command NAME → command class
```

Conceptually:

```text
Capabilities
   │
   ├── _events
   │     └── Event → refresh commands
   │
   └── _commands
         └── NAME → configured command implementation
```

The new helper is:

```python
Capabilities.get_command(name)
```

This allows two devices to select different Python command classes even when ECOVACS uses the same protocol command name.

Example:

```text
Device A capabilities
    └── "clean" → CommandA

Device B capabilities
    └── "clean" → CommandB
```

This is particularly relevant to ongoing GOAT mower `clean` work, where a mower-specific implementation may need to coexist with another device-family implementation using the same wire name.

## Command discovery

The development implementation recursively scans capability dataclasses for directly configured:

```text
Command instances
Command classes
commands inside lists/tuples
nested capability dataclasses
```

Arbitrary callable wrappers such as:

```python
lambda value: SetCommand(value, ...)
```

are not directly discoverable as command classes.

Those cases continue to depend on legacy/global fallback unless another directly discoverable same-name command is found.

## Duplicate names

The per-device mapping stores one command class per:

```text
NAME
```

and preserves the first directly discovered command when duplicates exist in the same capability tree.

This means the architecture primarily solves:

```text
same wire name across different devices/families
```

rather than full payload-aware multi-dispatch for several same-name commands inside one device.

## Legacy message lookup

PR #1772 changes legacy JSON message lookup to prefer:

```text
device.capabilities.get_command(name)
```

before falling back to the global:

```text
COMMANDS
```

registry.

## MQTT P2P lookup

The MQTT P2P path similarly prefers the subscribed device's configured command.

Routing identity is:

```text
q request  → receiver device
p response → sender device
```

If the device explicitly configures a same-name command that is not P2P-capable, the code does not silently substitute another global P2P implementation.

## GOAT integration caveat

PR #1778 configures two O1200 volume semantics under the same wire name:

```text
setVolume
```

with system volume wrapped in a lambda and `SetFallVolume` directly configured.

Because PR #1772 discovers direct command classes but not arbitrary lambdas, the combined branches require an explicit O1200 `setVolume` routing test before the interaction should be considered fully verified.

See:

[Device-specific command routing](command-routing.md)

---

# Event refresh mapping

`Capabilities` recursively builds a mapping from event types to their refresh commands.

Conceptually:

```text
BatteryEvent
    ↓
GetBattery

VolumeEvent
    ↓
GetVolume

RoomsEvent
    ↓
GetAreaSet
```

for the O1200 area-name development profile.

Therefore subscribing to:

```text
RoomsEvent
```

can trigger the capability refresh machinery without the consumer knowing the raw `getAreaSet` command.

PR #1774 specifically tests that:

```text
get_refresh_commands(RoomsEvent)
```

returns:

```text
[GetAreaSet()]
```

for O1200 development support.

---

# Capability-driven integration

This architecture allows consumers to ask:

```text
Does the device expose clean.areas?
```

instead of:

```python
if model == "O1200":
    send getAreaSet
```

Preferred pattern:

```text
capability exists?
       │
    ┌──┴──┐
    │     │
   no    yes
    │     │
    ▼     ▼
skip   subscribe/use
```

This is especially valuable as more GOAT models are investigated.

---

# O1200 area names and Home Assistant

The corresponding Home Assistant development branch subscribes to:

```text
RoomsEvent
```

when:

```text
capabilities.clean.areas
```

exists.

The mower entity then exposes a:

```text
rooms
```

attribute mapping slugified names to IDs.

The tested example is equivalent to:

```yaml
rooms:
  ostkanten: 4
  sentrum: 1
  vestkanten: 2
```

This confirms that the capability architecture is sufficient for a consumer integration without requiring Home Assistant to understand `getAreaSet` or compressed ECOVACS payloads.

---

# `CapabilityLifeSpan`

`CapabilityLifeSpan` represents maintenance/consumable information.

Known reviewed GOAT lifetime types include:

```text
BLADE
LENS_BRUSH
```

The O1200 additionally exposes:

```text
WEED_ROPE
TRIMMER_BRUSH
```

The hardware profile selects which lifetime types apply.

---

# `CapabilityStats`

Statistics are grouped under:

```text
CapabilityStats
```

with common event groups:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

Development work also adds:

```text
mowing_job_progress
```

as a model-semantic flag.

For the researched O1200 path, it tells consumers that:

```text
area
mowed_area
time
```

have mower-job-progress semantics.

---

# `CapabilitySettings`

`CapabilitySettings` collects device settings.

Reviewed upstream GOAT settings include:

```text
advanced_mode
border_switch
child_lock
cut_direction
moveup_warning
cross_map_border_warning
safe_protect
true_detect
volume
```

Development O1200 work adds additional mower-specific settings including:

```text
area_parameter
ai_recognition
animal_protection
humanoid_ai
narrow_adapt
rain_delay
fall_volume
```

The existence of a field in the dataclass does not establish support.

Support is determined by the hardware profile.

---

# Top-level `Capabilities`

The shared top-level structure includes concepts such as:

```text
device_type
availability
battery
charge
clean
custom
error
life_span
map
network
play_sound
settings
state
stats
```

For GOAT:

| Capability | Mower interpretation |
| --- | --- |
| `device_type` | identifies mower |
| `availability` | reachable/available |
| `battery` | battery status |
| `charge` | return to / use station |
| `clean` | mowing actions and area metadata |
| `custom` | low-level command access |
| `error` | mower errors |
| `life_span` | blade/accessory maintenance |
| `map` | map capability when explicitly supported |
| `network` | network information |
| `play_sound` | trigger sound |
| `settings` | mower/device settings |
| `state` | operational state |
| `stats` | mowing statistics |

The new area-name work belongs under:

```text
clean.areas
```

rather than:

```text
map
```

---

# Hardware profiles

The hardware profile is the authoritative client-side place for determining which capability is enabled for a model.

A command existing elsewhere in the source tree does not mean every device can use it.

For example, after PR #1774 the researched O1200 development profile conceptually has:

```python
Capabilities(
    device_type=DeviceType.MOWER,
    clean=CapabilityClean(
        action=CapabilityCleanAction(
            command=CleanV2,
        ),
        areas=CapabilityEvent(
            RoomsEvent,
            [GetAreaSet()],
        ),
    ),
    map=None,
    ...
)
```

This describes three separate facts:

```text
general mowing action: yes
area-name metadata: yes
full map capability: no
```

---

# Mowing actions

The shared action enum contains:

```text
START
PAUSE
RESUME
STOP
```

with JSON values:

```text
start
pause
resume
stop
```

GOAT profiles use:

```text
CleanV2
```

for general mowing control.

---

# Start versus resume handling

The shared command implementation contains state-aware handling.

Conceptually:

```text
START while PAUSED
    → RESUME
```

and:

```text
RESUME while not PAUSED
    → START
```

This lets higher-level integrations use a simpler start/resume interface.

---

# Operational state

Common state values include:

```text
IDLE
CLEANING
RETURNING
DOCKED
ERROR
PAUSED
```

For GOAT user interfaces:

```text
CLEANING
```

should normally be displayed as:

```text
MOWING
```

---

# `GetCleanInfoV2`

Reviewed GOAT profiles use:

```text
GetCleanInfoV2
```

wire:

```text
getCleanInfo_V2
```

to retrieve current operational state.

Possible normalised states include:

```text
CLEANING
PAUSED
RETURNING
IDLE
ERROR
```

---

# Area operations versus area metadata versus area settings

GOAT now has three clearly distinct capability concepts.

## 1. Area mowing action

```text
CapabilityCleanAction.area
```

Example:

```text
CleanAreaV2
```

Purpose:

```text
start mowing selected target(s)
```

## 2. Area metadata

```text
CapabilityClean.areas
```

Example:

```text
CapabilityEvent(RoomsEvent, [GetAreaSet()])
```

Purpose:

```text
retrieve area IDs and display names
```

## 3. Area parameters

```text
settings.area_parameter
```

Example:

```text
AreaParameterEvent
GetAreaParameter
SetAreaParameter
```

Purpose:

```text
read/write zone-specific mowing settings
```

Conceptually:

```text
Area/zone support
      │
      ├── start it
      ├── name/identify it
      └── configure it
```

These should remain separate capabilities even when they share the same logical lawn zone.

---

# Current O1200 zone-capability picture

Development evidence currently gives:

```text
Area identity/name
    ✓ getAreaSet / RoomsEvent

Area-specific settings
    ✓ areaID / AreaParameterEvent

Selected-zone start
    ? client capability still unresolved

Full map
    ? separate work; not implied by area names
```

This is substantially more precise than treating "zone support" as one binary feature.

---

# Capability support versus protocol support

Maintain three separate questions:

```text
Does the physical/protocol feature exist?
            │
            ▼
Does deebot_client implement it?
            │
            ▼
Does this hardware profile expose it?
```

A fourth consumer layer may then ask:

```text
Does Home Assistant expose it?
```

These stages can have different statuses.

---

# Capability documentation convention

For newly documented mower features, record:

| Field | Description |
| --- | --- |
| Feature | Human-readable mower feature |
| Capability | `deebot_client` capability path |
| Event | Normalised event |
| GET command | Refresh command |
| SET/execute command | Writable/action command |
| Protocol name | Wire command/message |
| Models | Evidence-backed hardware profiles |
| Branch/status | Upstream or development |
| Tests | Automated coverage |
| Device evidence | App/protocol/physical validation |
| Unknowns | Remaining semantic gaps |

Example for area names:

```text
Feature: O1200 area names
Capability: clean.areas
Event: RoomsEvent
GET command: GetAreaSet
Protocol: getAreaSet
Model: 2i0fns
Status: PR #1774 / development
Evidence: protocol + live device + tests
Map capability: not implied
```

---

# Why this architecture matters

A capability-based design prevents integrations from becoming a collection of model-name exceptions.

Preferred:

```text
if clean.areas exists:
    use RoomsEvent
```

rather than:

```text
if model is O1200:
    parse compressed subsets
```

Protocol reverse-engineering stays in `deebot_client`.

Consumers receive stable normalised semantics.

---

# Development flow

A typical GOAT feature should move through:

```text
Observe app/device
      │
      ▼
Capture protocol
      │
      ▼
Identify payload
      │
      ▼
Implement command/message
      │
      ▼
Normalise event
      │
      ▼
Expose capability
      │
      ▼
Add tests
      │
      ▼
Verify live device
      │
      ▼
Expose in integration
```

PR #1774 is a good example:

```text
captured getAreaSet
      │
      ▼
decoded compressed subsets
      │
      ▼
reused Room / RoomsEvent
      │
      ▼
added clean.areas
      │
      ▼
enabled for 2i0fns
      │
      ▼
tested
      │
      ▼
live end-to-end verified
      │
      ▼
HA development consumes RoomsEvent
```

---

# Related documentation

- [Overview](overview.md)
- [Device-specific command routing](command-routing.md)
- [Supported models](supported-models.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [O1200 area names](area-names.md)
- [O1200 area parameters](area-parameters.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
