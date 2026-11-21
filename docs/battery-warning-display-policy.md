# InfoWindow ESP32-C6 — low-battery-only display policy

**Experimental specification, not yet implemented or hardware tested.**  
Scope: `feature/esp32-c6-zigbee-infowindow` only. Do not edit or merge the working Raspberry Pi `master`.

## Display requirement (explicit user preference)

**Show absolutely no battery icon, text, percentage or reserved visible marker when the battery is healthy.** The original task display should look unchanged.

- **NORMAL:** no on-screen battery indicator of any kind.
- **LOW:** show a small, legible `LOW BAT` warning in the header, only after a genuine low-battery transition.
- **CRITICAL:** replace the low alert with a clearer `CHARGE AAs` warning *if* power is sufficient for a safe complete e-paper refresh. Never risk a partial screen refresh when undervoltage is detected.
- **RECOVERED:** remove the warning entirely once the pack has recovered (e.g. the two NiMH AAs are recharged/replaced), even if no task data changed.

Battery readings may still be exposed as diagnostics in Home Assistant; the *screen* stays clean until low.

## Independent update trigger

The device wakes every 30 minutes and measures pack voltage. The rendered-screen dirty condition is:

```
should_refresh =
  task_snapshot_changed
  || displayed_date_changed
  || layout_or_firmware_assets_changed
  || low_battery_display_state_changed
```

In particular, **a LOW or CRITICAL transition is enough by itself to refresh the full screen**. Existing Waveshare 880×528 tri-colour panel should be treated as full-refresh-only unless its exact hardware revision proves otherwise. A refresh is triggered only when the *display state* changes, not when voltage drifts while already LOW.

Battery status must be evaluated locally, without requiring Zigbee to work. Maintain the last valid task snapshot/layout in local persistent storage so a battery-only refresh can redraw the existing display even while disconnected. If the snapshot is unavailable, fall back to a safe local screen without fabricating tasks.

## Measurement / state machine

- Pack: **2 × IKEA LADDA rechargeable NiMH AAs**, either 1900 mAh or 2450 mAh, in series; exact version to be confirmed.
- Sample pack voltage through a high-impedance divider switched off in sleep; account for ADC calibration and regulator/battery voltage sag.
- Measure after brief settling; optionally sample under a known representative load so the state tracks ability to drive radio/EPD rather than idle open-circuit voltage alone.
- Do **not** map NiMH voltage linearly to a percentage. Choose LOW / CRITICAL thresholds only after profiling the actual hardware, battery pack, and boost converter. Make thresholds firmware configurable.
- Add hysteresis and multi-sample confirmation (e.g. two successive 30-minute measurements) for the LOW and recovery transitions; an immediate critical response is permissible on verified severe sag.
- Keep the *observed battery state* separate from *last successfully rendered battery state*. Commit display state only when full screen refresh succeeds. This prevents the warning being considered shown if a brownout interrupted a refresh.
- A recharged pack can initially show a high reading due to recovery; require sustained normal readings before clearing the alert.
- Critically low voltage: skip optional Wi-Fi/OTA and other high-current operations; if there is insufficient headroom for a complete refresh, leave the previous e-paper image intact and minimise power draw.

## Layout

Use the existing 25 px-high header (see `infowindow.py`) for a compact warning aligned to the far right without covering the centred third-column title or date. Reserve **no visible battery placeholder** when NORMAL. Render text legibly with the available red/black/white planes. Validate positioning and 0°/180° screen rotation on the actual panel. Prefer concise `LOW BAT` rather than an imprecise numeric percentage.

## Acceptance tests

1. Healthy battery, unchanged task data: no battery mark, no refresh.
2. Healthy battery, changed tasks: refresh task screen with no battery mark.
3. Unchanged tasks, NORMAL→LOW: refresh once and display LOW BAT.
4. LOW remains LOW across many wakes: no battery-only repeat refresh.
5. Unchanged tasks, LOW→NORMAL after confirmed recharge: refresh and remove warning completely.
6. Zigbee unavailable at LOW transition: local cached task display still updates warning.
7. CRITICAL state: only refresh if regulator can complete a full update; otherwise preserve last image.
8. Brownout during refresh: last-rendered state must not be advanced; recover safely later.
9. Low-battery event reported to HA when connected, but loss of HA does not suppress on-screen warnings.
10. No unnecessary Wi-Fi radio session solely to change the warning.

Note: 30-minute sleep means on-screen warning/recovery can lag the real state by up to approximately 30 minutes (plus confirmation cycles).
