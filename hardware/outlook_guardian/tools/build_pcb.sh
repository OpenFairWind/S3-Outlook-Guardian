#!/bin/sh
# Export the netlist from the schematic, rebuild the unrouted board and plot it.
cd "$(dirname "$0")/.." || exit 1
K=/Applications/KiCad/KiCad.app/Contents
CLI=$K/MacOS/kicad-cli
PY=$K/Frameworks/Python.framework/Versions/Current/bin/python3
$CLI sch export netlist --format kicadsexpr -o build/netlist.net outlook_guardian.kicad_sch >/dev/null 2>&1 || exit 1
$PY tools/gen_pcb.py 2>&1 | grep -v -e Fontconfig -e stdpbase
