# Known limitations

This page documents current limitations, implementation gaps and unresolved areas in ECOVACS GOAT mower support.

Last reviewed against:

- upstream `DeebotUniverse/client.py` `dev`
- GOAT mower development branches
- Home Assistant branch `feature/ecovacs-mower-progress`
- documented GOAT protocol and physical-device observations

Date: **2026-08-23**

## Purpose

A supported GOAT hardware profile does not imply complete support for every feature available in the official ECOVACS app or physical mower.

There are several possible layers:

```text
Physical mower supports feature
          │
          ▼
ECOVACS protocol exposes feature
          │
          ▼
deebot_client understands protocol
          │
          ▼
hardware profile exposes capability
          │
          ▼
consumer integration exposes feature
```

A feature may be missing or incomplete at any one of these layers.

---

# Summary

Major known limitations currently include:

- incomplete O1200 selected-zone capability
- mower-specific settings still residing only in development branches
- incomplete cross-model verification
- device-specific same-name command routing remains an open PR rather than reviewed upstream architecture
- O1200 cutting-height protocol mapped, but raw `mowHeightLevel` → physical height mapping incomplete
- O1200 `cutMode` mapped as a raw zone parameter, but its app/user-facing enum semantics remain incomplete
- O1200 `obstacleHeight` mapped as a raw zone parameter, but its exact physical meaning/unit remains incomplete
- relationship between O1200 zone `angle` and global `cut_direction` remains incomplete
- mowing speed not mapped
- no separate explicit ECOVACS ETA field identified
- O1200 progress semantics not yet cross-model verified
- O1200 area names/IDs are mapped in development via `getAreaSet`, but selected-zone start and full zone geometry remain separate gaps
- static GOAT map parser/rendering stack exists in open drafts, but hardware wiring, acquisition and live layers remain incomplete
- AI/obstacle settings not fully correlated with ECOVACS app wording
- physical effects of AI settings not systematically tested
- incomplete rain-delay lifecycle interpretation
- animal-protection runtime behaviour not fully understood
- several protection-state flags have unknown semantics
- mower scheduling is not fully mapped/documented
- generic vacuum-oriented terminology remains present in the shared client API
- firmware and model differences can change behaviour
- `deebot_client` support and Home Assistant entity support are separate layers

---

# Upstream versus development support

Some functionality documented in this repository exists only in development branches.

## Reviewed upstream baseline

The reviewed upstream GOAT profiles expose common functionality including:

```text
battery
charging / return to station
mowing control
state
statistics
maintenance lifetime
network
sound
common settings
```

Common upstream mower settings include:

```text
advanced_mode
border_switch
cut_direction
child_lock
moveup_warning
cross_map_border_warning
safe_protect
true_detect
volume
```

## Development-only mower features

Development work adds features including:

```text
mowed_area
mowing_job_progress
ai_recognition
animal_protection
humanoid_ai
narrow_adapt
rain_delay
fall_volume
protect_state
```

These should not be described as generally available in a reviewed upstream release until merged.

---

# Hardware profile support is not a full device specification

A hardware profile answers:

```text
What does the current Python client expose?
```

It does not necessarily answer:

```text
What can the physical mower do?
```

A missing capability may reflect:

- unknown protocol
- unfinished implementation
- missing model evidence
- a deliberate model difference
- an integration gap

This distinction is particularly important for GOAT because the official app exposes mower functionality that may not yet be represented by the common client abstraction.

---

# O1200 selected-zone mowing

The physical GOAT O1200 supports selecting and mowing a defined lawn zone through the ECOVACS app.

However, the reviewed upstream O1200 hardware profile exposes:

```python
CapabilityClean(
    action=CapabilityCleanAction(
        command=CleanV2,
    ),
)
```

without:

```text
area=CleanAreaV2
```

The result is:

```text
Physical mower/app
     │
     └── selected-zone mowing works

Reviewed upstream profile
     │
     └── only general CleanV2 action exposed
```

Status:

**Known implementation/research gap**

Possible explanations include:

- O1200 uses a different area command
- existing `CleanAreaV2` can work but is not wired
- zone identifiers require additional metadata
- O1200 uses another command family
- implementation has simply not been completed

The correct solution should be based on captured O1200 traffic rather than copying another mower profile without verification.

---

