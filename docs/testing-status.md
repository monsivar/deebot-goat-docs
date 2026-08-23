# GOAT testing status

This page tracks the implementation and verification status of ECOVACS GOAT mower functionality documented in this repository.

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* `feature/mower-stats-progress`
* `feature/ecovacs-mower-settings`
* GOAT protocol observations and physical-device tests from this research project

Date: **2026-08-23**

## Purpose

A feature can exist at several different levels of confidence.

For example:

```text
Protocol field observed
        │
        ▼
Python implementation
        │
        ▼
Automated parser/command tests
        │
        ▼
Hardware capability enabled
        │
        ▼
Physical mower behaviour verified
        │
        ▼
Integration behaviour verified
```

These levels should not be treated as equivalent.

This page therefore records them separately.

---

# Status definitions

| Status                | Meaning                                                       |
| --------------------- | ------------------------------------------------------------- |
| **Upstream**          | Implemented in current upstream `DeebotUniverse/client.py`    |
| **Fork**              | Implemented in a development branch but not reviewed upstream |
| **Python tested**     | Covered by automated client tests                             |
| **Protocol observed** | Relevant data or command was seen in real GOAT communication  |
| **Device tested**     | Physical mower behaviour was exercised and correlated         |
| **App observed**      | Behaviour or value was confirmed in the ECOVACS app           |
| **Unverified**        | Interpretation or physical effect remains uncertain           |
| **Not mapped**        | No confirmed client/protocol implementation yet               |

---

# Important distinction

An automated Python test proves that:

```text
given payload
    │
    ▼
parser/command
    │
    ▼
expected Python result
```

works as intended.

It does **not** automatically prove:

```text
physical mower
    │
    ▼
actually behaves as assumed
```

Likewise, observing an app option does not automatically identify its ECOVACS wire command.

This distinction is especially important for AI, obstacle and protection settings.

---

# Overall status matrix

