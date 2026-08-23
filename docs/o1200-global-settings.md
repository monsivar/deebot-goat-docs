# O1200 global mower settings

This page documents the global ECOVACS GOAT O1200 LiDAR settings implemented in the development work represented by:

- [`PR #1776 — Add GOAT rain settings support`](https://github.com/DeebotUniverse/client.py/pull/1776)
- [`PR #1778 — Add GOAT mower settings support`](https://github.com/DeebotUniverse/client.py/pull/1778)

Last reviewed: **2026-08-24**

> [!IMPORTANT]
> Both PRs were still open at the time of this review.
>
> The functionality described here is therefore **development/fork support**, not part of the reviewed upstream `dev` baseline.

## Relationship between PR #1776 and PR #1778

PR #1776 introduced the rain/protection subset:

```text
rain configuration
runtime protection state
```

PR #1778 incorporates that work and adds the remaining researched global O1200 settings:

```text
AI recognition
smart mowing with avoidance
narrow passage adaptation
animal protection
system-volume handling for mower payloads
lifted-alarm volume
mower setting push messages
```

For documentation purposes:

```text
#1776
  │
  └── rain/protection foundation
          │
          ▼
#1778
  │
  └── combined O1200 global-settings implementation
```

PR #1778 should therefore be treated as the broader settings PR, while PR #1776 remains useful as the detailed provenance of the rain/protection implementation.

---

# Scope

These are **global mower settings/state**.

They are separate from the zone-specific:

```text
AreaParameter
```

family documented in:

[O1200 area parameters](area-parameters.md)

Conceptually:

```text
O1200 settings
   │
   ├── global
   │     ├── rain
   │     ├── AI
   │     ├── animal protection
   │     └── volume
   │
   └── per-zone
         ├── mowHeightLevel
         ├── cutMode
         ├── obstacleHeight
         └── angle
```

---

# Current capability summary

| Feature | Capability | Event | GET | SET | PUSH |
| --- | --- | --- | --- | --- | --- |
| Rain configuration | `settings.rain_delay` | `RainDelayEvent` | none | `SetRainDelay` | `onRainDelay` |
| Runtime protection | `protect_state` | `ProtectStateEvent` | none | none | `onProtectState` |
| AI recognition | `settings.ai_recognition` | `AiRecognitionEvent` | `GetRecognization` | `SetRecognization` | `onRecognization` |
| Smart mowing with avoidance | `settings.humanoid_ai` | `HumanoidAiEvent` | `GetHumanoidAi` | `SetHumanoidAi` | `onHumanoidAI` |
| Narrow passage adaptation | `settings.narrow_adapt` | `NarrowAdaptEvent` | `GetNarrowAdapt` | `SetNarrowAdapt` | `onNarrowAdapt` |
| Animal protection | `settings.animal_protection` | `AnimalProtectionEvent` | `GetAnimalProtection` | `SetAnimalProtection` | `onAnimProtect` |
| System volume | `settings.volume` | `VolumeEvent` | `GetVolume` | `SetVolume` | `onVolume` |
| Lifted-alarm volume | `settings.fall_volume` | `FallVolumeEvent` | `GetVolume` | `SetFallVolume` | `onVolume` |
| Mower lifted warning state | `settings.moveup_warning` | `MoveUpWarningEvent` | existing GET | existing SET | `onMoveupWarning` |

Strongest model evidence:

```text
GOAT O1200 LiDAR
hardware ID: 2i0fns
```

The new settings are intentionally wired only to this profile in the development implementation.

---

# Rain configuration

## Capability

```text
settings.rain_delay
```

Event:

```text
RainDelayEvent
```

Fields:

```text
enabled
delay
```

Setter:

```text
SetRainDelay
```

Wire command:

```text
setRainDelay
```

Push:

```text
onRainDelay
```

## Supported delay values

The setter accepts:

```text
0–300 minutes
```

in:

```text
30-minute increments
```

Equivalent values:

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

Unsupported values raise `ValueError`.

## No GET command is invented

The implementation deliberately does **not** introduce:

```text
getRainDelay
```

because such a refresh command was not sufficiently observed/documented.

The capability therefore uses:

```python
CapabilitySet(
    RainDelayEvent,
    [],
    SetRainDelay,
)
```

State is reported through:

```text
onRainDelay
```

## ACK versus reported state

A successful P2P acknowledgement does not itself publish the final configuration event.

Conceptually:

```text
SetRainDelay
      │
      ▼
ACK
      │
      ▼
onRainDelay
      │
      ▼
RainDelayEvent
```

The reported push should be treated as state confirmation.

Detailed rain semantics:

[Rain and protection](rain-and-protection.md)

---

# Runtime protection state

Capability:

```text
protect_state
```

Event:

```text
ProtectStateEvent
```

Push:

```text
onProtectState
```

No refresh GET command is attached.

Mapped fields:

```text
isAnimProtect        → is_anim_protect
isRainProtect        → is_rain_protect
isRainDelay          → is_rain_delay
isEStop              → is_e_stop
isLocked             → is_locked
isPinCode            → is_pin_code
isPrepareDataSuccess → is_prepare_data_success
```

The implementation deliberately preserves these as raw booleans without inventing semantics for states that have not been observed.

A real-rain observation confirmed:

```text
isRainProtect = 1
isRainDelay   = 0
```

The meaning of:

```text
isRainDelay = 1
```

remains unconfirmed.

---

# Deliberately excluded rain semantics

PR #1776 explicitly does **not** add semantic mappings for:

```text
event code 2052
```

or rain-specific:

```text
pause reason
```

values.

Reason:

```text
semantics not sufficiently documented
```

This is an important evidence rule.

The presence of an observed numeric event/reason is not enough to turn it into a named mower state.

These should remain research observations until independently correlated with physical/app behaviour.

---

# AI recognition

Capability:

```text
settings.ai_recognition
```

Commands:

```text
GetRecognization
SetRecognization
```

Wire:

```text
getRecognization
setRecognization
```

Push:

```text
onRecognization
```

Protocol field:

```text
state
```

Event:

```text
AiRecognitionEvent
```

The ECOVACS spelling:

```text
Recognization
```

is preserved in protocol/Python command names.

User-facing documentation should prefer:

```text
AI recognition
```

Status:

```text
Fork implemented / Python tested
```

The exact ECOVACS app label and full physical effect still require correlation.

---

# Smart mowing with avoidance

Capability:

```text
settings.humanoid_ai
```

Commands:

```text
GetHumanoidAi
SetHumanoidAi
```

Wire:

```text
getHumanoidAI
setHumanoidAI
```

Push:

```text
onHumanoidAI
```

Protocol field:

```text
enable
```

Event:

```text
HumanoidAiEvent
```

Implementation description:

```text
Smart mowing with avoidance
```

The wire term:

```text
HumanoidAI
```

should not automatically be interpreted as a human-only detection feature.

---

# Narrow passage adaptation

Capability:

```text
settings.narrow_adapt
```

Commands:

```text
GetNarrowAdapt
SetNarrowAdapt
```

Wire:

```text
getNarrowAdapt
setNarrowAdapt
```

Push:

```text
onNarrowAdapt
```

Protocol field:

```text
state
```

Event:

```text
NarrowAdaptEvent
```

Status:

```text
Fork implemented / Python tested
```

The exact physical routing/navigation change still requires systematic A/B testing.

---

# Animal protection

Capability:

```text
settings.animal_protection
```

Event:

```text
AnimalProtectionEvent
```

Fields:

```text
enabled
start
end
```

Commands:

```text
GetAnimalProtection
SetAnimalProtection
```

Wire:

```text
getAnimProtect
setAnimProtect
```

Push:

```text
onAnimProtect
```

## Time normalisation

Device/app times are normalised to:

```text
HH:MM
```

For example:

```text
8:5
```

becomes:

```text
08:05
```

## Complete-configuration writes

`SetAnimalProtection` writes the complete tuple:

```text
enable
start
end
```

on every write.

Conceptually:

```json
{
  "enable": 1,
  "start": "20:00",
  "end": "08:00"
}
```

This has an integration consequence:

> A higher-level UI that changes only `enabled`, `start`, or `end` must preserve the latest known sibling values.

Safe pattern:

```text
latest AnimalProtectionEvent
        │
        ▼
replace one requested field
        │
        ▼
SetAnimalProtection(
    enabled,
    start,
    end
)
        │
        ▼
onAnimProtect
```

PR #1778 notes that toggle writes were observed directly and time updates were confirmed through push-state updates.

---

# Volume architecture

PR #1778 adds mower-specific volume handling while preserving compatibility with existing ECOVACS devices.

## Existing `SetVolume` remains compatible

Historically:

```python
SetVolume(volume)
```

could send only:

```json
{
  "volume": 6
}
```

PR #1778 extends the command with optional:

```text
channel
total
```

rather than requiring them globally.

Conceptually:

```python
SetVolume(
    volume,
    channel=None,
    total=None,
)
```

This allows older device behaviour to continue unchanged.

---

# O1200 system volume

The O1200 hardware profile explicitly uses:

```python
SetVolume(
    volume,
    channel="sys",
    total=10,
)
```

Resulting wire payload:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 6
}
```

The current O1200 implementation therefore assumes the observed mower scale:

```text
total = 10
```

This should be described as:

```text
observed O1200 protocol behaviour
```

rather than a universal ECOVACS volume rule.

---

# Lifted-alarm volume

The mower exposes a separate:

```text
fallVolume
```

value.

Normalised event:

```text
FallVolumeEvent
```

Capability:

```text
settings.fall_volume
```

Setter:

```text
SetFallVolume
```

Wire command:

```text
setVolume
```

Payload:

```json
{
  "type": "fall",
  "total": 10,
  "volume": 6
}
```

The same:

```text
getVolume
onVolume
```

protocol family can report both normal system volume and lifted-alarm volume.

---

# Reading mower volume

A complete mower payload can contain:

```text
total
volume
fallVolume
searchVolume
```

Example shape:

```json
{
  "total": 10,
  "volume": 5,
  "fallVolume": 2,
  "searchVolume": 10
}
```

The development parser exposes:

```text
volume
    → VolumeEvent

fallVolume
    → FallVolumeEvent
```

## `searchVolume`

The payload field:

```text
searchVolume
```

is observed/read in the complete mower volume payload.

It is **not** exposed as its own capability.

Reason documented by PR #1778:

```text
no setter protocol has been observed
```

Therefore current status is:

```text
protocol field observed
read in payload context
no normalised writable capability
```

A future implementation should not invent a setter from similarity with other volume channels.

---

# `onVolume`

Push:

```text
onVolume
```

reuses the same volume parser.

It can update:

```text
VolumeEvent
FallVolumeEvent
```

depending on the payload.

If:

```text
type = "fall"
```

the message is treated as lifted-alarm volume.

If a normal complete mower payload contains:

```text
volume
fallVolume
```

both corresponding events can be emitted.

---

# Move-up warning versus lifted-alarm volume

PR #1778 also registers:

```text
onMoveupWarning
```

through:

```text
OnMoveUpWarning
```

This should be kept conceptually separate from:

```text
fall_volume
```

One represents the mower lifted/move-up warning state.

The other represents the volume level used for the lifted alarm.

Conceptually:

```text
lifted warning state
        ≠
lifted warning volume
```

---

# Push-message family

PR #1778 registers mower push handlers:

```text
onRecognization
onHumanoidAI
onNarrowAdapt
onMoveupWarning
onAnimProtect
onVolume
onRainDelay
onProtectState
```

This is important because settings changed through the ECOVACS app can update the normalised client state without requiring every integration to poll continuously.

---

# Model-specific wiring

The new capabilities are intentionally wired to:

```text
2i0fns
```

only.

This is a deliberate safety boundary.

A command implementation existing in the library does not mean other GOAT hardware profiles should expose it automatically.

Cross-model support requires evidence.

---

# Validation recorded by the PRs

## PR #1776

The PR reports:

```text
20 focused rain/protect-state tests passed
729 tests passed in the broad Windows-compatible suite
11 deselected
Ruff passed
mypy passed
git diff --check passed
```

## PR #1778

The PR reports:

```text
31 targeted pytest tests passed
targeted Ruff passed
targeted mypy passed
git diff --check passed
```

An extended run reported:

```text
359 passed
3 failed
```

The PR attributes those three failures to the existing Windows checkout representation of hardware symlinks as text files, not to the changed mower-setting code.

These numbers describe the validation state of the PR branches at the time of submission.

They are not a substitute for upstream CI/merge status.

---

# Home Assistant implications

These capabilities are not all exposed by the reviewed Home Assistant mower work.

Likely mappings include:

| Capability | Likely HA representation |
| --- | --- |
| `ai_recognition` | switch |
| `humanoid_ai` | switch |
| `narrow_adapt` | switch |
| `animal_protection.enabled` | switch |
| animal start/end | time |
| `rain_delay.enabled` | switch |
| rain delay | number/select |
| `volume` | number |
| `fall_volume` | number |
| protection runtime booleans | binary_sensor |

Structured settings need state-preserving writes.

This applies especially to:

```text
animal protection
rain configuration
```

Do not expose:

```text
searchVolume
```

as a writable entity until a setter protocol is known.

---

# Current assumptions and unresolved items

## Observed O1200 volume scale

Current setter wiring uses:

```text
total = 10
```

This is evidence-backed for the researched O1200 but should not be generalised automatically.

## `searchVolume`

Observed in read payloads.

Setter unknown.

## Animal protection

Configuration structure is known.

Physical behaviour during the configured schedule still needs systematic testing.

## AI controls

Protocol mappings are known.

Exact app labels and interaction between:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
```

remain incomplete.

## Rain runtime

Actual rain protection is observed.

The `isRainDelay=1` lifecycle remains unconfirmed.

## Rain pause/event codes

Numeric event/pause mappings intentionally remain undocumented at the semantic layer until evidence improves.

---

# What PR #1776/#1778 resolves

The following are no longer "unknown protocol command" gaps for the researched O1200:

```text
rain configuration
AI recognition
smart mowing with avoidance
narrow passage adaptation
animal protection configuration
system mower volume shape
lifted-alarm volume
runtime protection-state message
mower settings push updates
```

The remaining work is primarily:

```text
physical/app semantic correlation
Home Assistant representation
cross-model verification
unmapped searchVolume setter
rain lifecycle details
interaction between related avoidance controls
```

---

# Related documentation

- [Settings](settings.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
- [O1200 area parameters](area-parameters.md)
