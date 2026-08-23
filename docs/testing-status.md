# GOAT testing status

This page tracks implementation, automated-test, protocol-observation and physical-device verification status for ECOVACS GOAT mower functionality documented in this repository.

Last reviewed against:

- upstream `DeebotUniverse/client.py` `dev`
- `feature/mower-stats-progress`
- `feature/ecovacs-mower-settings`
- `feature/ecovacs-mower-rain-settings`
- Home Assistant branch `feature/ecovacs-mower-progress`
- GOAT protocol observations and physical-device tests from this research project

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
Automated client tests
        │
        ▼
Hardware capability enabled
        │
        ▼
Physical mower behaviour verified
        │
        ▼
Home Assistant integration
        │
        ▼
Home Assistant tests
```

These levels should not be treated as equivalent.

---

# Status definitions

| Status | Meaning |
| --- | --- |
| **Upstream** | Implemented in reviewed upstream `DeebotUniverse/client.py` |
| **Fork** | Implemented in a development branch but not reviewed upstream |
| **Python tested** | Covered by automated `deebot_client` tests |
| **Protocol observed** | Relevant data/command observed in real GOAT communication |
| **Device tested** | Physical mower behaviour exercised and correlated |
| **App observed** | Behaviour/value confirmed in the official ECOVACS app |
| **HA implemented** | Implemented in the Home Assistant development branch |
| **HA tested** | Covered by Home Assistant automated tests |
| **Derived** | Calculated from other fields rather than directly supplied |
| **Unverified** | Interpretation or physical effect remains uncertain |
| **Not mapped** | No confirmed protocol/client implementation yet |

---

# Important distinction

An automated client test proves that:

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
behaves as assumed
```

Likewise, a Home Assistant test can prove that an event is exposed correctly as an entity without proving that the underlying ECOVACS protocol interpretation applies to every mower model.

---

# Overall status matrix

