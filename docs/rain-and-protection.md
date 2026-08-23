# Rain and protection behaviour

This page documents rain configuration and runtime protection states observed and implemented during ECOVACS GOAT mower protocol research.

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* development branch `feature/ecovacs-mower-settings`

Date: **2026-08-23**

## Overview

GOAT rain handling consists of at least two separate concepts:

1. **rain configuration**
2. **current protection state**

These should not be treated as the same thing.

Rain configuration determines whether rain protection is enabled and how long the mower should wait after rain.

Runtime protection state indicates whether the mower currently considers a protection condition active.

Conceptually:

```text
Configuration
     │
     ├── rain protection enabled
     └── post-rain delay
              │
              ▼
          mower logic
              │
              ▼
Runtime protection state
     │
     ├── rain protection active
     └── rain-delay state
```

The development implementation deliberately keeps these concepts separate.

---

# Implementation status

Rain-specific support described on this page is not part of the reviewed upstream `dev` baseline.

It is implemented in the mower development branches and connected to the GOAT O1200 LiDAR hardware profile used during protocol research.

Current evidence:

| Feature                                            | Status                      |
| -------------------------------------------------- | --------------------------- |
| Set rain configuration                             | Fork implemented            |
| Receive rain configuration                         | Fork implemented            |
| Rain delay validation                              | Fork implemented and tested |
| Active rain-protection state                       | Protocol observed           |
| Protection-state parser                            | Fork implemented and tested |
| Animal-protection runtime flag                     | Fork implemented            |
| Emergency-stop flag                                | Fork implemented            |
| Lock state flag                                    | Fork implemented            |
| PIN-code flag                                      | Fork implemented            |
| Full semantics of every protection flag transition | Not fully verified          |

---

# Rain configuration

The mower development implementation represents rain configuration with:

```text
RainDelayEvent
```

containing:

```python
enabled: bool
delay: int
```

The meaning is:

```text
enabled
    │
    └── whether mower rain protection is configured/enabled

delay
    │
    └── post-rain delay in minutes
```

Example:

```text
enabled = true
delay   = 180
```

means that rain protection is enabled with a configured delay of 180 minutes.

It does **not** mean that the mower is currently experiencing rain.

---

# `setRainDelay`

Rain configuration is changed using:

```text
SetRainDelay
```

with ECOVACS protocol command:

```text
setRainDelay
```

The request contains:

```text
enable
delay
```

Example:

```json
{
  "enable": 1,
  "delay": 180
}
```

The Python API uses:

```python
SetRainDelay(
    enabled=True,
    delay=180,
)
```

Boolean conversion is:

```text
False → 0
True  → 1
```

---

# Supported delay values

The current implementation accepts delays from:

```text
0
```

through:

```text
300
```

minutes in increments of:

```text
30
```

minutes.

The complete accepted set is:

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

Equivalent range:

```text
0–300 minutes
30-minute increments
```

Examples of accepted configurations:

```text
enabled=False, delay=180
enabled=True,  delay=0
enabled=True,  delay=30
enabled=True,  delay=180
enabled=True,  delay=300
```

Values outside the supported set are rejected.

Examples:

```text
-1
1
15
301
```

result in a:

```text
ValueError
```

in the current implementation.

---

# Delay value when disabled

The protocol permits the configuration to contain both:

```text
enable = 0
```

and a retained delay value.

For example:

```json
{
  "enable": 0,
  "delay": 180
}
```

should not automatically be interpreted as inconsistent.

It can represent:

```text
rain protection disabled
+
configured delay value retained
```

An integration should therefore preserve both fields independently rather than forcing the delay to zero whenever protection is disabled.

---

# Command acknowledgement

`setRainDelay` supports MQTT/P2P command handling.

A successful acknowledgement can contain a normal response such as:

```json
{
  "code": 0,
  "msg": "ok"
}
```

However, the command acknowledgement itself does not create the final `RainDelayEvent`.

The implementation explicitly expects the resulting state to be reported separately through:

```text
onRainDelay
```

Conceptually:

```text
SetRainDelay
      │
      ▼
setRainDelay
      │
      ▼
acknowledgement
      │
      │
      └── command accepted
              │
              ▼
        onRainDelay
              │
              ▼
       RainDelayEvent
```

This distinction is useful because command success and resulting mower configuration are not necessarily the same protocol message.

---

# `onRainDelay`

The mower reports rain configuration through:

```text
onRainDelay
```

The parser expects:

```text
enable
delay
```

For example:

```json
{
  "enable": 1,
  "delay": 180
}
```

