# Obstacle avoidance and AI-related settings

This page documents obstacle-, recognition- and navigation-related settings identified for ECOVACS GOAT mowers.

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* development branch `feature/ecovacs-mower-settings`

Date: **2026-08-23**

## Overview

Several GOAT protocol settings appear related to obstacle detection, recognition or navigation behaviour.

The currently identified settings include:

```text
TrueDetect
AI recognition / Recognization
Humanoid AI
Narrow adaptation
Animal protection
```

These features should not be assumed to be interchangeable.

Although their names suggest related functions, they are represented by separate ECOVACS commands and separate `deebot_client` events.

The current documentation therefore treats each protocol feature independently until its exact ECOVACS app meaning has been verified.

---

# Current implementation status

| Feature                   | Upstream | Development fork | GOAT O1200 capability |
| ------------------------- | :------: | :--------------: | :-------------------: |
| TrueDetect                |     ✓    |         ✓        |           ✓           |
| AI recognition            |     —    |         ✓        |           ✓           |
| Humanoid AI               |     —    |         ✓        |           ✓           |
| Narrow passage adaptation |     —    |         ✓        |           ✓           |
| Animal protection         |     —    |         ✓        |           ✓           |

`TrueDetect` is already part of the reviewed upstream GOAT hardware profiles.

The other settings are currently implemented in the mower development branch and wired to the O1200 LiDAR profile used during protocol research.

---

# Do not merge these settings conceptually

A tempting interpretation would be:

```text
all AI/obstacle settings
        │
        ▼
one obstacle-avoidance feature
```

The protocol evidence does not support that simplification.

Instead, ECOVACS exposes separate controls:

```text
getTrueDetect
setTrueDetect

getRecognization
setRecognization

getHumanoidAI
setHumanoidAI

getNarrowAdapt
setNarrowAdapt

getAnimProtect
setAnimProtect
```

The safer model is therefore:

```text
Obstacle / navigation system
        │
        ├── TrueDetect
        ├── AI recognition
        ├── Humanoid AI
        ├── Narrow adaptation
        └── Animal protection
```

Their exact relationships may become clearer after systematic ECOVACS app correlation.

---

# TrueDetect

Capability:

```text
settings.true_detect
```

Event:

```text
TrueDetectEvent
```

Commands:

```text
GetTrueDetect
SetTrueDetect
```

Protocol names:

```text
getTrueDetect
setTrueDetect
```

Type:

```text
boolean
```

Status:

**Upstream implemented**

All five reviewed GOAT hardware profiles currently expose this capability.

---

# What can safely be said about TrueDetect

The feature is a boolean ECOVACS setting.

The client knows how to:

```text
read current value
set enabled/disabled
emit TrueDetectEvent
```

What cannot safely be concluded from the source code alone is exactly which GOAT app control or physical avoidance behaviour it represents.

The protocol term:

```text
TrueDetect
```

is an ECOVACS product/protocol name.

It should therefore not automatically be documented as:

```text
all obstacle avoidance
```

or:

```text
AI object recognition
```

without device correlation.

---

# AI recognition

The mower development branch introduces:

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

ECOVACS protocol names:

```text
getRecognization
setRecognization
```

The spelling:

```text
Recognization
```

is preserved because it is the name used by the ECOVACS protocol.

The user-facing documentation uses:

```text
AI recognition
```

instead.

Status:

**Fork implemented**

---

# AI recognition protocol field

The AI-recognition commands use:

```text
state
```

as their boolean protocol field.

Conceptually:

```json
{
  "state": 1
}
```

represents enabled and:

```json
{
  "state": 0
}
```

represents disabled.

The development test suite verifies both values.

The corresponding normalised events are conceptually:

```python
AiRecognitionEvent(True)
```

and:

```python
AiRecognitionEvent(False)
```

---

# AI recognition architecture

```text
GetRecognization
       │
       ▼
getRecognization
       │
       ▼
state
       │
       ▼
AiRecognitionEvent
```

Changing the feature follows:

```text
SetRecognization
       │
       ▼
setRecognization
       │
       ▼
state = 0 / 1
```

This maps naturally to a boolean integration control.

---

# Humanoid AI

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

ECOVACS protocol names:

```text
getHumanoidAI
setHumanoidAI
```

Status:

**Fork implemented**

---

# Current implementation description

The implementation describes this feature as:

```text
Smart mowing with avoidance
```

and the corresponding event as:

```text
Smart mowing with avoidance event
```

This is currently the strongest implementation-level description available.

