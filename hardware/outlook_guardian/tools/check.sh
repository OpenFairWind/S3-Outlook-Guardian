#!/bin/sh
# Regenerate the schematic and run ERC. Library-table warnings are dropped:
# they only say that KiCad's global tables are not set up for kicad-cli.
cd "$(dirname "$0")/.." || exit 1
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
python3 tools/gen_sch.py || exit 1
$CLI sch upgrade outlook_guardian.kicad_sch >/dev/null 2>&1
$CLI sch erc --severity-all --format json -o build/erc.json outlook_guardian.kicad_sch >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open("build/erc.json"))
v = [x for s in d["sheets"] for x in s["violations"] if x["type"] not in ("lib_symbol_issues", "footprint_link_issues")]
print("ERC:", collections.Counter(x["type"] for x in v))
for x in v:
    print(" ", x["severity"], x["type"], x["description"], "|", "; ".join(i["description"] for i in x["items"]))
PY
