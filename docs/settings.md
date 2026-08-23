# GOAT mower settings

This page provides an overview of known ECOVACS GOAT mower settings in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py) and mower-specific settings implemented during GOAT protocol research.

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* development branch `feature/ecovacs-mower-settings`

Date: **2026-08-23**

## Scope

This page focuses on configurable mower settings.

It distinguishes between:

* settings already implemented upstream
* mower-specific settings implemented in the development fork
* runtime protection states that are reported by the mower but are not themselves settings
* mower features that remain unmapped

Detailed rain/protection and AI/obstacle behaviour are documented on separate pages.

---

# Evidence levels

The following status terms are used throughout this page.

| Status                   | Meaning                                                          |
| ------------------------ | ---------------------------------------------------------------- |
| **Upstream implemented** | Present in current `DeebotUniverse/client.py` `dev`              |
| **Fork implemented**     | Implemented in the development fork but not in reviewed upstream |
| **Protocol observed**    | Seen in actual GOAT communication                                |
| **Device tested**        | Behaviour verified against a physical mower                      |
| **Unverified**           | Interpretation still needs additional evidence                   |

Implementation in Python tests is not the same as physical-device testing.

---

# Settings architecture

Device settings are grouped under:

```text
Capabilities.settings
```

using:

```python
CapabilitySettings(...)
```

A setting normally connects:

```text
Get command
    │
    ▼
Event
    │
    ▲
    │
Set command
```

For example:

```text
GetBorderSwitch
       │
       ▼
BorderSwitchEvent
       ▲
       │
SetBorderSwitch
```

This allows integrations to retrieve the current value, receive updates and change the setting through a common capability model.

---

# Current settings overview

## Upstream settings

The reviewed GOAT hardware profiles currently expose the following common upstream settings:

| Feature                  | Capability                 | Read | Write | Status               |
| ------------------------ | -------------------------- | :--: | :---: | -------------------- |
| Advanced mode            | `advanced_mode`            |   ✓  |   ✓   | Upstream implemented |
| Border switch            | `border_switch`            |   ✓  |   ✓   | Upstream implemented |
| Cutting direction        | `cut_direction`            |   ✓  |   ✓   | Upstream implemented |
| Child lock               | `child_lock`               |   ✓  |   ✓   | Upstream implemented |
| Move-up warning          | `moveup_warning`           |   ✓  |   ✓   | Upstream implemented |
| Cross-map border warning | `cross_map_border_warning` |   ✓  |   ✓   | Upstream implemented |
| Safe protect             | `safe_protect`             |   ✓  |   ✓   | Upstream implemented |
| TrueDetect               | `true_detect`              |   ✓  |   ✓   | Upstream implemented |
| Volume                   | `volume`                   |   ✓  |   ✓   | Upstream implemented |

These capabilities are present in the reviewed upstream mower profiles.

Their exact user-facing wording can differ from the ECOVACS application.

---

# Development mower settings

The development branch adds several GOAT-specific capabilities, currently connected to the O1200 LiDAR profile used for protocol investigation.

| Feature                     | Capability          | Protocol                                | Status           |
| --------------------------- | ------------------- | --------------------------------------- | ---------------- |
| AI recognition              | `ai_recognition`    | `getRecognization` / `setRecognization` | Fork implemented |
| Animal protection           | `animal_protection` | `getAnimProtect` / `setAnimProtect`     | Fork implemented |
| Smart mowing with avoidance | `humanoid_ai`       | `getHumanoidAI` / `setHumanoidAI`       | Fork implemented |
| Narrow passage adaptation   | `narrow_adapt`      | `getNarrowAdapt` / `setNarrowAdapt`     | Fork implemented |
| Rain sensor/delay           | `rain_delay`        | `setRainDelay` / `onRainDelay`          | Fork implemented |
| Lifted-alarm volume         | `fall_volume`       | `getVolume` / `setVolume`               | Fork implemented |

The same branch also adds:

```text
ProtectStateEvent
```

but this is a runtime mower status rather than a configurable setting.

---

# Advanced mode

Capability:

```text
settings.advanced_mode
```

Event:

```text
AdvancedModeEvent
```

Commands:

```text
GetAdvancedMode
SetAdvancedMode
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

The protocol name does not by itself fully explain the mower-specific user-facing meaning of "advanced mode".

Its behaviour should therefore be described from ECOVACS app correlation or physical testing rather than inferred only from the command name.

---

# Border switch

Capability:

```text
settings.border_switch
```

Event:

```text
BorderSwitchEvent
```

Commands:

```text
GetBorderSwitch
SetBorderSwitch
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

