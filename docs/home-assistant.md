# Home Assistant integration

This page documents how ECOVACS GOAT mower functionality maps to Home Assistant and how newly researched mower capabilities could be exposed in the integration.

Last reviewed against:

* `DeebotUniverse/client.py`
* Home Assistant development branch `feature/ecovacs-mower-progress`
* mower development branches documented in this repository

Date: **2026-08-23**

## Architecture

The intended architecture is:

```text
ECOVACS mower
      │
      ▼
ECOVACS protocol
      │
      ▼
deebot_client
      │
      ├── capabilities
      ├── commands
      └── events
             │
             ▼
Home Assistant Ecovacs integration
             │
             ▼
Home Assistant entities
```

Home Assistant should normally consume normalised `deebot_client` capabilities and events rather than interpreting ECOVACS protocol payloads directly.

This separation is important because protocol handling belongs in `deebot_client`, while Home Assistant should focus on representing functionality through appropriate entity platforms.

---

# Current mower entity

GOAT devices are identified by:

```text
DeviceType.MOWER
```

and exposed in Home Assistant using the:

```text
lawn_mower
```

platform.

The development implementation creates:

```text
EcovacsMower
```

for devices where:

```python
device.capabilities.device_type is DeviceType.MOWER
```

This prevents mower devices from being represented as vacuum entities.

---

# Current `lawn_mower` features

The current mower entity exposes:

```text
START_MOWING
PAUSE
DOCK
```

through:

```text
LawnMowerEntityFeature.START_MOWING
LawnMowerEntityFeature.PAUSE
LawnMowerEntityFeature.DOCK
```

The underlying commands are:

| Home Assistant action | `deebot_client`              |
| --------------------- | ---------------------------- |
| Start mowing          | `CleanV2(CleanAction.START)` |
| Pause                 | `CleanV2(CleanAction.PAUSE)` |
| Dock                  | `Charge()`                   |

This is already covered by Home Assistant automated tests.

---

# Mower state mapping

The current integration maps shared `deebot_client` states into mower-specific Home Assistant activities.

| `deebot_client` state | Home Assistant mower activity |
| --------------------- | ----------------------------- |
| `State.CLEANING`      | `MOWING`                      |
| `State.RETURNING`     | `RETURNING`                   |
| `State.DOCKED`        | `DOCKED`                      |
| `State.ERROR`         | `ERROR`                       |
| `State.PAUSED`        | `PAUSED`                      |
| `State.IDLE`          | `PAUSED`                      |

The important translation is:

```text
CLEANING → MOWING
```

This prevents vacuum-oriented terminology from appearing in the mower entity.

---

# `IDLE` currently maps to `PAUSED`

The shared `deebot_client` model contains:

```text
State.IDLE
```

while the Home Assistant lawn-mower activity model used by the implementation does not provide a directly equivalent idle mapping in this code.

The current implementation therefore maps:

```text
State.IDLE
    ↓
LawnMowerActivity.PAUSED
```

This is an implementation compromise and should not be interpreted as proof that the mower's physical job is always paused when `deebot_client` reports `IDLE`.

If the Home Assistant mower model later provides a better representation, this mapping could be revisited.

---

# Stop mowing

`deebot_client` supports:

```text
CleanAction.STOP
```

and physical GOAT stop behaviour has been observed.

However, the current Home Assistant mower entity exposes only:

```text
START_MOWING
PAUSE
DOCK
```

There is no corresponding stop action in the current `EcovacsMower` implementation.

Therefore:

```text
Protocol/client
    │
    └── STOP supported

Home Assistant mower entity
    │
    └── STOP not currently exposed
```

Status:

**Client supported / Home Assistant integration gap**

This should not be confused with docking.

```text
STOP
```

and:

```text
DOCK
```

are separate ECOVACS operations.

---

# Start versus resume

The Home Assistant entity currently calls:

```text
CleanAction.START
```

for:

```text
START_MOWING
```

It does not need a separate Home Assistant resume action because the shared `deebot_client` command implementation contains state-aware START/RESUME handling.

When the mower is paused:

```text
START requested
      │
      ▼
deebot_client sees PAUSED
      │
      ▼
RESUME is sent
```

This provides a natural mapping from Home Assistant's single start action to both starting and resuming GOAT mowing.

---

# Current mower sensors

The Ecovacs sensor platform already adapts several generic statistics names for mower devices.

Examples include:

```text
Area mowed
Mowing duration
Total area mowed
Total mowing duration
Total mowings
```

instead of vacuum-oriented labels such as:

```text
Area cleaned
Cleaning duration
Total cleanings
```

This is the preferred design pattern:

```text
shared client event
       │
       ▼
device-type-specific Home Assistant wording
```

rather than changing the generic client event solely for UI terminology.

---

# Battery

Battery is exposed as a normal Home Assistant battery sensor.

Source:

```text
BatteryEvent
```

Entity type:

```text
sensor
```

Device class:

```text
battery
```

Unit:

```text
%
```

This is a diagnostic/status entity rather than a mower-control setting.

---

# Maintenance/lifespan sensors

GOAT maintenance values are exposed through Home Assistant sensors based on:

```text
LifeSpanEvent
```

Examples include:

```text
Blade lifespan
Lens brush lifespan
```

For models supporting additional types, potential values include:

```text
Weed rope lifespan
Trimmer brush lifespan
```

The hardware profile determines which lifespan entities are created.

These are diagnostic sensors.

---

# Network and error sensors

The generic Ecovacs integration also exposes diagnostic information such as:

```text
IP address
Wi-Fi RSSI
Wi-Fi SSID
Error
```

These are useful for diagnostics but are not mower-specific controls.

Some diagnostic entities are disabled by default.

---

# Mowing job progress

The development pair:

```text
client.py:
feature/mower-stats-progress

Home Assistant core:
feature/ecovacs-mower-progress
```

introduces explicit support for mower job progress.

The client capability adds:

```python
CapabilityStats(
    ...
    mowing_job_progress=True,
)
```

for the researched O1200 profile.

Home Assistant checks this flag before exposing the mower-specific progress interpretation.

This is preferable to assuming that every device sending `StatsEvent` uses the fields in the same way.

---

# Progress capability flag

The client adds:

```text
stats.mowing_job_progress
```

with default:

```text
False
```

The O1200 development profile sets:

```text
mowing_job_progress=True
```

Conceptually:

```text
StatsEvent available
        │
        ▼
Does model declare
mowing_job_progress?
        │
     ┌──┴──┐
     │     │
    no    yes
     │     │
     ▼     ▼
generic   mower-progress
stats     interpretation
```

This allows model-specific semantics without changing statistics behaviour for unrelated ECOVACS devices.

---

# Area mowed during current job

When mower job progress is supported, Home Assistant uses:

```text
StatsEvent.mowed_area
```

for the current:

```text
Area mowed
```

sensor rather than:

```text
StatsEvent.area
```

The protocol/client representation is:

```text
mowedArea
      ↓
mowed_area
      ↓
Home Assistant area sensor
```

The current O1200 test uses:

```text
mowed_area = 28699
```

and Home Assistant presents:

```text
2.8699 m²
```

through its area-unit conversion.

---

# Mowing progress percentage

The Home Assistant development branch calculates progress as:

```python
mowed_area / area * 100
```

provided:

```text
area is present
area != 0
mowed_area is present
```

Otherwise progress is returned as unknown/`None`.

Conceptually:

```text
completed area
────────────── × 100
 total area
```

The resulting sensor is:

```text
Mowing progress
```

with unit:

```text
%
```

and suggested display precision:

```text
0 decimal places
```

---

# Missing progress is not zero

The implementation correctly distinguishes:

```text
mowed_area = 0
```

from:

```text
mowed_area = None
```

and also rejects progress calculation when:

```text
area = 0
```

or:

```text
area = None
```

This is important because unavailable statistics should not be presented as:

```text
0% complete
```

when the real state is:

```text
progress unknown
```

---

# Estimated mowing duration

For models declaring:

```text
mowing_job_progress=True
```