| Feature | Upstream | Fork | Python tested | Protocol observed | Device/app tested | HA status | Current confidence |
| --- | :---: | :---: | :---: | :---: | :---: | --- | --- |
| Device identified as mower | ✓ | — | ✓ | — | ✓ | Implemented | High |
| Battery | ✓ | — | ✓ | ✓ | ✓ | Implemented | High |
| Return to dock | ✓ | — | ✓ | ✓ | ✓ | Implemented/tested | High |
| Start mowing | ✓ | — | ✓ | ✓ | ✓ | Implemented/tested | High |
| Pause mowing | ✓ | — | ✓ | ✓ | ✓ | Implemented/tested | High |
| Resume mowing | ✓ | — | ✓ | ✓ | ✓ | Via state-aware START path | High |
| Stop mowing | ✓ | — | ✓ | ✓ | ✓ | Not exposed as lawn_mower feature | High client confidence |
| Selected-zone mowing | Partial | — | Generic tests | ✓ behaviour | ✓ | Not exposed | Medium |
| O1200 area capability | — | — | — | Behaviour confirmed | ✓ | Not exposed | Open implementation gap |
| Current mower state | ✓ | — | ✓ | ✓ | ✓ | Implemented/tested | High |
| Common statistics | ✓ | — | ✓ | ✓ | ✓ | Implemented | High |
| `mowedArea` | — | ✓ | ✓ | ✓ | ✓ protocol/app | Implemented for progress path | High for O1200 field |
| `mowing_job_progress` flag | — | ✓ | ✓ via integration use | — | — | Implemented/tested | High implementation confidence |
| Current area mowed | — | ✓ raw field | ✓ | ✓ | ✓ | Implemented/tested | High for O1200 path |
| Mowing progress percentage | — | — | — | Derived | — | Implemented/tested | High as derived O1200 value |
| `StatsEvent.time` as estimated duration | — | Model semantic flag | — | Source semantics partly unresolved | App estimate observed | Implemented/tested | Medium/High for current O1200 integration |
| Separate explicit ETA field | — | — | — | Not identified | App value observed | — | Not mapped |
| Border switch | ✓ | — | existing tests | project evidence | project-tested | Generic switch architecture | Medium/High |
| Cutting direction | ✓ | — | existing tests | — | not systematic | Number architecture | Medium |
| Child lock | ✓ | — | existing tests | — | not systematic | Generic switch architecture | Medium |
| Move-up warning | ✓ | message refinement | existing tests | push mapped | not systematic | Generic switch architecture | Medium |
| Cross-map border warning | ✓ | — | existing tests | — | not systematic | Generic switch architecture | Medium |
| Safe protect | ✓ | — | existing tests | — | semantics incomplete | Generic switch architecture | Medium |
| TrueDetect | ✓ | — | existing tests | — | physical effect not mapped | Generic switch architecture | Medium |
| System volume | ✓ | refined | ✓ | ✓ | not systematic | Number architecture | High implementation confidence |
| Lifted-alarm volume | — | ✓ | ✓ | ✓ | physical effect not systematic | Not yet exposed | Medium/High |
| Rain configuration | — | ✓ | ✓ | ✓ | ✓ | Not yet exposed | High for O1200 |
| Active rain protection | — | ✓ | ✓ | ✓ | ✓ real rain | Not yet exposed | High for observed state |
| Post-rain delay runtime state | — | ✓ | parser tested | partial | not fully observed | Not yet exposed | Low/Medium |
| AI recognition | — | ✓ | ✓ | captured/mapped | physical effect not mapped | Not yet exposed | Medium |
| Humanoid AI / smart avoidance | — | ✓ | ✓ | captured/mapped | physical effect not mapped | Not yet exposed | Medium |
| Narrow passage adaptation | — | ✓ | ✓ | captured/mapped | physical effect not mapped | Not yet exposed | Medium |
| Animal protection configuration | — | ✓ | ✓ | captured/mapped | physical effect incomplete | Not yet exposed | Medium |
| Animal protection runtime flag | — | ✓ | ✓ | ✓ | transitions incomplete | Not yet exposed | Medium |
| Emergency-stop flag | — | ✓ | ✓ | field mapped | behaviour not mapped | Not yet exposed | Low/Medium |
| Locked-state flag | — | ✓ | ✓ | field mapped | child-lock relation unknown | Not yet exposed | Low/Medium |
| PIN-code flag | — | ✓ | ✓ | field mapped | semantics unknown | Not yet exposed | Low |
| Cutting height | — | — | — | — | app/model feature requires mapping | — | Not mapped |
| GOAT mowing efficiency/mode | — | — | — | — | requires mapping | — | Not mapped |
| Mowing speed | — | — | — | — | requires mapping | — | Not mapped |
| Scheduling | Partial generic ecosystem only | — | — | GOAT mapping incomplete | App feature area | — | Not mapped for GOAT |
| GOAT map semantics | Partial generic client map support | separate research | — | incomplete | app/device mapping exists | separate work | Incomplete |

---

# Basic mowing control

The basic mowing lifecycle currently has the strongest end-to-end evidence.

The sequence exercised on a physical GOAT while protocol behaviour was observed includes:

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

Return to the charging station was also exercised separately:

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

**Upstream / Python tested / Protocol observed / Device tested**

Confidence:

**High**

---

# Start/resume state handling

The shared client automatically handles START/RESUME mismatches.

Conceptually:

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

This is covered by client tests.

The Home Assistant mower entity can therefore use its start action without needing a separate user-facing resume feature.

---

# Home Assistant mower entity

The development Home Assistant integration exposes mower devices using:

```text
lawn_mower
```

and currently supports:

```text
START_MOWING
PAUSE
DOCK
```

Automated tests verify that these call:

```text
CleanV2(CleanAction.START)
CleanV2(CleanAction.PAUSE)
Charge()
```

respectively.

The state mapping includes:

```text
State.CLEANING → MOWING
State.RETURNING → RETURNING
State.DOCKED → DOCKED
State.ERROR → ERROR
State.PAUSED → PAUSED
State.IDLE → PAUSED
```