# O1200 area names are mapped in development

The status of area-name metadata changed with PR #1774.

For the researched O1200, the development client now exposes:

```text
CapabilityClean.areas
```

using:

```text
GetAreaSet
RoomsEvent
Room
```

Real-device validation produced:

```text
4 → Østkanten
1 → Sentrum
2 → Vestkanten
```

and a live refresh test confirmed that subscribing to `RoomsEvent` triggers `getAreaSet` and returns the expected names and IDs.

Status:

**Protocol observed / Fork implemented / Python tested / Device validated**

The Home Assistant area-name development branch also exposes these mappings through the mower's:

```text
rooms
```

extra-state attribute.

## Remaining limitation

This does **not** mean selected-zone mowing control is solved.

The reviewed upstream O1200 profile still lacks:

```text
CapabilityCleanAction.area
```

and the exact relationship between the selected-zone start target and the known `GetAreaSet` IDs should be explicitly confirmed.

Likewise, area names do not imply complete map/geometry support.

See:

[O1200 area names](area-names.md)

# Multi-zone mowing semantics

The generic `CleanAreaV2` implementation can encode multiple numeric targets.

However, GOAT-specific questions remain:

- Are multiple mower zones supported in one job on every relevant model?
- Does order matter?
- Can order be explicitly configured?
- Does ECOVACS optimise order automatically?
- Can each zone have different mowing parameters?
- How is progress reported for a multi-zone job?

Status:

**Not fully verified**

---

# Generic area modes may not map directly to GOAT terminology

The shared client defines:

```text
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

These names originate from generic ECOVACS/DEEBOT support.

They should not automatically be interpreted as official GOAT concepts without protocol correlation.

In particular:

```text
SPOT_AREA
```

may correspond to a lawn zone in some flows, but that mapping should be confirmed per model.

---

# O1200 cutting height is protocol-mapped, but physical semantics remain incomplete

The status of cutting height changed with the area-parameter development work.

For the researched O1200, the protocol field is:

```text
mowHeightLevel
```

inside a zone-specific:

```text
AreaParameter
```

associated with:

```text
areaID
```

Read/write/push support is implemented through:

```text
getAreaParameter
setAreaParameter
onAreaParameter
```

Status:

**Protocol observed / Fork implemented / Python tested**

Therefore it is no longer correct to describe O1200 cutting height as:

```text
protocol unknown
```

or:

```text
not mapped
```

## Remaining limitation

The raw value still needs a complete physical/user-facing mapping.

Open questions include:

- valid level range
- minimum/maximum physical cutting height
- physical unit
- step size
- whether the level mapping is linear
- cross-model compatibility

For example:

```text
mowHeightLevel = 10
```

is a known raw value, but should not be labelled as `10 mm` without evidence.

---

# Global cutting direction versus area angle

Reviewed upstream exposes:

```text
settings.cut_direction
```

through:

```text
GetCutDirection
SetCutDirection
```

The O1200 area-parameter protocol separately exposes:

```text
AreaParameter.angle
```

for a specific:

```text
areaID
```

The relationship between these two mechanisms is not fully established.

Possible interpretations include:

- global default versus per-zone override
- model-generation differences
- separate app functions

They should not be treated as identical until correlated.

---

# O1200 zone cut mode is mapped at the raw protocol level

The O1200 area-parameter record contains:

```text
cutMode
```

normalised as:

```text
cut_mode
```

Status:

**Protocol observed / Fork implemented / Python tested**

The remaining limitation is not discovery of the field.

It is the mapping between integer values and:

- ECOVACS app labels
- mowing behaviour
- possible efficiency/pattern concepts

Do not automatically equate:

```text
cutMode
```

with the generic client:

```text
efficiency_mode
```

without evidence.

---

# O1200 zone obstacle-height parameter is mapped at the raw protocol level

The O1200 area-parameter record contains:

```text
obstacleHeight
```

normalised as:

```text
obstacle_height
```

Status:

**Protocol observed / Fork implemented / Python tested**

Its exact:

- app wording
- physical meaning
- valid range
- unit

remain incompletely documented.

It is also distinct from boolean/AI controls such as TrueDetect, Recognization and HumanoidAI.

---

# Mowing speed is not mapped

No dedicated GOAT mowing-speed capability has been confirmed.

If the app provides speed choices, the research still needs to establish:

```text
app option
   │
   ▼
