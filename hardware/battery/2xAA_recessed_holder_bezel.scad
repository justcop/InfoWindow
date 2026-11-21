/*
 InfoWindow: two-AA rechargeable battery holder mounting bezel
 Experimental fit-check v0.1. NOT a final fabrication drawing.
 Designed around a common enclosed holder 67 x 33 x 19 mm,
 e.g. Multicomp MP000368/MP000375. Verify actual holder and
 Perspex dimensions before cutting. Assumes battery holder has a
 removable lid accessible from the REAR (positive Z).

 Coordinate model: Perspex rear surface is z=0, Perspex/front-screen
 space is negative Z. The flange remains on the Perspex rear face;
 the sleeve projects through a rectangular slot towards the display.
 External M3 fasteners clamp the bezel to the Perspex via washers;
 do not tap or countersink thin Perspex directly.

 This printed part is a MOUNTING BEZEL, not a battery holder.
 An actual battery holder provides the metal contacts and lid.
 The holder is retained in the bezel by a removable nonconductive
 side adhesive/clip solution developed after test fit. Do not glue
 the lid shut. Verify sufficient room for lid sliding direction.
*/
$fn=48;

// Measured nominal 2x AA box dimensions in millimetres.
holder_l=67;
holder_w=33;
holder_h=19;

// Printer/holder tolerance: 0.5mm clearance on EACH side.
clearance=0.5;
wall=2.0;
flange_thickness=3.0;
sleeve_depth=18.0;
flange_l=98;
flange_w=49;

// Screw holes through flange; Perspex holes should be independently
// drilled to a suitable clearance based on its thickness/expansion.
hole_d=3.4;
hole_spacing=87; // two mounting holes, separated along length

inside_l=holder_l+2*clearance;
inside_w=holder_w+2*clearance;
sleeve_l=inside_l+2*wall;
sleeve_w=inside_w+2*wall;

// Nominal Perspex rectangular slot: ~ (sleeve_l+1) x (sleeve_w+1).
// Here: 73mm x 39mm; verify after printing the bezel.

difference() {
    union() {
        // Rear-visible fixing flange z=0..3
        translate([-flange_l/2,-flange_w/2,0])
            cube([flange_l,flange_w,flange_thickness]);
        // Sleeve projecting through Perspex towards the screen
        translate([-sleeve_l/2,-sleeve_w/2,-sleeve_depth])
            cube([sleeve_l,sleeve_w,sleeve_depth]);
    }

    // Main receptacle; rear opening kept fully accessible.
    // Bottom 1mm of sleeve is a retaining ledge.
    translate([-inside_l/2,-inside_w/2,-sleeve_depth+1.0])
        cube([inside_l,inside_w,sleeve_depth+flange_thickness]);

    // Bottom opening retains a ~1.5mm wide seating lip.
    translate([-(inside_l-3)/2,-(inside_w-3)/2,-sleeve_depth-0.05])
        cube([inside_l-3,inside_w-3,1.15]);

    // Wire exit from near one short end of holder, through shelf.
    translate([-inside_l/2-0.4,-3,-sleeve_depth-0.05])
        cube([6,6,2.2]);

    // Finger-access cutouts on both long sides of the rear flange.
    // These permit pulling the enclosed battery box from the bezel
    // for lid removal even if its lid slides sideways.
    for(side=[-1,1])
      translate([-7.0,side>0 ? inside_w/2-0.5 : -inside_w/2-7.0,-1.0])
        cube([14.0,7.5,flange_thickness+1.1]);

    // Two accessible flat-head-free fixing holes.
    for(x=[-hole_spacing/2,hole_spacing/2])
      translate([x,0,-0.1])
        cylinder(h=flange_thickness+0.2,d=hole_d);
}
