# Known limitations

This page documents current limitations, implementation gaps and unresolved areas in ECOVACS GOAT mower support.

Last reviewed against:

* upstream `DeebotUniverse/client.py` `dev`
* development branches used for GOAT mower research
* documented GOAT protocol and physical-device observations

Date: **2026-08-23**

## Purpose

A supported GOAT hardware profile does not imply complete support for every feature available in the ECOVACS app or physical mower.

There are several possible gaps:

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

A feature may be missing at any one of these layers.

This page attempts to identify where the current gaps are.

---

# Summary

Major known limitations currently include:

* incomplete O1200 selected-zone capability
* mower-specific settings still residing only in development branches
* incomplete cross-model verification
* cutting height not mapped
* mowing speed not mapped
* GOAT-specific mowing efficiency/mode not mapped
* ECOVACS ETA source not identified
* zone names and zone metadata not fully mapped
* no complete mower map abstraction
* AI/obstacle settings not fully correlated with ECOVACS app wording
* physical effects of AI settings not systematically tested
* incomplete rain-delay lifecycle interpretation
* animal-protection runtime behaviour not fully understood
* several protection-state flags have unknown semantics
* generic vacuum-oriented terminology remains present in the client API
* firmware and model differences can change behaviour

---

# Upstream versus development support

Some functionality documented in this repository exists only in development branches.

This distinction is important.

## Current upstream baseline

The reviewed upstream GOAT profiles expose common functionality such as:

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

The GOAT mower development work adds features such as:

```text
mowed_area
ai_recognition
animal_protection
humanoid_ai
narrow_adapt
rain_delay
fall_volume
protect_state
```

These should not be documented as generally available in released or upstream `deebot_client` until merged.

---

# O1200 selected-zone mowing

The physical GOAT O1200 supports selecting and mowing a defined lawn zone through the ECOVACS application.

However, the current reviewed upstream O1200 hardware profile exposes:

```python
CapabilityClean(
    action=CapabilityCleanAction(
        command=CleanV2,
    ),
)
```

and does not assign:

```text
area=CleanAreaV2
```

The result is:

```text
Physical mower/app
     │
     └── selected-zone mowing works

Current upstream profile
     │
     └── only generic CleanV2 exposed
```

Status:

**Known implementation gap**

Possible explanations include:

* O1200 uses a different area protocol
* existing `CleanAreaV2` can be used but is not yet wired
* zone identifiers require additional map metadata
* O1200 uses another command family
* implementation simply has not yet been completed

The correct solution should be based on captured O1200 traffic rather than copying the capability from another GOAT profile without verification.

---

# Zone names are not yet fully exposed

The ECOVACS app can present human-readable lawn-area names.

The low-level area command accepts numeric values rather than human-readable names.

A complete integration therefore needs a mapping similar to:

```text
"Front lawn"
      │
      ▼
zone identifier
      │
      ▼
mowing command
```

The current GOAT documentation does not yet establish a complete protocol source for:

```text
zone ID
zone name
zone geometry
zone ordering
zone metadata
```

Status:

**Incomplete**

---

# Multi-zone mowing semantics

The generic `CleanAreaV2` implementation supports multiple numeric targets.

For example:

```text
5,8
```

can be encoded in one command.

However, GOAT-specific questions remain:

* Are multiple mower zones supported in one job?
* Does order matter?
* Can mowing order be explicitly configured?
* Does ECOVACS automatically optimise order?
* Can each zone use different mowing parameters?
* How is progress reported for a multi-zone job?

Status:

**Not fully verified**

---

# Generic area modes may not map directly to mower terminology

The shared client defines:

```text
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

These names originate from generic DEEBOT support.

They should not automatically be interpreted as:

```text
GOAT zone
GOAT custom mowing area
GOAT free mowing
```

without protocol correlation.

In particular:

```text
SPOT_AREA
```

may represent a mower zone in some flows, but this should be confirmed rather than assumed.

---

# Cutting height is not mapped

Cutting height is an important mower-specific setting but no dedicated GOAT cutting-height capability has been identified in the reviewed implementation.

Current state:

```text
ECOVACS mower feature
       │
       ▼
