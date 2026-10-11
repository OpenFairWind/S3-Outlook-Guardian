#!/usr/bin/env python3
"""Print pad positions and nets of the given references: pads.py U4 J3 ..."""
import sys

import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
for ref in sys.argv[2:]:
    fp = b.FindFootprintByReference(ref)
    out = []
    for p in fp.Pads():
        if p.GetNumber():
            out.append("%s(%.1f,%.1f %s)" % (p.GetNumber(), pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y), p.GetNetname()))
    print(ref, " ".join(out))
