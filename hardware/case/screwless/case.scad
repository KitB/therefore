include <BOSL2/std.scad>;
include <BOSL2/rounding.scad>;
include <BOSL2/metric_screws.scad>
use <../utils.scad>;
include <../shape.scad>;

$fn = 10;
epsilon = 0.01;

// Thicknesses
wall_thickness = 2;
roof_thickness = 3;
floor_thickness = 1.5;
plate_thickness = 3;
switch_clip_thickness = 1.5;
switch_clip_overhang = 0.75;
overhang = 4;
fit_delta = 0.3;

// Switch-related dimensions
switch_hole_side = 14.45; // switch holes will be a square of side <this>
keycap_edge_clearance = 2; // desired distance between keycap edge and case.
_lower_switch_height = 8.3; // distance from top of plate to bottom of switch
under_plate_clearance = _lower_switch_height - plate_thickness;
basin_drop = 6; // roughly equal to the distance from the top of the plate to the bottom of the keycap

inner_height = basin_drop + under_plate_clearance + roof_thickness;
outer_height = inner_height + floor_thickness;

function roundit(path) = round_corners(path, curve = "smooth", measure = "joint", size = 4);

d = 19.05;
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

test = false;

case_path = test ? case_path_test : case_points;
keyhole_path = test ? keyhole_path_test : bounding_points;
switches = test ? switch_locations_test : switch_locations;
electronics_path = difference([case_path, keyhole_path]);


case_inner_path = roundit(offset(case_path, delta = keycap_edge_clearance + fit_delta + wall_thickness, closed = true));
case_outer_path = roundit(offset(case_path, delta = keycap_edge_clearance + fit_delta + wall_thickness * 2, closed = true));

function innards_outer(path) = roundit(offset(path, delta = keycap_edge_clearance + wall_thickness, closed = true));
function innards_inner(path) = roundit(offset(path, delta = keycap_edge_clearance, closed = true));

module innards_outer_solid (path) {
  offset_sweep(innards_outer(path), height = inner_height, bottom = os_chamfer(height = inner_height, width = wall_thickness));
}

module innards_inner_solid (path) {
  offset_sweep(innards_inner(path), height = inner_height, bottom = os_chamfer(height = inner_height, width = wall_thickness));
}

intersection_square = square(60);

module sliced (top, bottom) {
  intersection () {
    translate([- 10, - 10, bottom])
      linear_extrude(top - bottom)
        square(200);

    children();
  }
}

module _case_outer_solid () {
  offset_sweep(case_outer_path, height = outer_height, bottom = os_smooth(joint = 4));
}

module _case_inner_solid () {
  offset_sweep(case_inner_path, height = inner_height, bottom = os_chamfer(height = inner_height, width = wall_thickness));
}

module base () {
  difference() {
    _case_outer_solid();

    up(floor_thickness + epsilon)
    _case_inner_solid();
  }
}

module basin () {
  module plate () {
    intersection () {
      innards_outer_solid(case_path);
      difference() {
        sliced(top = inner_height - roof_thickness, bottom = inner_height - basin_drop - plate_thickness)
        innards_outer_solid(keyhole_path);

        sliced(top = inner_height - roof_thickness, bottom = inner_height - basin_drop)
        innards_inner_solid(keyhole_path);
      }

    }
  }
  module switch_hole () {
    down(epsilon)
    linear_extrude(plate_thickness + epsilon * 2)
    square(switch_hole_side, center = true);

    up(switch_clip_thickness)
    linear_extrude(switch_clip_thickness + epsilon)
    square(switch_hole_side + switch_clip_overhang * 2, center = true);
  }
  module switch_holes () {
    up(inner_height - basin_drop - plate_thickness)
    pnp(switches)
    switch_hole();
  }
  difference() {
    plate();
    switch_holes();
  }
}

module lid () {
  sliced (top = inner_height, bottom = inner_height - roof_thickness) {
    difference() {
      innards_outer_solid(case_path);
      innards_inner_solid(keyhole_path);
    }
  }
}

module innards () {
  up(floor_thickness) {
    basin();
    lid();
  }
}

//base();

//cube([50, 50, 0.5], center = true);

