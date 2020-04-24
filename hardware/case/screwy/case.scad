include <BOSL2/std.scad>;
include <BOSL2/rounding.scad>;
include <BOSL2/metric_screws.scad>
use <../utils.scad>;
include <../shape.scad>;

$fn = 15;
epsilon = 0.01;

// Thicknesses
wall_thickness = 1.5;
roof_thickness = 3;
floor_thickness = 1.5;
plate_thickness = 3.5;
switch_clip_thickness = 1.5;
switch_clip_overhang = 0.75;
separator_thickness = 20;

smoothness = 1;

screw_inner_diameter = 4.3;
screw_outer_diameter = 8.3;

// Switch-related dimensions
switch_hole_side = 14.45; // switch holes will be a square of side <this>
keycap_edge_clearance = 2; // desired distance between keycap edge and case.
_lower_switch_height = 8.3; // distance from top of plate to bottom of switch
under_plate_clearance = _lower_switch_height - plate_thickness;
basin_drop = 6; // roughly equal to the distance from the top of the plate to the bottom of the keycap

// calculated dimensions
inner_height = basin_drop + under_plate_clearance + roof_thickness;
outer_height = inner_height + floor_thickness;

innards_outer_height = basin_drop + plate_thickness + roof_thickness;
innards_inner_height = basin_drop + roof_thickness;

case_path_outer_offset = keycap_edge_clearance +  wall_thickness + 5;
case_path_inner_offset = case_path_outer_offset - wall_thickness;


function roundit(path) = round_corners(path, curve = "smooth", measure = "joint", size = 4);

d = 19.06;
keyhole_path_test = reverse([
[0, 0],
[0, d * 2],
[d, d * 2],
[d, d],
[d * 2, d],
[d * 2, 0],
[0, 0]
]);

case_path_test = reverse([
[0, 0],
[0, d * 2],
[d * 2, d * 2],
[d * 2, 0],
[0, 0]
]);

switch_locations_test = [
[d * 0.5, d * 0.5, 0],
[d * 1.5, d * 0.5, 0],
[d * 0.5, d * 1.5, 0]
];

s = keycap_edge_clearance + (case_path_outer_offset - keycap_edge_clearance) / 2;
adjust = 0.8;
screw_locations_test = [
  [-(s - adjust), -(s - adjust), 0],
  [d * 2 + (s - adjust), -(s - adjust), 0],
  [d * 2 + (s - adjust), d * 2 + (s - adjust), 0],
[-(s - adjust), d * 2 + (s - adjust), 0],
];

screw_locations = [
[-(s - adjust), -(s - adjust), 135],
[-(s - adjust), y3 + (s - adjust), 45],
[x1 - 0.2 * s, y3 + s + 0.8 * adjust, 25],
[x3 + 0.5 * s, yn + s + 0.8 * adjust, 335],
[xn + s, y2, 275],
[xn + (s - adjust), -(s - adjust), 225],
];

test = false;

case_path = test ? case_path_test : case_points;
keyhole_path = test ? keyhole_path_test : bounding_points;
switches = test ? switch_locations_test : switch_locations;
screws = test ? screw_locations_test : screw_locations;
electronics_path = difference([case_path, keyhole_path]);


function innards_outer(path) = roundit(offset(path, delta = keycap_edge_clearance + wall_thickness, closed = true));
function innards_inner(path) = roundit(offset(path, delta = keycap_edge_clearance, closed = true));

case_inner_path = roundit(offset(case_path, delta = case_path_inner_offset, closed = true));
case_outer_path = roundit(offset(case_path, delta = case_path_outer_offset, closed = true));
separator_inner_path = roundit(offset(case_path, delta = keycap_edge_clearance, closed = true));

module switch_hole () {
  down(epsilon)
  linear_extrude(plate_thickness + epsilon * 2)
    square(switch_hole_side, center = true);

  up(switch_clip_thickness + epsilon)
  linear_extrude(plate_thickness)
    square(switch_hole_side + switch_clip_overhang * 2, center = true);
}

plate_screws = pad_angles([
  [5.08, 2.42],
  [5.08, 95.8],
  [91.35, 101.6],
  [138, 123.7],
  [178.4, 2.42],
  [178.65, 70.82],
]);