protocol command unknown
       │
       ▼
no deebot_client capability
```

A complete implementation would need to determine:

* GET command
* SET command
* push message, if any
* valid values
* physical unit
* minimum height
* maximum height
* step size
* whether values differ by model
* whether changes can be made during mowing

Status:

**Not mapped**

---

# Cutting direction is not cutting height

Upstream already exposes:

```text
settings.cut_direction
```

with:

```text
CutDirectionEvent.angle
```

This must not be confused with blade cutting height.

They are separate concepts:

```text
cut_direction
      │
      └── mowing/path direction angle

cutting_height
      │
      └── physical grass cutting height
```

Only the first is currently mapped.

---

# Mowing speed is not mapped

No dedicated GOAT mowing-speed capability has been confirmed in the reviewed source.

If the app provides speed choices, their mapping still needs to be captured.

Required research includes:

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
physical speed
```

Status:

**Not mapped**

---

# GOAT-specific mowing efficiency/mode is not mapped

The generic `CapabilitySettings` structure contains:

```text
efficiency_mode
```

for supported ECOVACS devices.

The existence of this generic capability does not prove that GOAT's mowing-efficiency or mowing-mode options use the same protocol.

Therefore:

```text
generic efficiency_mode exists
```

must not be interpreted as:

```text
GOAT mowing efficiency supported
```

Status:

**Not mapped for GOAT**

---

# Estimated duration / ETA is not implemented

The ECOVACS app displays an estimated duration when starting a mowing operation.

That app behaviour has been observed.

However, the current research has not identified a dedicated normalised client field such as:

```text
estimated_duration
estimated_remaining_time
eta
```

The progress development branch currently adds:

```text
mowed_area
```

rather than ETA.

Therefore:

```text
ECOVACS app ETA
```

and:

```text
StatsEvent.time
```

must not be treated as equivalent.

Status:

**App observed / protocol source unresolved**

---

# Locally calculated ETA would be different

A consumer could theoretically calculate an estimate using:

```text
elapsed time
+
completed area
+
total area
```

but such an estimate would be locally derived.

It might differ significantly from the ECOVACS app because ECOVACS may account for:

* planned path
* geometry
* mowing pattern
* speed
* obstacles
* charging stops
* battery state
* navigation overhead
* zone transitions

Any locally calculated ETA should therefore be clearly labelled as derived rather than ECOVACS-reported.

---

# `mowedArea` is not upstream yet

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

but it is not part of the reviewed upstream baseline.

Status:

**Fork implemented**

This means integrations depending on current upstream cannot yet assume the field exists.

---

# Progress percentage is not a protocol field

The current development implementation preserves:

```text
area
mowed_area
```

rather than producing:

```text
progress_percent
```

This is intentional.

A percentage such as:

```text
mowed_area / area × 100
```

is a derived value and requires confirmation that both raw values:

* represent the same job
* use the same unit
* have compatible semantics

Status:

**Derived / not directly implemented**

---

# Statistics units require care

Fields such as:

```text
area
mowedArea
time
```

should not automatically be presented with assumed physical units without verification.

Possible risks include:

```text
raw value interpreted as m²
when protocol uses another area scale
```

or:

```text
time interpreted as seconds
when mower semantics differ
```

Integrations should only apply units once independently established.

---

# Mower settings are currently O1200-focused

The newly researched mower settings are wired primarily to:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

in the development branch.

These include:

```text
AI recognition
Humanoid AI
narrow adaptation
animal protection
rain delay
lifted-alarm volume
protection state
```

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

* navigation hardware
* LiDAR/camera configuration
* RTK hardware
* product generation
* region
* firmware
* accessory configuration

Each new hardware profile should therefore be enabled from evidence rather than product-name similarity.

---

# AI settings are not fully correlated with the app

Several separate protocol controls are known:

```text
TrueDetect
Recognization
HumanoidAI
NarrowAdapt
```

but their exact one-to-one mapping to ECOVACS app labels is not yet completely documented.

Current architecture:

```text
known wire command
        │
        ▼
known client event
        │
        ▼
unknown/exact app wording
```

This means user-facing labels should be chosen conservatively until systematic app correlation is completed.

