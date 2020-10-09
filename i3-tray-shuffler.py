#!/usr/bin/env python3.8

import os
import re
from subprocess import run
from typing import List, NamedTuple, Optional


I3_CONFIG_PATH = os.path.expanduser("~/.config/i3/config")


class Monitor(NamedTuple):
    width: int
    height: int
    x: int
    y: int
    physical_width: Optional[int] = None
    physical_height: Optional[int] = None
    name: Optional[str] = None


class Window(NamedTuple):
    id: str
    width: int
    height: int
    x: int
    y: int
    name: Optional[str] = None


def get_monitors() -> List[Monitor]:
    result = run(["xrandr", "--listmonitors"], capture_output=True, text=True)
    assert result.returncode == 0
    monitors = []
    for line in filter(None, map(str.strip, result.stdout.splitlines()[1:])):
        # FIXME: I think "name" here captures the monitor, but we want the output
        assert (match := re.match(r"(?P<i>\d+): \+?\*?(?P<name>\S+) (?P<width>\d+)/(?P<physical_width>\d+)x(?P<height>\d+)/(?P<physical_height>\d+)\+(?P<x>\d+)\+(?P<y>\d+) .*", line)), repr(line)
        monitors.append(Monitor(**{k: int(v) if Monitor.__annotations__[k] == int else v for k, v in match.groupdict().items() if k in Monitor.__annotations__.keys() and v is not None}))
    return monitors


def main():
    monitors = get_monitors()
    result = run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)
    assert result.returncode == 0
    fullscreened_monitors = set()
    for line in filter(None, map(str.strip, result.stdout.splitlines())):
        if match := re.match(r"(?P<id>0x[0-9a-f]+) (?P<name>.*): \(.*\)  (?P<width>\d+)x(?P<height>\d+)\+-?\d+\+-?\d+  \+(?P<x>-?\d+)\+(?P<y>-?\d+)", line):
            window = Window(**{k: int(v) if Window.__annotations__[k] == int else v for k, v in match.groupdict().items() if k in Window.__annotations__.keys()})
            # TODO: check if the monitor is occluded, not just "is a window exactly fullscreened"
            # (though if we're doing that, we could plausibly just check whether the tray is occluded)
            if any((monitor := m).width == window.width and m.height == window.height and m.x == window.x and m.y == window.y for m in monitors):
                # Check that the window is actually mapped
                result = run(["xwininfo", "-id", window.id], capture_output=True, text=True)
                if result.returncode == 0 and "Map State: IsViewable" in "".join(result.stdout.splitlines()[3:]):
                    fullscreened_monitors.add(monitor.name)
    if fullscreened_monitors:
        print(", ".join(fullscreened_monitors))
    with open(I3_CONFIG_PATH, "r") as f:
        monitor_preference_order = []  # best first
        for line in f:
            if match := re.match(r"(?P<indent>\s*)(?P<comment># )?tray_output (?P<output>\S+) # managed by i3-tray-shuffler(?P<extra>.*)", line):
                assert match["output"] != "none"
                assert match["output"] not in monitor_preference_order
                assert "/" not in match["output"]
                monitor_preference_order.append((match["output"], match["comment"] or "", match["extra"]))
    replacements = []
    for monitor, existing_comment, extra in monitor_preference_order:
        note = ""
        if any(m.name == monitor for m in monitors) or monitor == "primary":
            if monitor in fullscreened_monitors:
                comment = "# "
            else:
                comment = ""
        else:
            comment = "# "
            note = " (monitor not found)"
        if comment != existing_comment or note not in extra:
            replacements.append((fr"(\s*)(# )?(tray_output {monitor} # managed by i3-tray-shuffler).*", f"\\1{comment}\\3{note}"))
    if replacements:
        for r in replacements:
            run(["sed", "-E", "-i.backup", f"s/{r[0]}/{r[1]}/", I3_CONFIG_PATH])
        run(["i3-msg", "reload"])


if __name__ == "__main__":
    main()
