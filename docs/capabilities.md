# GOAT capability architecture

This page explains how ECOVACS GOAT mower functionality is represented by the capability architecture in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py).

Last reviewed against the upstream `dev` branch: **2026-08-23**.

## Overview

`deebot_client` uses a capability model to describe what each supported device can do.

For GOAT devices, a hardware profile creates a `Capabilities` object and identifies the device as:

```python
device_type=DeviceType.MOWER
```

The same general capability framework is also used for DEEBOT vacuum robots, so some class and command names still use terms such as `clean`, even when the physical device is a robotic lawn mower.

For mower documentation, these should normally be interpreted as mowing operations.

At a high level, the architecture can be viewed as:

```text
Hardware profile
      │
      ▼
 Capabilities
      │
      ├── commands
      │     │
      │     ▼
      │  ECOVACS API / device
      │
      └── events
            │
            ▼
      current client state
```

A hardware profile therefore describes which generic client capabilities are connected to the commands and events supported for that device.

## Commands, messages and events

Three concepts are particularly important when reading `deebot_client`.

### Command

A command requests something from or sends an action to the mower.

Examples include:

```text
GetBattery
Charge
CleanV2
GetCleanInfoV2
GetStats
SetBorderSwitch
```

Commands may be used to:

* request the current value of a setting
* request mower status
* start or control an operation
* change a setting

### Message

A message represents data returned or pushed through the ECOVACS protocol.

Message handlers interpret the protocol payload and convert relevant information into client events.

### Event

An event is the normalised state exposed internally by `deebot_client`.

Examples include:

```text
BatteryEvent
StateEvent
StatsEvent
BorderSwitchEvent
LifeSpanEvent
```

Consumers of the library should generally depend on these normalised events rather than directly interpreting raw ECOVACS protocol payloads.

A simplified flow for a readable setting is therefore:

```text
Get command
    │
    ▼
ECOVACS response
    │
    ▼
Message handler
    │
    ▼
Event
```

For a writable setting:

```text
Set command
    │
    ▼
ECOVACS/device
    │
    ▼
response or later status update
    │
    ▼
Event
```

## Core capability types

The capability module defines several reusable capability classes.

These classes describe different interaction patterns.

## `CapabilityEvent`

`CapabilityEvent` represents a value that can be obtained and represented by an event.

Conceptually:

```python
CapabilityEvent(
    event=SomeEvent,
    get=[SomeGetCommand()],
)
```

It contains:

* the event type
* one or more commands that can refresh that event

A mower battery capability is an example:

```python
battery=CapabilityEvent(
    BatteryEvent,
    [GetBattery()],
)
```

This means that `BatteryEvent` represents battery state and `GetBattery()` can be used to refresh it.

## `CapabilitySet`

`CapabilitySet` extends `CapabilityEvent` with a command for changing the value.

Conceptually:

```python
CapabilitySet(
    event=SomeEvent,
    get=[GetSomething()],
    set=SetSomething,
)
```

This creates the common pattern:

```text
GET current value
SET new value
EVENT representing current value
```

GOAT cutting direction currently uses this type.

## `CapabilitySetEnable`

`CapabilitySetEnable` is a specialised `CapabilitySet` for boolean settings.

Its writable value is effectively:

```text
True / False
```

Several existing GOAT settings use this pattern, including:

* advanced mode
* border switch
* child lock
* move-up warning
* cross-map border warning
* safe protect
* TrueDetect

This pattern is particularly useful for integrations because it maps naturally to an on/off control.

## `CapabilityExecute`

`CapabilityExecute` represents an action rather than a persistent state.

Conceptually:

```python
CapabilityExecute(SomeCommand)
```

Examples include actions such as:

* return to / charge at station
* play sound

There does not need to be a directly associated setting value.

## `CapabilityTypes`

Some capabilities define a known set of supported values.

`CapabilityTypes` provides the list of types or enum values supported by a capability.

This allows integrations to know which options should be presented rather than accepting arbitrary values.

## `CapabilitySetTypes`

`CapabilitySetTypes` combines:

* readable event state
* a set command
* an explicitly supported set of values

This is useful for settings that behave like selectable modes.

## `CapabilityNumber`

`CapabilityNumber` represents a numeric setting and adds:

```text
min
max
```

to the underlying readable/writable capability.

This allows integrations to expose an appropriate numeric control with known limits.

The upstream GOAT profiles reviewed here do not currently use this type for cutting height, but the capability abstraction is suitable for settings represented by bounded numeric values.

## `CapabilityCleanAction`

Mowing control is represented through the shared `CapabilityCleanAction` abstraction.

It contains:

```python
command
area
```

where:

* `command` performs the main start/pause/resume/stop action
* `area` optionally starts an area-specific operation

The area command is optional:

```python
area: ... | None = None
```

This is why one mower profile can support the general mowing action without necessarily exposing area mowing through the same capability.

## `CapabilityClean`

`CapabilityClean` contains the common operation capability.

The shared abstraction can additionally contain features used by other device types, including:

```text
continuous
count
log
preference
work_mode
```

The currently reviewed GOAT hardware profiles primarily use the `action` part of this structure.

For mower documentation, the `clean` capability should generally be understood as the **mowing-operation capability**.

## `CapabilityLifeSpan`

`CapabilityLifeSpan` represents consumable or maintenance lifetime information.

It combines:

* `LifeSpanEvent`
* commands for retrieving lifetime data
* a list of supported lifetime types
* a reset command

For GOAT mowers, known upstream lifetime types include:

```text
BLADE
LENS_BRUSH
```

and on the O1200 LiDAR profile additionally:

```text
WEED_ROPE
TRIMMER_BRUSH
```

The hardware profile determines which of these lifetime types are exposed for each mower.

## `CapabilityStats`

Statistics are grouped into:

```python
clean
report
total
```

which correspond to:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

The generic class uses the word `clean`, but on a mower the values should be interpreted in the context of mowing activity.

Detailed mower-specific fields are documented separately.

## `CapabilitySettings`

`CapabilitySettings` collects device settings into a common structure.

The generic class contains settings used across multiple ECOVACS product types, so not every field is relevant to mowers.

Examples in the common structure include vacuum-oriented settings such as:

```text
carpet_auto_fan_boost
mop_auto_wash_frequency
sweep_mode
```

and settings currently used by GOAT profiles such as:

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

Each hardware profile selects only the capabilities that are appropriate for that device.

This distinction is important:

> The existence of a field in `CapabilitySettings` does not mean that every device supports it.

Support is determined by the device's hardware profile.

## Top-level `Capabilities`

The main `Capabilities` object contains the features exposed for a device.

The current shared structure includes:

```text
device_type
availability
battery
charge
clean
custom
error
fan_speed
life_span
map
network
play_sound
settings
state
station
stats
water
```

Some fields are mandatory in the common model, while others are optional.

For a GOAT mower, these generic terms map approximately as follows:

| `deebot_client` capability | GOAT interpretation               |
| -------------------------- | --------------------------------- |
| `device_type`              | Identifies the device as a mower  |
| `availability`             | Whether the device can be reached |
| `battery`                  | Battery charge level/state        |
| `charge`                   | Return to / use charging station  |
| `clean`                    | Mowing control                    |
| `custom`                   | Low-level custom command access   |
| `error`                    | Mower errors                      |
| `life_span`                | Blade/accessory maintenance life  |
| `network`                  | Device network information        |
| `play_sound`               | Trigger mower sound               |
| `settings`                 | Device and mower settings         |
| `state`                    | Current operational state         |
| `stats`                    | Mowing/statistical information    |

Capabilities such as `water` and vacuum station functions are not relevant to the reviewed mower profiles.

## Hardware profiles

A hardware profile connects the generic capability system to a specific mower model.

For example, a typical GOAT profile contains structures conceptually similar to:

```python
Capabilities(
    device_type=DeviceType.MOWER,
    battery=CapabilityEvent(
        BatteryEvent,
        [GetBattery()],
    ),
    charge=CapabilityExecute(Charge),
    clean=CapabilityClean(
        action=CapabilityCleanAction(
            command=CleanV2,
            area=CleanAreaV2,
        ),
    ),
    ...
)
```

This is the primary place to determine whether a capability is currently enabled for a particular model.

The presence of a command implementation elsewhere in the source tree does not automatically mean that all devices expose that command.

## Event refresh mapping

The capability architecture automatically builds a mapping between events and their GET commands.

During `Capabilities` initialisation, `_get_events()` recursively examines capability dataclasses.

When it finds a `CapabilityEvent`, it records:

```text
Event type → GET command(s)
```

The resulting mapping is stored internally as `_events`.

The method:

```python
get_refresh_commands(event)
```

can then return the commands required to refresh a particular event.

Conceptually:

```text
BatteryEvent
    ↓
GetBattery()

VolumeEvent
    ↓
GetVolume()

TrueDetectEvent
    ↓
GetTrueDetect()
```

This is useful for integrations because they can request updated state based on an event type without hard-coding all of the underlying protocol commands themselves.

## Mowing actions

The common action enum currently contains four actions:

```text
START
PAUSE
RESUME
STOP
```

Their JSON values are:

```text
start
pause
resume
stop
```