module plate () {
  difference() {
    linear_sweep(innards_inner(keyhole_path), plate_thickness + epsilon);

    pnp(switches)
    switch_hole();

    pnp(plate_screws) {
      down(epsilon)
      cylinder(h = plate_thickness - 3 + epsilon * 2, d2 = 3.3, d1 = 3.1);
      up(plate_thickness - 3)
      cylinder(h = 3 + epsilon * 3, d1 = 3.3, d2 = 6.5);
    }
  }
}

module usb_hole () {
  rotate([90, 0, 0])
    down(2)
    linear_extrude(4)
    region([round_corners(square([9, 3], center = true), curve = "smooth", measure = "joint", size = 1.5)]);
}

usb_screw_x_diff = 0.3 * 25.4;

usb_location = [165, -8, 8];
usb_screws = [[165 - usb_screw_x_diff, -4.4, 0], [165 + usb_screw_x_diff, -4.4, 0]];

module shell () {
  difference() {
    linear_sweep(case_outer_path, 16);
    up(floor_thickness)
    linear_sweep(case_inner_path, 16);

    translate(usb_location)
      usb_hole();
  }

  pnp(screws)
  difference() {
    cylinder(h = 16, d = 6);
    up(floor_thickness)
    cylinder(h = 16 - floor_thickness + epsilon, d2 = 3.4, d1 = 2.5);
  }

  pnp(usb_screws)
  difference() {
    cylinder(h = 9, d = 4);
    up(floor_thickness)
    cylinder(h = 9 - floor_thickness + epsilon, d2 = 3, d1 = 2.5);
  }

  pnp(plate_screws)
  difference () {
    cylinder(h = 4, d = 4.5);
    up(floor_thickness)
    cylinder(h = 4 + epsilon, d1 = 3, d2 = 3.4);
  }
}

module magnet () {
  linear_extrude(2.2)
    square([10.1, 3.1], center = true);
}

magnet_locations = [
  [-5, 50, 90],
  [xn + s, 50, 90],
  [(xn + s) / 2, -5, 0],
  [x3 - 12, yn, 25],
];

module lid () {
  difference () {
    // Make the plate
    linear_sweep(case_outer_path, roof_thickness);

    // Let the keycaps through
    down(epsilon / 2)
    linear_sweep(innards_inner(keyhole_path), roof_thickness + epsilon);

    // Let the screws through
    pnp(screws)
    down(epsilon / 2)
    cylinder(h = roof_thickness + epsilon, d1 = 3.4, d2 = 6);

    pnp(magnet_locations)
    #magnet();
  }
}

module separator_inner () {
  si_thickness = separator_thickness - roof_thickness * 2;
  difference () {
    // Make the plate
    linear_sweep(case_outer_path, si_thickness);

    down(epsilon)
    linear_sweep(separator_inner_path, si_thickness + epsilon * 2);

    down(epsilon)
    pnp(screws) {
      cylinder(h = si_thickness / 2 + epsilon, d1 = 3.4, d2 = 2.5);
      up(si_thickness / 2 - epsilon)
      cylinder(h = si_thickness / 2 + epsilon * 3, d2 = 3.4, d1 = 2.5);
    }
  }
}

module separator_outer () {
  difference () {
    // Make the plate
    linear_sweep(case_outer_path, roof_thickness);

    // Let the keycaps through
    down(epsilon / 2)
    linear_sweep(separator_inner_path, roof_thickness + epsilon);

    // Let the screws through
    pnp(screws)
    down(epsilon / 2)
    cylinder(h = roof_thickness + epsilon, d1 = 3.4, d2 = 6);

    pnp(magnet_locations)
    #magnet();
  }
}

*intersection () {
  shell();

  translate([165 - 15, -10, -1])
  cube([30, 10, 30]);
}

right(1.8)
fwd(0.7)
up(5)
color("black")
*import("plate_exclude.svg");

*up(10)
plate();

//*rotate([0, 180 ,180])
*up(30)
lid();

*shell();

*rotate([0, 180 ,180])
separator_outer();

*separator_inner();
