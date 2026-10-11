#!/usr/bin/env python3
"""Build outlook_guardian.kicad_pcb, ready for the autorouter, from the schematic netlist.

Run with KiCad's own Python, after exporting build/netlist.net:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 tools/gen_pcb.py

The outline, the mounting slots and the positions of the module, the GPIO
header, the display socket, the USB socket, the buttons and the NMEA 2000
terminal block are those of the Hat Labs HALMET board (CC BY 4.0).
"""
import json
import math
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fanout  # noqa: E402
from placement import PLACE  # noqa: E402
from sexpr import find, first, parse  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
KICAD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
SCH = "outlook_guardian.kicad_sch"

mm = pcbnew.FromMM


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def read_netlist():
    net = parse(open(os.path.join(OUT, "build", "netlist.net")).read())
    comps = {}
    for c in find(first(net, "components"), "comp"):
        ref = first(c, "ref")[1]
        fields = {f[1][1]: (f[2] if len(f) > 2 else "") for f in find(first(c, "fields") or [], "field")}
        comps[ref] = dict(value=first(c, "value")[1], footprint=first(c, "footprint")[1],
                          uuid=first(c, "tstamps")[1], mpn=fields.get("MPN", ""), pads={})
    for n in find(first(net, "nets"), "net"):
        name = first(n, "name")[1]
        for node in find(n, "node"):
            comps[first(node, "ref")[1]]["pads"][first(node, "pin")[1]] = name
    return comps


def edge(board, kind, *pts):
    s = pcbnew.PCB_SHAPE(board)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.05))
    if kind == "line":
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(*pts[0]))
        s.SetEnd(pt(*pts[1]))
    else:
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(pt(*pts[0]), pt(*pts[1]), pt(*pts[2]))
    board.Add(s)


def outline(board):
    """The HALMET outline: 89 x 58 mm, concave corners, tab on the right."""
    edge(board, "line", (89, 65.5), (89, 106.5))
    edge(board, "line", (169.5, 57), (97.5, 57))
    edge(board, "line", (169.5, 115), (97.5, 115))
    edge(board, "arc", (97.5, 57), (95.010408, 63.010408), (89, 65.5))
    edge(board, "line", (178, 90.3), (178, 106.5))
    edge(board, "line", (172, 90.3), (172.000092, 63.020889))
    edge(board, "arc", (172.000092, 63.020889), (170.149866, 60.259661), (169.5, 57))
    edge(board, "arc", (169.5, 115), (171.989592, 108.989592), (178, 106.5))
    edge(board, "arc", (89, 106.5), (95.010408, 108.989592), (97.5, 115))
    edge(board, "line", (178, 90.3), (172, 90.3))


SILK_REFS = {"U1", "U2", "U3", "U4", "U5", "U6", "J1", "J2", "J3", "J4", "J6"}

# Silkscreen labels: (text, x, y, size)
LABELS = [
    ("L", 92.27, 97.2, 0.8), ("H", 96.08, 97.2, 0.8), ("V+", 99.89, 97.2, 0.8), ("GND", 103.7, 97.2, 0.8),
    ("ACK", 94.2, 72.9, 0.9), ("SNOOZE", 104.4, 72.9, 0.9), ("SPEAKER", 124.8, 73.1, 0.8),
    ("BOOT", 165.25, 102.3, 0.8), ("RESET", 158.7, 113.4, 0.8),
    ("GND", 159.0, 102.2, 0.8), ("SDA", 145.3, 102.2, 0.8),
    ("USB", 175.6, 92.3, 0.8),
]

BOARD_POLY = [(97.5, 57), (169.5, 57), (170.15, 60.26), (172, 63.02), (172, 90.3), (178, 90.3), (178, 106.5),
              (171.99, 108.99), (169.5, 115), (97.5, 115), (95.01, 108.99), (89, 106.5), (89, 65.5),
              (95.01, 63.01)]