This is one of the settings likely associated with mower border/edge behaviour.

The exact relationship between the protocol term `borderSwitch` and the wording presented by different ECOVACS GOAT app versions should be documented from device observation.

---

# Cutting direction

Capability:

```text
settings.cut_direction
```

Event:

```text
CutDirectionEvent
```

Commands:

```text
GetCutDirection
SetCutDirection
```

The event contains:

```python
angle: int
```

Unlike the simple on/off settings, cutting direction is represented as a numeric angle.

Status:

**Upstream implemented**

This is distinct from cutting height.

No cutting-height capability has been identified in the reviewed upstream implementation.

---

# Child lock

Capability:

```text
settings.child_lock
```

Commands:

```text
GetChildLock
SetChildLock
```

Event:

```text
ChildLockEvent
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

---

# Move-up warning

Capability:

```text
settings.moveup_warning
```

Commands:

```text
GetMoveUpWarning
SetMoveUpWarning
```

Event:

```text
MoveUpWarningEvent
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

The protocol name is retained here.

Mower-specific UI wording should be based on observed ECOVACS behaviour.

---

# Cross-map border warning

Capability:

```text
settings.cross_map_border_warning
```

Commands:

```text
GetCrossMapBorderWarning
SetCrossMapBorderWarning
```

Event:

```text
CrossMapBorderWarningEvent
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

---

# Safe protect

Capability:

```text
settings.safe_protect
```

Commands:

```text
GetSafeProtect
SetSafeProtect
```

Event:

```text
SafeProtectEvent
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

The protocol name should not automatically be interpreted as a specific physical safety feature without additional device correlation.

---

# TrueDetect

Capability:

```text
settings.true_detect
```

Commands:

```text
GetTrueDetect
SetTrueDetect
```

Event:

```text
TrueDetectEvent
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

`TrueDetect` is an ECOVACS protocol/product term.

Its exact mower-specific relationship to obstacle detection and avoidance should be documented separately from AI-recognition settings.

---

# System volume

Capability:

```text
settings.volume
```

Commands:

```text
GetVolume
SetVolume
```

Event:

```text
VolumeEvent
```

Upstream already supports general volume.

The mower development branch refines O1200 volume handling by explicitly using:

```text
type = "sys"
total = 10
```

when changing the normal system-volume channel.

Conceptual request:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 5
}
```

The requested volume is supplied by the caller.

Status:

**Upstream implemented / mower handling refined in fork**

---

# Lifted-alarm volume

The mower development branch identifies a second volume channel associated with the alarm used when the mower is lifted.

Capability:

```text
settings.fall_volume
```

Event:

```text
FallVolumeEvent
```

The same ECOVACS protocol commands are used:

```text
getVolume
setVolume
```

but the channel is:

```text
fall
```

A write uses a structure equivalent to:

```json
{
  "type": "fall",
  "total": 10,
  "volume": 5
}
```

The development parser can obtain the value in two observed representations:

```text
type = "fall"
```

or as a:

```text
fallVolume
```

field included in a general volume response.

Status:

**Fork implemented**

---

# AI recognition

The development branch introduces:

```text
settings.ai_recognition
```

Event:

```text
AiRecognitionEvent
```

Commands:

```text
GetRecognization
SetRecognization
```

Protocol names:

```text
getRecognization
setRecognization
```

Note that `Recognization` is the spelling used by the ECOVACS protocol and is therefore preserved in the command class names.

The setting is represented as:

```text
boolean
```

with the protocol state stored in:

```text
state
```

Status:

**Fork implemented**

This feature is documented in more detail in the obstacle/AI documentation because its exact relationship with obstacle recognition requires app/device correlation.

---

# Smart mowing with avoidance

The development branch introduces:

```text
settings.humanoid_ai
```

Event:

```text
HumanoidAiEvent
```

Commands:

```text
GetHumanoidAi
SetHumanoidAi
```

Protocol names:

```text
getHumanoidAI
setHumanoidAI
```

The implementation describes this feature as:

```text
Smart mowing with avoidance
```

Type:

```text
boolean
```

Status:

**Fork implemented**

The unusual protocol name `HumanoidAI` should not be interpreted literally without further ECOVACS-specific context.

The user-facing mower feature should be documented according to observed app behaviour.

---

# Narrow passage adaptation

Capability:

```text
settings.narrow_adapt
```

Event:

```text
NarrowAdaptEvent
```

Commands:

```text
GetNarrowAdapt
SetNarrowAdapt
```

Protocol names:

```text
getNarrowAdapt
setNarrowAdapt
```

The setting uses the protocol field:

```text
state
```

and is represented in the client as a boolean enable/disable capability.

Status:

**Fork implemented**

The implementation describes it as:

```text
Narrow passage adaptation
```

This is likely relevant to navigation through constrained lawn passages, but exact physical behaviour should be documented from mower testing.

---

# Animal protection

Animal protection is more complex than a normal boolean setting.

Capability:

```text
settings.animal_protection
```

Event:

```text
AnimalProtectionEvent
```

Commands:

```text
GetAnimalProtection
SetAnimalProtection
```

Protocol names:

```text
getAnimProtect
setAnimProtect
```

The complete configuration contains:

```text
enabled
start
end
```

Conceptually:

```text
Animal protection
├── enabled
├── start time
└── end time
```

A protocol write is equivalent to:

```json
{
  "enable": 1,
  "start": "20:00",
  "end": "08:00"
}
```

The actual times are supplied by the caller.

## Time format

The implementation normalises device times to:

```text
HH:MM
```

For example:

```text
8:00
```

becomes:

```text
08:00
```

and:

```text
7:05
```

becomes:

```text
07:05
```

This makes the exposed event format consistent even if the mower does not zero-pad the value.

Status:

**Fork implemented**

The feature is particularly important because it demonstrates that some mower protection options are schedules rather than simple on/off switches.

---

# Rain sensor and post-rain delay

Capability:

```text
settings.rain_delay
```

Event:

```text
RainDelayEvent
```

Set command:

```text
SetRainDelay
```

Protocol write:

```text
setRainDelay
```

Reported state:

```text
onRainDelay
```

The event contains:

```python
enabled: bool
delay: int
```

Conceptually:

```text
Rain configuration
├── sensor/protection enabled
└── post-rain delay in minutes
```

The write payload is equivalent to:

```json
{
  "enable": 1,
  "delay": 120
}
```

## Supported delay values

The development implementation accepts:

```text
0
30
60
90
120
150
180
210
240
270
300
```

minutes.

In other words:

```text
0–300 minutes
in 30-minute increments
```

Unsupported values are rejected by the client.

For example:

```text
45 minutes
```

is not a valid value in the current implementation.

## State reporting

Unlike most normal settings in the capability model, the O1200 development capability currently has no explicit GET command:

```python
rain_delay=CapabilitySet(
    RainDelayEvent,
    [],
    SetRainDelay,
)
```

Instead, resulting state is reported through:

```text
onRainDelay
```

which generates:

```text
RainDelayEvent
```

Status:

**Fork implemented / protocol observed**

Rain behaviour is documented in greater detail in `rain-and-protection.md`.

---

# Configuration versus active protection

The rain configuration and current rain-protection state are different concepts.

Configuration:

```text
RainDelayEvent
├── enabled
└── delay
```

Runtime protection:

```text
ProtectStateEvent
├── is_rain_protect
└── is_rain_delay
```

This distinction is important.

For example:

```text
Rain protection enabled
```

does not mean:

```text
Mower is currently stopped because it is raining
```

The first is configuration.

The second is runtime state.

---

# Runtime `ProtectStateEvent`

The development branch introduces a top-level:

```text
protect_state
```

capability using:

```text
ProtectStateEvent
```

This is **not writable**.

It represents boolean protection states pushed by the mower.

The event contains:

```text
is_anim_protect
is_rain_protect
is_rain_delay
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

These values originate from:

```text
onProtectState
```

and are intentionally preserved without over-interpreting unknown transitions.

## Known rain observation

During actual-rain protocol observation, the implementation notes the following observed state:

```text
isRainProtect = 1
isRainDelay = 0
```

This provides direct evidence that:

```text
isRainProtect
```

can represent an active rain-protection condition.

The meaning of every possible:

```text
isRainDelay
```

transition should not be inferred until separately observed.

Status:

**Fork implemented / protocol observed**

---

# Animal configuration versus animal protection state

The same configuration/runtime distinction applies to animal protection.

Configuration:

```text
AnimalProtectionEvent
├── enabled
├── start
└── end
```

Runtime state:

```text
ProtectStateEvent.is_anim_protect
```

The two should not be merged into one boolean.

Conceptually:

```text
Animal protection configured
          │
          ▼
enabled + schedule
```

versus:

```text
Animal protection currently active
          │
          ▼