the Home Assistant development branch interprets:

```text
StatsEvent.time
```

as:

```text
Estimated mowing duration
```

rather than the generic:

```text
Mowing duration
```

The sensor uses:

```text
SensorDeviceClass.DURATION
```

with protocol/client values represented natively as seconds and a suggested Home Assistant display unit of minutes.

The current automated test uses:

```text
time = 2304
```

and expects:

```text
38.4 minutes
```

in Home Assistant.

---

# ETA interpretation should remain model-specific

The Home Assistant branch deliberately gates this interpretation behind:

```text
mowing_job_progress
```

This distinction is important.

It means the implementation does **not** claim:

```text
StatsEvent.time
```

always means estimated duration on every ECOVACS device.

Instead:

```text
normal device
    │
    ▼
time → operation duration

mower with mowing_job_progress
    │
    ▼
time → estimated mowing duration
```

The exact ECOVACS semantics should continue to be verified on additional GOAT models before enabling the flag elsewhere.

---

# Current progress entities

For the researched O1200 implementation, Home Assistant creates entities equivalent to:

```text
sensor.goat_o1200_lidar_area_mowed
sensor.goat_o1200_lidar_mowing_progress
sensor.goat_o1200_lidar_estimated_mowing_duration
```

These are explicitly covered by Home Assistant tests.

---

# Total statistics

Cumulative statistics remain separate from current-job progress.

They are exposed through:

```text
TotalStatsEvent
```

as concepts such as:

```text
Total area mowed
Total mowing duration
Total mowings
```

These should not be used for active-job progress calculations.

---

# Current boolean mower settings

The Home Assistant Ecovacs integration already maps a number of:

```text
CapabilitySetEnable
```

settings to:

```text
switch
```

entities.

GOAT-relevant examples include:

| `deebot_client` capability | Home Assistant type |
| -------------------------- | ------------------- |
| `advanced_mode`            | switch              |
| `true_detect`              | switch              |
| `border_switch`            | switch              |
| `child_lock`               | switch              |
| `moveup_warning`           | switch              |
| `cross_map_border_warning` | switch              |
| `safe_protect`             | switch              |

These are normally classified as:

```text
EntityCategory.CONFIG
```

and several are disabled by default in the entity registry.

This is a sensible pattern for advanced mower configuration.

---

# Why advanced settings may be disabled by default

GOAT exposes many settings that are not required for normal day-to-day mower control.

Making all of them enabled by default could create a large and confusing device page.

A reasonable Home Assistant structure is:

```text
Primary entities
    │
    ├── lawn mower
    ├── battery
    ├── progress
    └── key status

Advanced configuration
    │
    ├── TrueDetect
    ├── border behaviour
    ├── child lock
    └── other settings
```

with less commonly used configuration entities disabled by default.

---

# Cutting direction

Home Assistant already represents:

```text
settings.cut_direction
```

as a:

```text
number
```

entity.

Current configuration:

```text
minimum = 0
maximum = 180
step = 1
unit = °
```

Source event:

```text
CutDirectionEvent.angle
```

This is a good example of using the Home Assistant entity type that naturally matches the `deebot_client` capability.

---

# Volume

System volume is also represented as a:

```text
number
```

entity.

Current defaults include:

```text
minimum = 0
maximum = 10
step = 1
```

The maximum can also be updated from:

```text
VolumeEvent.maximum
```

when the device reports it.

Status:

**Currently represented**

---

# Newly researched mower settings

The mower settings development branch adds capabilities that are not yet represented by the reviewed Home Assistant progress branch.

These include:

```text
ai_recognition
humanoid_ai
narrow_adapt
animal_protection
rain_delay
fall_volume
protect_state
```

These require Home Assistant platform work after the corresponding `deebot_client` support is available.

---

# Recommended: AI recognition

Capability:

```text
settings.ai_recognition
```

Type:

```text
CapabilitySetEnable
```

Recommended Home Assistant representation:

```text
switch
```

Potential role:

```text
configuration entity
```

Because the exact user-facing app wording is still being mapped, naming should remain conservative until correlation is complete.

