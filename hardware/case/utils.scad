module pnp(locations) {
  for (loc = locations) {
    x = loc[0];
    y = loc[1];
    a = loc[2];
    translate([x, y])
    rotate(a)
    children();
  }
}