# Supported GOAT mower models

This page documents ECOVACS GOAT mower models that currently have dedicated hardware profiles in the upstream [`DeebotUniverse/client.py`](https://github.com/DeebotUniverse/client.py) project.

Last reviewed against the upstream `dev` branch: **2026-08-23**.

## What "supported" means here

A model being listed on this page means that `deebot_client` contains a dedicated hardware profile for that model and identifies it as a mower.

It does **not** mean that every feature available in the ECOVACS app is currently implemented.

There are several different layers of support:

* the mower can be identified by `deebot_client`
* common mower commands can be issued
* status and events can be parsed
* individual settings can be read or changed
* model-specific features may or may not yet be implemented

The hardware profiles are therefore best interpreted as a description of what the Python client currently exposes, rather than a complete description of what the physical mower itself can do.

## Upstream mower profiles

The following dedicated mower profiles are currently present upstream.

| Model                        | Hardware identifier | Hardware profile                                                                                                            |
| ---------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| ECOVACS GOAT G1              | `5xu9h3`            | [`deebot_client/hardware/5xu9h3.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/hardware/5xu9h3.py) |
| ECOVACS GOAT A1600 RTK       | `xmp9ds`            | [`deebot_client/hardware/xmp9ds.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/hardware/xmp9ds.py) |
| ECOVACS GOAT A3000 LiDAR Pro | `51rcxt`            | [`deebot_client/hardware/51rcxt.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/hardware/51rcxt.py) |
| ECOVACS GOAT O500 Panorama   | `300lc5`            | [`deebot_client/hardware/300lc5.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/hardware/300lc5.py) |
| ECOVACS GOAT O1200 LiDAR     | `2i0fns`            | [`deebot_client/hardware/2i0fns.py`](https://github.com/DeebotUniverse/client.py/blob/dev/deebot_client/hardware/2i0fns.py) |

All of these profiles use:

```python
device_type=DeviceType.MOWER
```

This is important because mower devices are explicitly separated from vacuum devices in the common capability model.

## Upstream capability comparison

The table below compares capabilities currently declared by the hardware profiles.

A check mark means the capability is connected in the upstream hardware profile. It does not necessarily mean that every possible behaviour of that feature has been tested on every physical mower model.

| Capability                    |  G1 | A1600 RTK | A3000 LiDAR Pro | O500 Panorama | O1200 LiDAR |
| ----------------------------- | :-: | :-------: | :-------------: | :-----------: | :---------: |
| Availability                  |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Battery                       |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Return to / charge at station |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| General mowing action         |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Area mowing via `CleanAreaV2` |  ✓  |     ✓     |        ✓        |       ✓       |      —      |
| Custom command support        |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Error reporting               |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Network information           |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Play sound                    |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Current mower state           |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Mowing statistics             |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Total statistics              |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |
| Consumable lifetime           |  ✓  |     ✓     |        ✓        |       ✓       |      ✓      |

## Common mower actions

The upstream mower profiles currently use the JSON mower command family.

For general mowing, the profiles use:

```python
CleanV2
```

For G1, A1600 RTK, A3000 LiDAR Pro and O500 Panorama, the hardware profiles also expose:

```python
CleanAreaV2
```

as the area-specific mowing command.

The O1200 LiDAR profile currently exposes `CleanV2`, but does **not** connect `CleanAreaV2` to its `CapabilityCleanAction`.

This difference should be interpreted carefully.

It means:

> Area mowing is not currently exposed through the O1200 hardware capability profile in upstream `deebot_client`.

It does **not** by itself prove that the physical O1200 mower or ECOVACS protocol is incapable of zone or area mowing.

Protocol observations and device testing should be used to determine whether this is an implementation gap or an intentional model difference.

## Common state handling

All five profiles currently construct their general mower state from:

```python
GetChargeState()
GetCleanInfoV2()
```

This allows charging state and current mowing information to contribute to the common `StateEvent`.

More detailed mowing progress and job information may be available through additional events or protocol messages and is documented separately.

## Common settings

The five upstream mower profiles currently expose the same basic settings set.

### Advanced mode

```text
GetAdvancedMode
SetAdvancedMode
```

Capability:

```text
advanced_mode
```

### Border switch

```text
GetBorderSwitch
SetBorderSwitch
```

Capability:

```text
border_switch
```

### Cutting direction

```text
GetCutDirection
SetCutDirection
```

Capability:

```text
cut_direction
```

Unlike most settings in this group, cutting direction is not represented simply as a boolean enable/disable capability.

### Child lock

```text
GetChildLock
SetChildLock
```

Capability:

```text
child_lock
```

### Move-up warning

```text
GetMoveUpWarning
SetMoveUpWarning
```

Capability:

```text
moveup_warning
```

### Cross-map border warning

```text
GetCrossMapBorderWarning
SetCrossMapBorderWarning
```

Capability:

```text
cross_map_border_warning
```

### Safe protect

```text
GetSafeProtect
SetSafeProtect
```

Capability:

```text
safe_protect
```

### TrueDetect

```text
GetTrueDetect
SetTrueDetect
```

Capability:

```text
true_detect
```

### Volume

```text
GetVolume
SetVolume
```

Capability:

```text
volume
```

These names originate from the ECOVACS/deebot protocol and do not always directly match the wording used in the ECOVACS mobile application.

Their mower-specific meaning should therefore be documented from actual device behaviour rather than inferred only from the command name.

## Consumable lifetime differences

Most of the upstream GOAT profiles currently expose two mower-specific lifetime types:

```text
BLADE
LENS_BRUSH
```

This applies to:

* GOAT G1
* GOAT A1600 RTK
* GOAT A3000 LiDAR Pro
* GOAT O500 Panorama

The O1200 LiDAR profile additionally exposes:

```text
WEED_ROPE
TRIMMER_BRUSH
```

Its complete upstream lifetime set is therefore:

```text
BLADE
LENS_BRUSH
WEED_ROPE
TRIMMER_BRUSH
```

The presence of a lifetime type in the client indicates that the protocol/client can represent its maintenance state. It should not automatically be interpreted as proof that every retail configuration of the mower physically includes the corresponding accessory.

## Statistics

All five mower profiles expose the same three statistics-related event groups:

```text
StatsEvent
ReportStatsEvent
TotalStatsEvent
```

The hardware profiles use:

```text
GetStats
GetTotalStats
```

while `ReportStatsEvent` is available for reported/pushed statistics without a refresh command declared in these profiles.

The exact mower-specific fields carried by these events are documented separately in the progress and statistics documentation.

## Capabilities not yet sufficient for feature completeness

A dedicated hardware profile does not guarantee complete access to all app features.

Examples of mower functionality that may require additional protocol research or implementation include:

* mowing progress
* estimated job duration
* detailed zone information
* cutting height
* mowing speed or efficiency settings
* rain delay
* rain protection state
* obstacle-recognition behaviour
* AI-related settings
* animal protection
* narrow-area adaptation
* scheduling
* map-specific mower functions
* other model-specific settings

Some of these capabilities have already been observed or implemented in development work outside the current upstream `dev` profile and will be documented separately.

## Model differences should be evidence-based

GOAT models differ in navigation hardware, accessories and available app features.

However, documentation in this repository should avoid assuming that a marketing difference automatically implies a protocol difference.

A model-specific difference should preferably be supported by at least one of:

1. a different upstream hardware profile
2. a different command or event implementation
3. a different protocol payload
4. reproducible physical-device testing
5. reproducible ECOVACS app behaviour

When the evidence is incomplete, the feature should be marked as **Unverified** rather than presented as a confirmed model limitation.

## Current upstream summary

At the time of this review:

* five dedicated GOAT mower hardware profiles are present
* all five are explicitly identified as `DeviceType.MOWER`
* all five support the common `CleanV2` mowing action
* four profiles expose `CleanAreaV2` for area mowing
* the O1200 LiDAR profile does not currently expose `CleanAreaV2`
* all five expose the same common settings group
* all five expose mower statistics and total statistics
* all five expose blade and lens-brush lifetime information
* O1200 LiDAR additionally exposes weed-rope and trimmer-brush lifetime information

Future upstream changes may alter this matrix.
