# i3-tray-shuffler

Moves your i3bar tray out of the way of full-screen applications.

## Installation

Put `i3-tray-shuffler.py` somewhere.

Python 3.8+ is required.

## Usage

In the `bar` section of your i3 config file, adjust the `tray_output`
lines to look like this (assuming you'd like your tray to appear on
HDMI-1 if possible, or eDP-1 if that monitor is full):

```
bar {
    tray_output HDMI-1 # managed by i3-tray-shuffler
    tray_output eDP-1 # managed by i3-tray-shuffler
    tray_output primary # managed by i3-tray-shuffler
}
```

The comments are important.

Run i3-tray-shuffler whenever you'd like your tray to move to an
unoccupied monitor. i3 will only be reloaded when necessary, so you can
run it more often than you need to if you like.
