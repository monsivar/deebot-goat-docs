# Mowing control

This page documents the basic mowing-control operations used by ECOVACS GOAT mowers in [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py).

Last reviewed against the upstream `dev` branch: **2026-08-23**.

The focus of this page is:

* start mowing
* pause mowing
* resume mowing
* stop mowing
* return to charging station
* how these actions affect the normalised mower state

Zone and area selection are documented separately because they add additional protocol parameters on top of the basic mowing actions.

## Terminology

`deebot_client` was originally designed around robotic vacuum cleaners, and the shared API therefore uses terminology such as:

```text
clean
CleanAction
CleanMode
CLEANING
```

For a GOAT mower these should generally be interpreted as:

| `deebot_client` term | GOAT meaning           |
| -------------------- | ---------------------- |
| clean                | mow                    |
| cleaning             | mowing                 |
| clean action         | mowing action          |
| clean mode           | mowing mode            |
| clean area           | mow selected area/zone |

The underlying names are retained in this documentation when referring to actual Python classes, enums or protocol commands.

## Basic architecture

GOAT mower control is exposed through:

```text
Capabilities.clean.action
```

The mower hardware profiles use:

```python
CapabilityClean(
    action=CapabilityCleanAction(
        command=CleanV2,
        ...
    ),
)
```

`CleanV2` is therefore the central command implementation for the normal mowing lifecycle.

The protocol command name is:

```text
clean_V2
```

## Supported actions

The common `CleanAction` enum defines four actions:

```text
START
PAUSE
RESUME
STOP
```

Their JSON values are:

| Action               | Protocol value |
| -------------------- | -------------- |
| `CleanAction.START`  | `start`        |
| `CleanAction.PAUSE`  | `pause`        |
| `CleanAction.RESUME` | `resume`       |
| `CleanAction.STOP`   | `stop`         |

Return to station is not part of `CleanAction`.

It uses the separate `Charge` command.

---

# Start mowing

A normal mowing operation is started with:

```python
CleanV2(CleanAction.START)
```

The `CleanV2` implementation constructs content equivalent to:

```json
{
  "act": "start",
  "content": {
    "type": "auto"
  }
}
```

The surrounding ECOVACS request envelope is omitted here because this documentation focuses on the command-specific payload.

The default mowing type is based on:

```text
CleanMode.AUTO
```

whose protocol value is:

```text
auto
```

## Expected state

When the mower reports that it is actively working, the shared state parser converts this to:

```text
State.CLEANING
```

For mower integrations, this should normally be presented to users as something equivalent to:

```text
Mowing
```

rather than "Cleaning".

---

# Pause mowing

An active mowing operation can be paused with:

```python
CleanV2(CleanAction.PAUSE)
```

The command-specific payload is equivalent to:

```json
{
  "act": "pause",
  "content": {
    "type": ""
  }
}
```

When mower status subsequently reports:

```text
motionState = "pause"
```

the shared parser generates:

```text
State.PAUSED
```

This provides a normalised paused state to integrations consuming the client.

## Device observation

Pause was exercised during physical-device testing for this documentation project as part of a complete mowing sequence.

The observed sequence was:

```text
Start mowing
    ↓
Mower begins working
    ↓
Pause
    ↓
Mower stops mowing but keeps the current job
```

The job can then be continued with the resume operation.

Status:

**Device tested**

---

# Resume mowing

A paused mowing operation can be resumed with:

```python
CleanV2(CleanAction.RESUME)
```

The command-specific structure is equivalent to:

```json
{
  "act": "resume",
  "content": {}
}
```

Resume differs from start because it is intended to continue the currently paused mowing job rather than create a completely new one.

## State-aware start/resume handling

The shared `Clean` implementation includes logic to handle common start/resume mismatches.

If an integration requests:

```text
RESUME
```

but the last known state is **not**:

```text
PAUSED
```

the implementation changes the requested action to:

```text
START
```

The reverse also applies.

If an integration requests:

```text
START
```

while the latest known state is:

```text
PAUSED
```

the command is changed to:

```text
RESUME
```

Conceptually:

```text
Requested RESUME
      │
      ├── state = PAUSED ──────► RESUME
      │
      └── state != PAUSED ─────► START
```

