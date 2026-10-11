#!/usr/bin/env python3
"""Compare the netlist exported from the schematic with the pin map in design.py."""
import os
import sys

import design
from sexpr import find, first, parse

here = os.path.dirname(os.path.abspath(__file__))
net = parse(open(os.path.join(here, "..", "build", "netlist.net")).read())
got = {}
for n in find(first(net, "nets"), "net"):
    name = first(n, "name")[1].lstrip("/")
    for node in find(n, "node"):
        got[(first(node, "ref")[1], first(node, "pin")[1])] = name
want = {(p["ref"], num): netname for p in design.PARTS for num, netname in p["pins"].items() if netname}
bad = 0
for key in sorted(set(got) | set(want)):
    g, w = got.get(key), want.get(key)
    if w is None and g is not None and g.startswith("unconnected-"):
        continue
    if g != w:
        bad += 1
        print("MISMATCH", key, "schematic:", g, "design:", w)
print("pins checked: %d, mismatches: %d" % (len(want), bad))
sys.exit(1 if bad else 0)
