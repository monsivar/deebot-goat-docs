# Zone and area mowing

This page documents how selected-area mowing is represented in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py), and how the generic client concepts relate to ECOVACS GOAT mower zones.

Last reviewed against the upstream `dev` branch: **2026-08-23**.

## Overview

ECOVACS GOAT mowers can divide a lawn into separately selectable mowing areas in the ECOVACS app.

The app may present these areas as lawn zones or named areas.

`deebot_client`, however, uses generic abstractions originally shared with robotic vacuum cleaners:

```text
CleanArea
CleanAreaV2
CleanMode
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

The terminology therefore needs to be interpreted carefully.

For GOAT devices, an "area" in `deebot_client` may represent a mower zone or another selected mowing target.

It should not automatically be assumed that vacuum concepts such as "room" have the same semantic meaning on a mower.

---

# Capability model

Selected-area mowing is exposed through:

```text
Capabilities.clean.action.area
```

The generic capability definition allows the area command to be optional:

```python
CapabilityCleanAction(
    command=...,
    area=...,
)
```

Conceptually:

```text
CapabilityCleanAction
        │
        ├── command → normal mowing lifecycle
        │
        └── area    → selected-area start
```

The normal action command handles:

```text
START
PAUSE
RESUME
STOP
```

while the area command determines the target when starting a selected-area job.

Once started, the normal pause/resume/stop lifecycle can still apply.

---

# `CleanAreaV2`

The V2 implementation used by supported GOAT profiles is:

```text
CleanAreaV2
```

It extends:

```text
CleanV2
```

and accepts three important parameters:

```text
mode
area
cleanings
```

The Python constructor conceptually looks like:

```python
CleanAreaV2(
    mode,
    area,
    cleanings=1,
)
```

where:

* `mode` identifies the selection/mowing type
* `area` contains target identifiers or coordinates
* `cleanings` represents an operation count where relevant

The command is always created as a start operation.

---

# Protocol command

Because `CleanAreaV2` extends `CleanV2`, the ECOVACS command name remains:

```text
clean_V2
```

The area selection is placed inside the command's `content`.

The general structure is:

```json
{
  "act": "start",
  "content": {
    "type": "...",
    "value": "..."
  }
}
```

The exact interpretation of `value` depends on the selected `CleanMode`.

---

# `CleanMode`

The shared client currently defines:

```text
AUTO
SPOT_AREA
CUSTOM_AREA
FREE_CLEAN
```

with protocol values:

| Client mode   | Protocol value |
| ------------- | -------------- |
| `AUTO`        | `auto`         |
| `SPOT_AREA`   | `spotArea`     |
| `CUSTOM_AREA` | `customArea`   |
| `FREE_CLEAN`  | `freeClean`    |

These names originate from the generic ECOVACS protocol/client model.

They should not automatically be treated as the names used by the GOAT application.

---

# `SPOT_AREA`

For `SPOT_AREA`, `CleanAreaV2` joins the supplied area identifiers with commas.

Example:

```python
CleanAreaV2(
    CleanMode.SPOT_AREA,
    [5, 8],
)
```

produces command-specific content equivalent to:

```json
{
  "act": "start",
  "content": {
    "type": "spotArea",
    "value": "5,8"
  }
}
```

The upstream test suite labels this case:

```text
Rooms V2
```

because the same abstraction is used by vacuum robots.

For mower documentation, these numeric values should more neutrally be described as:

```text
selected area identifiers
```

until their exact GOAT-specific semantics are verified.

On a GOAT mower, they may correspond to lawn-zone identifiers rather than indoor room identifiers.

---

# Multiple selected areas

The generic implementation supports multiple values in the area list.

For example:

```python
[5, 8]
```

becomes:

```text
5,8
```

This demonstrates that the command format can represent more than one target identifier.

Conceptually:

```text
Selected targets
    │
    ├── 5
    └── 8
         │
         ▼
      "5,8"