wire command
   │
   ▼
raw value
   │
   ▼
physical behaviour
```

Status:

**Not mapped**

---

# Current-job progress is not upstream

The protocol field:

```text
mowedArea
```

has been mapped in:

```text
feature/mower-stats-progress
```

to:

```text
StatsEvent.mowed_area
```

and the development hardware profile adds:

```text
mowing_job_progress=True
```

for the researched O1200 path.

This is not part of the reviewed upstream baseline.

Status:

**Fork implemented**

Consumers depending on upstream alone cannot yet assume these fields/flags exist.

---

# Mowing progress percentage is derived, not protocol data

There is no dedicated ECOVACS protocol field or `deebot_client` event field named:

```text
progress_percent
```

The Home Assistant development branch derives:

```text
mowed_area / area × 100
```

when:

```text
mowing_job_progress=True
```

This calculation is implemented and tested for the O1200 progress path.

Therefore the correct limitation is **not**:

```text
progress percentage is not implemented
```

but:

```text
progress percentage is not a protocol/client field;
it is a model-gated derived Home Assistant value
```

Status:

**Derived / HA implemented / HA tested**

Cross-model semantics remain unverified.

---

# Estimated mowing duration: current implementation versus protocol limitation

The official ECOVACS app displays an estimated duration when a mowing operation is started.

The Home Assistant mower-progress development currently interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

when the model declares:

```text
mowing_job_progress=True
```

This is implemented and covered by Home Assistant tests for the researched O1200 path.

Therefore the correct current statement is:

> O1200 progress development has an implemented, model-gated estimated-duration presentation based on `StatsEvent.time`.

However, an important protocol limitation remains:

> A separate explicit ECOVACS field such as `eta`, `estimated_duration` or `estimated_remaining_time` has not been identified.

These are not contradictory.

Status:

```text
O1200 HA duration interpretation:
Implemented/tested

Separate explicit ETA protocol field:
Not identified
```

---

# Estimated duration must not be generalised

The model-gated Home Assistant interpretation does not prove:

```text
StatsEvent.time = estimated duration
```

for all GOAT models.

Likewise, it does not prove that the value represents:

```text
estimated remaining time
```

rather than:

```text
estimated total mowing duration
```

Cross-model and in-job behaviour remain research targets.

---

# Statistics units require model-aware handling

The Home Assistant O1200 progress path currently treats:

```text
area / mowed_area → square centimetres
time              → seconds
```

and converts them for display.

This mapping is implemented and tested in the integration.

However, it should not automatically be treated as a universal protocol-unit rule for every GOAT statistics payload.

Status:

**Known O1200 integration mapping / cross-model verification incomplete**

---

# Locally calculated remaining-time ETA would be a separate concept

A consumer could theoretically calculate remaining time from:

```text
elapsed time
progress fraction
```

or from other available statistics.

Such a value would be **locally derived**.

It would not necessarily equal the ECOVACS app estimate, which may account for:

- route planning
- geometry
- mowing pattern
- speed
- obstacles
- charging stops
- battery state
- navigation overhead
- zone transitions

Any locally calculated remaining-time estimate should therefore be clearly labelled as derived.

---

# Mower settings are currently O1200-focused

Newly researched settings are wired primarily to:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

in development work.

These include:

```text
AI recognition
Humanoid AI / smart avoidance
narrow adaptation
animal protection
rain delay
lifted-alarm volume
protection state
```

PR #1778 additionally refines O1200 system-volume payload handling while preserving the shared `SetVolume(volume)` interface.

This does not establish support on all GOAT models.

Status for other models:

**Unverified**

---

# Similar GOAT models may still use different protocols

It is unsafe to assume:

```text
GOAT model A supports command
          │
          ▼
all GOAT models support command
```

Differences may depend on:

- navigation hardware
- LiDAR/camera configuration
- RTK hardware
- product generation
- region
- firmware
- accessories

New hardware-profile capabilities should be enabled from evidence rather than product-name similarity.

---

# AI settings are not fully correlated with the app

Several separate protocol controls are known:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
Animal protection
```

Their exact one-to-one relationship with official app labels is not fully documented.

Do not collapse them into one generic obstacle-avoidance switch.

Status:

**Protocol/client mapping partially established / app semantics incomplete**

---

# Physical effects of AI settings are incompletely tested

Client command/event tests verify protocol representations for AI-related settings.

They do not prove all physical effects.

Important remaining A/B tests include:

- obstacle approach with setting OFF/ON
- narrow passage behaviour OFF/ON
- human/person presence where safe and appropriate
- interaction between TrueDetect and other AI controls
- animal-protection schedule behaviour

Status:

**Implementation confidence higher than behavioural confidence**

---

# Humanoid AI naming remains ambiguous

The wire name:

```text
HumanoidAI
```

does not by itself prove that the setting only affects human detection.

The implementation currently describes it as:

```text
Smart mowing with avoidance
```

Until app/physical correlation is stronger, user-facing wording should remain conservative.

---

# Animal protection configuration versus runtime state

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

Runtime protection is separately represented through:

```text
ProtectStateEvent.is_anim_protect
```

The exact relationship between schedule boundaries and runtime transitions is not fully established.

`SetAnimalProtection` writes the complete `enabled` / `start` / `end` tuple. Integrations must therefore preserve sibling values when changing one field.

Animal protection should not automatically be described as a generic "night restriction".

Status:

**Configuration mapped / runtime behaviour incomplete**

---

# Rain-delay lifecycle remains incomplete

Rain configuration is well mapped:

```text
enabled
delay
```

and actual rain has been correlated with:

```text
isRainProtect = 1
isRainDelay   = 0
```

However, the exact physical meaning of:

```text
isRainDelay = 1
```

has not been conclusively observed.

Likely hypothesis:

```text
post-rain waiting period
```

but this remains unconfirmed.

PR #1776 also deliberately does not map rain-related event code `2052` or rain-specific pause-reason values because their semantics are not sufficiently documented.

---

# Automatic resume after rain is unresolved

The project does not yet have a complete observation of:

```text
dry
 │
 ▼
rain
 │
 ▼
protection
 │
 ▼
rain stops
 │
 ▼
configured delay
 │
 ▼
resume / ready
```

Questions remain about whether the mower:

- automatically resumes the same job
- returns to ready state
- requires a new command
- behaves differently based on schedule/job type

Status:

**Open research question**

---

# Protection-state flags have uneven semantic confidence

The development parser exposes:

```text
is_anim_protect
is_rain_protect
is_rain_delay
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

Semantic confidence differs.

## Strongest

```text
is_rain_protect
```

has direct real-rain evidence.

## Partial

```text
is_anim_protect
is_rain_delay
is_e_stop
```

are structurally mapped but need more transition correlation.

## Weak/unresolved

```text
is_locked
is_pin_code
is_prepare_data_success
```

should not receive strong user-facing labels without further evidence.

In particular:

```text
is_locked
```

must not automatically be equated with:

```text
child_lock
```

---

# O1200 volume protocol still has one unmapped channel

A complete O1200 volume payload can include:

```text
volume
fallVolume
searchVolume
```

PR #1778 maps:

```text
volume     → VolumeEvent
fallVolume → FallVolumeEvent
```

but does not expose:

```text
searchVolume
```

as a separate capability.

Reason:

```text
no setter protocol has been observed
```

The O1200 setters also currently use the observed:

```text
total = 10
```

scale.

This is an evidence-backed O1200 assumption, not a universal ECOVACS volume rule.

Status:

```text
system volume: mapped
lifted-alarm volume: mapped
searchVolume: read field only
cross-model volume scale: unverified
```

---

# GOAT map support is now partially implemented in a stacked draft

The earlier description:

```text
no complete GOAT mower map abstraction
```

is now too broad.

The current stacked development work implements a **static map MVP**:

```text
#1567
shared mower group/segment/point geometry

#1782
O1200 static onMI main boundary

#1788
onArI work-area geometry
+ getAreaSet names/IDs
+ work-area registration

