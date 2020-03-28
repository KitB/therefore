use <BOSL/math.scad>;
x0 = 0;
xn = 183;

x2 = 141.6;
x3 = xn - 23.54;
x1 = x3 - 79.76;


y0 = 0;
yn = 137;

y1 = 66.71;
y2 = y1 + 18.98;
y3 = yn - 37.2;

bounding_points = [
[x0, y0],
[x2, y0],
[x2, y1],
[xn, y2],
[x3, yn],
[x1, y3],
[x0, y3],
[x0, y0],
];

module bounding_path () {
  mirror([0, 1, 0])
    polygon(points = bounding_points);
}

case_points = [
[x0, y0],
[xn, y0],
[xn, y2],
[x3, yn],
[x1, y3],
[x0, y3],
[x0, y0],
];

module case_path () {
  polygon(points = case_points);
}

sx0 = 0;
sxn = 15.61;
sxcut = 0.813;

sy0 = 0;
syn = 14;
sycut = 9.503 - 4.494;

switch_hole_points = [];


function cat (LS) = [for (L = LS, a = L) a];
function add (mat, vec) = [for (mv = mat) mv + vec];
function mul (mat, vec) = [for (mv = mat) vmul(mv, vec)];
function pad_angles (locations) = [for (loc = locations) concat(loc, [0])];

inter_switch_distance = 19.05;
d = inter_switch_distance;

finger_locations = pad_angles([
  [0,        0], [d,     0], [2 * d,    -1.27], [3 * d,    -2.82], [4 * d,    -1.27], [5 * d,     1.9], [6.25 * d,     1.9],
  [0, 1.25 * d], [d,     d], [2 * d,     d - 1.27], [3 * d,     d - 2.82], [4 * d,     d - 1.27], [5 * d,     d + 1.9], [6.25 * d,     d + 1.9],
                 [d, 2 * d], [2 * d, 2 * d - 1.27], [3 * d, 2 * d - 2.82], [4 * d, 2 * d - 1.27], [5 * d, 2 * d + 1.9], [6.25 * d, 2 * d + 1.9],
  [0, 2.75 * d], [d, 3 * d], [2 * d, 3 * d - 1.27], [3 * d, 3 * d - 2.82], [4 * d, 3 * d - 1.27], [5 * d, 3 * d + 1.9], [6.25 * d, 3 * d + 1.9],
                             [2 * d, 4 * d - 1.27], [3 * d, 4 * d - 2.82], [4 * d, 4 * d - 1.27], [5 * d, 4 * d + 1.9], [   6 * d, 4 * d + 1.9],
]);

a = -25;
thumb_locations = rot(a, cp=[3 * d + 7, 4 * d - 2.82, 0], p=add([
  [d - 14 , d * 2.75 + 14, a],
  [0 - 14 , d * 2.75 + 14, a],
  [0 - 14 , d * 1.25 + 14, a],
  [-d - 14 , d * 1.25 + 14, a],
  [-d - 14 , d * 2.25 + 14, a],
  [-d - 14 , d * 3.25 + 14, a],
], [2.9, -3.1, 0]));

_switch_locations = concat(finger_locations, thumb_locations);

switch_locations = add(mul(_switch_locations, [-1, 1, -1]), [xn - 10 - 40.73, 7 + 4.62, 0]);

