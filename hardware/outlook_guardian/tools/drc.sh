#!/bin/sh
# Run DRC and print a summary: drc.sh [type-to-list ...]
cd "$(dirname "$0")/.." || exit 1
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$CLI pcb drc --severity-all --schematic-parity --format json -o build/drc.json outlook_guardian.kicad_pcb >/dev/null 2>&1
python3 - "$@" <<'PY'
import json, collections, sys
d = json.load(open("build/drc.json"))
v = [x for x in d.get("violations", []) if x["type"] != "lib_footprint_issues"]
print("DRC violations:", dict(collections.Counter(x["type"] for x in v)))
print("unconnected:", len(d.get("unconnected_items", [])), "parity:", len(d.get("schematic_parity", [])))
for x in d.get("schematic_parity", [])[:10]:
    print("  parity:", x["description"], "|", "; ".join(i["description"] for i in x["items"]))
for x in v:
    if x["type"] in sys.argv[1:] or "all" in sys.argv[1:]:
        print(" ", x["type"], "|", x["description"], "|", "; ".join("%s @(%.1f,%.1f)" % (i["description"], i["pos"]["x"], i["pos"]["y"]) for i in x["items"]))
PY