is_anim_protect
```

This distinction will matter when exposing the feature in Home Assistant.

---

# O1200 development profile

The development branch currently connects the newly mapped mower settings specifically to:

```text
GOAT O1200 LiDAR
hardware ID: 2i0fns
```

The additional capability wiring includes:

```text
ai_recognition
animal_protection
humanoid_ai
narrow_adapt
rain_delay
fall_volume
protect_state
```

This provides strong implementation evidence for the researched O1200.

It does **not** automatically prove that the same protocol commands work unchanged on:

* GOAT G1
* GOAT A1600 RTK
* GOAT A3000 LiDAR Pro
* GOAT O500 Panorama

Support on those models should be added only when supported by protocol evidence or physical testing.

---

# Capability summary

| Feature                   | Event                        | Get/source                 | Set                        | Type           | Current status |
| ------------------------- | ---------------------------- | -------------------------- | -------------------------- | -------------- | -------------- |
| Advanced mode             | `AdvancedModeEvent`          | `GetAdvancedMode`          | `SetAdvancedMode`          | bool           | Upstream       |
| Border switch             | `BorderSwitchEvent`          | `GetBorderSwitch`          | `SetBorderSwitch`          | bool           | Upstream       |
| Cutting direction         | `CutDirectionEvent`          | `GetCutDirection`          | `SetCutDirection`          | int/angle      | Upstream       |
| Child lock                | `ChildLockEvent`             | `GetChildLock`             | `SetChildLock`             | bool           | Upstream       |
| Move-up warning           | `MoveUpWarningEvent`         | `GetMoveUpWarning`         | `SetMoveUpWarning`         | bool           | Upstream       |
| Cross-map border warning  | `CrossMapBorderWarningEvent` | `GetCrossMapBorderWarning` | `SetCrossMapBorderWarning` | bool           | Upstream       |
| Safe protect              | `SafeProtectEvent`           | `GetSafeProtect`           | `SetSafeProtect`           | bool           | Upstream       |
| TrueDetect                | `TrueDetectEvent`            | `GetTrueDetect`            | `SetTrueDetect`            | bool           | Upstream       |
| System volume             | `VolumeEvent`                | `GetVolume`                | `SetVolume`                | int            | Upstream       |
| AI recognition            | `AiRecognitionEvent`         | `GetRecognization`         | `SetRecognization`         | bool           | Fork           |
| Animal protection         | `AnimalProtectionEvent`      | `GetAnimalProtection`      | `SetAnimalProtection`      | bool + times   | Fork           |
| Smart mowing/avoidance    | `HumanoidAiEvent`            | `GetHumanoidAi`            | `SetHumanoidAi`            | bool           | Fork           |
| Narrow passage adaptation | `NarrowAdaptEvent`           | `GetNarrowAdapt`           | `SetNarrowAdapt`           | bool           | Fork           |
| Rain configuration        | `RainDelayEvent`             | `onRainDelay`              | `SetRainDelay`             | bool + minutes | Fork           |
| Lifted-alarm volume       | `FallVolumeEvent`            | `GetVolume`                | `SetFallVolume`            | int            | Fork           |
| Runtime protection        | `ProtectStateEvent`          | `onProtectState`           | —                          | state flags    | Fork           |

---

# Settings not yet mapped

Several mower features remain outside the reviewed upstream and development capability set.

These should remain explicit research targets rather than being inferred from unrelated generic capabilities.

## Cutting height

No dedicated GOAT cutting-height capability has been identified in the reviewed source.

Status:

**Not yet mapped**

A future implementation would require identifying:

* protocol command
* response/message
* valid height range
* physical unit
* whether height changes are motorised on the model
* model-specific supported values

---

# Mowing efficiency / mowing mode

No confirmed GOAT-specific capability for the app's mowing efficiency/mode control has been identified in the reviewed source.

The shared client contains generic concepts such as:

```text
efficiency_mode
```

for other ECOVACS devices.

The existence of that generic field does not prove that GOAT mower efficiency settings use the same protocol.

Status:

**Not yet mapped for GOAT**

---

# Mowing speed

No dedicated GOAT mowing-speed capability has been identified in the reviewed implementation.

Status:

**Not yet mapped**

If the ECOVACS app exposes multiple speed levels, their protocol representation should be captured before adding a client abstraction.

---

# Additional obstacle behaviour

Several related features now have protocol mappings:

```text
TrueDetect
AI recognition
Humanoid AI
Narrow adapt
```

but their exact relationship with the different obstacle/AI options presented by the ECOVACS app still needs systematic mapping.

These are therefore documented separately in:

```text
obstacle-and-ai.md
```

---

# Recommended documentation rule

When a new mower setting is discovered, record at least:

| Field         | Description                         |
| ------------- | ----------------------------------- |
| Feature       | User-facing meaning                 |
| App wording   | Label used by ECOVACS app, if known |
| Protocol name | ECOVACS command/message             |
| Capability    | `deebot_client` capability          |
| Event         | Normalised state event              |
| Get command   | How state is retrieved              |
| Set command   | How it is changed                   |
| Payload       | Relevant fields                     |
| Valid values  | Known allowed values                |
| Model         | Mower where observed                |
| Firmware      | Firmware where verified             |
| Evidence      | Upstream/fork/protocol/device       |
| Notes         | Unknowns or model differences       |

This helps prevent a protocol name from being mistaken for a confirmed user-facing interpretation.

---

# Model portability

A mower setting should not automatically be enabled for every GOAT hardware profile simply because:

* the command exists
* another GOAT model supports it
* the app displays a similar option
* the devices share a capability framework

A safer development flow is:

```text
Observe feature on model
        │
        ▼
