#!/usr/bin/env python3
"""Generate outlook_guardian.kicad_sch from design.py.

Every pin gets a short wire stub ending in a net label (or a power symbol), so
the connectivity of the sheet is exactly the pin map in design.py.
"""
import copy
import math
import os
import uuid

import design
from sexpr import S, Sym, dump, find, first, parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
PROJECT = "outlook_guardian"
KICAD_SYMBOLS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
NS = uuid.UUID("6f0c3a52-3f5e-4b7e-9a57-0d7f2f1d9c11")
ROOT = str(uuid.uuid5(NS, "root"))
STUB = 2.54
FONT = S("font", S("size", 1.27, 1.27))

_libs = {}


def uid(key):
    return str(uuid.uuid5(NS, key))


def load_symbol(lib_id):
    """Return a flattened copy of a stock symbol, named lib:name."""
    lib, name = lib_id.split(":")
    if lib not in _libs:
        with open(os.path.join(KICAD_SYMBOLS, lib + ".kicad_sym")) as f:
            _libs[lib] = {s[1]: s for s in find(parse(f.read()), "symbol")}
    sym = copy.deepcopy(_libs[lib][name])
    ext = first(sym, "extends")
    if ext:
        parent = copy.deepcopy(_libs[lib][ext[1]])
        props = {p[1]: p for p in find(sym, "property")}
        merged = []
        for item in parent:
            if isinstance(item, list) and item[0] == "property" and item[1] in props:
                merged.append(props.pop(item[1]))
            elif isinstance(item, list) and item[0] == "symbol":
                item[1] = name + item[1][len(ext[1]):]
                merged.append(item)
            else:
                merged.append(item)
        merged[1] = name
        sym = merged
    sym[1] = lib_id
    return sym


def pins_of(sym):
    out = []
    for unit in find(sym, "symbol"):
        for pin in find(unit, "pin"):
            at = first(pin, "at")
            out.append(dict(number=first(pin, "number")[1], name=first(pin, "name")[1], type=str(pin[1]),
                            x=float(at[1]), y=float(at[2]), angle=float(at[3]),
                            length=float(first(pin, "length")[1])))
    return out


def body_box(sym, pins):
    xs, ys = [], []
    for unit in find(sym, "symbol"):
        for rect in find(unit, "rectangle"):
            for key in ("start", "end"):
                xs.append(float(first(rect, key)[1]))
                ys.append(float(first(rect, key)[2]))
    if not xs:
        for p in pins:
            a = math.radians(p["angle"])
            xs.append(p["x"] + p["length"] * math.cos(a))
            ys.append(p["y"] + p["length"] * math.sin(a))
        xs += [-1.5, 1.5]
        ys += [-1.5, 1.5]
    return min(xs), min(ys), max(xs), max(ys)


def xform(x, y, rot):
    """Library coordinates (y up) to sheet offsets (y down) for a symbol rotation."""
    yd = -y
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return x * c + yd * s, -x * s + yd * c


def snap(v):
    """Snap to the 1.27 mm connection grid."""
    return round(v / 1.27) * 1.27


def r(v):
    return round(v, 3)


def effects(justify=None, hide=False, size=1.27, bold=False):
    font = S("font", S("size", size, size))
    if bold:
        font.append(S("bold", Sym("yes")))
    e = S("effects", font)
    if justify:
        e.append(S("justify", *[Sym(j) for j in justify.split()]))
    if hide:
        e.append(S("hide", Sym("yes")))
    return e


def prop(name, value, x, y, angle=0, justify=None, hide=False):
    return S("property", name, value, S("at", r(x), r(y), angle), effects(justify, hide))