def zone(board, net, layer, poly=None, priority=0, clearance=0.25):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net if isinstance(net, pcbnew.NETINFO_ITEM) else board.FindNet(net))
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(clearance))
    z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    o = z.Outline()
    o.NewOutline()
    for x, y in poly or [(88, 56), (179, 56), (179, 116), (88, 116)]:
        o.Append(mm(x), mm(y))
    z.SetIsFilled(False)
    board.Add(z)
    return z


def keepout(board, poly, name):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    o = z.Outline()
    o.NewOutline()
    for x, y in poly:
        o.Append(mm(x), mm(y))
    board.Add(z)


def silk(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS, angle=0, justify=None):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetLayer(layer)
    t.SetPosition(pt(x, y))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    t.SetTextAngleDegrees(angle)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    if justify == "left":
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)


# Net classes. Rail is narrow enough to enter the amplifier's 0.5 mm pitch pads;
# the current on these nets is carried by the planes and the copper areas.
CLASSES = {
    "Power": (0.8, 0.8, 0.4, ["/VIN_RAW", "/VIN_FUSED", "/VIN_PROT", "/VIN_BUCK", "/SW"]),
    "Speaker": (0.5, 0.6, 0.3, ["/SPK_P", "/SPK_N"]),
    "Rail": (0.3, 0.6, 0.3, ["+5V", "+3V3", "GND", "/USB_VBUS", "/USB_5V", "/AMP_OUTP", "/AMP_OUTN", "/DISP_3V3"]),
}


def net_classes(pro):
    """Add the net classes and the project rules to the project file."""
    with open(pro) as f:
        d = json.load(f)
    ns = d["net_settings"]
    default = ns["classes"][0]
    ns["classes"] = [default]
    ns["netclass_patterns"] = []
    for i, (name, (width, via, drill, nets)) in enumerate(CLASSES.items()):
        ns["classes"].append(dict(default, name=name, track_width=width, via_diameter=via, via_drill=drill, priority=i))
        ns["netclass_patterns"] += [{"netclass": name, "pattern": n} for n in nets]
    d["board"]["design_settings"]["rules"]["min_resolved_spokes"] = 1
    with open(pro, "w") as f:
        json.dump(d, f, indent=2)
        f.write("\n")