Status:

**Client fork implemented / Home Assistant not yet exposed**

---

# Recommended: Humanoid AI

Capability:

```text
settings.humanoid_ai
```

Type:

```text
CapabilitySetEnable
```

Recommended Home Assistant representation:

```text
switch
```

The implementation currently describes this as:

```text
Smart mowing with avoidance
```

A user-facing translation should preferably use confirmed ECOVACS app terminology rather than the raw:

```text
Humanoid AI
```

wire name.

Status:

**Client fork implemented / Home Assistant not yet exposed**

---

# Recommended: narrow passage adaptation

Capability:

```text
settings.narrow_adapt
```

Type:

```text
CapabilitySetEnable
```

Recommended Home Assistant representation:

```text
switch
```

Entity category:

```text
CONFIG
```

Status:

**Client fork implemented / Home Assistant not yet exposed**

---

# Recommended: lifted-alarm volume

Capability:

```text
settings.fall_volume
```

Event:

```text
FallVolumeEvent
```

Recommended representation:

```text
number
```

Likely range based on current implementation:

```text
0–10
```

with:

```text
step = 1
```

This should remain separate from normal system volume.

Conceptually:

```text
Volume
├── system volume
└── lifted-alarm volume
```

Status:

**Client fork implemented / Home Assistant not yet exposed**

---

# Animal protection needs multiple entities

Animal protection cannot accurately be represented by a single switch because its capability contains:

```text
enabled
start
end
```

A possible Home Assistant representation is:

```text
switch.goat_animal_protection
time.goat_animal_protection_start
time.goat_animal_protection_end
```

However, all three values belong to one ECOVACS configuration object.

This creates an implementation concern.

When changing only:

```text
enabled
```

the client command still needs:

```text
start
end
```

Likewise, changing:

```text
start
```

requires retaining:

```text
enabled
end
```

Home Assistant therefore needs to keep the latest complete `AnimalProtectionEvent` when constructing each write.

---

# Avoid destructive partial updates

Structured settings such as animal protection should not be implemented like independent protocol fields if the ECOVACS command expects the entire configuration.

Bad conceptual behaviour:

```text
user changes start time
        │
        ▼
send only start
```

when protocol expects:

```text
enabled + start + end
```

Preferred pattern:

```text
latest AnimalProtectionEvent
        │
        ├── enabled
        ├── start
        └── end
             │
             ▼
change requested field
             │
             ▼
send complete configuration
```

This prevents one Home Assistant entity from accidentally resetting another value.

---

# Rain configuration also needs multiple controls

Rain configuration contains:

```text
enabled
delay
```

Possible Home Assistant representation:

```text
switch.goat_rain_protection
number.goat_rain_delay
```

A numeric delay entity naturally matches:

```text
0–300 minutes
step = 30 minutes
```

A select entity with the explicit supported values would also be possible.

Because both values belong to one:

```text
SetRainDelay(enabled, delay)
```

command, the same complete-state principle applies.

---

# Rain switch write example

If the current configuration is:

```text
enabled = True
delay = 180
```

and the user turns rain protection off, Home Assistant should conceptually send:

```text
enabled = False
delay = 180
```

rather than:

```text
enabled = False
delay = 0
```

unless the user explicitly changed the delay.

The protocol supports retaining a configured delay while rain protection is disabled.

---

# Rain delay write example

Likewise, if the current state is:

```text
enabled = True
delay = 180
```

and the user selects:

```text
240 minutes
```

the command should preserve:

```text
enabled = True
```

and send:

```text
SetRainDelay(
    enabled=True,
    delay=240,
)
```

---

# Runtime protection belongs in binary sensors

The development client exposes:

```text
ProtectStateEvent
```

with runtime booleans.

These are not configuration switches.

Recommended Home Assistant type:

```text
binary_sensor
```

Potential mappings include:

| Client field              | Recommended representation         |
| ------------------------- | ---------------------------------- |
| `is_rain_protect`         | binary sensor                      |
| `is_rain_delay`           | binary sensor                      |
| `is_anim_protect`         | binary sensor                      |
| `is_e_stop`               | binary sensor                      |
| `is_locked`               | binary sensor                      |
| `is_pin_code`             | possibly diagnostic binary sensor  |
| `is_prepare_data_success` | diagnostic only, if exposed at all |

This preserves the distinction between:

```text
configuration
```

and:

```text
current runtime condition
```

---

# Current binary-sensor platform needs extension

The reviewed Ecovacs binary-sensor platform currently mainly uses the generic:

```text
CapabilityEvent
```

pattern and does not yet define GOAT `ProtectStateEvent` entities.

Therefore supporting mower protection state requires new entity descriptions.

Conceptually:

```text
caps.protect_state
       │
       ▼
ProtectStateEvent
       │
       ├── rain active
       ├── animal protection active
       ├── emergency stop
       └── lock/security states
```

Multiple Home Assistant binary sensors can subscribe to the same underlying event while extracting different boolean fields.

---

# Do not make runtime protection writable

For example:

```text
binary_sensor.goat_rain_protection_active
```

should not be implemented as:

```text
switch.goat_rain_protection_active
```

because:

```text
is_rain_protect
```

is a reported runtime condition.

The writable configuration belongs to:

```text
RainDelayEvent / SetRainDelay
```

These are separate concepts.

---

# Zone mowing

Selected-zone mowing is not currently exposed by the reviewed:

```text
EcovacsMower
```

entity.

The standard mower implementation currently controls:

```text
start
pause
dock
```

without passing area identifiers.

This is especially relevant for O1200, where the current upstream client profile also lacks an area capability.

Status:

**Not exposed in current Home Assistant mower entity**

---

# Zone selection is not a simple scalar setting

A single-zone selector could theoretically be represented by:

```text
select
```

but this becomes inadequate when:

* multiple zones can be selected
* zone order matters
* per-zone settings exist
* mowing mode accompanies the selection

A future Home Assistant design should therefore be based on confirmed GOAT functionality rather than forcing all zone mowing into a single simple select.

---

# Potential zone architecture

A future implementation could conceptually separate:

```text
Zone metadata
    │
    ├── ID
    ├── name
    └── geometry

Mowing action
    │
    ├── selected zones
    ├── mode
    └── other options
```

The user-facing action should use zone names while `deebot_client` sends numeric identifiers.

For example:

```text
"Front lawn"
      │
      ▼
zone ID 5
      │
      ▼
mower command
```

---

# Area names

Human-readable zone names should be treated as metadata, not embedded into the low-level mowing command.

A Home Assistant implementation should ideally display:

```text
Front lawn
Side lawn
Back lawn
```

while internally maintaining:

```text
5
8
12
```

or whatever identifiers the mower protocol actually uses.

This keeps UI and protocol responsibilities separate.

---

# Cutting height

No cutting-height capability is currently mapped in the documented client work.

Therefore Home Assistant should **not** create a speculative cutting-height entity.

Once the protocol is mapped, a likely representation would be:

```text
number
```

if height is a continuous stepped numeric range.

For example:

```text
number.goat_cutting_height
```

would require confirmed:

```text
minimum
maximum
step
unit
```

before implementation.

Status:

**Not yet mapped**

---

# Mowing speed

No mower-speed capability is currently mapped.

Depending on protocol semantics, a future Home Assistant representation might be:

```text
select
```

for discrete modes such as:

```text
slow
normal
fast
```

or:

```text
number
```

for a numeric speed.

The protocol should determine the entity type rather than the app appearance alone.

Status:

**Not yet mapped**

---

# Mowing efficiency/mode

Likewise, a GOAT mowing-efficiency mode should likely become:

```text
select
```

if ECOVACS exposes a fixed set of modes.

However, the generic:

```text
efficiency_mode
```

capability used elsewhere in the library should not be reused for GOAT until protocol compatibility is confirmed.

Status:

**Not yet mapped**

---

# Entity-type guidelines

A useful rule for future GOAT integration work is:

| Capability shape         | Home Assistant representation                |
| ------------------------ | -------------------------------------------- |
| Main mower lifecycle     | `lawn_mower`                                 |
| `CapabilitySetEnable`    | `switch`                                     |
| Numeric `CapabilitySet`  | `number`                                     |
| Fixed enum/options       | `select`                                     |
| Measurement/status value | `sensor`                                     |
| Runtime boolean state    | `binary_sensor`                              |
| Scheduled time value     | `time`                                       |
| One-shot action          | button/action/service depending on semantics |

The actual feature semantics remain more important than the Python type alone.

---

# Recommended primary GOAT entity set

A mature GOAT device page could eventually expose the most important entities prominently:

```text
lawn_mower.goat
sensor.goat_battery
sensor.goat_area_mowed
sensor.goat_mowing_progress
sensor.goat_estimated_mowing_duration
```

when supported by the model.

Less commonly changed settings can remain configuration entities and may be disabled by default.

---

# Recommended configuration group

Potential advanced/configuration entities include:

```text
TrueDetect
AI recognition
smart avoidance
narrow passage adaptation
border behaviour
cutting direction
system volume
lifted-alarm volume
rain protection
rain delay
animal protection
animal protection schedule
```

These should not overwhelm the main mower controls.

---

# Recommended diagnostic/status group

Useful status and diagnostic entities include:

```text
battery
error
Wi-Fi RSSI
lifespan values
rain protection active
rain delay active
animal protection active
emergency stop
lock/security state
```

Not every raw protocol flag needs to be enabled by default.

Fields whose semantics remain unclear should normally remain hidden from normal users until better understood.

---

# `isPrepareDataSuccess`

Although:

```text
ProtectStateEvent.is_prepare_data_success
```

is available in the development parser, its user-facing meaning is not known.

Recommendation:

```text
Do not expose by default.
```

It may be useful for diagnostics during development, but a cryptic binary sensor would add little value to normal users.

---

# `isPinCode`

The same caution applies to:

```text
is_pin_code
```

until its exact meaning is established.

It should not be labelled:

```text
PIN enabled
```

or:

```text
PIN required
```

without evidence.

If exposed during research, it should be diagnostic and clearly labelled as an unresolved protocol state.

---

# Lock state

Likewise:

```text
is_locked
```

should not automatically replace or duplicate:

```text
child_lock
```

until their relationship is understood.

Home Assistant should avoid creating two apparently identical user-facing entities for protocol concepts whose semantics may differ.

---

# Capability-driven entity creation

The existing Ecovacs integration uses capability-driven entity creation.

Conceptually:

```text
Does device expose capability?
         │
       ┌─┴─┐
       │   │
      no  yes
       │   │
       ▼   ▼
 no entity entity created
```

This is particularly valuable for GOAT because mower models differ.

New entities should continue to follow this pattern rather than checking hard-coded model names wherever possible.

---

# Model-specific semantic flags

Sometimes the same generic event has different semantics on a mower model.

The progress implementation handles this with:

```text
CapabilityStats.mowing_job_progress
```

This is a useful pattern when semantics differ but the underlying event type can remain shared.

It is preferable to logic such as:

```python
if model == "O1200":
```

inside Home Assistant.

The client hardware profile should describe the capability whenever possible.

---

# Home Assistant should not parse ECOVACS payloads

Protocol-specific fields such as:

```text
mowedArea
isRainProtect
getRecognization
setAnimProtect
```

belong in:

```text
deebot_client
```

Home Assistant should ideally receive:

```text
StatsEvent.mowed_area
ProtectStateEvent.is_rain_protect
AiRecognitionEvent
AnimalProtectionEvent
```

This keeps protocol reverse-engineering isolated from integration presentation.

---

# Development dependency order

GOAT features should generally be added in this order:

```text
1. protocol understood
       │
       ▼
2. deebot_client implementation
       │
       ▼
3. deebot_client tests
       │
       ▼
4. hardware capability enabled
       │
       ▼
5. Home Assistant entity
       │
       ▼
6. Home Assistant tests/translations
```

Adding a Home Assistant entity before the client has a stable normalised capability should usually be avoided.

---

# Home Assistant test coverage