and:

```text
Requested START
      │
      ├── state = PAUSED ──────► RESUME
      │
      └── state != PAUSED ─────► START
```

This behaviour makes higher-level integrations more tolerant of differences between the requested action and the current mower state.

## Device observation

Resume was tested as part of the same physical mower sequence:

```text
Start
  ↓
Pause
  ↓
Resume
  ↓
Mowing continues
```

Status:

**Device tested**

---

# Stop mowing

A mowing operation can be terminated with:

```python
CleanV2(CleanAction.STOP)
```

The command-specific payload is equivalent to:

```json
{
  "act": "stop",
  "content": {
    "type": ""
  }
}
```

Stop is semantically different from pause.

A paused job is intended to remain resumable.

A stopped job should be treated as terminated.

Conceptually:

```text
PAUSE
  │
  └──► retain job ──► RESUME

STOP
  │
  └──► terminate job
```

## ECOVACS app behaviour

The ECOVACS application may request user confirmation before stopping an active mowing task.

That confirmation belongs to the app/user-interface layer.

The protocol operation itself is represented by the `stop` mowing action.

An integration such as Home Assistant may choose whether it wants to add its own confirmation layer.

## Device observation

Stop was tested on the physical mower after a start → pause → resume sequence.

Observed sequence:

```text
Start
  ↓
Pause
  ↓
Resume
  ↓
Stop
  ↓
Confirm stop in ECOVACS app
  ↓
Current mowing job ends
```

Status:

**Device tested**

---

# Return to charging station

Returning the mower to its charging station is not implemented through:

```text
CleanAction
```

Instead, GOAT hardware profiles expose:

```python
charge=CapabilityExecute(Charge)
```

The protocol command name is:

```text
charge
```

and the command-specific arguments are:

```json
{
  "act": "go"
}
```

For a mower this should normally be understood as:

```text
Return to dock / charging station
```

rather than simply "charge".

## Successful return command

When the `Charge` command receives a successful response, `deebot_client` generates:

```text
State.RETURNING
```

Conceptually:

```text
Charge()
   ↓
{"act": "go"}
   ↓
Mower starts returning
   ↓
State.RETURNING
```

## Already docked

The command handler recognises ECOVACS response code:

```text
30007
```

as meaning that the device is already charging.

In that case the client generates:

```text
State.DOCKED
```

instead of treating the response as a command failure.

## Device observation

Return-to-dock was also exercised independently during physical-device testing.

The user-facing ECOVACS app action labelled as docking/returning corresponded to the mower leaving its current activity and returning toward its station.

Status:

**Device tested**

---

# Charging-state refresh

GOAT hardware profiles also use:

```text
GetChargeState
```

to retrieve charging state.

Its ECOVACS command name is:

```text
getChargeState
```

When returned data contains:

```json
{
  "isCharging": 1
}
```

the client generates:

```text
State.DOCKED
```

This means that docking state can be derived both from:

* the immediate response to a return-to-station command
* later charging-state refreshes

---

# Operational states

The shared client state model currently contains:

| State       | Mower interpretation |
| ----------- | -------------------- |
| `IDLE`      | Mower idle           |
| `CLEANING`  | Mowing               |
| `RETURNING` | Returning to station |
| `DOCKED`    | Docked / charging    |
| `ERROR`     | Error state          |
| `PAUSED`    | Mowing paused        |

The Python enum names are generic and shared with vacuum robots.

An integration should normally translate these into mower-appropriate user-facing labels.

For example:

```text
State.CLEANING  → Mowing
State.RETURNING → Returning to dock
State.DOCKED    → Docked
State.PAUSED    → Paused
```

---

# Status from `GetCleanInfoV2`

The reviewed GOAT profiles use:

```text
GetCleanInfoV2
```

along with:

```text
GetChargeState
```

to establish current device state.

The ECOVACS command name for the mowing information request is:

```text
getCleanInfo_V2
```

The shared parser currently recognises several protocol conditions.

## Active mowing

When the returned high-level state indicates an active operation and:

```text
motionState = "working"
```

the client reports:

```text
State.CLEANING
```