The `IDLE → PAUSED` mapping is an integration compromise, not a physical mower semantic claim.

---

# Stop mowing in Home Assistant

The client supports:

```text
CleanAction.STOP
```

and physical stop behaviour has been observed.

The reviewed Home Assistant mower entity does not expose a corresponding stop feature.

Therefore:

```text
client STOP support
       │
       ▼
Home Assistant integration gap
```

Status:

**Client supported / Device tested / HA not exposed**

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

The generic upstream client implements and tests:

```text
CleanAreaV2
```

for:

```text
spotArea
customArea
freeClean
```

However, the exact GOAT zone-ID relationship is not fully established.

Status:

**Generic upstream implementation / Generic Python tests / GOAT behaviour observed**

Confidence:

**Medium**

---

# O1200 selected-zone implementation gap

The reviewed upstream O1200 hardware profile does not expose:

```text
CapabilityCleanAction.area
```

despite the physical mower/app supporting selected-zone mowing.

Current state:

```text
Physical capability exists
        │
        ▼
exact O1200 protocol mapping still needs confirmation
        │
        ▼
client hardware capability missing
```

Status:

**Known implementation/research gap**

---

# Common mowing statistics

Upstream already implements:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
GetStats
GetTotalStats
```

and all reviewed GOAT hardware profiles expose the common statistics capability.

Status:

**Upstream / Python tested**

Confidence:

**High for the architecture**

Optional mower-specific fields and semantics still require model evidence.

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

from ECOVACS:

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

**Fork / Python tested / Protocol observed**

Strongest current model evidence:

```text
GOAT O1200
```

Confidence:

**High for the raw field**

---

# O1200 mowing progress percentage

No dedicated:

```text
progress_percent
```

field is added to `deebot_client`.

The Home Assistant development branch derives:

```text
mowed_area / area * 100
```

when the hardware profile declares:

```text
mowing_job_progress=True
```

The calculation is covered by automated Home Assistant tests, including missing/zero-value cases.

Status:

**Derived / HA implemented / HA tested**

This corrects an earlier project-documentation state where the percentage was described only as a possible future integration calculation.

---

# O1200 estimated mowing duration

The official ECOVACS app displays an estimated duration for a mowing job.

The current Home Assistant progress development interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

when:

```text
mowing_job_progress=True
```

The sensor is configured as a duration value with native seconds and suggested display in minutes.

Automated Home Assistant tests verify this representation.

Status:

**HA implemented / HA tested / App observed**

Important limitation:

The project has **not** identified a separate explicit ECOVACS protocol field named ETA/remaining-time/estimated-duration.

Therefore this should be described as:

> a model-specific interpretation of the existing statistics field used by the O1200 progress integration

rather than:

> a universal ECOVACS ETA field

Confidence:

**Medium/High for the current O1200 integration semantics; unresolved as a universal protocol rule**

---

# O1200 progress units

The Home Assistant progress path currently uses:

```text
area / mowed_area → square centimetres
time              → seconds
```

and converts them for display.

Automated tests verify examples including:

```text
28699 → 2.8699 m²
2304 s → 38.4 min
```

Status:

**HA implemented / HA tested**

These should remain model/path-specific until cross-model verification is available.

---

# Separate explicit ETA field

No dedicated normalised client field has been identified such as:

```text
eta
estimated_remaining_time
estimated_duration
```

Status:

**Not mapped**

This remains a separate research question from the existing O1200 `StatsEvent.time` interpretation.

---

# Rain configuration

The mower development work implements:

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

Status:

**Fork / Python tested / Protocol observed / Device tested**

Strongest current model evidence:

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

and the observation is represented in test fixtures.

Status:

**Fork / Python tested / Protocol observed during real rain**

Confidence:

**High for `isRainProtect` in the observed state**

---

# `isRainDelay`

Parsing and boolean conversion for:

```text
isRainDelay
```

are implemented and tested.

However, the physical condition represented by:

```text
isRainDelay = 1
```

has not yet been conclusively correlated.

A likely hypothesis is:

```text
post-rain waiting period
```

but this remains unconfirmed.

Status:

**Parser tested / semantics partially unverified**

Confidence:

**Low/Medium**

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

Automated tests verify enabled and disabled values.

Status:

**Fork / Python tested**

Exact app wording and physical effect remain open.

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

Implementation description:

```text
Smart mowing with avoidance
```

Status:

**Fork / Python tested**

Do not infer that this setting only concerns human detection from the wire name alone.

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

Normalised event:

```text
NarrowAdaptEvent
```

Field:

```text
state
```

Status:

**Fork / Python tested**

Physical navigation effect still needs systematic A/B testing.

Confidence:

**Medium**

---

# Animal protection

Configuration is represented by:

```text
AnimalProtectionEvent
```

with:

```text
enabled
start
end
```

and commands/messages:

```text
getAnimProtect
setAnimProtect
onAnimProtect
```

The development tests verify time normalisation and configuration parsing.

Runtime state is separately represented through:

```text
ProtectStateEvent.is_anim_protect
```

Status:

**Fork / Python tested / Protocol mapped**

Physical schedule transitions and behaviour remain incomplete.

Confidence:

**Medium**

---

# Other protection-state flags

Mapped fields include:

```text
isEStop
isLocked
isPinCode
isPrepareDataSuccess
```

Their Python forms are:

```text
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