class Sheet:
    def __init__(self):
        self.items = []
        self.lib = {}
        self.count = 0
        self.pwr = 0

    def symbol(self, lib_id):
        if lib_id not in self.lib:
            self.lib[lib_id] = load_symbol(lib_id)
        return self.lib[lib_id]

    def instance(self, lib_id, ref, x, y, rot, props, pins, power=False):
        self.count += 1
        node = S("symbol", S("lib_id", lib_id), S("at", r(x), r(y), rot), S("unit", 1),
                 S("exclude_from_sim", Sym("no")), S("in_bom", Sym("no" if power or ref[:2] == "TP" or ref[0] == "H" else "yes")),
                 S("on_board", Sym("yes")), S("dnp", Sym("no")), S("uuid", uid("sym" + ref)))
        node += props
        for p in pins:
            node.append(S("pin", p["number"], S("uuid", uid("pin%s.%s" % (ref, p["number"])))))
        node.append(S("instances", S("project", PROJECT, S("path", "/" + ROOT, S("reference", ref), S("unit", 1)))))
        self.items.append(node)

    def wire(self, x1, y1, x2, y2):
        self.items.append(S("wire", S("pts", S("xy", r(x1), r(y1)), S("xy", r(x2), r(y2))),
                            S("stroke", S("width", 0), S("type", Sym("default"))),
                            S("uuid", uid("wire%s,%s,%s,%s" % (r(x1), r(y1), r(x2), r(y2))))))

    def label(self, net, x, y, dx, dy):
        if dx < 0:
            angle, justify = 180, "right bottom"
        elif dx > 0:
            angle, justify = 0, "left bottom"
        elif dy < 0:
            angle, justify = 90, "left bottom"
        else:
            angle, justify = 270, "right bottom"
        self.items.append(S("label", net, S("at", r(x), r(y), angle), effects(justify),
                            S("uuid", uid("label%s,%s,%s" % (net, r(x), r(y))))))

    def power(self, net, x, y, dx, dy):
        lib_id = design.POWER_NETS[net]
        sym = self.symbol(lib_id)
        # GND draws below its pin, the supply symbols above it.
        if net == "GND":
            rot = {(0, 1): 0, (-1, 0): 270, (1, 0): 90, (0, -1): 180}[(dx, dy)]
        else:
            rot = {(0, -1): 0, (-1, 0): 90, (1, 0): 270, (0, 1): 180}[(dx, dy)]
        self.pwr += 1
        ref = "#PWR%03d" % self.pwr
        tx, ty = x + dx * 3.8, y + dy * 3.8
        justify = {(-1, 0): "right", (1, 0): "left"}.get((dx, dy))
        props = [prop("Reference", ref, x, y, hide=True),
                 prop("Value", net, tx, ty, justify=justify, hide=(net == "GND" and dy == 0)),
                 prop("Footprint", "", x, y, hide=True),
                 prop("Datasheet", "", x, y, hide=True),
                 prop("Description", "", x, y, hide=True)]
        self.instance(lib_id, ref, x, y, rot, props, pins_of(sym), power=True)

    def flag(self, net, x, y):
        x, y = snap(x), snap(y)
        sym = self.symbol("power:PWR_FLAG")
        self.pwr += 1
        ref = "#FLG%03d" % self.pwr
        props = [prop("Reference", ref, x, y, hide=True),
                 prop("Value", "PWR_FLAG", x, y - 5, hide=False),
                 prop("Footprint", "", x, y, hide=True),
                 prop("Datasheet", "", x, y, hide=True),
                 prop("Description", "", x, y, hide=True)]
        self.instance("power:PWR_FLAG", ref, x, y, 0, props, pins_of(sym), power=True)
        self.wire(x, y, x + 5.08, y)
        self.label(net, x + 5.08, y, 1, 0)

    def part(self, p):
        sym = self.symbol(p["sym"])
        pins = pins_of(sym)
        x, y = snap(p["x"]), snap(p["y"])
        rot = p["rot"]
        if rot is None:
            # Two-pin parts drawn vertically in the library lie flat on the sheet.
            rot = 90 if len(pins) == 2 and {pins[0]["angle"], pins[1]["angle"]} == {90.0, 270.0} else 0
        x0, y0, x1, y1 = body_box(sym, pins)
        hidden = [prop("Footprint", p["fp"], x, y, hide=True),
                  prop("Datasheet", "", x, y, hide=True),
                  prop("Description", "", x, y, hide=True)]
        if p["mpn"]:
            hidden.append(prop("MPN", p["mpn"], x, y, hide=True))
        if len(pins) <= 2 and p["sym"].split(":")[0] not in ("Connector_Generic", "Connector", "Mechanical"):
            # A field angle is relative to the symbol: 90 on a rotated part reads flat.
            # and its justification is mirrored.
            jr, jl = ("left", "right") if rot == 90 else ("right", "left")
            props = [prop("Reference", p["ref"], x - 0.6, y - 3.4, rot, justify=jr),
                     prop("Value", p["value"], x + 0.6, y - 3.4, rot, justify=jl)]
        elif len(pins) <= 2 or len(pins) == 1:
            props = [prop("Reference", p["ref"], x, y - y1 - 3.6), prop("Value", p["value"], x, y - y1 - 1.6)]
        else:
            props = [prop("Reference", p["ref"], x + x0, y - y1 - 1.4, justify="left"),
                     prop("Value", p["value"], x + x0, y - y0 + 1.6, justify="left")]
        self.instance(p["sym"], p["ref"], x, y, rot, props + hidden, pins)

        seen = set()
        for pin in pins:
            num = pin["number"]
            if num not in p["pins"]:
                if pin["type"] == "no_connect":
                    continue
                raise SystemExit("%s: pin %s (%s) is not mapped" % (p["ref"], num, pin["name"]))
            net = p["pins"][num]
            px, py = xform(pin["x"], pin["y"], rot)
            px, py = x + px, y + py
            a = math.radians(pin["angle"])
            ox, oy = xform(-math.cos(a), -math.sin(a), rot)
            ox, oy = int(round(ox)), int(round(oy))
            key = (r(px), r(py))
            if key in seen:
                continue
            seen.add(key)
            if net is None:
                self.items.append(S("no_connect", S("at", r(px), r(py)), S("uuid", uid("nc%s.%s" % (p["ref"], num)))))
                continue
            ex, ey = px + ox * STUB, py + oy * STUB
            self.wire(px, py, ex, ey)
            if net in design.POWER_NETS:
                self.power(net, ex, ey, ox, oy)
            else:
                self.label(net, ex, ey, ox, oy)
        unknown = set(p["pins"]) - {pin["number"] for pin in pins}
        if unknown:
            raise SystemExit("%s: no such pins %s" % (p["ref"], sorted(unknown)))

    def text(self, string, x, y, size=2.0, bold=True):
        self.items.append(S("text", string, S("exclude_from_sim", Sym("no")), S("at", r(x), r(y), 0),
                            effects("left bottom", size=size, bold=bold), S("uuid", uid("text" + string))))

    def box(self, x0, y0, x1, y1):
        self.items.append(S("rectangle", S("start", x0, y0), S("end", x1, y1),
                            S("stroke", S("width", 0.2), S("type", Sym("dash"))),
                            S("fill", S("type", Sym("none"))), S("uuid", uid("box%s,%s" % (x0, y0)))))