produces:

```python
RainDelayEvent(
    enabled=True,
    delay=180,
)
```

Likewise:

```json
{
  "enable": 0,
  "delay": 180
}
```

becomes:

```python
RainDelayEvent(
    enabled=False,
    delay=180,
)
```

Status:

**Fork implemented**

---

# No GET command in current implementation

Unlike many normal settings, the researched O1200 capability currently has no explicit GET command attached to rain configuration:

```python
rain_delay=CapabilitySet(
    RainDelayEvent,
    [],
    SetRainDelay,
)
```

The empty list means:

```text
no refresh command currently assigned
```

State is instead obtained from the mower's:

```text
onRainDelay
```

message.

This may change if a reliable GET command is identified later.

---

# Configuration versus runtime rain state

This is the most important distinction in the rain implementation.

## Configuration

Represented by:

```text
RainDelayEvent
```

Fields:

```text
enabled
delay
```

This answers questions such as:

```text
Is rain protection configured?
How long should the mower wait after rain?
```

## Runtime state

Represented by:

```text
ProtectStateEvent
```

Relevant fields:

```text
is_rain_protect
is_rain_delay
```

This answers questions about what the mower currently reports as an active protection condition.

The two event types should not be merged.

---

# `onProtectState`

GOAT protection state is reported through:

```text
onProtectState
```

The development parser exposes the message as:

```text
ProtectStateEvent
```

with seven boolean values:

```python
is_anim_protect: bool
is_rain_protect: bool
is_rain_delay: bool
is_e_stop: bool
is_locked: bool
is_pin_code: bool
is_prepare_data_success: bool
```

The field mapping is:

| Protocol field         | Python field              |
| ---------------------- | ------------------------- |
| `isAnimProtect`        | `is_anim_protect`         |
| `isRainProtect`        | `is_rain_protect`         |
| `isRainDelay`          | `is_rain_delay`           |
| `isEStop`              | `is_e_stop`               |
| `isLocked`             | `is_locked`               |
| `isPinCode`            | `is_pin_code`             |
| `isPrepareDataSuccess` | `is_prepare_data_success` |

---

# Why the event preserves raw booleans

The implementation intentionally avoids inventing semantics for state combinations that have not been observed.

The protocol gives fields such as:

```text
isRainProtect
isRainDelay
```

but field names alone are not sufficient to describe every possible mower transition.

The safer approach is:

```text
protocol boolean
      │
      ▼
normalised Python boolean
      │
      ▼
interpret only observed states
```

rather than:

```text
protocol field name
      │
      ▼
assumed meaning
```

This is especially important for protection logic because inaccurate interpretation could cause an integration to report misleading mower state.

---

# Observed active rain state

During actual rain, the following state was observed:

```text
isRainProtect = 1
isRainDelay   = 0
```

The remaining reported values in the captured example were:

```text
isAnimProtect         = 0
isEStop               = 0
isLocked              = 0
isPinCode             = 0
isPrepareDataSuccess  = 1
```

The corresponding client event is:

```python
ProtectStateEvent(
    is_anim_protect=False,
    is_rain_protect=True,
    is_rain_delay=False,
    is_e_stop=False,
    is_locked=False,
    is_pin_code=False,
    is_prepare_data_success=True,
)
```

This state is explicitly preserved in the development test suite as:

```text
observed-rain
```

Evidence:

**Device/protocol observed**

---

# Meaning of `isRainProtect`

Based on the actual-rain observation:

```text
isRainProtect = 1
```

is strong evidence that this field can indicate an active rain-protection condition.

A reasonable current interpretation is therefore:

```text
is_rain_protect = True
        │
        ▼
mower currently reports rain protection active
```

This is stronger evidence than merely interpreting the field name because the state was correlated with real rain.

---

# Meaning of `isRainDelay`

The development implementation intentionally does not fully define the semantics of:

```text
isRainDelay = 1
```

because the actual-rain observation contained:

```text
isRainDelay = 0
```

A likely hypothesis is that `isRainDelay` represents a post-rain waiting state, but that should remain a hypothesis until the transition is directly observed.

Current status:

```text
isRainDelay = 0 during actual rain
```

**Observed**

```text
isRainDelay = 1 meaning post-rain waiting period
```

**Not yet confirmed**

This distinction should remain in the documentation until a controlled rain/dry transition is captured.

---

# Expected rain lifecycle

A possible conceptual lifecycle is:

```text
Dry
 │
 ▼
Rain detected
 │
 ▼
isRainProtect = 1
 │
 ▼
Rain stops
 │
 ▼
configured delay
 │
 ▼
mowing allowed again
```