For GOAT mowers using `CleanV2`, the protocol command name is:

```text
clean_V2
```

For a normal start operation, the command includes an automatic mode.

The common `CleanV2` implementation also prepares appropriate content for pause and stop operations.

## Start versus resume handling

The shared command implementation includes state-aware handling for start and resume.

If the client requests:

```text
RESUME
```

while the device is not currently paused, the command can be converted to:

```text
START
```

Likewise, if:

```text
START
```

is requested while the current state is paused, it can be converted to:

```text
RESUME
```

This means that the higher-level operation is partly protected against mismatches between the requested action and the latest known `StateEvent`.

This behaviour exists in the shared command layer and is not unique to mowers.

## Operational state

The shared `State` model currently contains:

```text
IDLE
CLEANING
RETURNING
DOCKED
ERROR
PAUSED
```

For mower use, `CLEANING` represents an active mowing operation.

The terminology again reflects the shared history of the library rather than mower-specific user-facing names.

## `GetCleanInfoV2`

The reviewed GOAT profiles use:

```text
GetCleanInfoV2
```

as part of current-state retrieval.

Its protocol command name is:

```text
getCleanInfo_V2
```

The shared parser can map returned information into states such as:

```text
CLEANING
PAUSED
RETURNING
IDLE
ERROR
```

For example, a reported motion state of:

```text
working
```

can become:

```text
State.CLEANING
```

and:

```text
pause
```

can become:

```text
State.PAUSED
```

The mower state is therefore normalised into the same common state model used by the rest of the library.

## Area operations

`CleanAreaV2` extends `CleanV2` with area-specific content.

The common implementation accepts:

```text
mode
area
cleanings
```

and produces protocol content containing a mowing/cleaning type and value.

The generic `CleanMode` enum currently contains:

```text
AUTO
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

Not all names necessarily correspond directly to terminology used by the ECOVACS GOAT app.

As with other shared abstractions, mower-specific protocol behaviour should be documented from observed device behaviour rather than inferred only from generic enum names.

## Capability support versus protocol support

A distinction should always be maintained between three layers:

```text
Protocol knows about feature
          │
          ▼
deebot_client implements command/event
          │
          ▼
hardware profile exposes capability
```

These are not equivalent.

For example, it is possible for:

1. ECOVACS protocol traffic to reveal a mower setting,
2. a command and event implementation to be added to `deebot_client`,
3. but the setting not yet to be enabled in a particular hardware profile.

Likewise, a feature may exist in a development branch without yet being available in upstream `dev`.

The documentation in this repository therefore records both implementation state and testing evidence.

## Capability documentation convention

For newly documented mower features, use the following fields where practical:

| Field                   | Description                                                    |
| ----------------------- | -------------------------------------------------------------- |
| **Feature**             | Human-readable mower feature                                   |
| **Capability**          | `deebot_client` capability field                               |
| **Event**               | Normalised event generated by the client                       |
| **Get command**         | Command used to retrieve state                                 |
| **Set/execute command** | Command used to change or perform the feature                  |
| **Protocol name**       | ECOVACS command/message name where known                       |
| **Models**              | Hardware profiles exposing the capability                      |
| **Evidence**            | Upstream, fork, device-tested, protocol-observed or unverified |

Example:

```text
Feature: Border switch
Capability: settings.border_switch
Event: BorderSwitchEvent
Get command: GetBorderSwitch
Set command: SetBorderSwitch
Evidence: Upstream implemented
```

This convention will make it easier to compare app functionality, protocol observations, Python implementation and Home Assistant exposure.

## Why this architecture matters for GOAT development

The capability system provides a useful separation between:

* raw ECOVACS protocol behaviour
* Python command implementations
* parsed state events
* device-specific support
* integration-facing functionality

When adding a newly discovered GOAT feature, the normal development path is therefore approximately:

```text
Observe protocol
      │
      ▼
Understand payload
      │
      ▼
Implement message/event
      │
      ▼
Implement Get/Set command
      │
      ▼
Add capability abstraction if needed
      │
      ▼
Enable capability in hardware profile
      │
      ▼
Add tests
      │
      ▼
Expose through consuming integration
```

Not every feature requires a new top-level capability type. Existing abstractions such as `CapabilitySetEnable`, `CapabilitySet`, `CapabilityNumber` or `CapabilityExecute` should be reused when they accurately represent the mower feature.

## Related documentation

See also:

* [Supported models](supported-models.md)
* Mowing control *(planned)*
* Progress and statistics *(planned)*
* Mower settings *(planned)*
* Rain and protection *(planned)*
* Obstacle and AI features *(planned)*
* Protocol reference *(planned)*
* Home Assistant integration *(planned)*
