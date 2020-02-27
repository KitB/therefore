$fn = 100;

sheath_outer_width = 2.6;
sheath_outer_length = 8.4;

module typec_sheath_outer() {
  module end_cylinder() {
    circle(sheath_outer_width / 2);
  }

  translate([-(sheath_outer_length - sheath_outer_width) / 2, 0, 0])
  union() {
    end_cylinder();
    translate([0, - (sheath_outer_width / 2), 0])
      square([sheath_outer_length - sheath_outer_width, sheath_outer_width]);
    translate([sheath_outer_length - sheath_outer_width, 0, 0])
    end_cylinder();
  }
}

module typec_sheath_inner() {
  offset(r=-0.3) typec_sheath_outer();
}

module typec_male(length=6) {
  linear_extrude(length)
  difference() {
    typec_sheath_outer();
    typec_sheath_inner();
  }
}

typec_male();