The unresolved question is whether:

```text
isRainDelay = 1
```

is the protocol indication used during the delay phase.

Until observed, this lifecycle should not be presented as confirmed protocol behaviour.

---

# Controlled future test

A useful future rain experiment would capture the entire sequence:

```text
1. mower dry
2. rain protection enabled
3. rain begins
4. active rain protection
5. rain stops
6. post-rain waiting period
7. delay expires
8. mower becomes available for mowing again
```

For each stage, record:

```text
onRainDelay
onProtectState
mower StateEvent
ECOVACS app status
timestamp
```

This would allow direct mapping of:

```text
isRainProtect
isRainDelay
```

through the complete lifecycle.

---

# Animal protection runtime state

`ProtectStateEvent` also contains:

```text
is_anim_protect
```

This should be distinguished from the animal-protection configuration documented in `settings.md`.

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

Conceptually:

```text
Configured schedule
       │
       ▼
animal protection logic
       │
       ▼
is_anim_protect
```

The configuration tells us what should happen.

The runtime field tells us what the mower currently reports.

---

# Scheduled animal protection

The mower-specific implementation exposes animal protection through:

```text
getAnimProtect
setAnimProtect
```

with:

```text
enable
start
end
```

Example:

```json
{
  "enable": 1,
  "start": "20:00",
  "end": "08:00"
}
```

The Python event normalises times to:

```text
HH:MM
```

The feature therefore appears to be a scheduled protection mode rather than a simple global on/off switch.

The exact relationship between the configured schedule and:

```text
isAnimProtect
```

should be verified through timed device observation.

---

# Emergency-stop state

`ProtectStateEvent` exposes:

```text
is_e_stop
```

from protocol field:

```text
isEStop
```

The current implementation exposes this value without further interpretation.

Status:

**Protocol field mapped**

The exact trigger conditions and reset behaviour should be verified before building advanced automation logic around it.

For UI purposes, it is a candidate for a read-only binary status rather than a writable setting.

---

# Locked state

The protection-state message contains:

```text
isLocked
```

mapped to:

```text
is_locked
```

This is again exposed as a runtime boolean.

It should not automatically be assumed to be identical to:

```text
ChildLockEvent
```

because the protocol exposes them through separate mechanisms.

Possible relationships between:

```text
child_lock
```

and:

```text
is_locked
```

require device correlation.

---

# PIN-code state

The message also exposes:

```text
isPinCode
```

mapped to:

```text
is_pin_code
```

The implementation deliberately does not interpret this as:

* PIN configured
* PIN currently requested
* mower unlocked by PIN
* anti-theft state

without evidence.

Status:

**Protocol field mapped / semantics unverified**

---

# `isPrepareDataSuccess`

Another reported field is:

```text
isPrepareDataSuccess
```

mapped to:

```text
is_prepare_data_success
```

The actual-rain observation contained:

```text
isPrepareDataSuccess = 1
```

but its user-facing significance has not been established.

It is retained because it is part of the observed protection-state message and may prove useful when analysing state transitions.

Status:

**Protocol field mapped / semantics unverified**

---

# Boolean conversion

Protocol state values are converted to normal Python booleans.

For example:

```json
{
  "isAnimProtect": 1,
  "isRainProtect": 0,
  "isRainDelay": 1,
  "isEStop": 0,
  "isLocked": 1,
  "isPinCode": 0,
  "isPrepareDataSuccess": 1
}
```

becomes:

```python
ProtectStateEvent(
    is_anim_protect=True,
    is_rain_protect=False,
    is_rain_delay=True,
    is_e_stop=False,
    is_locked=True,
    is_pin_code=False,
    is_prepare_data_success=True,
)
```

This conversion behaviour is covered by the development test suite.

The test proves parser behaviour.

It does not prove the physical interpretation of this particular combination.

---

# Firmware context

The protection-state and rain-delay test fixtures currently use firmware header:

```text
1.13.10
```

This provides useful context for the researched protocol examples.

However, protocol compatibility should not be assumed solely from this firmware value.

Future GOAT firmware versions may:

* add fields
* remove fields
* change state transitions
* alter command support
* change allowed delay values

Protocol observations should therefore record firmware whenever practical.

---

# Mower state versus protection state

`ProtectStateEvent` should not replace the normal mower:

```text
StateEvent
```

The two answer different questions.

## `StateEvent`

Examples:

```text
MOWING
PAUSED
RETURNING
DOCKED
IDLE
ERROR
```

