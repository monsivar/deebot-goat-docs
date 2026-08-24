# GOAT mower settings

This page provides an overview of known ECOVACS GOAT mower settings in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py) and mower-specific settings implemented during GOAT protocol research.

Last reviewed against:

- upstream `DeebotUniverse/client.py` `dev`
- mower development branches
- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)
- [`PR #1776`](https://github.com/DeebotUniverse/client.py/pull/1776)
- [`PR #1778`](https://github.com/DeebotUniverse/client.py/pull/1778)

Date: **2026-08-24**

## Scope

This page distinguishes between:

- settings implemented in reviewed upstream
- mower-specific settings implemented in development branches
- O1200 zone-specific area parameters
- runtime protection state, which is not itself a setting
- values whose protocol is mapped but whose physical/user-facing semantics remain incomplete
- features that remain unmapped

Implementation in Python is not the same as complete physical-device verification.

The combined O1200 global-settings implementation is documented in detail in [O1200 global settings](o1200-global-settings.md).

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

Common patterns include:

```text
CapabilitySetEnable
CapabilitySet
CapabilityNumber
CapabilitySetTypes
```

A typical setting connects:

```text
GET
 │
 ▼
Event
 ▲
 │
SET
```

Some mower settings also receive a corresponding push message.

---

# Common upstream GOAT settings

The five reviewed upstream GOAT hardware profiles expose the following common settings:

| Feature | Capability | Type | Reviewed upstream |
| --- | --- | --- | :---: |
| Advanced mode | `advanced_mode` | boolean | ✓ |
| Border switch | `border_switch` | boolean | ✓ |
| Cutting direction | `cut_direction` | numeric angle | ✓ |
| Child lock | `child_lock` | boolean | ✓ |
| Move-up warning | `moveup_warning` | boolean | ✓ |
| Cross-map border warning | `cross_map_border_warning` | boolean | ✓ |
| Safe protect | `safe_protect` | boolean | ✓ |
| TrueDetect | `true_detect` | boolean | ✓ |
| Volume | `volume` | numeric | ✓ |

The protocol names do not always directly match wording in the ECOVACS application.

Model-specific meaning should therefore be established from app/device correlation where necessary.

---

# O1200 zone-specific area parameters

Development work in:

- [`PR #1767`](https://github.com/DeebotUniverse/client.py/pull/1767)
- [`PR #1768`](https://github.com/DeebotUniverse/client.py/pull/1768)
- [`PR #1776`](https://github.com/DeebotUniverse/client.py/pull/1776)
- [`PR #1778`](https://github.com/DeebotUniverse/client.py/pull/1778)

adds a zone-specific setting capability:

```text
settings.area_parameter
```

for the researched:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

The capability is conceptually:

```python
area_parameter=CapabilitySet(
    AreaParameterEvent,
    [GetAreaParameter()],
    SetAreaParameter,
)
```

Each area record contains:

```text
area_id
mow_height_level
cut_mode
obstacle_height
angle
```

Wire fields:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

Detailed documentation:

**[O1200 area parameters](area-parameters.md)**

Status:

**Fork implemented / Python tested / Protocol observed**

---

# Cutting height

For the researched O1200, cutting height is represented by:

```text
mowHeightLevel
```

normalised as:

```text
mow_height_level
```

inside the zone-specific:

```text
AreaParameter
```

Client status:

**Protocol observed / Fork implemented / Python tested**

The Home Assistant development branch `feature/ecovacs-area-parameter` adds a tested semantic conversion:

```text
3.0–8.0 cm
0.5 cm steps
```

using:

```python
height_cm = (17 - mow_height_level) / 2
```

| `mowHeightLevel` | HA semantic height |
| ---: | ---: |
| 11 | 3.0 cm |
| 10 | 3.5 cm |
| 9 | 4.0 cm |
| 8 | 4.5 cm |
| 7 | 5.0 cm |
| 6 | 5.5 cm |
| 5 | 6.0 cm |
| 4 | 6.5 cm |
| 3 | 7.0 cm |
| 2 | 7.5 cm |
| 1 | 8.0 cm |

HA semantic status:

**Implemented/tested**

Remaining work is now limited to independent physical/app validation of the complete table and cross-model verification.

# Zone-specific cut mode / mowing speed

The O1200 area-parameter protocol contains:

```text
cutMode
```

normalised as:

```text
cut_mode
```

The Home Assistant development branch maps:

```text
7 → Gentle / 0.35 m/s
4 → Efficient / 0.5 m/s
```

and tests both directions.

Therefore the researched O1200 has a **zone mowing-speed semantic mapping through `cutMode`**.

This does not prove a separate standalone speed command exists, and it should not automatically be equated with generic:

```text
efficiency_mode
```

Status:

```text
Protocol observed
Client fork implemented/tested
HA semantic mapping implemented/tested
physical/cross-model validation still useful
```

# Zone-specific obstacle/environment mode

The O1200 area-parameter protocol contains:

```text
obstacleHeight
```

normalised as:

```text
obstacle_height
```

The HA development mapping is:

```text
1 → flat terrain / short grass <10 cm
2 → normal environment <15 cm
3 → high-grass environment <20 cm
```

The mapping is tested both ways.

It remains distinct from:

```text
true_detect
ai_recognition
humanoid_ai
narrow_adapt
animal_protection
```

The remaining uncertainty is primarily the exact physical/app interpretation and cross-model applicability, rather than the absence of a semantic mapping.

# Zone-specific angle

The O1200 area-parameter record contains:

```text
angle
```

associated with a specific:

```text
areaID
```

The HA development conversion is:

```python
user_degrees = (270 - raw_angle) % 360
```

with reverse conversion using the same expression.

Automated helper tests cover several values.

Status:

```text
raw field mapped
HA semantic conversion implemented/tested
```

The unresolved question is the relationship between this per-zone angle and upstream global:

```text
settings.cut_direction
```

—not how to convert the O1200 raw area-angle field itself.

# Complete-tuple write behaviour

`SetAreaParameter` writes:

```text
areaID
mowHeightLevel
cutMode
obstacleHeight
angle
```

together.

Therefore integrations exposing individual controls should preserve the current values of fields that the user is not changing.

Recommended pattern:

```text
AreaParameterEvent
      │
      ▼
find target area
      │
      ▼
copy full tuple
      │
      ▼
change one field
      │
      ▼
SetAreaParameter
      │
      ▼
onAreaParameter confirms state
```

This is an important design constraint for future Home Assistant support.

---

# Advanced mode

Capability:

```text
settings.advanced_mode
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

The exact mower-specific user-facing meaning should be correlated with the app rather than inferred from the name alone.

---

# Border switch

Capability:

```text
settings.border_switch
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

The feature is associated with border/edge behaviour, but exact app wording can vary.

---

# Global cutting direction

Capability:

```text
settings.cut_direction
```

Commands:

```text
GetCutDirection
SetCutDirection
```

Event:

```text
CutDirectionEvent
```

Type:

```text
angle
```

Status:

**Upstream implemented**

Do not confuse this with:

```text
mowHeightLevel
```

and do not yet assume it is identical to the O1200 zone-specific:

```text
AreaParameter.angle
```

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

Status:

**Upstream implemented**

This should not automatically be equated with:

```text
ProtectStateEvent.is_locked
```

without protocol correlation.

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

Development message support also includes:

```text
onMoveupWarning
```

Status:

**Upstream setting / development push refinement**

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

Status:

**Upstream implemented**

Exact mower-facing semantics should remain evidence-based.

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

Status:

**Upstream implemented**

The protocol name is not sufficient to define every physical safety behaviour.

---

# TrueDetect

Capability:

```text
settings.true_detect
```

Commands:

```text
getTrueDetect
setTrueDetect
```

Status:

**Upstream implemented**

All reviewed GOAT hardware profiles expose this setting.

Its precise relationship to newer O1200 AI/avoidance settings remains incompletely mapped.

---

# Development AI and navigation settings

The O1200 development work adds several separate settings.

## AI recognition

Capability:

```text
ai_recognition
```

Commands:

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

Status:

**Fork implemented / Python tested**

## Humanoid AI / smart mowing with avoidance

Capability:

```text
humanoid_ai
```

Commands:

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

Implementation description:

```text
Smart mowing with avoidance
```

Status:

**Fork implemented / Python tested**

## Narrow passage adaptation

Capability:

```text
narrow_adapt
```

Commands:

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

Status:

**Fork implemented / Python tested**

Detailed documentation:

[Obstacle and AI](obstacle-and-ai.md)

---

# Animal protection

Capability:

```text
animal_protection
```

Commands:

```text
getAnimProtect
setAnimProtect
```

Push:

```text
onAnimProtect
```

Configuration contains:

```text
enabled
start
end
```

The time values are normalised to:

```text
HH:MM
```

Status:

**Fork implemented / Python tested / Protocol observed**

## Complete-configuration writes

`SetAnimalProtection` writes the complete configuration:

```text
enable
start
end
```

on every update.

Therefore a higher-level integration changing only one value must preserve the other two current values.

Conceptually:

```text
latest AnimalProtectionEvent
        │
        ▼
replace requested field
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

PR #1778 reports direct observation of toggle writes and confirmation of time updates through pushed state.

This configuration should be kept separate from runtime:

```text
ProtectStateEvent.is_anim_protect
```

Detailed implementation notes:

[O1200 global settings](o1200-global-settings.md)

---

# Rain configuration

Capability:

```text
rain_delay
```

Event:

```text
RainDelayEvent
```

Setter:

```text
setRainDelay
```

Push:

```text
onRainDelay
```

Fields:

```text
enabled
delay
```

Accepted development values:

```text
0–300 minutes
30-minute increments
```

The current O1200 development capability has no explicit refresh GET assigned and relies on the push state.

No undocumented:

```text
getRainDelay
```

command is introduced.

PR #1776 also deliberately avoids assigning meanings to rain-related event code `2052` or rain-specific pause-reason values because their semantics are not sufficiently documented.

Status:

**Fork implemented / Python tested / Protocol observed**

Detailed documentation:

- [Rain and protection](rain-and-protection.md)
- [O1200 global settings](o1200-global-settings.md)

---

# Volume

The common GOAT profiles expose system volume.

PR #1778 extends the shared `getVolume` / `setVolume` family for the O1200 while keeping existing `SetVolume(volume)` behaviour backward compatible.

A complete O1200 mower payload can contain:

```text
total
volume
fallVolume
searchVolume
```

## System volume

Capability:

```text
volume
```

O1200 setter wiring:

```text
type  = sys
total = 10
```

Example:

```json
{
  "type": "sys",
  "total": 10,
  "volume": 6
}
```

The `total=10` value is based on observed O1200 behaviour and should not be treated as a universal ECOVACS volume rule.

Status:

**Upstream capability / O1200 protocol handling refined in PR #1778**

## Lifted-alarm volume

Capability:

```text
fall_volume
```

Event:

```text
FallVolumeEvent
```

Protocol channel/type:

```text
fall
```

Setter:

```text
SetFallVolume
```

Wire command:

```text
setVolume
```

Example:

```json
{
  "type": "fall",
  "total": 10,
  "volume": 6
}
```

Status:

**Fork implemented / Python tested**

## `searchVolume`

The field:

```text
searchVolume
```

has been observed in the complete mower volume payload.

It is not exposed as a separate capability because no setter protocol has been observed.

Status:

**Observed read field / no writable capability**

Detailed documentation:

[O1200 global settings](o1200-global-settings.md)

---

# Runtime protection state is not a setting

Development work adds:

```text
ProtectStateEvent
```

with fields:

```text
is_anim_protect
is_rain_protect
is_rain_delay
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

This is runtime state.

It should not be represented as user-editable switches simply because the values are booleans.

For example:

```text
is_rain_protect
```

describes a reported condition, while:

```text
rain_delay.enabled
```

is configuration.

---

# Settings that still require protocol/semantic research

For the researched O1200, the following are now mapped substantially further than raw-field discovery:

```text
mowHeightLevel
    → 3.0–8.0 cm in 0.5 cm steps (HA semantic mapping)

cutMode
    → 7 Gentle / 0.35 m/s
    → 4 Efficient / 0.5 m/s

obstacleHeight
    → 1 short-grass <10 cm
    → 2 normal <15 cm
    → 3 high-grass <20 cm

AreaParameter.angle
    → user degrees via (270 - raw) % 360
```

Remaining work includes:

```text
independent physical/app validation of these mappings
confirmation of complete valid raw ranges
cross-model applicability
AreaParameter.angle ↔ global cut_direction relationship
whether any separate standalone mowing-speed command exists
```

Other important gaps include scheduling and additional global mower behaviour not yet represented by known capabilities.

# Model scope

The newly researched area-parameter and AI/rain settings are currently O1200-focused.

Do not assume another GOAT supports them because:

```text
the product name is similar
```

or:

```text
the app exposes a similar-looking option
```

Enable model capabilities from evidence.

---

# Integration guidance

Suggested high-level entity shapes are:

| Capability/value | Likely integration representation |
| --- | --- |
| boolean `CapabilitySetEnable` | switch |
| simple numeric setting | number |
| known enum | select |
| runtime boolean state | binary_sensor |
| measurement | sensor |
| scheduled time | time |
| zone parameter tuple | action/service or carefully modelled per-zone controls |

The O1200 area-parameter tuple should **not** be split into independent writable entities unless the implementation preserves unchanged sibling values when writing.

---

# Current status summary

| Feature | Current status |
| --- | --- |
| Common GOAT settings | Upstream implemented |
| Global cutting direction | Upstream implemented |
| O1200 `area_parameter` | Fork implemented / tested |
| O1200 `mowHeightLevel` | Protocol mapped / fork implemented |
| O1200 `cutMode` | Protocol mapped / fork implemented |
| O1200 `obstacleHeight` | Protocol mapped / fork implemented |
| O1200 area `angle` | Protocol mapped / fork implemented |
| Physical cutting-height mapping | Incomplete |
| `cutMode` enum semantics | Incomplete |
| `obstacleHeight` semantics/unit | Incomplete |
| Mowing speed | Not mapped |
| AI recognition | Fork implemented |
| Humanoid AI | Fork implemented |
| Narrow adaptation | Fork implemented |
| Animal protection | Fork implemented |
| Rain configuration | Fork implemented |
| Lifted-alarm volume | Fork implemented |
| Runtime protection state | Fork implemented, not a setting |

---

# Related documentation

- [O1200 area parameters](area-parameters.md)
- [O1200 global settings](o1200-global-settings.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Zones and areas](zones-and-areas.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