The mower development branch includes dedicated tests for:

```text
lawn mower state
start mowing
pause
dock
```

The progress work additionally tests:

```text
area mowed
mowing progress
estimated mowing duration
missing progress inputs
unit conversion
entity IDs
translation keys
unique IDs
```

This means the current mower/progress representation is tested at the Home Assistant entity layer in addition to the lower-level client tests.

---

# Current tested mower lifecycle

Home Assistant tests verify that:

```text
State.CLEANING
      │
      ▼
LawnMowerActivity.MOWING
```

and:

```text
State.DOCKED
      │
      ▼
LawnMowerActivity.DOCKED
```

They also verify that Home Assistant services invoke:

```text
Charge()
CleanV2(CleanAction.PAUSE)
CleanV2(CleanAction.START)
```

for the corresponding mower actions.

---

# Current implementation summary

## Implemented in Home Assistant mower work

Current branch support includes:

```text
GOAT lawn_mower entity
start mowing
pause
dock
mower-aware activity mapping
mower-specific statistic labels
battery
maintenance sensors
total mowing statistics
```

The progress development adds, when supported by the client model:

```text
current area mowed
mowing progress percentage
estimated mowing duration
```

## Already naturally supported by generic entity architecture

Existing GOAT capabilities can map through current generic platforms for features such as:

```text
TrueDetect → switch
border switch → switch
child lock → switch
move-up warning → switch
safe protect → switch
cut direction → number
volume → number
```

## Client features still requiring Home Assistant work

Newly researched capabilities include:

```text
AI recognition
Humanoid AI / smart avoidance
narrow adaptation
animal protection
rain configuration
lifted-alarm volume
runtime protection state
```

## Still requiring protocol/client work first

Do not yet implement speculative Home Assistant entities for:

```text
cutting height
mowing speed
GOAT mowing efficiency/mode
unverified zone control
unverified security-state meanings
```

---

# Recommended design principle

The Home Assistant integration should expose:

```text
what the mower means
```

rather than:

```text
what the original vacuum-oriented protocol calls it
```

Examples:

```text
State.CLEANING
      ↓
Mowing
```

```text
cleanings
      ↓
Mowings
```

```text
stats area
      ↓
Area mowed
```

while retaining protocol naming inside `deebot_client`.

This separation allows GOAT support to coexist cleanly with existing DEEBOT vacuum support.

---

# Relevant client source

## Progress development

* [`deebot_client/capabilities.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/capabilities.py)
* [`deebot_client/events/__init__.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/events/__init__.py)
* [`deebot_client/hardware/2i0fns.py`](https://github.com/monsivar/client.py/blob/feature/mower-stats-progress/deebot_client/hardware/2i0fns.py)

## Mower settings development

* [`deebot_client/capabilities.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/capabilities.py)
* [`deebot_client/hardware/2i0fns.py`](https://github.com/monsivar/client.py/blob/feature/ecovacs-mower-settings/deebot_client/hardware/2i0fns.py)

# Relevant Home Assistant development source

* [`homeassistant/components/ecovacs/lawn_mower.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/homeassistant/components/ecovacs/lawn_mower.py)
* [`homeassistant/components/ecovacs/sensor.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/homeassistant/components/ecovacs/sensor.py)
* [`homeassistant/components/ecovacs/switch.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/homeassistant/components/ecovacs/switch.py)
* [`homeassistant/components/ecovacs/number.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/homeassistant/components/ecovacs/number.py)
* [`homeassistant/components/ecovacs/select.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/homeassistant/components/ecovacs/select.py)
* [`homeassistant/components/ecovacs/binary_sensor.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/homeassistant/components/ecovacs/binary_sensor.py)

# Relevant Home Assistant tests

* [`tests/components/ecovacs/test_lawn_mower.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/tests/components/ecovacs/test_lawn_mower.py)
* [`tests/components/ecovacs/test_sensor.py`](https://github.com/monsivar/core/blob/feature/ecovacs-mower-progress/tests/components/ecovacs/test_sensor.py)

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
* [Known limitations](known-limitations.md)
