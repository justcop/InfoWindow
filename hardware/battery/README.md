# InfoWindow two-AA battery compartment — mechanical prototype

This is experimental **on `feature/esp32-c6-zigbee-infowindow` only**. It does not change the working Pi implementation or the original 3D case.

## Preferred layout: recessed box behind acrylic

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