```

Whether all GOAT models and firmware versions support multi-zone mowing through the same representation should be verified separately.

---

# `CUSTOM_AREA`

`CUSTOM_AREA` represents coordinate-based selection in the generic client.

Example:

```python
CleanAreaV2(
    CleanMode.CUSTOM_AREA,
    [
        1580.0,
        -4087.0,
        3833.0,
        -7525.0,
    ],
)
```

produces:

```json
{
  "act": "start",
  "content": {
    "type": "customArea",
    "value": "1580.0,-4087.0,3833.0,-7525.0"
  }
}
```

This format originates from the shared ECOVACS clean-area implementation.

The four values are treated by the existing code as custom-area coordinates.

## GOAT interpretation

The presence of `CUSTOM_AREA` in the shared command implementation does **not** by itself prove that arbitrary coordinate-based mowing is supported by all GOAT models.

Three levels must be distinguished:

```text
Generic command implementation exists
            │
            ▼
GOAT hardware profile exposes CleanAreaV2
            │
            ▼
Specific mode works on physical GOAT
```

Only the first two can be inferred directly from upstream source code.

Physical mower testing is required to confirm mower-specific coordinate behaviour.

---

# `FREE_CLEAN`

`FREE_CLEAN` has a slightly different payload format.

For this mode, `CleanAreaV2` prefixes the selected values with the requested number of cleanings/mowing passes.

Example:

```python
CleanAreaV2(
    CleanMode.FREE_CLEAN,
    [5, 8],
)
```

with the default:

```text
cleanings = 1
```

produces:

```json
{
  "act": "start",
  "content": {
    "type": "freeClean",
    "value": "1,5,8"
  }
}
```

The first value is therefore:

```text
1
```

followed by the selected identifiers:

```text
5,8
```

Conceptually:

```text
cleanings + selected targets
       │
       ▼
   1 + 5 + 8
       │
       ▼
    "1,5,8"
```

---

# Repeated operation example

The upstream test suite also verifies:

```python
CleanAreaV2(
    CleanMode.FREE_CLEAN,
    [0],
    cleanings=2,
)
```

which produces:

```json
{
  "act": "start",
  "content": {
    "type": "freeClean",
    "value": "2,0"
  }
}
```

The upstream test describes this as:

```text
FreeClean single room 2x
```

Again, "room" is generic vacuum terminology from the shared test suite.

For a mower, it is safer to describe the structure as:

```text
two operations/passes for selected target 0
```

unless GOAT-specific behaviour has been confirmed.

---

# Zone mowing observed on a physical GOAT

Selected-zone mowing has been observed during physical GOAT testing for this documentation project.

A single lawn zone was selected in the ECOVACS application and started as its own mowing job.

The resulting mower behaviour confirmed that:

* a defined lawn zone can be selected independently
* the mower can start a job scoped to that selection
* the resulting job uses the normal mowing lifecycle
* pause is possible during the selected-zone job
* the job can be resumed
* the job can be stopped

Observed workflow:

```text
Select one lawn zone
       │
       ▼
Start zone mowing
       │
       ▼
Mowing selected zone
       │
       ▼
Pause
       │
       ▼
Resume
       │
       ▼
Stop
```

Evidence:

**Device tested / protocol observed**

The test confirms the user-facing behaviour of selected-zone mowing.

Further protocol documentation is required before claiming a universal mapping between an ECOVACS app zone identifier and every generic `CleanAreaV2` mode.

---

# Zone name versus zone identifier

The ECOVACS app can display human-readable names for lawn zones.

At protocol level, mowing commands normally require identifiers or encoded target values rather than the human-readable label itself.

Conceptually:

```text
ECOVACS app
"Front lawn"
     │
     ▼
internal zone identifier
     │
     ▼
CleanAreaV2 payload
```

This distinction is important for integrations.

A user interface ideally exposes:

```text
Front lawn
Back lawn
Side lawn
```

while the underlying client sends the identifiers expected by the mower.

The human-readable name should therefore be treated as metadata associated with a protocol-level zone ID.

---

# Area lists are not names

`CleanAreaV2` currently accepts:

```python
list[int | float]
```

rather than strings representing area names.

This strongly indicates that the low-level operation expects:

* numeric area identifiers
* coordinate values
* or another numeric representation

depending on `CleanMode`.

The Python API therefore separates:

```text
human-readable area metadata
```

from:

```text
numeric command target
```

Integrations should maintain the mapping between the two where zone names are available.

---

# Area mowing support by model

Current upstream hardware profiles expose `CleanAreaV2` for:

| Model                | `CleanAreaV2` |
| -------------------- | :-----------: |
| GOAT G1              |       ✓       |
| GOAT A1600 RTK       |       ✓       |
| GOAT A3000 LiDAR Pro |       ✓       |
| GOAT O500 Panorama   |       ✓       |
| GOAT O1200 LiDAR     |       —       |

The O1200 profile currently contains:

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

The other four reviewed profiles expose both the normal command and area command.

---

# Important O1200 distinction

The missing area capability in the current O1200 hardware profile should **not** be interpreted as proof that the physical mower cannot mow named zones.

It means only:

> The current upstream O1200 `deebot_client` hardware profile does not expose `CleanAreaV2` through `CapabilityCleanAction.area`.

Possible explanations include:

1. the O1200 uses a different protocol representation
2. area mowing has not yet been implemented for this profile
3. the feature requires additional map/zone information
4. the feature behaves differently from other GOAT models
5. the feature exists in the mower/app but is not yet represented by the client

This should remain an open implementation question until confirmed by protocol evidence or testing.

---

# Starting an area job versus controlling it

Area selection is mainly relevant when the job starts.

Once the job is active, the normal control lifecycle remains conceptually separate.

```text
CleanAreaV2(...)
       │
       ▼