| Feature                         | Upstream |   Fork  |  Python tested |             Protocol observed             |               Device/app tested               | Current confidence             |
| ------------------------------- | :------: | :-----: | :------------: | :---------------------------------------: | :-------------------------------------------: | ------------------------------ |
| Device identified as mower      |     ✓    |    —    |        ✓       |                     —                     |                       ✓                       | High                           |
| Battery                         |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Return to dock                  |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Start mowing                    |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Pause mowing                    |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Resume mowing                   |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Stop mowing                     |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Selected-zone mowing            |  Partial |    —    |    ✓ generic   |                     ✓                     |                       ✓                       | Medium                         |
| O1200 area capability           |     —    |    —    |        —       |                ✓ behaviour                |                       ✓                       | Open implementation gap        |
| Current mower state             |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| Statistics                      |     ✓    |    —    |        ✓       |                     ✓                     |                       ✓                       | High                           |
| `mowedArea` progress data       |     —    |    ✓    |        ✓       |                     ✓                     |                 ✓ protocol/app                | High for O1200 data field      |
| Calculated mowing percentage    |     —    |    —    |        —       |                 derivable                 |                       —                       | Derived, not implemented       |
| App estimated duration          |     —    |    —    |        —       |                 Unresolved                |                       ✓                       | App observed only              |
| Border switch                   |     ✓    |    —    | existing tests |                     —                     |                 project-tested                | Medium/High                    |
| Cutting direction               |     ✓    |    —    | existing tests |                     —                     |         not systematically documented         | Medium                         |
| Child lock                      |     ✓    |    —    | existing tests |                     —                     |         not systematically documented         | Medium                         |
| Move-up warning                 |     ✓    |    —    | existing tests |           ✓ push support in fork          |         not systematically documented         | Medium                         |
| Cross-map border warning        |     ✓    |    —    | existing tests |                     —                     |         not systematically documented         | Medium                         |
| Safe protect                    |     ✓    |    —    | existing tests |                     —                     |              semantics incomplete             | Medium                         |
| TrueDetect                      |     ✓    |    —    | existing tests |                     —                     |           physical effect not mapped          | Medium                         |
| System volume                   |     ✓    | refined |        ✓       |                     ✓                     |         not systematically documented         | High implementation confidence |
| Lifted-alarm volume             |     —    |    ✓    |        ✓       |                     ✓                     | physical effect not systematically documented | Medium/High                    |
| Rain configuration              |     —    |    ✓    |        ✓       |                     ✓                     |                       ✓                       | High for O1200                 |
| Active rain protection          |     —    |    ✓    |        ✓       |                     ✓                     |                       ✓                       | High for observed state        |
| Post-rain delay runtime state   |     —    |    ✓    |  parser tested |                  partial                  |               not fully observed              | Low/Medium                     |
| AI recognition                  |     —    |    ✓    |        ✓       | implementation based on captured protocol |           physical effect not mapped          | Medium                         |
| Humanoid AI / smart avoidance   |     —    |    ✓    |        ✓       | implementation based on captured protocol |           physical effect not mapped          | Medium                         |
| Narrow passage adaptation       |     —    |    ✓    |        ✓       | implementation based on captured protocol |           physical effect not mapped          | Medium                         |
| Animal protection configuration |     —    |    ✓    |        ✓       | implementation based on captured protocol |        physical effect not fully mapped       | Medium                         |
| Animal protection runtime flag  |     —    |    ✓    |        ✓       |                     ✓                     |          transition not fully tested          | Medium                         |
| Emergency-stop flag             |     —    |    ✓    |        ✓       |           field observed/mapped           |              behaviour not mapped             | Low/Medium                     |
| Locked-state flag               |     —    |    ✓    |        ✓       |           field observed/mapped           |       relationship to child lock unknown      | Low/Medium                     |
| PIN-code flag                   |     —    |    ✓    |        ✓       |           field observed/mapped           |               semantics unknown               | Low                            |
| Cutting height                  |     —    |    —    |        —       |                     —                     |       app/model feature requires mapping      | Not mapped                     |
| GOAT mowing efficiency/mode     |     —    |    —    |        —       |                     —                     |                requires mapping               | Not mapped                     |
| Mowing speed                    |     —    |    —    |        —       |                     —                     |                requires mapping               | Not mapped                     |
| Explicit protocol ETA           |     —    |    —    |        —       |               not identified              |               app value observed              | Not mapped                     |

---

# Basic mowing control

The basic mowing lifecycle currently has the strongest end-to-end evidence.

The following sequence has been exercised on a physical GOAT while protocol behaviour was observed:

```text
START
  │
  ▼
MOWING
  │
  ▼
PAUSE
  │
  ▼
PAUSED
  │
  ▼
RESUME
  │
  ▼
MOWING
  │
  ▼
STOP
```

Return to charging station was also tested separately:

```text
RETURN TO DOCK
       │
       ▼
RETURNING
       │
       ▼
DOCKED
```

Relevant upstream implementations include:

```text
CleanV2
GetCleanInfoV2
Charge
GetChargeState
```

Status:

**Upstream implemented / Python tested / protocol observed / device tested**

Confidence:

**High**

---

# Start/resume state handling

The shared client automatically handles some START/RESUME mismatches.

Examples:

```text
START requested while PAUSED
        │
        ▼
RESUME sent
```

and:

```text
RESUME requested while not PAUSED
        │
        ▼
START sent
```

This behaviour is covered by upstream automated tests.

Status:

**Upstream / Python tested**

---

# Selected-zone mowing

A defined GOAT lawn zone has been selected and mowed independently through the ECOVACS app during protocol investigation.

The physical lifecycle:

```text
select zone
    │
    ▼
start
    │
    ▼
pause
    │
    ▼
resume
    │
    ▼
stop
```

was observed.

The generic upstream client also implements and tests:

```text
CleanAreaV2
```

for:

```text
spotArea
customArea
freeClean
```

However, the exact mapping between GOAT zone IDs and the generic modes is not yet fully established.

Status:

**Generic upstream implementation / upstream Python tests / GOAT device behaviour observed**

Confidence:

**Medium**

---

# O1200 selected-zone implementation gap

The reviewed upstream O1200 hardware profile does not currently expose:

```text
CleanAreaV2
```

through:

```text
CapabilityCleanAction.area
```

despite selected-zone mowing being available on the physical mower/app.

This should currently be tracked as:

```text
Physical capability exists
        │
        ▼
protocol mapping needs confirmation
        │
        ▼
deebot_client hardware capability missing
```

Status:

**Known implementation/research gap**

---

# Current mowing statistics

Upstream already implements:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
GetStats
GetTotalStats
```

and GOAT hardware profiles expose the common statistics capability.

Status:

**Upstream / Python tested / device-protocol relevant**

Confidence:

**High**

---

# `mowedArea`

The development branch:

```text
feature/mower-stats-progress
```

adds:

```text
StatsEvent.mowed_area
```

from ECOVACS field:

```text
mowedArea
```

Parsing is implemented for:

```text
getStats
onStats
```

and covered by automated tests.

Status:

**Fork / Python tested / protocol observed**

Current strongest model evidence:

```text
GOAT O1200
```

Confidence:

**High for the raw field**

---

# Mowing progress percentage

No dedicated:

```text
progress_percent
```

field has been added to `deebot_client`.

A percentage may potentially be derived from:

```text
mowed_area / area
```

if the two values are confirmed to represent completed and total target area in matching units.

Status:

**Derived concept**

Confidence:

**Requires semantic/unit verification before integration exposure**

---

# Estimated mowing duration

The ECOVACS app displays an estimated duration when a mowing job is started.

This has been observed at the application level.

A corresponding explicit protocol field has not yet been identified in the current implementation.

The progress branch does not add an ETA field.

Status:

**App observed / protocol source unresolved / not implemented**

This should remain separate from:

```text
StatsEvent.time
```

until the exact semantics are established.

---

# Rain configuration

The mower development branch implements:

```text
SetRainDelay
RainDelayEvent
OnRainDelay
```

with:

```text
enabled
delay
```

The accepted delay range is:

```text
0–300 minutes
```

in:

```text
30-minute increments
```

Automated tests cover accepted and rejected values.

Protocol configuration has also been correlated during GOAT research.

Status:

**Fork / Python tested / protocol observed / device tested**

Current strongest model evidence:

```text
GOAT O1200
```

Confidence:

**High**

---

# Active rain protection

A real-rain observation produced:

```text
isRainProtect = 1
isRainDelay   = 0
```

through:

```text
onProtectState
```

The development branch preserves this in:

```text
ProtectStateEvent
```

and the actual-rain example is represented in automated test coverage.

Status:

**Fork / Python tested / protocol observed during real rain**

Confidence:

**High for `isRainProtect` active-rain interpretation**

---

# `isRainDelay`

The parser and boolean conversion for:

```text
isRainDelay
```

are implemented and tested.

However, the physical transition represented by:

```text
isRainDelay = 1
```

has not yet been conclusively correlated.

A likely hypothesis is:

```text
post-rain waiting period
```

but it should remain unconfirmed until directly observed.

Status:

**Parser tested / semantics partially unverified**

Confidence:

**Low to medium**

---

# AI recognition

Development implementation:

```text
getRecognization
setRecognization
onRecognization
```

Normalised event:

```text
AiRecognitionEvent
```

Field:

```text
state
```

Automated tests verify both:

```text
state = 0
state = 1
```

Status:

**Fork / Python tested**

The exact physical effect and ECOVACS app label still require systematic mapping.

Confidence:

**Medium**

---

# Humanoid AI / smart mowing with avoidance

Development implementation:

```text
getHumanoidAI
setHumanoidAI
onHumanoidAI
```

Normalised event:

```text
HumanoidAiEvent
```

Field:

```text
enable
```

The implementation describes this feature as:

```text
Smart mowing with avoidance
```

Automated tests verify enabled/disabled parsing and commands.

Status:

**Fork / Python tested**

Physical behavioural effect:

**Not yet systematically verified**

Confidence:

**Medium**

---

# Narrow passage adaptation

Development implementation:

```text
getNarrowAdapt
setNarrowAdapt
onNarrowAdapt
```

Event:

```text
NarrowAdaptEvent
```

Field:

```text
state
```

Automated tests cover both states.

Status:

**Fork / Python tested**

Still requiring physical verification:

```text
minimum passage width
route-planning effect
mowing behaviour inside passages
clearance changes
```

Confidence:

**Medium**

---

# Animal protection

The development implementation supports:

```text
getAnimProtect
setAnimProtect
onAnimProtect
```

Configuration:

```text
enabled
start
end
```

Automated tests verify both parsing and time normalisation.

Example:

```text
6:30
```

is normalised to:

```text
06:30
```

Status:

**Fork / Python tested**

The runtime protection message also contains:

```text
isAnimProtect
```

but the exact physical relationship between the schedule and runtime flag remains to be fully verified.

Confidence:

**Medium**

---

# Protection-state flags

`ProtectStateEvent` currently contains:

```text
is_anim_protect
is_rain_protect
is_rain_delay
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

