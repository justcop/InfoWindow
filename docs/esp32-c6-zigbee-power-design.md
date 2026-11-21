# InfoWindow ESP32-C6 Zigbee design — 2 × rechargeable AA

> Experimental design only. This work must remain on `feature/esp32-c6-zigbee-infowindow`. Do not modify, deploy, or merge into `master` without explicit approval.
>
> Status: architecture and battery budget, not yet hardware validated.

## Decisions

- Display: retain existing Waveshare 7.5-inch HD e-paper HAT (B), 880 × 528, black/red/white, SPI. Verify exact revision/controller and electrical supply before hardware purchase.
- Controller: ESP32-C6 (Zigbee IEEE 802.15.4 plus optional Wi-Fi), in a **low-leakage custom module/carrier**, not a conventional USB dev board for final battery use.
- Power: **2 × IKEA LADDA AA rechargeable NiMH cells in series** (user's existing batteries). Confirm whether their cells are **1900 mAh** or **2450 mAh**; both are nominally 1.2 V/cell. Pack voltage ~2.4 V; rated energy ~4.56 Wh for LADDA 1900 or ~5.88 Wh for LADDA 2450, before losses. Series capacity stays 1900 or 2450 mAh respectively, not double. Use matched cells of the same age, capacity, and state of charge.
- Regulator: low-quiescent-current 3.3 V boost supply with enough peak input current for RF bursts and display start-up; size based on measurements. Include energy buffer capacitors. Cut e-paper controller power after refresh via a low-leakage load switch; verify HAT power interface.
- Sleep: ESP32-C6 **deep sleep for 30 minutes** between updates. No immediate Zigbee wake demanded by the user; pending larger downloads are delivered on next scheduled wake.
- Home Assistant / ZHA: fetch Todoist upstream and normalise/compact task data centrally, send snapshots over a custom ZHA/Zigbee application protocol. Keep auth credentials off the display.
- Rare large transfers: on scheduled wake receive a Zigbee indication that Wi-Fi download is pending, power up Wi-Fi temporarily, fetch versioned resources/images/OTA over authenticated local transport, disable Wi-Fi, then sleep.
- Refresh only if logical task list/layout changes; preserve last image on network failure.

## 30-minute wake cycle

1. Wake from RTC, sample battery voltage with switched divider, verify supply is adequate.
2. Reinitialise Zigbee stack and attempt quick network re-attachment, with bounded retries / timeout.
3. Request latest snapshot/version from HA; acknowledge per chunk. Prefer compact, versioned full snapshots initially over deltas; handle > Zigbee packet size with sequencing, CRC/hash, and retransmission. Expect roughly 1–3 kB of task data, not ~116 kB of raw tri-colour framebuffer.
4. If data unchanged and no maintenance job, immediately sleep.
5. If content changed, render text/icons locally using small embedded bitmap fonts with column/priority mapping reflecting the current Pi app; turn on display driver, write black and red buffers over SPI, wait for completion, sleep/power off display.
6. If HA flags rare Wi-Fi work, activate Wi-Fi only now, fetch authenticated payload with integrity checks and download bounds, then resume ordinary sleep. Preserve prior working firmware/image on failure.
7. Save minimal status (protocol version, hash, last update, errors) in RTC/flash as appropriate; avoid frequent flash writes. Sleep until next 30-minute slot.

The existing Pi code in `infowindow.py` uses Pillow, Todoist API, and Pi GPIO/SPI; these cannot run unmodified on ESP32. First share the same task filtering/layout model, and port the visual renderer to a compact ESP-IDF or Arduino graphics layer. ESP32-C6 has 512 KB SRAM; two packed 880 × 528 1-bit colour planes require about 116,160 bytes. Profile available heap and use paged/streaming drawing if needed.

## Zigbee/ZHA-specific risk

Deep sleep reboots the Zigbee stack. On wake the device may need to re-attach, costing time and energy; a 30-minute interval may exceed some parent/router child aging timeouts. Verify behaviour of the actual ZHA coordinator/router, retry bounds, and recovery after multiple missed wakes. Do not assume queued commands remain buffered for the whole interval. Instead, have HA retain the desired latest snapshot and return it when the device requests it. Prefer a dedicated custom manufacturer-specific Zigbee cluster/protocol rather than pretending task lists are ordinary numeric sensors.

## Battery budget (provisional, not a measurement)

IKEA LADDA AA options: 1900 mAh × 2 cells in series × 1.2 V ≈ **4.56 Wh** nominal, or 2450 mAh × 2 × 1.2 V ≈ **5.88 Wh** nominal. Plan a rough 3.0–3.8 Wh usable for the 1900 cells and ~3.9–4.9 Wh for 2450 after conversion, ageing, load and protective cutoff; verify under real load. The higher-capacity pack has ~29% more nominal energy, not twice the current or twice the voltage.

48 network wakes/day. Illustrative active-energy scenarios at a nominal 3.3 V load:
- Fast: 10 seconds at 80 mA per wake = 0.035 Wh/day (before refreshes, sleep overhead). Could reach ~2–3 months in an excellent low-leakage build.
- Moderate: 15 seconds at 90 mA per wake = 0.059 Wh/day (before refreshes and sleep overhead). Roughly 4–8 weeks with normal overhead.
- Slow: 30 seconds at 120 mA per wake = 0.158 Wh/day (before refreshes and sleep overhead). Roughly 1–3 weeks if retries / refreshes are expensive.

E-paper panel specification: typical 50 mW refresh, 21 s full refresh = ~0.00029 Wh per display refresh; **the ESP32 and other circuitry may remain awake throughout this interval**, so total refresh-cycle energy is higher. Optimize firmware idle waiting and power gating.

Provisional planning targets: **LADDA 1900: 4–8 weeks** between charges; **LADDA 2450: ~5–10 weeks** at the same load (approximately 29% longer). These are hypotheses, not validated runtime claims; rapid rejoin or slow repeated rejoin can change outcomes greatly. Battery output must support RF current spikes without brownouts. Use externally charged matched NiMH cells, a NiMH charger (not Li-ion charging IC), and verify deep-discharge / cell reversal handling. Standard NiMH packs are 2.4 V nominal and need a 3.3 V boost, not a buck-only regulator.

## On-screen low-battery warning

**Normal battery: show absolutely no battery indicator on the e-paper screen.** A transition to LOW or CRITICAL must trigger a screen refresh independently of task changes; recovery must remove the warning, even when the task list is unchanged. If Zigbee is offline, use a cached task snapshot to redraw the existing screen. See [the detailed low-battery-only display policy](battery-warning-display-policy.md) for state transitions, hysteresis, measurement, layout and tests.

## Acceptance measurements / gates

- Verify exact HAT wiring, required input voltage, and logic levels; brownout/peak-load test with a two-cell pack.
- Log current/energy at battery terminals: idle (including regulator + e-paper driver), wake+rejoin, Zigbee exchange, changed-screen refresh, Wi-Fi fetch, low voltage, and failure retries.
- Test Zigbee reconnect after 30 minutes across 100+ cycles with ZHA; parent aging and power interruption must not require user re-pairing.
- Confirm Wi-Fi fails safely and never sticks on indefinitely.
- Show battery state, last successful task sync, and firmware version in HA.
- Continue to display last known good screen when network is unavailable.
- Verify back-to-back offline and restart behaviour, no unbounded flash writes or network retries.

## References

- Existing application: `infowindow.py`, `mod_todo/mod_todoist.py`, `driver/epd7in5b.py`, `driver/epdconfig.py`.
- ESP32-C6 datasheet: https://documentation.espressif.com/esp32-c6_datasheet_en.html
- Espressif Zigbee deep-sleep end-device example: https://github.com/espressif/esp-zigbee-sdk/tree/main/examples/sleepy_devices/deep_sleep_end_device
- Waveshare display: https://www.waveshare.com/7.5inch-hd-e-paper-hat-b.htm
- IKEA LADDA AA 1900 mAh: https://www.ikea.com/gb/en/p/ladda-rechargeable-battery-hr06-aa-1-2v-00509814/
- IKEA LADDA AA 2450 mAh: https://www.ikea.com/gb/en/p/ladda-rechargeable-battery-hr06-aa-1-2v-50504692/
