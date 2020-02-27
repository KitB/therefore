use <../typec.scad>
// TODO: cable-hole between plate hole and bits hole
module case (
part = "main",
thickness = 2,
base_clearance = 10,
plate_svg = "../shapes/plate.optimized.svg",
case_svg = "../shapes/case.svg",
logo_svg = "../shapes/logo.svg",
plate_thickness = 2,
under_plate_clearance = 2,
overhang = 4,
fudge = 0.01,
) {
  // how much space does the plate take up (ish)
  plate_height = under_plate_clearance + plate_thickness;
  // how much room do we need for the electronics
  bits_height = max(base_clearance, plate_height);
  // how high is the main part (without lid)
  main_height = max(base_clearance, plate_height) + thickness * 2;

  module s_plate () {
    import(plate_svg, center = false);
  }

  module s_case () {
    import(case_svg, center = false);
  }

  module case_outline () {
    offset(thickness) s_case();
  }

  module case_solid () {
    linear_extrude(main_height) case_outline();
  }

  module plate_hole () {
    // hole for the keys to sit in
    translate([0, 0, main_height - plate_height - thickness])
      linear_extrude(main_height * 2) s_plate();
  }

  module bits_shape () {
    translate([- thickness / 2, thickness / 2])
      offset(r = thickness * .5)
        offset(delta = - thickness)
          difference() {
            offset(delta = - fudge * 5) s_case();
            offset(delta = fudge * 5) s_plate();
          }
  }

  module bits_hole () {
    // hole for the electronics to sit in
    translate([0, 0, main_height - bits_height])
      linear_extrude(main_height * 2)
        bits_shape();
  }

  module main_case () {

    module solid () {
      linear_extrude(main_height) case_outline();
    }

    module logo () {
      translate([0, 0, main_height - plate_height - thickness - 0.1])
        linear_extrude(main_height * 2)
          import(logo_svg);

      translate([0, 0, - fudge])
        linear_extrude(0.1) import(logo_svg);
    }

    module typec_hole() {
      translate([20, 140, (main_height + thickness) / 2])
      rotate([90, 0, 0])
      linear_extrude(10)
      offset(delta=0.1)
      typec_sheath_outer();
    }

    difference() {
      solid();
      plate_hole();
      bits_hole();
      logo();
      typec_hole();
    }
  }


  module lid () {
    difference() {
      union() {
        // Top of lid
        translate([0, 0, thickness])
          linear_extrude(thickness)
            offset(delta = thickness) s_case();

        // fit bits
        linear_extrude(thickness + fudge)
          offset(delta = - 0.5)
            union() {
              s_plate();
              bits_shape();
            }
      }
      // hole for keys
      translate([0, 0, - fudge])
        linear_extrude(thickness + fudge * 2)
          offset(delta = - overhang)
            s_plate();
      translate([0, 0, thickness - fudge])
      linear_extrude(thickness + fudge * 2)
      offset(delta = -2)
      s_plate();
    }
  }

  if (part == "main") {
    main_case();
  } else if (part == "lid") {
    lid();
  }
}

case();