Selected-zone job starts
       │
       ├── Pause
       │
       ├── Resume
       │
       └── Stop
```

Those subsequent lifecycle actions are handled through the normal `CleanV2` action mechanism.

This means an integration does not necessarily require separate zone-specific versions of:

```text
Pause
Resume
Stop
```

The selected target belongs to the active mowing job.

---

# Status parsing and custom areas

The common `GetCleanInfo` parser contains handling for:

```text
customArea
```

When it encounters a custom-area operation, it extracts the associated area values.

The implementation currently logs them as:

```text
Last custom area values (x1,y1,x2,y2)
```

This further confirms that `CUSTOM_AREA` in the generic client is treated as coordinate-based selection.

However, this code belongs to the shared ECOVACS client and should not be used alone as evidence that coordinate mowing is available on every GOAT model.

---

# Integration design

A mower-oriented integration should avoid exposing generic vacuum terminology directly to users.

Instead of:

```text
Clean room
Spot area
Free clean
```

a GOAT integration should ideally expose concepts such as:

```text
Mow lawn
Mow zone
Select zones
Mow selected area
```

depending on which protocol behaviours have actually been verified.

## Suggested architecture

Conceptually:

```text
User selects:
"Front lawn"
"Back lawn"
       │
       ▼
Integration resolves zone IDs
       │
       ▼
deebot_client area capability
       │
       ▼
CleanAreaV2
       │
       ▼
ECOVACS mower
```

This keeps mower-specific terminology in the integration while allowing the shared client to retain its generic protocol abstractions.

---

# Evidence summary

## Upstream implemented

Confirmed in upstream source:

* `CapabilityCleanAction.area`
* `CleanAreaV2`
* `CleanMode.SPOT_AREA`
* `CleanMode.CUSTOM_AREA`
* `CleanMode.FREE_CLEAN`
* multiple selected identifiers
* coordinate-based custom-area payloads
* `cleanings` prefix for `FREE_CLEAN`
* area capability on four reviewed GOAT profiles

## Upstream tested

The upstream test suite verifies payload construction for:

* `spotArea`
* multiple target identifiers
* `customArea`
* coordinate values
* `freeClean`
* repeated `freeClean` operation

## Device tested / protocol observed

Physical GOAT testing confirms:

* selection of a defined lawn zone in the ECOVACS app
* starting a mowing job for that zone
* pause during the selected-zone job
* resume
* stop

## Not yet fully established

The following require further GOAT-specific investigation:

* exact mapping between app zone IDs and `SPOT_AREA`
* whether `FREE_CLEAN` has a mower-specific meaning
* whether `CUSTOM_AREA` is usable for arbitrary GOAT coordinates
* how human-readable zone names are retrieved
* multi-zone behaviour on each mower model
* O1200 area-mowing protocol
* whether mowing order can be specified for multiple zones
* whether per-zone mower settings can be attached to a job

---

# Relevant upstream source files

* [`deebot_client/capabilities.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/capabilities.py)
* [`deebot_client/models.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/models.py)
* [`deebot_client/commands/json/clean.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/clean.py)
* [`tests/commands/json/test_clean.py`](https://github.com/DeebotUniverse/client.py/blob/dev/tests/commands/json/test_clean.py)

## Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* [Mowing control](mowing-control.md)
* Progress and statistics *(planned)*
* Protocol reference *(planned)*
* Home Assistant integration *(planned)*
