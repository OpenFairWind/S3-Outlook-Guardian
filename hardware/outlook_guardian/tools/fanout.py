"""Plane connections for the Outlook Guardian board.

Ground, 5 V and 3.3 V are carried by the two inner layers. Every surface-mount
pad on one of those nets gets a short track to its own via here, before the
autorouter runs. While the autorouter works, each pad-and-via group carries a
private net name (PLN~<net>~<n>), so the autorouter sees the copper as a
finished obstacle and routes only the signals, on the two outer layers.
restore() puts the real nets back afterwards.
"""
import math

import pcbnew

PLANE_NETS = ("GND", "+5V", "+3V3")
PREFIX = "PLN~"
VIA, DRILL = 0.6, 0.3
CLEAR = 0.2

# The 5 V area of inner layer 2; the rest of that layer is 3.3 V.
ISLAND_5V = [(115, 56), (139.9, 56), (139.9, 103), (134, 103), (134, 107), (127, 107), (127, 103), (115, 103)]

mm = pcbnew.FromMM


def to_mm(v):
    return pcbnew.ToMM(v)


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _inside(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def _edge_dist(poly, x, y):
    return min(_seg_dist(x, y, *poly[i], *poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def _rect_dist(x, y, rect):
    x0, y0, x1, y1 = rect
    return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))


class Fanout:
    def __init__(self, board, outline):
        self.board = board
        self.outline = outline
        self.pads = []      # (rect, real net, layers, group id or None, is npth)
        self.vias = []      # (x, y, real net)
        self.tracks = []    # (ax, ay, bx, by, width, layer, real net)
        self.groups = {}    # id(pad) -> group number
        self.count = 0
        self.failed = []

    def _rect(self, pad):
        b = pad.GetBoundingBox()
        return (to_mm(b.GetLeft()), to_mm(b.GetTop()), to_mm(b.GetRight()), to_mm(b.GetBottom()))

    def _ok_point(self, x, y, radius, net, layer=None, is_via=False):
        """True if a circle of copper at (x, y) on net clears everything else."""
        if not _inside(self.outline, x, y) or _edge_dist(self.outline, x, y) < radius + 0.35:
            return False
        if x + radius > 171.2 and y < 91.0:      # antenna edge keep-out
            return False
        for rect, pnet, layers, npth in self.pads:
            if pnet == net and not npth:
                continue
            if layer is not None and layer not in layers:
                continue
            if _rect_dist(x, y, rect) < radius + (0.8 if npth else CLEAR):
                return False
        for vx, vy, vnet in self.vias:
            if vnet != net and math.hypot(x - vx, y - vy) < radius + VIA / 2 + CLEAR:
                return False
            if is_via and math.hypot(x - vx, y - vy) < 0.9:      # hole to hole
                return False
        for ax, ay, bx, by, w, tlayer, tnet in self.tracks:
            if tnet != net and (layer is None or layer == tlayer):
                if _seg_dist(x, y, ax, ay, bx, by) < radius + w / 2 + CLEAR:
                    return False
        return True

    def _ok_track(self, ax, ay, bx, by, width, net, layer):
        n = max(2, int(math.hypot(bx - ax, by - ay) / 0.1))
        return all(self._ok_point(ax + (bx - ax) * i / n, ay + (by - ay) * i / n, width / 2, net, layer)
                   for i in range(n + 1))

    def _plane_ok(self, x, y, net):
        if net == "GND":
            return True
        if _edge_dist(ISLAND_5V, x, y) < 0.7:
            return False
        return _inside(ISLAND_5V, x, y) == (net == "+5V")

    def add_track(self, ax, ay, bx, by, width, layer, net, group):
        t = pcbnew.PCB_TRACK(self.board)
        t.SetStart(pcbnew.VECTOR2I(mm(ax), mm(ay)))
        t.SetEnd(pcbnew.VECTOR2I(mm(bx), mm(by)))
        t.SetWidth(mm(width))
        t.SetLayer(layer)
        t.SetNet(self._net(net, group))
        self.board.Add(t)
        self.tracks.append((ax, ay, bx, by, width, layer, net))

    def add_via(self, x, y, net, group):
        v = pcbnew.PCB_VIA(self.board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetWidth(pcbnew.F_Cu, mm(VIA))
        v.SetDrill(mm(DRILL))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(self._net(net, group))
        self.board.Add(v)
        self.vias.append((x, y, net))

    def _net(self, net, group):
        name = "%s%s~%d" % (PREFIX, net, group)
        found = self.board.FindNet(name)
        if found is None:
            found = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(found)
        return found

    def run(self, links):
        """links: pads of one net joined by hand-drawn tracks, as
        (set of (ref, pad number), [(ax, ay, bx, by, width)], [(via x, via y)]), in mm.
        A link that brings its own vias gets no automatic ones."""
        plane_pads = []
        for fp in self.board.GetFootprints():
            for pad in fp.Pads():
                npth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
                layers = {l for l in (pcbnew.F_Cu, pcbnew.B_Cu) if pad.IsOnLayer(l)}
                net = pad.GetNetname()
                self.pads.append((self._rect(pad), net, layers, npth))
                if net in PLANE_NETS:
                    plane_pads.append((fp, pad))

        # Pads joined by a hand-drawn track share one group and one private net.
        manual = set()
        for pads, segs, vias in links:
            self.count += 1
            members = [p for fp, p in plane_pads if (fp.GetReference(), p.GetNumber()) in pads]
            if not members:
                raise SystemExit("link without pads: %s" % (pads,))
            net = members[0].GetNetname()
            layer = pcbnew.F_Cu if members[0].IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            for p in members:
                self.groups[id(p)] = self.count
                p.SetNet(self._net(net, self.count))
            for ax, ay, bx, by, w in segs:
                self.add_track(ax, ay, bx, by, w, layer, net, self.count)
            for x, y in vias:
                self.add_via(x, y, net, self.count)
                manual.add(self.count)

        done_groups = set()
        for fp, pad in sorted(plane_pads, key=lambda t: -t[1].GetBoundingBox().GetWidth() * t[1].GetBoundingBox().GetHeight()):
            net = pad.GetNetname()
            real = net.split("~")[1] if net.startswith(PREFIX) else net
            group = self.groups.get(id(pad))
            if group is None:
                self.count += 1
                group = self.count
                pad.SetNet(self._net(real, group))
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH or group in manual:
                done_groups.add(group)      # a through-hole pad reaches the plane by itself
                continue
            rect = self._rect(pad)
            w, h = rect[2] - rect[0], rect[3] - rect[1]
            want = 3 if w * h > 6 else 2 if w * h > 2.5 else 1
            if self._fan(fp, pad, rect, real, group, want):
                done_groups.add(group)
            elif id(pad) not in self.groups:
                self.failed.append("%s.%s [%s]" % (fp.GetReference(), pad.GetNumber(), real))
        for pads, _, _ in links:
            g = [self.groups[id(p)] for fp, p in plane_pads if (fp.GetReference(), p.GetNumber()) in pads][0]
            if g not in done_groups:
                self.failed.append("group %s" % (pads,))
        return self.failed

    def _fan(self, fp, pad, rect, net, group, want):
        layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
        cx, cy = to_mm(pad.GetPosition().x), to_mm(pad.GetPosition().y)
        fx, fy = to_mm(fp.GetPosition().x), to_mm(fp.GetPosition().y)
        out = math.atan2(cy - fy, cx - fx) if (abs(cx - fx) + abs(cy - fy)) > 0.05 else 0.0
        hx, hy = (rect[2] - rect[0]) / 2, (rect[3] - rect[1]) / 2
        width = max(0.2, min(0.5, 2 * min(hx, hy) - 0.02))
        cands = []
        for k in range(16):
            a = k * math.pi / 8
            ux, uy = math.cos(a), math.sin(a)
            reach = min(hx / abs(ux) if abs(ux) > 1e-6 else 1e9, hy / abs(uy) if abs(uy) > 1e-6 else 1e9)
            dev = abs((a - out + math.pi) % (2 * math.pi) - math.pi)
            for step in range(9):
                d = reach + VIA / 2 + 0.2 + step * 0.25
                cands.append((d + dev * 0.35, cx + ux * d, cy + uy * d))
        placed = []
        for _, x, y in sorted(cands):
            if any(math.hypot(x - px, y - py) < 1.0 for px, py in placed):
                continue
            if not self._plane_ok(x, y, net) or not self._ok_point(x, y, VIA / 2, net, is_via=True):
                continue
            if not self._ok_track(cx, cy, x, y, width, net, layer):
                continue
            self.add_track(cx, cy, x, y, width, layer, net, group)
            self.add_via(x, y, net, group)
            placed.append((x, y))
            if len(placed) >= want:
                break
        return bool(placed)


def restore(board):
    """Give every private plane net its real name back."""
    real = {}
    for name in PLANE_NETS:
        net = board.FindNet(name)
        if net is None:
            net = pcbnew.NETINFO_ITEM(board, name)
            board.Add(net)
        real[name] = net
    items = list(board.GetTracks()) + [p for fp in board.GetFootprints() for p in fp.Pads()]
    stale = set()
    for item in items:
        name = item.GetNetname()
        if name.startswith(PREFIX):
            stale.add(name)
            item.SetNet(real[name.split("~")[1]])
    return real