## Paused

When:

```text
motionState = "pause"
```

the client reports:

```text
State.PAUSED
```

## Returning

When:

```text
motionState = "goCharging"
```

or the top-level state is:

```text
goCharging
```

the client reports:

```text
State.RETURNING
```

## Idle

When the top-level state is:

```text
idle
```

the client reports:

```text
State.IDLE
```

## Error

The common parser can also convert alert-triggered status into:

```text
State.ERROR
```

---

# Observed control sequence

A complete control sequence was captured during physical GOAT testing for this project.

The tested workflow was:

```text
Start mowing
      │
      ▼
Mowing
      │
      ▼
Pause
      │
      ▼
Paused
      │
      ▼
Resume
      │
      ▼
Mowing
      │
      ▼
Stop
      │
      ▼
Job terminated
```

Return to station was also tested as a separate action:

```text
Dock / return command
      │
      ▼
Returning
      │
      ▼
Docked
```

These observations are useful because they confirm that the command/state concepts found in the source code correspond to actual GOAT behaviour.

However, the physical test was initiated through the ECOVACS app while protocol behaviour was being observed.

Therefore this evidence should be interpreted as:

**Device behaviour and protocol flow confirmed**

rather than automatically implying that every action has independently been exercised through every consuming integration.

---

# Control capability summary

| User action       | Client command   | Action/value     | Expected state          |
| ----------------- | ---------------- | ---------------- | ----------------------- |
| Start mowing      | `CleanV2`        | `start`          | `CLEANING`              |
| Pause mowing      | `CleanV2`        | `pause`          | `PAUSED`                |
| Resume mowing     | `CleanV2`        | `resume`         | `CLEANING`              |
| Stop mowing       | `CleanV2`        | `stop`           | normally idle/job ended |
| Return to station | `Charge`         | `go`             | `RETURNING`             |
| Charging/docked   | `GetChargeState` | `isCharging = 1` | `DOCKED`                |

The exact timing of state updates depends on responses and subsequent status messages from the mower.

---

# Whole-lawn versus selected-area mowing

Basic mowing control and area selection are related but separate concepts.

A general start operation uses:

```text
CleanV2
```

with automatic mode.

Some GOAT hardware profiles additionally expose:

```text
CleanAreaV2
```

for selected-area operations.

Area mowing adds parameters identifying the mowing mode and target area.

The start/pause/resume/stop lifecycle can still be conceptually separated from the initial choice of what should be mowed.

For example:

```text
Choose mowing target
       │
       ├── Whole lawn
       │
       └── Selected area/zone
              │
              ▼
         Start operation
              │
        ┌─────┴─────┐
        ▼           ▼
      Pause        Stop
        │
        ▼
      Resume
```

Detailed zone behaviour is documented in:

```text
zones-and-areas.md
```

---

# Stop versus return to station

Applications should not assume that:

```text
STOP
```

and:

```text
RETURN TO STATION
```

are the same operation.

They are represented by separate protocol commands.

```text
Stop mowing
    │
    ▼
CleanV2(STOP)
```

versus:

```text
Return to station
    │
    ▼
Charge()
```

Depending on mower behaviour and firmware, stopping a job may leave the mower idle rather than immediately instructing it to return to the dock.

If an automation explicitly requires docking, it should use the charging/return capability.

---

# Integration considerations

An integration exposing GOAT controls should ideally provide separate actions for:

* Start
* Pause
* Resume
* Stop
* Return to dock

It may simplify Start and Resume into a single user-facing control because the shared command implementation already contains state-aware start/resume handling.

However, preserving the distinction internally remains useful.

## Suggested state mapping

A mower-oriented interface could map states as follows:

| Client state | Suggested UI label |
| ------------ | ------------------ |
| `IDLE`       | Idle               |
| `CLEANING`   | Mowing             |
| `PAUSED`     | Paused             |
| `RETURNING`  | Returning          |
| `DOCKED`     | Docked             |
| `ERROR`      | Error              |

## Confirmation for stop

The official ECOVACS app uses an explicit confirmation step when stopping an active mowing job in the tested workflow.

This is a user-interface decision rather than a requirement of `CleanV2`.

