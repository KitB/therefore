use <case.scad>

color("#ddd")
case();

color("#ddd")
translate([-10, 0, 4])
rotate([0, 180, 0])
case(part="lid");

// electronics
translate([0, 73, 4])
cube([36, 29, 4.75]);

translate([0, 110, 4])
cube([35, 18, 2]);

/*
use <plate.scad>
translate([0, 0, 0])
plate();
*/
