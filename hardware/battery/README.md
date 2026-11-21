# InfoWindow 2 × AA battery compartment — mechanical design

> This work is experimental and remains on `feature/esp32-c6-zigbee-infowindow`; the existing Raspberry Pi and original case files on `master` are untouched.

## Preferred design (revision 2): panel-mounted holder with lift-off lid

**Recommendation: TAKACHI BC3-2L-B** (black, 2 × AA, **with wire leads**). The proprietary panel-mounted battery compartment has a **tool-free detachable snap-fit cover**, a separate fixing frame and supplied screws. Once installed, the lid is removed outward from the rear; no long track/slide clearance is necessary. We should confirm the exact thumb-release action on a physical sample.

Manufacturer: https://www.takachi-enclosure.com/products/BC  
Specific technical drawing (2 pages): https://www.takachi-enclosure.com/assets/attachments/images/BC3-2L-B.pdf  
Manufacturer's 3D example: https://www.takachi-enclosure.com/products/BC

Manufacturer dimensions for AA × 2, with wires:
- External footprint: **81.5 × 50.5 mm**
- Overall height/depth: **18.5 mm**; verify actual protrusion into the cavity after fitting
- Nominal Perspex cutout: **74 × 43 mm** with rounded corners (see technical PDF; not the old bezel's cutout)
- Supported panel thickness: **1.0–3.5 mm**
- Screwed retaining frame provided (four self-tapping M2.3 × 10 screws attaching to manufacturer's bosses, *not self-tapping into the Perspex*)
- 140 mm wires. Keep slack, strain-relieve cable, insulate terminals.
- Compatible with 2 × IKEA LADDA rechargeable AA cells in series; verify battery fit and polarity.

The mounting frame achieves the original request to secure the holder to the Perspex without having to design and print our own shell or make a sliding-cover clearance. The battery contacts and lid mechanism are factory-made. The relatively larger 74 × 43 mm cutout must be positioned well away from fixing points to avoid weakening the backing.

### Procedure before cutting Perspex

1. Measure Perspex thickness and cavity clearance in the intended spot (including existing printed frame, PCB, wiring, screen fasteners, and backing spacers).
2. Obtain the physical BC3-2L-B holder or a verified dimensional sample. Check lid pops off without needing to slide far or swing into an obstruction, test fit with actual IKEA LADDA AAs and examine the hand-access/release tab.
3. Print or cut a **paper template from the manufacturer's dimension drawing**; compare against all neighbouring fasteners.
4. Only then mark and cut the manufacturer-specified opening, with its specified corner radii; avoid sharp square corners, stress and overtightening. Do not use the old bezel's 73 × 39 mm cutout dimensions.
5. Insert the holder from the display/cavity side so the removable cover is accessible from the rear; secure with the supplied frame/screws according to the manufacturer's assembly diagram and cable route.
6. Confirm repeated lid removal and AA swaps in the mounted position. Validate battery lead polarity and power conversion before connecting to the ESP32.

### What if the Takachi is hard to source?

- Option A: a simple open 2 × AA battery tray recessed into a custom **printed box with vertical snap-off or captive-screw lid**. The printed lid must have a grip notch, mechanical stops, adequate finger clearance and replaceable contacts via the commercial tray.
- Option B: a **hinged-lid** enclosed 2 × AA battery holder, if the rear is sufficiently unobstructed to allow the lid to swing. A Switch Electronics GT-YM218 is listed at 102 × 39.5 × 20.6 mm; it is longer and potentially protrudes more than the Takachi.
- Option C: mount an enclosed holder on the *outer* surface of the Perspex with only a small wire hole; not as flush but avoids a large acrylic opening.

## Superseded concept (revision 1): sliding-lid holder in printed bezel

**The following design is kept as historical prototype reference only and is NOT approved for fabrication.** The likely slide travel of a commercial holder was not accommodated in the initial bezel. Its recessed slot and lid mechanism have not been validated. The STL/SCAD files in this folder remain unchanged for comparison.

## Original sliding-lid concept: recessed box behind acrylic

Use a commercially manufactured **enclosed two-AA holder** with its own metal battery contacts, wiring, and removable lid, and mount it in a 3D-printed bezel fastened to the rear Perspex plate. The box points into the gap between Perspex and screen while its lid remains accessible from the rear. **Do not cut the acrylic until fitting and orientation are verified.**

Example box: Multicomp Pro MP000368 / MP000375, advertised **67 × 33 × 19 mm**, with 150 mm leads and detachable lid. Switched version MP000375 is optional.

- Bezel outer flange: **98 × 49 × 3 mm**
- Sleeve extends **18 mm forward** into the void from the rear Perspex face
- Printed sleeve outside: **72 × 38 mm**
- **Preliminary**, not-final acrylic cutout: **73 × 39 mm** (adjust after measuring/printing)
- 2 × M3 bezel fixing holes at **87 mm centre-to-centre**
- Thin acrylic should use larger clearance holes, through-bolts, compatible washers/spacers and nuts, not thread-forming screws or countersinks.
- Finger notches permit lifting the battery box to access its existing lid; if the lid needs to slide, the holder may need to be drawn out by a few mm, using slack in its leads.
- **The box is NOT mechanically secured to the bezel yet**; first trial fit, then design a small serviceable retention latch/clip or removable retention screws. Do not permanently glue a serviceable battery box or its lid.

For the NiMH LADDA pair, feed a suitable low-quiescent 3.3V boost converter with sufficient peak-current capability (the existing ESP32 design spec covers this). Batteries must be removable for external charging. Provide strain relief and insulation for wiring, and avoid sharp acrylic edges.

### Alternative, no large Perspex cut

If the existing cavity has less than ~19 mm clearance, surface-mount an enclosed battery box on the outside of the rear Perspex using a custom screw-on cradle and pass the wires through a small grommeted hole instead. That increases exterior depth but avoids weakening the backplate.

### To confirm before cutting Perspex

1. Measure Perspex thickness and available cavity depth at the intended position (including clearances to the screen driver PCB, wires and screw heads).
2. Check that the proposed 98 × 49 mm bezel will not overlap existing screen-frame screws or wall-mounting hardware.
3. Obtain the **actual** enclosed holder and check whether the lid lifts or slides and which end the leads emerge from.
4. Print and test-fit the bezel; measure shrinkage/clearance and choose a releasable retention method.
5. Drill small mounting holes and cut the rectangular slot **only after** completing the above. Use acrylic-friendly drill/cut techniques, backing support, and avoid overtightening.

### Files

- [Parametric OpenSCAD prototype](2xAA_recessed_holder_bezel.scad) — adjust sizes after measurement.

### References

- [Multicomp Pro MP000368 enclosure (67×33×19 mm)](https://cpc.farnell.com/pro-power/pp002097/battery-box-2x-aa-wired/dp/BT06548)
- [Multicomp Pro MP000375 switched version](https://cpc.farnell.com/multicomp-pro/mp000375/battery-box-2x-aa-switched-wired/dp/BT06555)
- [Plaskolite OPTIX acrylic fabrication guidance](https://www.curbellplastics.com/wp-content/uploads/2022/11/Plaskolite-OPTIX-Acrylic-Fabrication-Guide.pdf)