---

# AI physical behaviour is not fully tested

Python tests prove that settings can be parsed and commands can be generated.

They do not prove what happens when the mower encounters an obstacle.

For example, it is not yet systematically established how enabling or disabling:

```text
AI recognition
Humanoid AI
TrueDetect
```

changes:

* obstacle clearance
* route planning
* stopping behaviour
* object recognition
* coverage around objects
* human detection
* animal detection

Status:

**Implementation mapped / physical effects incomplete**

---

# `HumanoidAI` should not be interpreted literally

The ECOVACS wire name:

```text
HumanoidAI
```

does not by itself prove that the feature only controls human detection.

The implementation currently describes the feature as:

```text
Smart mowing with avoidance
```

Until app/device testing establishes the exact scope, developer documentation should retain both:

```text
wire name: HumanoidAI
```

and:

```text
implementation description: smart mowing with avoidance
```

without adding stronger assumptions.

---

# Animal protection semantics remain incomplete

Animal protection configuration is known to contain:

```text
enabled
start
end
```

The runtime protection state also exposes:

```text
isAnimProtect
```

What remains to be conclusively mapped is the physical behaviour during that active window.

Questions include:

* Does mowing stop completely?
* Does mower speed change?
* Is obstacle recognition enhanced?
* Is only night-time operation affected?
* What happens when a job is already active when the window begins?
* Does mowing automatically resume when the window ends?

Status:

**Configuration mapped / runtime behaviour incomplete**

---

# Animal protection should not automatically be called a night restriction

Because the setting contains a schedule, it is tempting to label it:

```text
night mowing restriction
```

However, this may be an oversimplification.

Until app and mower behaviour are fully correlated, the documentation should retain:

```text
Animal protection
```

as the feature name.

A separate night-restriction setting may also exist.

---

# Rain-delay lifecycle is not fully mapped

Rain configuration and active rain protection are relatively well understood.

Known:

```text
RainDelayEvent
    ├── enabled
    └── delay
```

and actual rain has been observed with:

```text
isRainProtect = 1
isRainDelay = 0
```

What has not yet been conclusively observed is the complete transition:

```text
rain begins
    │
    ▼
active rain protection
    │
    ▼
rain stops
    │
    ▼
post-rain delay
    │
    ▼
delay expires
    │
    ▼
mowing permitted again
```

In particular, the exact meaning of:

```text
isRainDelay = 1
```

should remain unconfirmed until observed in context.

---

# Automatic resume after rain is unresolved

It is not yet fully documented whether the mower:

* resumes the interrupted job automatically
* remains paused
* returns to dock
* creates a new operation
* behaves differently based on schedule

after rain and post-rain delay.

Status:

**Needs controlled testing**

---

# Protection flags are only partially interpreted

`ProtectStateEvent` contains:

```text
is_anim_protect
is_rain_protect
is_rain_delay
is_e_stop
is_locked
is_pin_code
is_prepare_data_success
```

Parser behaviour is implemented.

Semantic confidence is not equal for all fields.

| Field                     | Current understanding                                      |
| ------------------------- | ---------------------------------------------------------- |
| `is_rain_protect`         | Strong correlation with active rain                        |
| `is_rain_delay`           | Likely related to post-rain delay; not confirmed           |
| `is_anim_protect`         | Related to animal protection; lifecycle incomplete         |
| `is_e_stop`               | Emergency-stop-related; trigger/reset behaviour unresolved |
| `is_locked`               | Lock-related; relationship with child lock unresolved      |
| `is_pin_code`             | PIN-related; exact meaning unresolved                      |
| `is_prepare_data_success` | Internal-looking state; user-facing significance unknown   |

Consumers should avoid inventing strong labels for unresolved flags.

---

# `isLocked` is not proven to equal child lock

The client already has:

```text
ChildLockEvent
```

from the normal child-lock setting.

Separately, protection state contains:

```text
isLocked
```

These may be related, but they are separate protocol concepts.

Do not assume:

```text
isLocked == ChildLockEvent.enabled
```

until tested.

---

# `isPinCode` semantics are unknown

The presence of:

```text
isPinCode
```

does not reveal whether it means:

* PIN is configured
* PIN is required
* PIN protection is active
* mower is unlocked
* anti-theft mode
* another security condition

Status:

**Mapped field / unresolved semantics**

---

# Map support is incomplete for mower use

The generic client has map abstractions intended largely around DEEBOT map functionality.

The reviewed GOAT profiles do not currently provide a complete mower-specific map capability covering concepts such as:

```text
lawn boundary
zones
no-go areas
navigation paths
charging station
mower position
zone names
mowing route
```

Some of these data may exist elsewhere in the protocol, but they are not yet represented as one complete GOAT map API.

Status:

**Incomplete**

---

# Static-map work is separate

Development/research work may exist around mower map handling, but map support should be documented independently from the current core mower controls until:

* protocol sources are identified
* coordinate systems are understood
* map objects are normalised
* model differences are known
* tests exist

Map availability should not be implied solely because other GOAT capabilities are working.

---

# Scheduling is not yet documented as a complete client feature

The ECOVACS app supports scheduled mower operation.

A complete GOAT scheduling protocol/API has not yet been documented in this repository.

Relevant questions include:

* schedule retrieval
* schedule creation
* schedule deletion
* weekday representation
* zone selection per schedule
* mowing mode per schedule
* weather/protection interaction
* timezone handling
* seasonal behaviour

Status:

**Not yet documented/mapped**

---

# Firmware compatibility cannot be assumed

GOAT firmware can change protocol behaviour.

A feature that works on one version may:

* change field names
* change allowed values
* gain new options
* stop sending a push message
* require a new app/client version
* become model-specific

Protocol observations should therefore include firmware context wherever possible.

---

# Cloud API compatibility can change independently

Some functionality depends not only on mower firmware but also on ECOVACS cloud behaviour.

Changes can occur in:

```text
authentication
API version requirements
cloud routing
command validation
device metadata
```

A mower protocol implementation that remains technically correct may still be affected by cloud-side changes.

---

# Generic terminology remains vacuum-oriented

`deebot_client` uses shared terminology such as:

```text
clean
cleaning
cleanings
room
CleanAction
CleanMode
CLEANING
```

For robotic lawn mowers these concepts often mean:

```text
mow
mowing
mowing jobs/passes
zone
mowing action
mowing mode
MOWING
```

This terminology mismatch is not necessarily a bug in the library.

It reflects the shared abstraction.

However, integrations should avoid exposing vacuum-oriented terms directly to mower users.

---

# `State.CLEANING` means mowing

The normalised client state:

```text
State.CLEANING
```

is used while a GOAT is actively mowing.

A user-facing integration should normally present:

```text
Mowing
```

rather than:

```text
Cleaning
```

The same principle applies throughout the shared capability architecture.

---

# `CapabilityClean` means mower operation

GOAT hardware profiles currently use:

```text
Capabilities.clean
```

because mower operations share the common cleaning-action abstraction.

This should be interpreted as:

```text
mowing-operation capability
```

for GOAT devices.

Renaming the shared abstraction would be a broader architectural decision and should not be required solely for mower support.

---

# `room` terminology in tests does not prove mower room semantics

Some upstream area tests use labels such as:

```text
Rooms
Rooms V2
FreeClean single room 2x
```

These tests originate from shared vacuum functionality.

When the same command code is used with a GOAT, documentation should instead use neutral terms such as:

```text
area identifier
zone identifier
selected target
```

unless the exact mower semantics have been established.

---

# Not every `CapabilitySettings` field applies to GOAT

The shared settings dataclass also contains capabilities designed for other ECOVACS products, including vacuum-related concepts.

The presence of a field in:

```text
CapabilitySettings
```

does not imply GOAT support.

Actual device support is determined by hardware-profile wiring.

This rule also applies in reverse:

new mower-specific capabilities may require expanding the generic capability model before they can be represented cleanly.

---

# Hardware profiles represent client support, not complete device specifications

A hardware profile answers:

```text
What does deebot_client expose for this device?
```

It does not necessarily answer:

```text
What can this mower physically do?
```

For example, the O1200 upstream profile currently lacks an area command even though zone mowing is available through the official app.