Third-party integrations may choose to provide a similar safeguard.

---

# Evidence summary

## Upstream implemented

Confirmed in current upstream source:

* `CleanAction.START`
* `CleanAction.PAUSE`
* `CleanAction.RESUME`
* `CleanAction.STOP`
* `CleanV2`
* `Charge`
* `GetChargeState`
* `GetCleanInfoV2`
* `State.CLEANING`
* `State.PAUSED`
* `State.RETURNING`
* `State.DOCKED`
* state-aware START/RESUME conversion

## Physically verified GOAT O1200 control — PR #1791

[`DeebotUniverse/client.py PR #1791`](https://github.com/DeebotUniverse/client.py/pull/1791) implements and verifies model-specific mower controls for the **ECOVACS GOAT O1200 LiDAR (`2i0fns`)**:

* **Wire command:** Uses `clean` rather than `clean_V2`.
* **Automatic mowing (`GoatClean`):**
  - Start: `{"act": "start", "content": {"type": "auto"}}`
  - Pause: `{"act": "pause", "content": {"type": "auto"}}`
  - Resume: `{"act": "resume", "content": {"type": "auto"}}`
  - Stop: `{"act": "stop", "content": {"type": "auto"}}`
* **Area mowing (`GoatCleanArea`):**
  - Single area: `{"act": "start", "content": {"type": "spotArea", "value": 1}}`
  - Multi-area: `{"act": "start", "content": {"type": "spotArea", "value": "1,2"}}` (preserves specified area order)
  - Pause/Resume/Stop: `{"act": "pause", "content": {"type": "spotArea"}}` (preserves active `spotArea` content type)
* **Mode tracking (`GoatCleanModeEvent`):** Dynamically tracks active mode (`auto` or `spotArea`) from `onCleanInfo` push events to ensure subsequent pause/resume/stop commands send matching content types.
* **Fail-closed validation:** Rejects vacuum-specific modes (`customArea`, `freeClean`), non-integer area IDs, empty lists, and `cleanings != 1`.
* **Physical device verification:** Two full command lifecycles physically verified against a live O1200 mower returning `ret=ok` across all transitions:
  1. Automatic mowing: START $\rightarrow$ PAUSE $\rightarrow$ RESUME $\rightarrow$ STOP.
  2. Multi-area mowing: areas 1,2 START $\rightarrow$ PAUSE $\rightarrow$ RESUME $\rightarrow$ STOP.

### PR #1791 summary and file breakdown

| Component | Scope | Upstream PR files |
| :--- | :--- | :--- |
| Mower commands | `GoatClean`, `GoatCleanArea` implementations | `deebot_client/commands/json/clean.py` |
| Event model | `GoatCleanModeEvent` mode tracking | `deebot_client/events/__init__.py` |
| Hardware wiring | O1200 clean capability mapping | `deebot_client/hardware/2i0fns.py` |
| Unit tests | 49 comprehensive mower control unit tests | `tests/hardware/test_2i0fns_clean.py` |

## Device tested / protocol observed

Observed during physical mower testing for this research:

* start mowing (auto & multi-area)
* pause active job (preserving active mode)
* resume paused job (preserving active mode)
* stop active job (preserving active mode)
* ECOVACS-app stop confirmation
* return to dock

## To document separately

The following related functionality is intentionally kept out of this page:

* zone identifiers
* selected-zone mowing
* area payloads
* mowing progress
* estimated job duration
* percentage complete
* mowing statistics
* scheduled mowing
* mower settings

These are covered by separate documentation pages.

---

# Relevant upstream source files

The main upstream files for this functionality are:

* [`deebot_client/capabilities.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/capabilities.py)
* [`deebot_client/models.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/models.py)
* [`deebot_client/commands/json/clean.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/clean.py)
* [`deebot_client/commands/json/charge.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/charge.py)
* [`deebot_client/commands/json/charge_state.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/commands/json/charge_state.py)

## Related documentation

* [Supported models](supported-models.md)
* [Capability architecture](capabilities.md)
* Zone and area mowing *(next/planned)*
* Progress and statistics *(planned)*
* Home Assistant integration *(planned)*