However, the protocol name:

```text
HumanoidAI
```

should not be interpreted literally as proof that the setting only relates to detecting humans.

Possible interpretations might include:

* person-aware mowing behaviour
* intelligent avoidance
* enhanced obstacle avoidance
* recognition-dependent mowing behaviour

but these should remain hypotheses until correlated with the ECOVACS app and physical mower behaviour.

---

# Humanoid AI protocol field

Unlike AI recognition, Humanoid AI uses:

```text
enable
```

rather than:

```text
state
```

The development tests verify:

```json
{
  "enable": 0
}
```

and:

```json
{
  "enable": 1
}
```

as disabled/enabled states.

This difference is small but technically important.

Protocol implementations should preserve the field expected by each ECOVACS command rather than assuming all boolean settings use the same key.

---

# Humanoid AI architecture

```text
GetHumanoidAi
      │
      ▼
getHumanoidAI
      │
      ▼
enable
      │
      ▼
HumanoidAiEvent
```

and:

```text
SetHumanoidAi
      │
      ▼
setHumanoidAI
      │
      ▼
enable = 0 / 1
```

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

Status:

**Fork implemented**

The implementation describes this feature as:

```text
Narrow passage adaptation
```

This wording provides a much stronger hint about its function than some of the AI-related protocol names.

---

# Narrow adaptation protocol field

The setting uses:

```text
state
```

as the protocol field.

Conceptually:

```json
{
  "state": 1
}
```

means enabled.

The development test suite verifies both enabled and disabled values.

---

# Likely functional area

Based on its implementation name, narrow adaptation is likely related to mower navigation in constrained passages.

Conceptually it may influence situations such as:

```text
large lawn
    │
    ▼
narrow connecting corridor
    │
    ▼
second lawn area
```

However, the exact physical effects remain to be documented.

Questions still requiring physical testing include:

* Does it allow traversal of narrower passages?
* Does it alter route planning?
* Does it change obstacle-clearance distance?
* Does it affect mowing inside the passage or only transit?
* Is it automatically required for particular map geometries?
* Does enabling it have any negative trade-offs?

Until tested, these should remain open questions.

---

# Animal protection

Animal protection is related to mower safety/avoidance but differs significantly from the other settings.

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

Status:

**Fork implemented**

---

# Animal protection is scheduled

Animal protection is not simply:

```text
enabled / disabled
```

Its complete configuration contains:

```text
enabled
start
end
```

Example:

```json
{
  "enable": 1,
  "start": "23:45",
  "end": "06:30"
}
```

This makes it fundamentally different from:

```text
TrueDetect
AI recognition
Humanoid AI
Narrow adaptation
```

which are currently represented as simple boolean controls.

---

# Why the schedule matters

A scheduled animal-protection feature strongly suggests that the mower's behaviour changes during a configured time window.

Conceptually:

```text
Animal protection enabled
          │
          ▼
    configured window
     start ─── end
          │
          ▼
different mower behaviour
```

The exact behaviour during this window should not be guessed.

Possible behaviours might include:

* mowing restriction
* enhanced recognition
* reduced mowing activity
* special avoidance behaviour
* night-time protection

but protocol configuration alone does not prove which mechanism ECOVACS uses.

---

# Runtime animal protection

The mower also reports:

```text
isAnimProtect
```

through:

```text
onProtectState
```

which is exposed as:

```text
ProtectStateEvent.is_anim_protect
```

This provides a useful distinction between:

```text
AnimalProtectionEvent
```

and:

```text
ProtectStateEvent.is_anim_protect
```

The first represents configuration.

The second represents runtime protection state.

Conceptually:

```text
enabled + start/end schedule
             │
             ▼
       mower evaluates time
             │
             ▼
      is_anim_protect
```

The exact transition should be tested by observing the mower before, during and after the configured time interval.

---

# Relationship between animal protection and AI

The protocol places animal protection alongside several recognition and avoidance features, but the implementation does not prove that it directly depends on:

```text
AI recognition
```

or:

```text
Humanoid AI
```

Possible relationships include:

```text
independent systems
```

or:

```text
animal protection
      │
      ▼
uses AI recognition internally
```

or:

```text
animal protection
      │
      ▼
changes mowing schedule rather than recognition
```

These relationships remain unverified.

Integrations should therefore expose the settings independently unless later evidence shows a dependency.

---

# Capability and field summary