#1789
shared Map capability
+ shared Rust SVG rendering
```

This resolves a substantial part of the static-map problem.

## What is still missing

The stack is not complete production GOAT map support.

PR #1789 explicitly does not yet implement:

```text
O1200 hardware wiring
AppPing/getMI acquisition lifecycle
getAreaSet lifecycle coordination
Home Assistant compatibility
mower position overlay
dock position
live-position → static-map transform
current_area
onMapTrack rendering
map editing
```

## Static versus live coordinates

The static boundary and registered work areas share a proven coordinate frame.

The live mower-position frame does not yet have a unique proven transform into that static frame.

Research currently supports 135° as the strongest tested rotation candidate, but translation remains non-unique.

Therefore no live position should be overlaid on the static map yet.

## AreaSet size semantics are family-specific

For O1200 `getAreaSet type="ar"`:

```text
envelope infoSize
```

is not the decompressed byte length.

The internal trimmed-LZMA size field is used instead.

Do not generalize that rule to `onMI` or grouped `onArI`, where `infoSize` has separate evidence.

## Hardware/model scope

The static O1200 parser/registration evidence should not be enabled on another GOAT model without direct captures.

PR #1567 has separate A1600 `onMapTrace` evidence, but that does not prove A1600 uses the identical O1200 static-map formats.

Status:

**Static map architecture implemented in open stacked drafts / production wiring and live layers incomplete**

See:

[GOAT mower map support](map.md)

---

# Scheduling is not fully mapped

The official ecosystem supports scheduled mower behaviour, but GOAT-specific schedule semantics are not yet fully documented here.

A complete mapping should identify:

```text
schedule ID
enabled state
weekdays
start time
timezone
zone selection
mowing mode/settings
```

Status:

**Incomplete**

---


# Device-specific command routing is not upstream yet

The reviewed upstream architecture still relies heavily on global command-name registries.

PR #1772 proposes a per-device command lookup derived from:

```text
Capabilities
```

so different device families can select different Python implementations with the same ECOVACS command name.

This is an important prerequisite for mower command work such as a mower-specific:

```text
clean
```

implementation.

Status:

```text
PR #1772 open
not merged into reviewed upstream baseline
```

Until the architecture lands, same-name device-family command implementations remain harder to represent safely.

---

# PR #1772 does not solve every same-name case

The proposed mapping stores one command class for each:

```text
Command.NAME
```

inside one device.

It uses first-wins behaviour for directly discoverable duplicate names.

This means it primarily solves:

```text
same name across different devices
```

not arbitrary:

```text
same name + multiple semantic implementations inside one device
```

Commands wrapped in lambdas are also not directly discoverable by the capability scan.

These are software architecture constraints rather than ECOVACS protocol limitations.

---

# `setVolume` cross-PR integration requires explicit verification

PR #1778 maps O1200:

```text
system volume
lifted-alarm volume
```

through the same ECOVACS wire command:

```text
setVolume
```

The system-volume setter is wrapped in a lambda to provide:

```text
type=sys
total=10
```

while:

```text
SetFallVolume
```

is directly configured.

PR #1772's device command discovery does not directly inspect arbitrary lambda targets and retains one direct command class per name.

Therefore the combination:

```text
#1772 + #1778
```

should have an explicit integration test before being considered fully verified.

The test should cover both:

```text
type=sys
type=fall
```

and resulting P2P/event behaviour.

Status:

**Open integration verification item**

---

# Firmware and cloud compatibility can change

ECOVACS can change:

- firmware behaviour
- cloud APIs
- authentication requirements
- command availability
- protocol fields
- app behaviour

A feature verified on one firmware version may need re-verification after updates.

Protocol observations should record firmware/app context where practical.

---

# Generic vacuum terminology remains in the API

The common client still contains terms such as:

```text
clean
cleaning
cleanings
room
CleanMode
State.CLEANING
```

For mower use:

```text
State.CLEANING
```

means mowing at the user-interface layer.

This shared naming is not necessarily a bug; it reflects the common device abstraction.

Consumer integrations should translate terminology where appropriate.

---

# `CapabilitySettings` fields do not imply GOAT support

The common capability dataclass includes settings used by many ECOVACS devices.

The existence of a field in:

```text
CapabilitySettings
```

does not mean GOAT supports that setting.

Support is established when the hardware profile actually assigns a capability, backed by appropriate evidence.

---

# Accessories/lifespans require care

The O1200 profile exposes additional lifespan types including:

```text
WEED_ROPE
TRIMMER_BRUSH
```

The existence of these protocol/client lifetime types does not prove every retail configuration physically includes the corresponding accessory.

---

# Availability does not equal ready-to-mow

A device can be available/online while being unable to mow due to:

- active rain protection
- emergency stop
- lock/security state
- charging
- another protection condition
- mower error

Availability should therefore not be treated as equivalent to operational readiness.

---

# State alone may not explain why the mower stopped

The shared state model provides broad values such as:

```text
PAUSED
DOCKED
ERROR
```

A protection-state or error event may be needed to explain the cause.

For example:

```text
mower not mowing
```

can result from very different conditions.

A mature integration may need to combine:

```text
StateEvent
ProtectStateEvent
ErrorEvent
```

rather than relying on one entity alone.

---

# Home Assistant feature parity is a separate layer

A capability existing in `deebot_client` does not automatically mean Home Assistant exposes it.

Examples:

- client STOP exists but reviewed HA mower entity does not expose stop
- mower-specific settings exist in development client branches but are not yet HA entities
- runtime protection flags are parsed but not yet exposed as GOAT binary sensors
- O1200 progress values are exposed only in the relevant HA development work

Feature matrices should therefore distinguish:

```text
client support
```

from:

```text
Home Assistant entity support
```

---

# Development branches are not upstream releases

This repository documents active development work.

Branch-level functionality can:

- change
- be rebased
- be split
- be rejected upstream
- be redesigned before merge

Documentation should therefore identify branch/review context when discussing non-upstream features.

---

# Raw logs should not be published

ECOVACS traffic can contain:

- account identifiers
- device identifiers
- credentials/tokens
- Wi-Fi data
- location/map information
- private metadata

Only sanitised examples should be committed publicly.

---

# Conservative model-support wording

Prefer:

```text
observed on O1200
```

or:

```text
implemented for O1200 development profile
```

over:

```text
GOAT supports this
```

unless the feature has been verified across enough models to justify the broader statement.

---

# High-priority gaps

| Priority | Gap | Why it matters |
| --- | --- | --- |
| High | O1200 selected-zone start command/metadata | Required for native selected-zone control |
| High | `mowHeightLevel` physical mapping | Converts known raw field into safe user-facing cutting height |
| High | `cutMode` enum/app mapping | Converts known raw field into meaningful mower modes |
| High | `obstacleHeight` semantics/unit | Required for safe user-facing control |
| High | area `angle` vs global `cut_direction` | Prevents duplicate/conflicting controls |
| High | Mowing speed | Core mower behaviour |
| High | Cross-model progress semantics | Prevents incorrect O1200 assumptions elsewhere |
| High | AI app-setting correlation | Required for safe user-facing labels |
| Medium | `StatsEvent.time` in-job behaviour | Clarifies estimated-duration semantics |
| Medium | Explicit ETA-field search | Distinguishes ECOVACS field from integration interpretation |
| Medium | Rain-delay lifecycle | Required for accurate runtime state |
| Medium | Animal-protection runtime | Required for accurate status/automation |
| Medium | Selected-zone target ↔ known area IDs | Required to connect O1200 name metadata to native zone mowing |
| Medium | Scheduling | Important mower automation |
| Medium | GOAT map semantics | Required for map/zone integration |
| Medium | Protection flags | Prevents misleading security labels |
| Medium | Cross-model setting verification | Needed before broad GOAT enablement |

---

# Recommended rule for resolving a limitation

For each missing feature:

```text
1. Identify official app behaviour
2. Change one variable at a time
3. Capture protocol traffic
4. Identify command/message/fields
5. Reproduce the finding
6. Implement normalised client event/command
7. Add automated client tests
8. Enable only supported hardware profiles
9. Verify physical mower behaviour
10. Add Home Assistant representation if appropriate
11. Update documentation and testing matrix
```

This keeps implementation evidence separate from assumption.

---

# Related documentation

- [Overview](overview.md)
- [Device-specific command routing](command-routing.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Mowing control](mowing-control.md)
- [Zones and areas](zones-and-areas.md)
- [GOAT mower map support](map.md)
- [Progress and statistics](progress-and-statistics.md)
- [Settings](settings.md)
- [O1200 global settings](o1200-global-settings.md)
- [O1200 area parameters](area-parameters.md)
- [O1200 area names](area-names.md)
- [Rain and protection](rain-and-protection.md)
- [Obstacle and AI](obstacle-and-ai.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Protocol observations](../research/protocol-observations.md)