This is why hardware profiles should be interpreted as implementation declarations rather than full product feature lists.

---

# Accessories and lifetime types require care

The O1200 profile exposes lifetime types including:

```text
BLADE
LENS_BRUSH
WEED_ROPE
TRIMMER_BRUSH
```

A lifetime type being exposed by the client does not necessarily prove that every retail mower package has that accessory physically installed.

Possible factors include:

* optional accessories
* shared firmware support
* regional packages
* future accessories

Documentation should distinguish protocol capability from included hardware.

---

# Availability is not the same as readiness to mow

A mower can be online and therefore:

```text
available = True
```

while still being unable to start mowing because of:

* rain protection
* animal protection
* charging state
* lock/security state
* error state
* emergency stop
* another active command

Integrations should therefore avoid treating generic device availability as:

```text
ready to mow
```

These are different concepts.

---

# State alone may not explain why mowing stopped

A normal mower state can say:

```text
PAUSED
IDLE
ERROR
```

while the reason may be represented elsewhere.

Useful additional context can include:

```text
ProtectStateEvent
ErrorEvent
ReportStatsEvent
```

A mature mower integration may eventually need to combine multiple events to present a meaningful user-facing reason.

---

# Integration feature parity is a separate layer

Even once a feature exists in `deebot_client`, Home Assistant or another consumer must explicitly expose it.

Therefore:

```text
implemented in deebot_client
```

does not automatically mean:

```text
available as Home Assistant entity/service
```

The Home Assistant integration should be documented separately.

---

# Current development branches are not upstream releases

Features documented from branches such as:

```text
feature/mower-stats-progress
feature/ecovacs-mower-settings
```

should be labelled clearly.

Until merged upstream, users of standard released `deebot_client` should not expect those APIs to exist.

---

# Raw logs are not suitable for publication

Protocol research often requires verbose logs containing device and account metadata.

These should not be published unchanged.

Before committing examples, remove:

* account IDs
* authentication tokens
* device IDs
* serial numbers
* Wi-Fi information
* precise location
* map coordinates when privacy-sensitive
* cloud credentials
* personally identifiable information

Only minimal sanitised protocol examples should be included in public documentation.

---

# Model support should be conservative

When a feature is verified on O1200, documentation should state:

```text
verified on O1200
```

rather than:

```text
GOAT supports this
```

unless evidence covers additional models.

Likewise:

```text
implemented in G1 profile
```

does not prove equivalent physical behaviour on every newer mower.

---

# Known high-priority gaps

The following currently appear to be the most valuable remaining research targets.

| Priority | Area                   | Main missing evidence                  |
| -------- | ---------------------- | -------------------------------------- |
| High     | O1200 zone mowing      | Exact command and zone-ID mapping      |
| High     | Cutting height         | GET/SET protocol and value mapping     |
| High     | Mowing mode/efficiency | App-to-protocol mapping                |
| High     | Mowing speed           | App-to-protocol mapping                |
| High     | AI settings            | Exact app labels and physical effects  |
| High     | ETA                    | Source of app estimated duration       |
| Medium   | Rain delay             | Full rain → delay → resume lifecycle   |
| Medium   | Animal protection      | Physical behaviour during schedule     |
| Medium   | Zone metadata          | Names, IDs and geometry                |
| Medium   | Scheduling             | Full mower schedule protocol           |
| Medium   | Maps                   | GOAT-specific map/data abstraction     |
| Medium   | Protection flags       | Lock/PIN/e-stop semantics              |
| Medium   | Cross-model support    | Verification on additional GOAT models |

---

# Recommended rule for closing a limitation

A limitation should only be marked resolved after the relevant evidence exists.

For a writable setting, ideal evidence is:

```text
app option identified
        │
        ▼
GET command captured
        │
        ▼
SET command captured
        │
        ▼
push/update captured
        │
        ▼
client implementation
        │
        ▼
automated tests
        │
        ▼
physical-device verification
```

Not every feature requires every step, but the documentation should clearly state which steps have actually been completed.

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
* [Testing status](testing-status.md)
* Home Assistant integration *(next/planned)*
