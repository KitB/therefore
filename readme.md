# Therefore Mechanical Keyboard

Therefore is a from-scratch ergodox clone focussing on ease of use between
multiple computers in multiple locations and firmware written in Python for ease
of customization.

### Design goals:

* USB-C, BLE, NRF24L01 dongle, and possibly Logitech Unifying Receiver
  connectivity
* Wireless split alongside TRRS as an option
* Compact and low-profile, designed for portability ("portodox" was a candidate
  name)
* Carrying case or magnetic snap-together of the halves
* Either easy-to-source parts (e.g. adafruit and bog-standard components) or
  a single PCB with everything on it manufactured by e.g. JLCPCB.
  
### Non-goals:

* Low latency: this is not a gaming keyboard; latency between split halves is
  important for avoiding transposition errors though.
* USB Hub: Sadly not possible over the wireless protocols.
* Adjustments to normal ergodox layout: In particular no adjustments will be
  made in the name of compactness; the goal is to make it as compact as possible
  within the layout of the normal ergodox.
  
 
 ## State of affairs
 I am typing this on a therefore made out of PCBs manufactured by JLCPCB with
 a case I 3d printed (and then cut up a little to make a bigger hole for USB
 cables). Each half has a Adafruit Feather NRF52840 and a hand-wired TRRS
 connector. It is very much a prototype but I have been typing on this
 keyboard alone for months now.
 
 Code for fully wireless operation is present and functional but latency between
 halves ruins it; I don't think this is inherent in BLE, just present in this
 implementation.
 
 ## License
 The firmware is BSD 3-clause licensed (see [firmware/python/LICENSE ](firmware/python/LICENSE))
 but the hardware is currently all-rights-reserved.
 It will in future be open source or at least free for non-commercial use.