internally represented using the shared client states.

## `ProtectStateEvent`

Examples:

```text
rain protection active
animal protection active
locked
emergency stop
```

A mower can therefore conceptually have:

```text
StateEvent = PAUSED
```

while simultaneously reporting:

```text
is_rain_protect = True
```

The protection event may help explain **why** the mower is not mowing, while the normal state describes **what it is currently doing**.

---

# Home Assistant representation

The distinction between configuration and runtime state should also be preserved in Home Assistant.

## Configuration entities

Potential examples:

```text
switch.goat_rain_protection
select.goat_rain_delay
```

or a number/select for supported delay values.

Animal protection may require:

```text
switch.goat_animal_protection
time.goat_animal_protection_start
time.goat_animal_protection_end
```

depending on integration design.

## Runtime binary sensors

Potential examples:

```text
binary_sensor.goat_rain_protection_active
binary_sensor.goat_rain_delay_active
binary_sensor.goat_animal_protection_active
binary_sensor.goat_emergency_stop
binary_sensor.goat_locked
```

The naming should make clear that these represent current state rather than configuration.

---

# Do not infer availability from configuration alone

An automation should not assume:

```text
rain protection enabled
```

means:

```text
mower unavailable
```

Likewise:

```text
animal protection enabled
```

does not necessarily mean:

```text
animal protection active now
```

Availability decisions should use runtime state when available.

Conceptually:

```text
Configuration
     │
     └── what the mower is configured to do

Runtime state
     │
     └── what protection is active now
```

---

# Current O1200 support

The development O1200 profile exposes:

```text
settings.rain_delay
```

and top-level:

```text
protect_state
```

The rain configuration capability uses:

```text
RainDelayEvent
SetRainDelay
```

while runtime state uses:

```text
ProtectStateEvent
onProtectState
```

This gives an integration both:

```text
configured behaviour
```

and:

```text
reported protection state
```

without merging the two.

---

# Evidence summary

## Fork implemented

Implemented in the mower development branch:

* `RainDelayEvent`
* `SetRainDelay`
* `OnRainDelay`
* rain delay validation
* `ProtectStateEvent`
* `OnProtectState`
* O1200 capability wiring
* parser and command tests

## Device/protocol observed

Directly supported by observed mower communication:

* `onProtectState`
* actual-rain state with:

  * `isRainProtect = 1`
  * `isRainDelay = 0`
* rain configuration messages
* rain enable state
* configured delay values

## Tested in Python

Tests cover:

* rain disabled with retained delay
* rain enabled with zero delay
* valid 30-minute increments
* 300-minute maximum
* invalid delay rejection
* `onRainDelay` parsing
* actual-rain protection-state fixture
* all-zero protection state
* boolean conversion for protection fields

## Not yet fully verified

Further observation is needed for:

* exact meaning of `isRainDelay = 1`
* transition from active rain to delay
* delay-expiry transition
* interaction between rain protection and an active mowing job
* automatic resume behaviour after rain
* model differences
* behaviour on firmware versions other than those observed
* exact meaning of `isPrepareDataSuccess`
* exact relationship between `isLocked` and child lock
* exact meaning of `isPinCode`
* emergency-stop trigger/reset lifecycle

---

# Recommended research capture

For future protection-state research, capture messages with:

```text
timestamp
firmware version
current app screen/state
weather or test condition
mower operational state
onRainDelay payload
onProtectState payload
relevant user action
```

The goal should be to correlate protocol transitions with reproducible physical events.

Raw logs should still be sanitised before publication.

---

# Relevant source files

## Development branch

* [`deebot_client/capabilities.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/capabilities.py)
* [`deebot_client/hardware/2i0fns.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/hardware/2i0fns.py)
* [`deebot_client/commands/json/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/rain_delay.py)
* [`deebot_client/events/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/events/rain_delay.py)
* [`deebot_client/messages/json/rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/rain_delay.py)
* [`deebot_client/events/protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/events/protect_state.py)
* [`deebot_client/messages/json/protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/messages/json/protect_state.py)
* [`deebot_client/commands/json/animal_protection.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/animal_protection.py)

## Tests

* [`tests/commands/json/test_rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/commands/json/test_rain_delay.py)
* [`tests/messages/json/test_rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/messages/json/test_rain_delay.py)
* [`tests/messages/json/test_protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/messages/json/test_protect_state.py)

## Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mower settings](settings.md)
* [Mowing control](mowing-control.md)
* Obstacle and AI features *(next)*
* Protocol reference *(planned)*
* Home Assistant integration *(planned)*