Capture protocol
        │
        ▼
Implement parser/command
        │
        ▼
Test payloads
        │
        ▼
Test physical mower
        │
        ▼
Enable hardware capability
```

This is especially important for settings that may depend on:

* navigation technology
* optional hardware
* firmware generation
* region
* mower model
* accessory configuration

---

# Home Assistant considerations

The different setting types naturally map to different integration controls.

## Boolean settings

Examples:

```text
advanced_mode
border_switch
child_lock
true_detect
ai_recognition
humanoid_ai
narrow_adapt
```

could map to switch-style entities.

## Numeric settings

Examples:

```text
volume
fall_volume
cut_direction
```

may map to numbers or selectors depending on valid ranges.

## Structured settings

Animal protection contains:

```text
enabled
start
end
```

and therefore cannot be represented accurately by a single switch alone.

## Rain configuration

Rain configuration combines:

```text
enabled
delay
```

and likewise requires more than one control if the full feature is exposed.

## Runtime states

Values in:

```text
ProtectStateEvent
```

should normally be sensors/binary sensors rather than writable switches.

---

# Evidence summary

## Upstream implemented

The reviewed upstream mower profiles expose:

* advanced mode
* border switch
* cutting direction
* child lock
* move-up warning
* cross-map border warning
* safe protect
* TrueDetect
* volume

## Fork implemented

The O1200 development profile additionally exposes:

* AI recognition
* animal protection
* smart mowing with avoidance / Humanoid AI
* narrow passage adaptation
* rain sensor configuration and delay
* lifted-alarm volume
* runtime protection state

## Protocol-observed details represented by the fork

Known protocol structures include:

* scheduled animal protection
* AI recognition state
* Humanoid AI enable state
* narrow-passage adaptation state
* rain enable state
* post-rain delay
* separate system/fall volume channels
* pushed runtime protection flags

## Not yet mapped

Important remaining mower settings include:

* cutting height
* GOAT-specific mowing efficiency/mode
* mowing speed
* any additional global mowing behaviour not yet correlated to protocol traffic

These should be investigated separately.

---

# Relevant source files

## Upstream

* [`deebot_client/capabilities.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/capabilities.py)
* [`deebot_client/hardware/2i0fns.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/hardware/2i0fns.py)

## Development branch

* [`deebot_client/capabilities.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/capabilities.py)
* [`deebot_client/hardware/2i0fns.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/hardware/2i0fns.py)
* [`deebot_client/commands/json/animal_protection.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/animal_protection.py)
* [`deebot_client/commands/json/humanoid_ai.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/humanoid_ai.py)
* [`deebot_client/commands/json/narrow_adapt.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/narrow_adapt.py)
* [`deebot_client/commands/json/recognization.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/recognization.py)
* [`deebot_client/commands/json/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/rain_delay.py)
* [`deebot_client/commands/json/volume.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/volume.py)
* [`deebot_client/events/protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/events/protect_state.py)
* [`deebot_client/events/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/events/rain_delay.py)
* [`deebot_client/messages/json/protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/protect_state.py)
* [`deebot_client/messages/json/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/rain_delay.py)

## Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mowing control](mowing-control.md)
* [Zone and area mowing](zones-and-areas.md)
* [Mowing progress and statistics](progress-and-statistics.md)
* Rain and protection *(next)*
* Obstacle and AI features *(planned)*
* Home Assistant integration *(planned)*
