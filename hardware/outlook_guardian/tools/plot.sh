#!/bin/sh
# Plot the board to build/<name>.png for a quick look: plot.sh [name] [layers]
cd "$(dirname "$0")/.." || exit 1
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
NAME=${1:-top}
$CLI pcb export svg --layers "${2:-F.Cu,F.SilkS,F.CrtYd,Edge.Cuts}" --mode-single --page-size-mode 2 \
    --exclude-drawing-sheet -o build/$NAME.svg outlook_guardian.kicad_pcb >/dev/null 2>&1 || exit 1
rm -f build/$NAME.svg.png
qlmanage -t -s 2600 -o build build/$NAME.svg >/dev/null 2>&1
mv build/$NAME.svg.png build/$NAME.png