| Feature           | Capability          | Protocol                                | Field(s)                 | Type            |
| ----------------- | ------------------- | --------------------------------------- | ------------------------ | --------------- |
| TrueDetect        | `true_detect`       | `getTrueDetect` / `setTrueDetect`       | enable-style boolean     | bool            |
| AI recognition    | `ai_recognition`    | `getRecognization` / `setRecognization` | `state`                  | bool            |
| Humanoid AI       | `humanoid_ai`       | `getHumanoidAI` / `setHumanoidAI`       | `enable`                 | bool            |
| Narrow adaptation | `narrow_adapt`      | `getNarrowAdapt` / `setNarrowAdapt`     | `state`                  | bool            |
| Animal protection | `animal_protection` | `getAnimProtect` / `setAnimProtect`     | `enable`, `start`, `end` | bool + schedule |

---

# Push/update messages

The mower-specific settings implementation also registers message handlers associated with these settings.

This allows state to be updated when ECOVACS reports a change rather than relying only on explicit GET requests.

Known mower-related message handlers include:

```text
OnRecognization
OnHumanoidAi
OnNarrowAdapt
OnAnimalProtection
```

Conceptually:

```text
user changes app setting
       │
       ▼
ECOVACS/device message
       │
       ▼
On... message handler
       │
       ▼
normalised Event
       │
       ▼
integration state updates
```

This is useful when the setting is modified outside Home Assistant or another consuming integration.

---

# Model-specific capability wiring

The development implementation deliberately connects these newly researched settings to the:

```text
GOAT O1200 LiDAR
hardware ID: 2i0fns
```

profile.

The hardware tests verify that:

```text
ai_recognition
animal_protection
humanoid_ai
narrow_adapt
fall_volume
```

are present on O1200.

They also verify that the same development settings are not automatically present on an unrelated device profile.

This reflects an important design rule:

> A command existing in `deebot_client` does not mean it should automatically be enabled for every ECOVACS device.

---

# Other GOAT models

The current development evidence does not yet justify automatically enabling the newly mapped AI settings on:

* GOAT G1
* GOAT A1600 RTK
* GOAT A3000 LiDAR Pro
* GOAT O500 Panorama

Some or all of those models may support the same features.

However, that should be established through:

* hardware-profile evidence
* app capability comparison
* protocol capture
* physical-device testing

rather than assumed from product similarity.

---

# Interaction with mower navigation

Several of these settings may affect the same physical mowing decision.

For example, when the mower approaches an object:

```text
Mower approaches object
        │
        ▼
sensor / camera / LiDAR input
        │
        ▼
recognition/navigation logic
        │
        ├── TrueDetect?
        ├── AI recognition?
        ├── Humanoid AI?
        └── other internal logic?
               │
               ▼
        continue / avoid / reroute
```

The question marks are intentional.

The protocol currently tells us that the controls exist, but not the internal precedence or dependency between them.

---

# Recommended systematic mapping

A reliable mapping should change one app setting at a time while capturing protocol traffic.

For each ECOVACS app option:

```text
1. record initial state
2. change only one toggle
3. observe outgoing command
4. observe resulting push message
5. restore original value
6. repeat
```

This makes it possible to create a table like:

| ECOVACS app label | Protocol command   | Field    | Confirmed |
| ----------------- | ------------------ | -------- | :-------: |
| App option A      | `setRecognization` | `state`  |     ✓     |
| App option B      | `setHumanoidAI`    | `enable` |     ✓     |
| App option C      | `setNarrowAdapt`   | `state`  |     ✓     |

Until this correlation has been performed, documentation should retain protocol-oriented names.

---

# Recommended physical testing

Protocol correlation establishes which toggle is which.

Physical testing is then needed to establish what the option actually changes.

For example, a repeatable obstacle test could use:

```text
same lawn
same obstacle
same route
same mowing mode
```

while changing only:

```text
one setting
```

Possible observations include:

* minimum avoidance distance
* whether mower stops
* whether mower reroutes
* whether mower attempts a closer approach
* whether object classification appears in the app
* whether mowing coverage around the obstacle changes

The goal should be reproducibility rather than subjective visual impressions.

---

# Avoidance distance

No dedicated mower capability for a numeric:

```text
obstacle avoidance distance
```

has been confirmed in the reviewed code.

If the ECOVACS app exposes such an option, it remains a separate research target.

It should not be conflated with the boolean:

```text
TrueDetect
AI recognition
Humanoid AI
```

settings.

Status:

**Not yet mapped**

---

# Night restrictions

Animal protection contains an explicit time window and is therefore potentially related to night-time mower behaviour.