def main():
    sheet = Sheet()
    for title, x0, y0, x1, y1 in design.BLOCKS:
        sheet.box(x0, y0, x1, y1)
        sheet.text(title, x0 + 2, y0 + 5)
    for p in design.PARTS:
        sheet.part(p)
    for net, x, y in design.PWR_FLAGS:
        sheet.flag(net, x, y)
    for i, line in enumerate(design.NOTES):
        sheet.text(line, 16, 271 + i * 3.2, size=1.3, bold=False)

    root = S("kicad_sch", S("version", 20250114), S("generator", "eeschema"), S("generator_version", "9.0"),
             S("uuid", ROOT), S("paper", "A3"),
             S("title_block", S("title", "Outlook Guardian"), S("date", design.DATE), S("rev", design.REV),
               S("company", "OpenFairWind"),
               S("comment", 1, "Spoken alarm annunciator for Signal K and NMEA 2000"),
               S("comment", 2, "Form factor, GPIO and display headers after Hat Labs HALMET (CC BY 4.0)")),
             S("lib_symbols", *[sheet.lib[k] for k in sorted(sheet.lib)]))
    root += sheet.items
    root.append(S("sheet_instances", S("path", "/", S("page", "1"))))
    root.append(S("embedded_fonts", Sym("no")))
    with open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w") as f:
        f.write(dump(root) + "\n")

    print("parts:", len(design.PARTS))


if __name__ == "__main__":
    main()
