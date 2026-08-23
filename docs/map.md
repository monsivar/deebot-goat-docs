# GOAT mower map support

This page documents the current GOAT mower map architecture and the stacked development work represented by:

- [`PR #1567 — add OnMapTrace for mower firmware`](https://github.com/DeebotUniverse/client.py/pull/1567)
- [`PR #1782 — parse mower onMI static map geometry`](https://github.com/DeebotUniverse/client.py/pull/1782)
- [`PR #1788 — parse GOAT work areas and zone metadata`](https://github.com/DeebotUniverse/client.py/pull/1788)
- [`PR #1789 — integrate GOAT static maps into shared Map capability`](https://github.com/DeebotUniverse/client.py/pull/1789)
- [`Issue #1785 — GOAT mower map support roadmap`](https://github.com/DeebotUniverse/client.py/issues/1785)

Last reviewed: **2026-08-24**

> [!IMPORTANT]
> This is a development stack.
>
> PR #1567 is open. PRs #1782, #1788 and #1789 are stacked drafts and are not ready for merge.
>
> The current stack implements a **static map MVP**, not complete GOAT map support.

## Current status at a glance

| Layer | Source | Current development status |
| --- | --- | --- |
| Shared mower grouped geometry | #1567 | Implemented/tested in open PR |
| Mower `onMapTrace` parser | #1567 | Implemented/tested; not part of static MVP rendering |
| O1200 static main boundary | #1782 | Implemented/tested in stacked draft |
| O1200 work-area geometry | #1788 | Implemented/tested in stacked draft |
| O1200 area IDs/names for map join | #1788 | Implemented/tested in stacked draft |
| Local-area → static-map registration | #1788 | Implemented/tested in stacked draft |
| Shared `Map` capability support for mower geometry | #1789 | Implemented/tested in stacked draft |
| SVG boundary + work-area rendering | #1789 | Implemented/tested in stacked draft |
| O1200 hardware capability wiring | — | Not yet implemented in #1789 |
| Acquisition/session lifecycle | research only | Not implemented in Map capability |
| Mower live-position overlay | research only | Coordinate transform not proven |
| Dock overlay | research only | Not implemented |
| `onMapTrack` live mowing plan rendering | research only | Not implemented |
| Map editing/write support | research only | Not implemented |
| Home Assistant map compatibility | — | Not implemented by this stack |

---

# Architecture

The intended static-map path is:

```text
ECOVACS GOAT
    │
    ├── onMI
    │     │
    │     ▼
    │  static main boundary
    │
    ├── onArI
    │     │
    │     ▼
    │  local work-area geometry
    │
    └── getAreaSet type="ar"
          │
          ▼
       area IDs + names

              │
              ▼
     register work areas into
       static-map coordinates
              │
              ▼
    MowerStaticMapEvent
    MowerWorkAreasEvent
              │
              ▼
      CapabilityMowerMap
              │
              ▼
       shared Python Map
              │
              ▼
       shared Rust renderer
              │
              ▼
        Map.get_svg_map()
```

The public rendering path remains the same as for existing map consumers:

```text
device.capabilities.map
        │
        ▼
device.map
        │
        ▼
Map.get_svg_map()
```

The mower stack does **not** introduce a parallel public mower-map API.

---

# Design principle: one mower geometry representation

Issue #1785 and PR #1567 establish one shared typed representation:

```text
group
  │
  └── segments
        │
        └── points
```

Python:

```text
MowerMapTraceGroup
MowerMapTraceSegment
```

A segment contains:

```python
points: list[tuple[int, int]]
raw: str | None
```

The original firmware geometry record is retained as:

```text
raw
```

so future research can re-check assumptions without making the raw device envelope part of the public event model.

This representation is reused by:

```text
onMapTrace
onMI static boundary
onArI work areas
Map rendering
```

The goal is to avoid separate incompatible coordinate models for every GOAT message family.

---

# PR #1567 — shared mower trace geometry

PR #1567 was originally motivated by mower firmware pushing:

```text
onMapTrace
```

with a schema completely different from the existing vacuum-oriented:

```text
GetMapTrace
```

response.

Observed source model in the PR:

```text
GOAT A1600 RTK
firmware 1.15.13
```

The same work was also informed by O1200 capture analysis.

## Mower `onMapTrace`

The observed mower envelope contains fields such as:

```text
mid
batid
serial
index
type
info
infoSize
```

where:

```text
info
```

contains Base64-encoded compressed data.

The decoded JSON contains groups with one or more coordinate segments.

Conceptually:

```json
[
  [
    "5",
    "0;-11850,-28849;-11800,-28899;...",
    "0;-12850,-23699;..."
  ],
  [
    "6",
    "0;-7899,-39700;..."
  ]
]
```

PR #1567 preserves this as structured mower geometry rather than reducing it to one undifferentiated string.

## Chunk reassembly

Mower `onMapTrace` can be chunked.

The parser:

```text
collects index chunks
      │
      ▼
requires a contiguous sequence from 0
      │
      ▼
joins compressed bytes
      │
      ▼
decompresses the complete stream
      │
      ▼
emits one complete MowerMapTraceEvent
```

The PR includes bounded buffering and tests for:

```text
out-of-order chunks
incomplete streams
new-cycle reset
independent concurrent keys
per-key memory limits
global memory limits
```

## Compatibility projection

PR #1567 also emits a flattened:

```text
MapTraceEvent
```

for existing legacy consumers.

That compatibility projection is separate from the typed mower event.

The static map stack described below uses the typed grouped geometry model as its source of truth.

## Scope

PR #1567 deliberately removed mower-specific SVG rendering after review.

It is a parser/data-model PR.

That separation is what makes #1789 able to integrate mower geometry later into the shared Map pipeline.

---

# Static map acquisition research

Before the static geometry parser was proposed, controlled diagnostics established how O1200 map traffic behaves.

These acquisition findings are protocol research.

They are **not yet production Map capability lifecycle code**.

## Normal MQTT carries the map stream

The tested O1200 map/position events were observed on the normal:

```text
mq*.ecouser.net
```

MQTT session.

A separate JMQ session was not required for map-stream activation in the controlled O1200 tests.

## `appping` activates the live stream

Controlled runs showed that:

```text
appping
```

can activate:

```text
onPos
onMapTrack
onMI
onArI
```

traffic on normal MQ during active mowing.

Both the reference N-GIoT path and an explicitly experimental legacy command path activated the stream in testing.

This proves the trigger behaviour for the researched mower.

It does not by itself select the correct production transport design.

## Presence lease

Repeated controlled runs measured an approximately:

```text
300-second
```

map/position presence lease after `appping`.

A renewal sent around:

```text
240 seconds
```

reset the lease, and traffic stopped approximately 300 seconds after the renewal when no further ping was sent.

Therefore an uninterrupted live-stream implementation would need an explicit renewal lifecycle.

The current static-map PR stack does not implement that lifecycle.

## Mower state affects stream shape

Observed O1200 behaviour differed by operating state.

During active mowing:

```text
onPos
```

was commonly close to a 2 Hz stream and:

```text
onMapTrack
```

was repeatedly present.

During a paused-state experiment, only two transient position events were seen after `appping`.

During return-to-dock, dense position traffic continued until docking while map-track traffic was limited to an initial burst.

This is one reason absence of map traffic must not automatically be interpreted as unsupported protocol.

---

# `getMI` and the static-map event family

Both tested control transports could issue:

```text
getMI
```

and solicit:

```text
onMI
onArI
```

while map presence was active.

The direct command acknowledgement did not contain the complete captured map-bearing value.

The map-bearing data arrived through the pushed event family.

Research therefore distinguishes:

```text
getMI
    │
    └── request/trigger

onMI / onArI
    │
    └── map-bearing push data
```

---

# Two observed `onMI.info` forms

Controlled captures identified two stable O1200 `onMI.info` representations.

They share the same outer protocol family but have different timing roles.

## Request-associated form

Observed representation length:

```text
876 characters
```

After the proven strict Base64 representation layer:

```text
657 bytes
```

Controlled timing experiments support the label:

```text
request-associated form
```

because it appeared promptly after explicit `getMI`.

This is the form parsed by PR #1782.

## Cadence-associated form

Observed representation length:

```text
52 characters
```

After strict Base64:

```text
38 bytes
```

Repeated captures support an approximately:

```text
60-second
```

cadence association.

A controlled repeatability experiment showed that explicit `getMI` did not reset that observed cadence.

This form is intentionally **not** treated as static geometry by PR #1782.

## Important semantic boundary

These labels describe timing association only.

They do not mean:

```text
876 = "full map" as a general protocol law
52  = "metadata" as a general protocol law
```

PR #1782 accepts only the exact evidenced geometry form and fails closed for the cadence form and unsupported structures.

---

# PR #1782 — O1200 `onMI` static main boundary

PR #1782 implements a narrow parser for the request-associated O1200:

```text
onMI
```

geometry.

## Validation chain

The parser requires:

```text
canonical Base64
      │
      ▼
observed trimmed LZMA-Alone framing
      │
      ▼
validated decoded size
      │
      ▼
exact supported JSON record shape
      │
      ▼
supported s1 geometry record
      │
      ▼
strict RLE expansion
      │
      ▼
MowerStaticMapEvent
```

Unknown or malformed representations do not emit misleading geometry.

## Shared event

The parser emits:

```python
MowerStaticMapEvent(
    mid=...,
    groups=[...],
    step_size=50,
)
```

using the shared:

```text
MowerMapTraceGroup
MowerMapTraceSegment
points
```

representation.

## Observed O1200 direction step

The captured O1200 geometry uses an observed step:

```text
50 coordinate units
```

This is stored explicitly as:

```text
step_size
```

It is **not** declared universal across GOAT models.

## Eight-direction RLE path

The observed RLE uses eight direction tokens.

Conceptually:

```text
1 → east
2 → south-east
3 → south
4 → south-west
5 → west
6 → north-west
7 → north
8 → north-east
```

Each step moves:

```text
50 units
```

in the corresponding x/y direction.

Repeated tokens can be run-length encoded.

## Golden O1200 geometry

The repository-safe fixture used by #1782 expands to:

```text
2,336 points
```

with observed bounds:

```text
x = -34350 .. 5750
y = -24350 .. 21350
```

The geometry matched the independent reference viewer point-for-point.

## Open contour preserved

The observed main boundary contains an open gap:

```text
(100, 0)
```

The parser does not mutate the source geometry to close it.

This distinction is important:

```text
stored protocol geometry
        ≠
visual polygon closure
```

The renderer may close a path visually later without changing the stored event.

## Still opaque

The static-map parser does not assign undocumented meanings to:

```text
group "2"
s1
centerX
centerY
using
serial
type
```

or transient:

```text
batid
```

metadata.

Unsupported records fail closed or remain outside the public geometry event.

---

# PR #1788 — O1200 work areas

PR #1788 adds the persistent named work-area layer.

It combines:

```text
onArI
    → area geometry

getAreaSet type="ar"
    → area ID + user-visible name

onMI
    → static main-map coordinate frame
```

The output is:

```text
MowerWorkAreasEvent
```

with each area already registered into the static-map coordinates.

---

# `onArI` work-area geometry

The observed complete O1200:

```text
onArI type=0
```

representation is chunked.

The parser validates:

```text
mid
batid
serial
index
infoSize
type
using
info
```

for the supported snapshot form.

## Complete snapshot assembly

The parser:

```text
strict Base64 per chunk
      │
      ▼
validate one snapshot identity
      │
      ▼
serial = expected chunk count
      │
      ▼
require indexes 0..serial-1
      │
      ▼
concatenate chunks
      │
      ▼
decode trimmed LZMA-Alone
      │
      ▼
verify decoded length
      │
      ▼
parse complete grouped snapshot
```

Incomplete or mixed snapshots are rejected.

## Geometry layer

For the observed O1200 format, persistent work-area geometry is carried in:

```text
layer "1"
```

Each area record contains:

```text
area ID
local start coordinate
eight-direction RLE path
```

The RLE path uses the same evidenced:

```text
50-unit
```

direction step as the static main map.

The local work-area coordinates are **not** yet in their final main-map position.

---

# `getAreaSet type="ar"` metadata

PR #1788 reads:

```text
getAreaSet
```

responses with:

```text
type = "ar"
```

for work-area metadata.

Observed rows provide:

```text
map ID
area ID
user-visible name
additional opaque fields
```

Empty area names are accepted.

The response envelope:

```text
aid
```

is not interpreted as a work-area ID.

---

# Important AreaSet framing rule

The AreaSet `infoSize` field behaves differently from the independently evidenced `onMI` and grouped `onArI` size checks.

A read-only analysis of:

```text
198 getAreaSet type="ar" responses
across 17 Phase 2 captures
```

found:

```text
trimmed LZMA-Alone prefix:
    present in all 198

internal four-byte decompressed-size value:
    matched actual decoded length in all 198

envelope infoSize:
    matched decoded length in 0 of 198
```

Observed envelope-minus-decoded differences were not even universally constant.

Therefore #1788 correctly treats AreaSet envelope:

```text
infoSize
```

as positive opaque envelope metadata.

The parser uses the decompressed-size value retained in the trimmed LZMA header as the output-size assertion.

This rule is deliberately scoped to:

```text
getAreaSet type="ar"
```

and is **not** generalized to:

```text
onMI
onArI
```

which retain their separately evidenced size validation.

---

# Area IDs and names

The area-name research previously documented through PR #1774 established O1200 IDs/names through a reusable:

```text
RoomsEvent
```

path.

PR #1788 uses the same underlying:

```text
getAreaSet type="ar"
```

evidence differently inside the mower map stack.

It does not need to convert map work-area metadata into vacuum-room semantics before joining it with geometry.

Conceptually:

```text
#1774 direction
getAreaSet
   │
   ▼
RoomsEvent
   │
   ▼
generic area-name consumer

#1788 map direction
getAreaSet
   │
   ▼
map-local area metadata
   │
   + onArI geometry
   │
   ▼
MowerWorkAreasEvent
```

PR #1788 states that this map-zone parsing direction supersedes the map-specific direction of #1774 if the stacked map design is accepted.

The #1774 work remains useful historical and consumer evidence, particularly for Home Assistant area-name integration.

---

# Registering work areas into the static map

The key finding behind #1788 is that work-area contours are stored in a **local coordinate frame**.

They cannot simply be plotted at their raw coordinates on top of the `onMI` boundary.

## Registration algorithm

For each area:

```text
local area RLE
      │
      ▼
direction sequence
      │
      ▼
find longest shared contiguous direction run
against static main boundary
      │
      ▼
derive translation from matched point indexes
      │
      ▼
translate the complete area contour
      │
      ▼
verify the matched points exactly
      │
      ▼
accept registered area
```

## Translation only

The static work-area registration introduces:

```text
translation
```

only.

It does **not** introduce:

```text
scale
rotation
```

for this relationship.

## Ambiguity handling

If the strongest shared direction run can correspond to multiple different translations, the registration is rejected.

The implementation prefers:

```text
no area snapshot
```

over:

```text
plausible-looking but incorrectly placed polygon
```

This is a central fail-closed design principle.

---

# Public work-area model

PR #1788 exposes:

```python
MowerWorkArea(
    name=...,
    geometry=MowerMapTraceGroup(...),
)
```

and:

```python
MowerWorkAreasEvent(
    mid=...,
    areas=[...],
    step_size=50,
)
```

The:

```text
geometry.group_id
```

preserves the work-area ID.

The geometry points have already been translated into the static-map coordinate frame.

---

# Snapshot coordination

A work-area snapshot is only emitted when the coordinator has compatible:

```text
static main map
onArI geometry
AreaSet metadata
```

for the same:

```text
mid
```

and expected step size.

The implementation replaces complete snapshots rather than incrementally appending stale areas.

It also requires the area IDs in geometry and metadata to match exactly.

This prevents:

```text
old metadata + new geometry
```

or:

```text
new metadata + incomplete geometry
```

from being presented as one current map.

---

# PR #1789 — shared Map capability

PR #1789 integrates the typed static mower data into the existing:

```text
Map
```

abstraction.

It does not create:

```text
MowerMap
```

as a parallel public API.

## New nested capability

The draft adds:

```python
@dataclass(frozen=True, kw_only=True)
class CapabilityMowerMap:
    static: CapabilityEvent[MowerStaticMapEvent]
    work_areas: CapabilityEvent[MowerWorkAreasEvent]
```

and:

```python
CapabilityMap(
    changed=...,
    mower=CapabilityMowerMap(...),
)
```

## Vacuum-specific map fields become optional

Existing fields such as:

```text
cached_info
major
minor
position
rooms
set
trace
```

become optional.

This allows a mower to expose the shared Map abstraction without falsely claiming support for unrelated vacuum map concepts.

Conceptually:

```text
CapabilityMap
    │
    ├── shared:
    │     changed
    │
    ├── optional vacuum layers
    │     cached_info
    │     position
    │     rooms
    │     trace
    │     ...
    │
    └── optional mower layers
          static
          work_areas
```

---

# Important current limitation: no O1200 hardware wiring

PR #1789 does **not** yet connect:

```text
CapabilityMap(mower=...)
```

to the O1200:

```text
2i0fns
```

hardware profile.

Therefore the stack currently proves:

```text
parser model
event model
Map adapter
SVG renderer
```

but not yet:

```text
normal O1200 device capability enabled end-to-end
```

Hardware wiring and acquisition lifecycle are follow-up work.

---

# Shared Map refresh

When a mower map capability is eventually configured, the shared `Map.refresh()` path can request refreshes for:

```text
mower.static.event
mower.work_areas.event
```

The exact production acquisition commands/lifecycle still need to be wired.

This distinction matters because a refreshable event model is not the same thing as a complete:

```text
AppPing → getMI → getAreaSet
```

session manager.

---

# SVG rendering

PR #1789 extends the existing Rust map renderer with typed mower geometry.

The static SVG contains:

```text
1. static main-boundary fill
2. registered work-area polygons
3. static main-boundary outline
```

## Main boundary

The static boundary defines the authoritative:

```text
viewBox
```

for the mower map.

## Work areas

Each registered area is filled using the existing room-color palette.

Names are retained in the typed model but are not rendered as SVG text in this first MVP.

## Coordinate projection

Mower coordinates are projected by:

```text
x_svg = x / step_size
y_svg = -y / step_size
```

The Y axis is inverted because SVG screen coordinates increase downward.

The observed O1200:

```text
step_size = 50
```

is therefore used as the current display scale for these fixtures.

## Visual closure

Open firmware contours remain open in stored event geometry.

The SVG path may close the polygon visually for fill/rendering.

This is a rendering decision only.

The source event is not mutated.

---

# Snapshot compatibility in MapData

The Python Map adapter caches the latest:

```text
MowerStaticMapEvent
MowerWorkAreasEvent
```

and combines them only when:

```text
mid matches
step_size matches
```

A static boundary can render before work areas arrive.

A work-area snapshot with incompatible map identity or scale is not overlaid onto the current boundary.

---

# Existing vacuum behaviour

The mower work is intentionally integrated without translating mower geometry into vacuum wire formats.

Vacuum map subscriptions are only enabled for capabilities the device actually declares.

Examples:

```text
position subscriber
    only if CapabilityMap.position exists

trace subscriber
    only if CapabilityMap.trace exists

room handling
    only if CapabilityMap.rooms exists

cached-map handling
    only if CapabilityMap.cached_info exists
```

PR #1789 reports that the existing vacuum SVG snapshots remain unchanged.

---

# Static map versus live map

The roadmap intentionally keeps these concepts separate.

## Static layers

Current static MVP:

```text
main lawn boundary
persistent named work-area polygons
```

## Live layers

Not part of the current static MVP:

```text
mower position
dock position
current area
live mowing plan
completed/remaining work
onMapTrack rendering
```

Flattening all of these into one cumulative trace would lose the semantic distinction visible in the official app.

---

# Live position remains in a different coordinate frame

Research has observed:

```text
onPos / getPos
```

position data.

However, the live position coordinates have not yet been proven to share the static `onMI` coordinate frame directly.

Controlled two-area research supports:

```text
135°
```

as the strongest tested static-to-live rotation candidate in the current evidence.

That is **not** a proven wire relation.

Translation remains non-unique under the tested constraints.

Therefore the current production-safe conclusion is:

```text
no proven live → static transform
```

and #1789 deliberately does not render mower position onto the static map.

---

# Dock position

Position research distinguishes mower and charge/dock coordinates.

A dock coordinate should only be considered usable when its own validity field allows it.

Captured cases with:

```text
chargePos.invalid = 1
chargePos = (0, 0)
```

must remain unavailable rather than being rendered as a real dock.

Dock overlay is not part of #1789.

---

# `onMapTrack`

The researched O1200 also emits:

```text
onMapTrack
```

during active mowing.

This is separate from:

```text
onMapTrace
```

handled by #1567.

Do not conflate the names.

## Observed MapTrack reconstruction research

Research has established enough structure to build strict diagnostic reconstruction, including:

```text
serial/index chunk assembly
canonical Base64
trimmed LZMA-Alone
decoded-length validation
outer grouped records
observed update policy
```

In the observed diagnostic format:

```text
update = 1
```

replaces a complete keyed state, while:

```text
update = 2
```

replaces individual records keyed by the first three semicolon fields.

Those findings remain **diagnostic/research semantics**.

They are not yet implemented as a production Map layer in this PR stack.

## Why it stays separate

`onMapTrack` appears to represent live mowing-plan/activity state.

Before rendering it, the client still needs evidence for:

```text
coordinate transform
snapshot/delta lifecycle
ordering
duplicates
gaps
reconnect behaviour
map-ID compatibility
```

---

# Observed map IDs

In the researched O1200 captures:

```text
onPos / onMapTrack
    → map ID 0

onMI / onArI / static area family
    → map ID 1
```

This correlation was repeatedly observed.

It should remain model/capture scoped.

Do not hard-code a universal rule that:

```text
all live GOAT data uses 0
all static GOAT data uses 1
```

without cross-model evidence.

---

# Map editing remains separate

The current map stack is read-only.

It does not implement:

```text
setAreaSet
SpecialContour writes
No-Entry Zone creation
boundary editing
work-area divide/merge
renaming
```

Controlled research did observe the:

```text
SpecialContour
```

family during creation/deletion of a **reduced-avoidance zone**.

That experiment must not be described as a No-Entry Zone test.

It established lifecycle/presence evidence, not a complete geometry parser.

Map editing should remain a later independent feature set.

---

# Safety and fail-closed parsing

The static map stack uses strict parsing intentionally.

Examples include:

```text
canonical Base64 only
bounded compressed/decompressed sizes
complete chunk sets only
validated map IDs
validated RLE tokens
geometry point caps
exact supported record shapes
ambiguous registration rejection
compatible snapshot IDs/scales only
```

Unknown structures do not get guessed meanings.

This is especially important for map data because a plausible but incorrectly placed polygon is worse than no polygon.

---

# Privacy

Raw mower maps can reveal private property layout and location-related information.

Public fixtures and documentation must not contain:

```text
account identity
device identity
authentication/session data
complete MQTT topics
precise private location
unsanitized property map data
```

Research captures should remain local/fail-closed unless explicitly sanitized and reviewed.

The public parser fixtures used in the PR stack are reduced, repository-safe representations approved for protocol testing.

---

# Relationship to PR #1774 area names

PR #1774 introduced an O1200 area-name capability based on:

```text
GetAreaSet
RoomsEvent
CapabilityClean.areas
```

That is a useful generic metadata path and has corresponding Home Assistant development work.

PR #1788 reuses the underlying AreaSet evidence directly inside the map stack to create:

```text
MowerWorkAreasEvent
```

where each name is attached to registered geometry.

Therefore the two concepts are:

```text
generic area-name metadata
        and
map work-area metadata + geometry
```

not necessarily two permanently separate protocol requests.

If the map stack is accepted, its area parsing direction supersedes the map-specific role originally proposed by #1774.

This should be resolved architecturally before both mechanisms are enabled redundantly on one hardware profile.

---

# Home Assistant implications

PR #1789 makes no Home Assistant compatibility changes.

A future HA map integration can continue to consume the existing public:

```text
Map.get_svg_map()
```

output if the client hardware profile exposes the mower map capability.

Before that is production-ready, the following are still needed:

```text
O1200 hardware wiring
acquisition/session lifecycle
consumer compatibility audit for optional CapabilityMap fields
HA integration/testing
```

Live mower position, dock and mowing-plan overlays should remain disabled until their coordinate semantics are independently proven.

---

# Validation summary

## PR #1567

The PR reports:

```text
705/705 full Python tests passed
real captured payload reproduction
```

and dedicated tests for chunking, corruption, memory bounds and grouped/segment preservation.

## PR #1782

The O1200 static boundary fixture validates:

```text
request-associated form only
2,336 points
known bounds
known open gap
point-for-point reference-viewer match
fail-closed invalid forms
```

## PR #1788

The rebased work-area implementation reports:

```text
67 relevant tests passed
```

and validates:

```text
onArI chunking
AreaSet framing
metadata/geometry ID agreement
deterministic translation registration
ambiguous-registration rejection
```

## PR #1789

The draft reports:

```text
Python Map/capability/mower tests: 21 passed
existing SVG snapshots: 6 unchanged/passed
Rust tests: 68 passed
mypy: passed
Ruff: passed
cargo fmt --check: passed
clippy -D warnings: passed
git diff --check: passed
```

This is strong software-level validation of the current stacked implementation.

It is not equivalent to merged upstream support or fully wired O1200 end-to-end map support.

---

# Model scope

## `onMapTrace`

PR #1567 contains direct evidence from:

```text
GOAT A1600 RTK
firmware 1.15.13
```

with additional O1200 analysis contributing to chunk handling.

## Static map stack

Strongest evidence for:

```text
onMI
onArI
getAreaSet registration
static rendering fixtures
```

is:

```text
GOAT O1200 LiDAR
hardware ID 2i0fns
```

The current #1789 draft does not yet enable the capability in that hardware file.

## Cross-model rule

Do not enable the mower map capability for another model because:

```text
it is also a GOAT
```

or because one message name looks similar.

Each hardware model needs direct capture evidence for the layers being enabled.

---

# What the current stack resolves

For the researched O1200, the stack substantially resolves:

```text
static main boundary representation
static boundary RLE decoding
observed coordinate step
persistent work-area geometry
area ID/name metadata for map join
work-area registration into main-map coordinates
typed mower static-map events
shared Map integration architecture
static SVG rendering
```

This is a significant change from the earlier state where "GOAT map support" was one undifferentiated unknown.

---

# What remains open

The highest-value remaining work is:

```text
1. production acquisition/session lifecycle
   AppPing / getMI / getAreaSet coordination

2. O1200 hardware capability wiring

3. consumer audit for optional CapabilityMap fields

4. Home Assistant compatibility/tests

5. live position → static coordinate transform

6. dock position overlay

7. current-area semantics

8. onMapTrack production model + rendering

9. completed/remaining mowing-plan layers

10. map editing/write support

11. cross-model verification
```

---

# Recommended implementation order

```text
#1567
shared grouped mower geometry
        │
        ▼
#1782
static onMI boundary
        │
        ▼
#1788
onArI + AreaSet work areas
        │
        ▼
#1789
shared Map + static SVG
        │
        ▼
acquisition/session lifecycle
        │
        ▼
O1200 hardware wiring
        │
        ▼
consumer / Home Assistant compatibility
        │
        ▼
live layers only after transforms are proven
```

This sequence matches the evidence-first design agreed in the map roadmap.

---

# Related documentation

- [Overview](overview.md)
- [Supported models](supported-models.md)
- [Capabilities](capabilities.md)
- [Zones and areas](zones-and-areas.md)
- [O1200 area names](area-names.md)
- [Protocol reference](protocol-reference.md)
- [Home Assistant](home-assistant.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