def main():
    comps = read_netlist()
    path = os.path.join(OUT, "outlook_guardian.kicad_pcb")
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    board.SetFileName(path)
    tb = board.GetTitleBlock()
    tb.SetTitle("Outlook Guardian")
    tb.SetRevision("0.1")
    tb.SetCompany("OpenFairWind")
    tb.SetComment(0, "Form factor, GPIO and display headers after Hat Labs HALMET (CC BY 4.0)")

    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_MinClearance = mm(0.15)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    ds.m_CopperEdgeClearance = mm(0.25)
    ds.m_HoleClearance = mm(0.25)
    ds.m_HoleToHoleMin = mm(0.5)

    nets = sorted({n for c in comps.values() for n in c["pads"].values()})
    for name in nets:
        board.Add(pcbnew.NETINFO_ITEM(board, name))

    missing = [r for r in comps if r not in PLACE]
    if missing:
        raise SystemExit("no placement for: %s" % " ".join(sorted(missing)))

    for ref, c in sorted(comps.items()):
        lib, name = c["footprint"].split(":")
        libdir = os.path.join(OUT, lib + ".pretty") if lib == "OutlookGuardian" else os.path.join(KICAD_FP, lib + ".pretty")
        fp = pcbnew.FootprintLoad(libdir, name)
        if fp is None:
            raise SystemExit("footprint not found: " + c["footprint"])
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        fp.SetPath(pcbnew.KIID_PATH("/" + c["uuid"]))
        fp.SetSheetname("/")
        fp.SetSheetfile(SCH)
        if c["mpn"]:
            fp.SetField("MPN", c["mpn"])
            fp.GetField("MPN").SetVisible(False)
        x, y, rot = PLACE[ref][:3]
        fp.SetPosition(pt(x, y))
        fp.SetOrientationDegrees(rot)
        numbers = set()
        for pad in fp.Pads():
            num = pad.GetNumber()
            if not num:
                continue
            numbers.add(num)
            if num in c["pads"]:
                pad.SetNet(board.FindNet(c["pads"][num]))
        unplaced = set(c["pads"]) - numbers
        if unplaced:
            raise SystemExit("%s: footprint %s has no pads %s" % (ref, name, sorted(unplaced)))
        # Only the ICs and some connectors are named on the silkscreen; the
        # other references are on the fabrication layer.
        fp.Reference().SetVisible(ref in SILK_REFS)
        board.Add(fp)
        if len(PLACE[ref]) > 3 and PLACE[ref][3] == "B":
            # Flipping needs the footprint to be on a board.
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)

    outline(board)

    # The two inner layers are planes: the autorouter gets the outer layers.
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    failed = fanout.Fanout(board, BOARD_POLY).run(links(board))
    if failed:
        raise SystemExit("no plane connection for: " + ", ".join(failed))

    # No tracks between the module and the board edge next to the antenna.
    keepout(board, [(171.3, 62), (173, 62), (173, 90.2), (171.3, 90.2)], "Antenna edge keep-out")

    # Room for the screw heads around the mounting slots.
    for ref in ("H1", "H2"):
        cx, cy = PLACE[ref][:2]
        keepout(board, [(cx + 3.1 * math.cos(math.radians(a)), cy + 3.1 * math.sin(math.radians(a)))
                        for a in range(0, 360, 30)], "Mounting slot " + ref)

    silk(board, "Outlook Guardian", 100, 60.2, 1.5, justify="left")
    silk(board, "rev 0.1", 100, 62.4, 1.0, justify="left")
    for text, x, y, size in LABELS:
        silk(board, text, x, y, size)
    silk(board, "Outline and headers after Hat Labs HALMET, CC BY 4.0", 131, 113.6, 0.8, pcbnew.B_SilkS)

    pcbnew.SaveBoard(path, board)
    net_classes(path.replace(".kicad_pcb", ".kicad_pro"))
    print("footprints:", len(comps), "nets:", len(nets))


def links(board):
    """Hand-drawn tracks that join pads of one plane net inside a footprint."""
    def pos(ref, num):
        return [(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
                for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num]

    # Regulator: output pin to the tab, under the body.
    (ax, ay), (bx, by) = pos("U2", "2")
    out = [({("U2", "2")}, [(ax, ay, bx, by, 1.0)], [])]
    # Amplifier: thermal pad to its three ground pins, with one via in the pad,
    # and the two supply pins joined.
    ex, ey = pos("U5", "17")[0]
    segs = []
    for num in ("3", "11", "15"):
        px, py = pos("U5", num)[0]
        segs.append((ex, py, px, py, 0.25) if abs(px - ex) > abs(py - ey) else (px, ey, px, py, 0.25))
    out.append(({("U5", n) for n in ("3", "11", "15", "17")}, segs, [(ex, ey)]))
    (ax, ay), (bx, by) = pos("U5", "7")[0], pos("U5", "8")[0]
    out.append(({("U5", "7"), ("U5", "8")}, [(ax, ay, bx, by, 0.25)], []))
    return out


def planes(board):
    """Restore the plane nets and add all copper zones. Called after routing."""
    net = fanout.restore(board)
    zone(board, net["GND"], pcbnew.In1_Cu)
    zone(board, net["+3V3"], pcbnew.In2_Cu)
    zone(board, net["+5V"], pcbnew.In2_Cu, poly=fanout.ISLAND_5V, priority=1)
    zone(board, net["GND"], pcbnew.F_Cu)
    zone(board, net["GND"], pcbnew.B_Cu)


if __name__ == "__main__":
    main()