Parsing is implemented.

However:

- `is_locked` is not proven to be identical to child lock
- `is_pin_code` semantics remain unresolved
- `is_prepare_data_success` has no established normal user-facing meaning
- emergency-stop transitions should be directly correlated before strong UI wording is used

Confidence:

**Low to Medium depending on field**

---

# TrueDetect

TrueDetect is implemented in reviewed upstream profiles.

Status:

**Upstream implemented**

The exact GOAT app label and physical relationship to other AI/avoidance settings are not fully mapped.

Confidence:

**High implementation confidence / Medium semantic confidence**

---

# Volume

System volume is supported upstream.

Development work also adds a separate lifted-alarm/fall volume interpretation using the same protocol command family.

Status:

```text
System volume:
Upstream

Lifted-alarm volume:
Fork / Python tested
```

The physical effect of the latter has not been systematically documented.

---

# Not-yet-mapped mower settings

The following remain important protocol-research targets:

```text
cutting height
GOAT mowing efficiency/mode
mowing speed
```

Status:

**Not mapped**

No speculative Home Assistant entities should be created until their protocol semantics and valid values are established.

---

# Firmware context

Mower behaviour can differ across firmware versions.

Some O1200 development fixtures use firmware context including:

```text
1.13.10
```

This should not be interpreted as a universal minimum/maximum or compatibility guarantee.

Observations should record firmware whenever practical.

---

# Confidence scale

## High

Strong agreement between implementation, tests and/or physical observation.

## Medium

Implementation and protocol interpretation are plausible and tested at the software level, but physical semantics are incomplete.

## Low

Field exists or parser is implemented, but the user-facing meaning remains unresolved.

---

# Strongest current areas

The strongest current project evidence is for:

- mower identification
- start/pause/resume/stop lifecycle
- return to dock
- common state handling
- common statistics architecture
- O1200 `mowedArea`
- O1200 model-gated progress calculation in Home Assistant
- O1200 model-gated estimated-duration presentation in Home Assistant
- O1200 rain configuration
- active rain-protection observation

---

# Highest-priority remaining research

Recommended priorities:

1. cutting height
2. mowing mode / efficiency
3. mowing speed
4. exact O1200 zone-ID command
5. cross-model progress-statistics verification
6. behaviour of `StatsEvent.time` throughout an active job
7. exact AI app-setting mapping
8. post-rain delay lifecycle
9. animal-protection runtime behaviour
10. zone names and metadata
11. scheduling
12. GOAT map semantics

---

# Related documentation

- [Overview](overview.md)
- [Supported models](supported-models.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Known limitations](known-limitations.md)
- [Protocol observations](../research/protocol-observations.md)
