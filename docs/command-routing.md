# Device-specific command routing

This page documents the command-routing architecture proposed in:

- [`DeebotUniverse/client.py` PR #1772 — Refactor command lookup per device`](https://github.com/DeebotUniverse/client.py/pull/1772)

Last reviewed: **2026-08-24**

> [!IMPORTANT]
> PR #1772 was still open at the time of this review.
>
> The architecture described here is therefore **development/fork behaviour**, not part of the reviewed upstream `dev` baseline.

## Why this matters for GOAT

ECOVACS devices from different product families can use the same wire command name while requiring different Python implementations or payload semantics.

The old lookup model is based primarily on global dictionaries keyed by command name.

Conceptually:

```text
"clean"
   │
   ▼
one globally registered Python command
```

That architecture assumes:

```text
one wire name
    =
one command implementation
```

This assumption becomes a blocker when two device families need:

```text
same wire name
different implementation
```

PR #1772 introduces a device-aware lookup so the hardware capability tree can select the command implementation appropriate for that device.

---

# Motivating mower example

The architectural problem is discussed in relation to the mower `clean` work in upstream PR #1624.

That work proposes a mower-specific command which uses wire name:

```text
clean
```

with mower/V2-style content.

Other ECOVACS devices already have a command implementation using the same:

```text
clean
```

wire name.

A single global command-name dictionary cannot safely represent:

```text
vacuum/device-family implementation
           and
mower-specific implementation
```

under the same key.

PR #1772 addresses that routing problem.

It does **not** itself:

- add `CleanMower`
- decide which mower models should use `clean`
- replace `CleanV2`
- change GOAT mowing payload semantics
- prove that every GOAT model uses the same clean command

It is an architectural prerequisite.

---

# Previous global lookup model

The existing client has global registries such as:

```text
COMMANDS
COMMANDS_WITH_MQTT_P2P_HANDLING
```

These are keyed by protocol command name.

Conceptually:

```python
COMMANDS["setVolume"] = SomeSetVolumeCommand
COMMANDS["clean"] = SomeCleanCommand
```

This works when command names are globally unique in meaning.

It becomes ambiguous when:

```text
Device A:
"clean" → CommandA

Device B:
"clean" → CommandB
```

because a Python dictionary can only have one effective value for:

```text
"clean"
```

---

# New per-device command lookup

PR #1772 adds a command lookup to each:

```text
Capabilities
```

instance.

During capability initialisation, the capability tree is scanned and directly configured command classes/instances are collected.

Conceptually:

```text
Hardware profile
      │
      ▼
Capabilities
      │
      ├── battery → GetBattery
      ├── clean.action.command → Clean...
      ├── settings.volume → GetVolume / Set...
      └── ...
      │
      ▼
per-device command lookup
```

The new public helper is:

```python
Capabilities.get_command(name)
```

Example concept:

```python
device_a.capabilities.get_command("clean")
    → CommandA

device_b.capabilities.get_command("clean")
    → CommandB
```

This removes the requirement that all device families share one Python implementation merely because ECOVACS reused a wire name.

---

# `_get_commands()`

The PR introduces an internal recursive helper conceptually equivalent to:

```text
_get_commands(capabilities)
```

It scans capability dataclasses for directly discoverable:

```text
Command instances
Command classes
nested capability dataclasses
lists/tuples containing commands
```

The result is stored as a read-only mapping:

```text
command name → command class
```

inside each `Capabilities` object.

---

# Directly discoverable commands

Examples of directly discoverable capability wiring include:

```python
CapabilityExecute(Charge)
```

and:

```python
CapabilitySet(
    SomeEvent,
    [GetSomething()],
    SetSomething,
)
```

because the command class or command instance is explicitly present in the dataclass tree.

These can participate in the device-specific command lookup.

---

# Lambda-wrapped or indirect commands

A command hidden behind an arbitrary callable such as:

```python
lambda value: SetSomething(value, ...)
```

is not directly discoverable as a command class by the recursive capability scan.

PR #1772 intentionally preserves existing global registry fallback for commands that cannot be discovered directly.

This is important:

```text
capability can execute command
```

does not necessarily mean:

```text
device-specific lookup can identify command class
```

when the setter is hidden behind a generic callable.

This is a current architectural limitation of the proposed discovery method, not a protocol limitation.

---

# Duplicate command names inside one device

The lookup uses first-wins behaviour.

When more than one directly discoverable command in the same capability tree has the same:

```text
NAME
```

the first/primary discovered implementation is retained.

Conceptually:

```text
first command NAME="x"
        │
        ▼
stored

later command NAME="x"
        │
        ▼
does not replace first
```

This solves:

```text
different device A vs device B
```

better than the global registry model.

It does **not** create a multi-dispatch system for several semantic variants of the same wire command inside one device.

That distinction matters for channel-based commands such as volume.

---

# Legacy JSON message lookup

Some ECOVACS push messages are resolved using legacy logic that converts message names back toward their related command names.

Conceptually:

```text
onError
   │
   ▼
getError
   │
   ▼
command/message class
```

PR #1772 changes this resolution order.

## Development resolution order

```text
1. device capabilities
2. global COMMANDS fallback
```

Conceptually:

```text
incoming legacy message
        │
        ▼
device.capabilities.get_command(name)
        │
    ┌───┴────┐
    │        │
 found    not found
    │        │
    ▼        ▼
 use it    global fallback
```

This allows the same legacy message/command name to resolve differently for different devices.

---

# Map fallback protection remains capability-based

The existing legacy map fallback protection is retained conceptually.

If the device has no:

```text
capabilities.map
```

then legacy map-specific fallback is skipped.

This remains important for GOAT devices where partial area/zone metadata should not automatically imply full vacuum-style map support.

---

# MQTT P2P command routing

The MQTT P2P path also needs device-specific routing because incoming P2P traffic contains only a command name plus sender/receiver device metadata.

PR #1772 adds a helper conceptually equivalent to:

```text
_get_p2p_command_type(
    command_name,
    data_type,
    device_id,
)
```

The lookup first checks the subscribed device's capabilities.

---

# P2P request routing

For a P2P request:

```text
q
```

the command belongs to the **receiver device**.

Conceptually:

```text
sender
  │
  │ q request
  ▼
receiver
```

Therefore command lookup uses:

```text
receiver device ID
```

The PR includes an explicit test for this rule.

---

# P2P response routing

For a P2P response:

```text
p
```

the responding command belongs to the **sender device**.

Conceptually:

```text
sender
  │
  │ p response
  ▼
receiver
```

Therefore command lookup uses:

```text
sender device ID
```

The PR includes an explicit test for this rule.

---

# P2P fallback rules

The proposed lookup follows these rules.

## Device configures a P2P-capable command

Use it:

```text
device-specific command
        │
        ▼
CommandMqttP2P subclass
        │
        ▼
use device-specific implementation
```

## Device does not configure the command

Use the existing global P2P registry as a compatibility fallback.

```text
no device command
      │
      ▼
global COMMANDS_WITH_MQTT_P2P_HANDLING
```

## Device explicitly configures a non-P2P command with that name

Do **not** silently substitute another global P2P implementation.

Conceptually:

```text
device says:
name → NonP2PCommand
        │
        ▼
do not use unrelated global P2P command
```

This is an important safety property.

A device's explicit capability configuration takes precedence over a generic global assumption.

---

# Why the non-P2P rule matters

Without this rule, the lookup could do:

```text
device-specific command found
      │
      └── not P2P
              │
              ▼
ignore device choice
              │
              ▼
use global same-name P2P command
```

That could parse or handle the payload using the wrong device-family semantics.

PR #1772 intentionally returns no P2P command instead.

---

# Backward compatibility

PR #1772 does not remove the global registries.

They remain fallback mechanisms.

This creates a migration path:

```text
device capability knows command
       │
       ▼
device-specific lookup

otherwise
       │
       ▼
legacy global lookup
```

This is useful because not every existing command is directly represented in a capability tree.

---

# Why capabilities are the right routing source

The hardware profile already answers:

```text
What does this device support?
```

Using that same capability tree to answer:

```text
Which implementation of wire command X belongs to this device?
```

keeps device-specific knowledge in one place.

Preferred architecture:

```text
hardware profile
      │
      ├── exposes feature
      └── selects command implementation
```

rather than maintaining a second large table:

```text
model → command-name → implementation
```

elsewhere in MQTT/message routing code.

---

# Relationship to event refresh lookup

Before PR #1772, `Capabilities` already built:

```text
Event type → GET command(s)
```

for:

```python
get_refresh_commands(event)
```

PR #1772 adds a second derived lookup:

```text
Command NAME → command class
```

for:

```python
get_command(name)
```

Conceptually:

```text
Capabilities
   │
   ├── _events
   │     └── Event → GET commands
   │
   └── _commands
         └── wire name → command class
```

Both are derived from the device's configured capability tree.

---

# Test coverage in PR #1772

The PR adds tests for:

- device-specific command lookup
- different command classes sharing one wire name
- unknown command returning `None`
- device-specific legacy message lookup
- device-specific MQTT P2P lookup
- global P2P fallback
- blocking an incorrect global P2P fallback
- P2P request routing to the receiver device
- P2P response routing to the sender device

Example test concept:

```text
Device A:
"setVolume" → SetVolume

Device B:
"setVolume" → AlternativeSetVolume
```

and each device resolves its own implementation.

---

# Current CI/review caveats

PR #1772 remains open.

The automated Codecov comment on the reviewed head reported:

```text
patch coverage ≈ 87.8%
project coverage ≈ 96.2%
```

with several changed branches/lines not fully covered.

CodSpeed also reported benchmark regressions, but the report explicitly warned that different runtime environments were being compared.

Therefore:

```text
performance regression confirmed
```

would be too strong a conclusion from that report alone.

The correct current status is:

```text
architecture implemented in PR
targeted behavioural tests added
patch coverage not complete
performance result requires comparable-environment verification
not merged upstream
```

---

# Important cross-PR integration review: `setVolume`

PR #1778 adds O1200 mower volume handling with two logical writable channels sharing the same ECOVACS wire name:

```text
setVolume
```

The O1200 capability wiring includes conceptually:

```text
system volume
    └── lambda → SetVolume(channel="sys", total=10)

fall/lifted volume
    └── direct SetFallVolume
```

Both command classes use wire name:

```text
setVolume
```

PR #1772 discovers direct command classes/instances from the capability tree, while arbitrary lambda-wrapped commands are not directly discoverable.

That creates an important integration question when the branches are combined:

```text
Which direct setVolume implementation becomes
the device-specific command lookup entry?
```

Based on the current architecture, this deserves an explicit combined-branch test.

This documentation therefore records:

**Cross-PR integration test required**

rather than claiming the combination is already proven correct.

The test should cover at least:

```text
incoming setVolume type=sys
incoming setVolume type=fall
P2P request handling
P2P response handling
resulting VolumeEvent
resulting FallVolumeEvent
```

This is a software-routing concern, not evidence that the underlying O1200 volume protocol is wrong.

---

# Same-name commands within one device remain a design constraint

PR #1772 primarily solves:

```text
same name
different device families
```

It is less general for:

```text
same name
same device
multiple semantic channels/implementations
```

because the lookup stores one command class per name.

Future designs may need one of:

```text
one parser that dispatches by payload
explicit primary command
payload-aware command resolution
capability metadata for aliases/channels
```

if multiple same-name implementations genuinely need independent routing inside one device.

---

# Relevance to GOAT mower clean commands

The main GOAT motivation remains the possibility that different ECOVACS device families use:

```text
clean
```

with different payload semantics.

PR #1772 makes this architecture possible:

```text
Vacuum/device A
clean → implementation A

GOAT/device B
clean → implementation B
```

without overwriting one global registry entry.

However, the actual mower command choice must still be established separately through:

```text
protocol evidence
hardware profile wiring
tests
physical-device verification
```

---

# What PR #1772 resolves

It substantially resolves the architectural limitation:

```text
wire command names must be globally unique
```

by introducing:

```text
device capability → command implementation
```

lookup.

It also improves:

```text
legacy message routing
MQTT P2P routing
device identity selection for P2P q/p traffic
```

---

# What PR #1772 does not resolve

It does not by itself resolve:

```text
which clean command every GOAT model should use
selected-zone mowing protocol
area parameters
map protocol
mower settings semantics
same-device multi-channel command ambiguity
commands hidden behind arbitrary callables
```

Those remain separate implementation/research topics.

---

# Recommended validation before merge/use with mower branches

1. Run the full command/message/MQTT test suite.
2. Test two device profiles using different classes with the same wire name.
3. Test legacy push-message resolution for both.
4. Test P2P requests and responses for both.
5. Combine with PR #1778 and test both O1200 `setVolume` channels.
6. Combine with any mower `clean` implementation and verify the intended device profile selects it.
7. Verify fallback behaviour on existing devices that do not directly expose the command in capabilities.
8. Re-run performance benchmarks in comparable environments.

---

# Evidence summary

| Item | Status |
| --- | --- |
| Per-device command lookup | PR implemented |
| `Capabilities.get_command()` | PR implemented |
| Recursive capability command discovery | PR implemented |
| Same wire name across devices | Python tested |
| Legacy device-specific lookup | Python tested |
| P2P device-specific lookup | Python tested |
| P2P request → receiver routing | Python tested |
| P2P response → sender routing | Python tested |
| Global compatibility fallback | Python tested |
| Incorrect global P2P fallback blocking | Python tested |
| Full patch coverage | Not complete at reviewed head |
| Comparable performance validation | Still required |
| `#1772 + #1778 setVolume` combined routing | Requires explicit integration test |
| Upstream merge | No |

---

# Related upstream work

- [`PR #1772`](https://github.com/DeebotUniverse/client.py/pull/1772)
- [`PR #1624 — mower clean command work`](https://github.com/DeebotUniverse/client.py/pull/1624)
- [`PR #1778 — O1200 global mower settings`](https://github.com/DeebotUniverse/client.py/pull/1778)

---

# Related documentation

- [Overview](overview.md)
- [Capabilities](capabilities.md)
- [Mowing control](mowing-control.md)
- [O1200 global settings](o1200-global-settings.md)
- [Protocol reference](protocol-reference.md)
- [Testing status](testing-status.md)
- [Known limitations](known-limitations.md)
