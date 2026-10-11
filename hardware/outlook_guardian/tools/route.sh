#!/bin/sh
# Rebuild the board from the schematic, autoroute it with Freerouting and run DRC.
# Needs Java and the Freerouting jar: set FREEROUTING to its path.
cd "$(dirname "$0")/.." || exit 1
FREEROUTING=${FREEROUTING:-$HOME/.local/share/freerouting/freerouting-1.9.0.jar}
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
tools/build_pcb.sh || exit 1
$PY tools/dsn.py export 2>&1 | grep -v -e Fontconfig -e stdpbase
rm -f build/outlook_guardian.ses
java -jar "$FREEROUTING" -de build/outlook_guardian.dsn -do build/outlook_guardian.ses -mp "${PASSES:-30}" \
    > build/freerouting.log 2>&1
grep -i -E "unrouted|incomplete|completed|score|violation" build/freerouting.log | tail -8
[ -f build/outlook_guardian.ses ] || { echo "no session file"; tail -20 build/freerouting.log; exit 1; }
$PY tools/dsn.py import 2>&1 | grep -v -e Fontconfig -e stdpbase
tools/drc.sh "$@"