All fields are parsed as booleans and automated tests cover conversion.

However, confidence differs per field.

| Field                     | Parser confidence | Semantic confidence           |
| ------------------------- | ----------------- | ----------------------------- |
| `is_rain_protect`         | High              | High for observed active rain |
| `is_rain_delay`           | High              | Low/Medium                    |
| `is_anim_protect`         | High              | Medium                        |
| `is_e_stop`               | High              | Low/Medium                    |
| `is_locked`               | High              | Low                           |
| `is_pin_code`             | High              | Low                           |
| `is_prepare_data_success` | High              | Low                           |

This is a good example of why:

```text
parser confidence
```

and:

```text
semantic confidence
```

should be tracked independently.

---

# TrueDetect

`TrueDetect` is already implemented upstream through:

```text
GetTrueDetect
SetTrueDetect
TrueDetectEvent
```

and exposed by reviewed GOAT profiles.

Implementation confidence:

**High**

GOAT-specific physical interpretation:

**Not yet systematically mapped**

The existence of the setting should therefore not be confused with complete knowledge of its real-world avoidance effect.

---

# Border/edge behaviour

Upstream exposes:

```text
BorderSwitchEvent
GetBorderSwitch
SetBorderSwitch
```

and border/edge behaviour has been part of the GOAT investigation.

Status:

**Upstream implemented**

Physical/app correlation has been investigated in the project, but model-specific behaviour should continue to be documented separately where necessary.

Confidence:

**Medium to high**

---

# Volume channels

Normal system volume is already supported upstream.

The mower development branch additionally distinguishes:

```text
system volume
```

from:

```text
lifted/fall alarm volume
```

through the same ECOVACS:

```text
getVolume
setVolume
```

protocol family.

Automated tests cover the mower-specific parsing and payloads.

Status:

**Upstream + fork refinement / Python tested**

Confidence:

**High implementation confidence**

---

# Not-yet-mapped settings

The following remain explicit research targets.

## Cutting height

Status:

**Not mapped**

Needed evidence:

```text
wire command
valid values
unit
GET response
SET payload
model support
physical change
```

---

## Mowing efficiency / mode

Status:

**Not mapped for GOAT**

The existence of a generic:

```text
efficiency_mode
```

capability elsewhere in `deebot_client` is not sufficient evidence that GOAT uses the same protocol.

---

## Mowing speed

Status:

**Not mapped**

Needed evidence includes:

```text
ECOVACS app options
wire command
value mapping
model support
physical speed difference
```

---

## Explicit ETA

Status:

**App observed / protocol not mapped**

The goal is to determine whether ECOVACS supplies:

```text
estimated duration
```

or whether the app calculates it from other data.

---

# Automated-test coverage summary

The mower development work includes dedicated tests for areas such as:

```text
mower settings commands
mower setting push messages
hardware capability wiring
animal protection
rain delay
protection state
volume channels
mowing statistics progress
```

This is important because newly mapped features are not merely registered in a hardware profile; their payload parsing and capability wiring are also exercised.

---

# Physical-device evidence rules

Use:

```text
Device tested
```

only when actual mower behaviour was exercised.

Use:

```text
Protocol observed
```

when a real mower/app communication payload was captured but the physical effect was not necessarily tested.

Use:

```text
Python tested
```

for unit/integration tests using fixtures or constructed payloads.

Examples:

```text
SetRainDelay rejects 15 minutes
    → Python tested

isRainProtect = 1 during actual rain
    → Protocol/device observed

HumanoidAI parser accepts enable = 1
    → Python tested

HumanoidAI changes physical avoidance distance
    → not yet verified
```

---

# Firmware context

Where possible, physical/protocol testing should record mower firmware.

Some current mower-related test fixtures use:

```text
1.13.10
```

as their firmware header.

This does not guarantee identical behaviour across:

```text
older firmware
newer firmware
other GOAT models
other regions
```

Future protocol observations should therefore include firmware context.

---

# Suggested confidence scale

For future documentation updates, the following scale can be useful.

## High confidence

Requires strong evidence such as:

```text
implemented
+
automatically tested
+
protocol/device correlation
```

or a mature upstream feature with established behaviour.

## Medium confidence

Typical when:

```text
protocol mapped
+
implementation tested
```

but the exact physical meaning is not fully understood.

## Low confidence

Typical when:

```text
field exists
```

but semantic meaning is inferred mainly from its name.

## Unknown

No reliable protocol mapping yet.

---

# Current strongest verified areas

The best-understood GOAT areas currently include:

```text
basic mowing lifecycle
return to dock
mower state
statistics framework
O1200 mowedArea field
rain configuration
active-rain protection state
```

These have multiple independent forms of evidence.

---

# Current priority research gaps

The most valuable remaining verification work includes:

```text
cutting height
mowing efficiency/mode
mowing speed
exact AI/app-setting mapping
physical effects of each AI setting
post-rain delay transition
animal-protection runtime behaviour
explicit ETA source
O1200 zone command
zone-name retrieval
multi-zone ordering
```

Filling these gaps should generally require new controlled protocol captures rather than assumptions based on field names.

---

# Relevant tests

## Upstream

* [`tests/commands/json/test_clean.py`](https://github.com/DeebotUniverse/client.py/blob/dev/tests/commands/json/test_clean.py)

## Mower settings branch

* [`tests/commands/json/test_mower_settings.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/commands/json/test_mower_settings.py)
* [`tests/commands/json/test_rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/commands/json/test_rain_delay.py)
* [`tests/commands/json/test_volume.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/commands/json/test_volume.py)
* [`tests/messages/json/test_mower_settings.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/messages/json/test_mower_settings.py)
* [`tests/messages/json/test_protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/messages/json/test_protect_state.py)
* [`tests/messages/json/test_rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/messages/json/test_rain_delay.py)
* [`tests/hardware/test_mower_settings.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/hardware/test_mower_settings.py)
* [`tests/hardware/test_protect_state.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/hardware/test_protect_state.py)
* [`tests/hardware/test_rain_delay.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/tests/hardware/test_rain_delay.py)

## Progress branch

* [`tests/commands/json/test_stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/tests/commands/json/test_stats.py)
* [`tests/messages/json/test_stats.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/tests/messages/json/test_stats.py)

---

# Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mowing control](mowing-control.md)
* [Zone and area mowing](zones-and-areas.md)
* [Mowing progress and statistics](progress-and-statistics.md)
* [Mower settings](settings.md)
* [Rain and protection](rain-and-protection.md)
* [Obstacle avoidance and AI](obstacle-and-ai.md)
* [Protocol reference](protocol-reference.md)
* Known limitations *(next/planned)*
* Home Assistant integration *(planned)*
