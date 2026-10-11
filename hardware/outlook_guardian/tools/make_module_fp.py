#!/usr/bin/env python3
"""Derive the project's module footprint from KiCad's ESP32-S3-WROOM-1.

The stock footprint keeps a 48 mm wide strip clear around the antenna. On the
HALMET outline the antenna overhangs the board edge and the USB socket sits on
the tab next to it, inside that strip. This copy narrows the keep-out and the
courtyard to 26 mm, so they cover the antenna and 4 mm either side of the
module but not the tab.
"""
import os

from sexpr import Sym, dump, find, first, parse

STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/RF_Module.pretty/ESP32-S3-WROOM-1.kicad_mod"
NAME = "ESP32-S3-WROOM-1_EdgeAntenna"
HALF = 13.0


def narrow(node):
    for item in node:
        if isinstance(item, list):
            if item and item[0] in ("start", "end", "xy") and abs(abs(float(item[1])) - 24) < 0.5:
                item[1] = Sym(str(HALF if float(item[1]) > 0 else -HALF))
            else:
                narrow(item)


fp = parse(open(STOCK).read())
fp[1] = NAME
for line in find(fp, "fp_line"):
    if first(line, "layer")[1] == "F.CrtYd":
        narrow(line)
# The silkscreen outline of the antenna would be printed past the board edge.
fp[:] = [x for x in fp if not (isinstance(x, list) and x[0] == "fp_line" and first(x, "layer")[1] == "F.SilkS"
                               and min(float(first(x, "start")[2]), float(first(x, "end")[2])) < -6.75)]
for z in find(fp, "zone"):
    narrow(z)
first(fp, "descr")[1] += " - antenna keep-out narrowed to 26 mm for an antenna that overhangs the board edge"
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "OutlookGuardian.pretty", NAME + ".kicad_mod")
open(out, "w").write(dump(fp) + "\n")