However, it should not automatically be documented as:

```text
night mowing disabled
```

until app behaviour confirms that interpretation.

There may also be a separate night restriction elsewhere in the protocol.

Status:

**Needs further mapping**

---

# Human versus animal recognition

The names:

```text
HumanoidAI
```

and:

```text
AnimProtect
```

suggest different protection categories.

However, their relationship to object classification remains unknown.

A future protocol capture should look for:

* detected-object messages
* object-type IDs
* recognition events
* avoidance-event payloads
* images or metadata associated with detections

This may reveal whether ECOVACS exposes classification information separately from the configuration toggles.

---

# Home Assistant representation

Once mappings are confirmed, the simple boolean settings naturally fit switch entities.

Possible examples:

```text
switch.goat_true_detect
switch.goat_ai_recognition
switch.goat_smart_avoidance
switch.goat_narrow_passage_adaptation
```

Animal protection requires multiple controls because it includes a schedule.

Possible representation:

```text
switch.goat_animal_protection
time.goat_animal_protection_start
time.goat_animal_protection_end
```

The exact entity names should use clear user-facing terminology once the ECOVACS app mapping is known.

---

# Avoid exposing protocol names unnecessarily

Names such as:

```text
Recognization
HumanoidAI
```

are useful for developer documentation but may be confusing in a normal user interface.

A good architecture separates:

```text
Protocol name
     │
     ▼
deebot_client capability
     │
     ▼
user-facing integration label
```

For example:

```text
getRecognization
       │
       ▼
ai_recognition
       │
       ▼
"AI object recognition"
```

but the final label should only be chosen once its meaning is confirmed.

---

# Evidence summary

## Upstream implemented

Confirmed upstream:

* `TrueDetectEvent`
* `GetTrueDetect`
* `SetTrueDetect`
* `settings.true_detect`
* TrueDetect capability wiring on reviewed GOAT profiles

## Fork implemented

Confirmed in the development branch:

* `AiRecognitionEvent`
* `GetRecognization`
* `SetRecognization`
* `settings.ai_recognition`
* `HumanoidAiEvent`
* `GetHumanoidAi`
* `SetHumanoidAi`
* `settings.humanoid_ai`
* `NarrowAdaptEvent`
* `GetNarrowAdapt`
* `SetNarrowAdapt`
* `settings.narrow_adapt`
* `AnimalProtectionEvent`
* `GetAnimalProtection`
* `SetAnimalProtection`
* `settings.animal_protection`

## Python-tested

Development tests verify:

* AI recognition enabled/disabled parsing
* AI recognition `state` field
* Humanoid AI enabled/disabled parsing
* Humanoid AI `enable` field
* narrow-adaptation enabled/disabled parsing
* narrow-adaptation `state` field
* animal-protection configuration
* animal-protection time zero-padding
* O1200 capability wiring
* command registration
* message registration
* model-specific capability behaviour

## Not yet fully mapped

Still requiring app/device correlation:

* exact ECOVACS app label for `TrueDetect`
* exact app label for `Recognization`
* exact app label for `HumanoidAI`
* exact app label for `NarrowAdapt`
* functional dependency between the settings
* physical avoidance changes caused by each toggle
* human/object recognition behaviour
* animal-protection physical behaviour
* night-time implications of animal protection
* numeric avoidance distance, if available
* model differences across the GOAT range

---

# Relevant source files

## Upstream

* [`deebot_client/commands/json/true_detect.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/true_detect.py)
* [`deebot_client/capabilities.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/capabilities.py)

## Development branch

* [`deebot_client/capabilities.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/capabilities.py)
* [`deebot_client/hardware/2i0fns.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/hardware/2i0fns.py)
* [`deebot_client/commands/json/recognization.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/recognization.py)
* [`deebot_client/commands/json/humanoid_ai.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/humanoid_ai.py)
* [`deebot_client/commands/json/narrow_adapt.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/narrow_adapt.py)
* [`deebot_client/commands/json/animal_protection.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/commands/json/animal_protection.py)
* [`deebot_client/events/__init__.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/events/__init__.py)

## Tests

* [`tests/commands/json/test_mower_settings.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/commands/json/test_mower_settings.py)
* [`tests/hardware/test_mower_settings.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/hardware/test_mower_settings.py)

## Related documentation

* [Mower settings](settings.md)
* [Rain and protection](rain-and-protection.md)
* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* Protocol reference *(planned)*
* Testing status *(planned)*
* Home Assistant integration *(planned)*
