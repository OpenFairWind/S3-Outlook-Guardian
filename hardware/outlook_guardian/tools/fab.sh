#!/bin/sh
# Export the fabrication and assembly files into fab/.
cd "$(dirname "$0")/.." || exit 1
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
P=outlook_guardian
rm -rf fab && mkdir -p fab/gerbers
$CLI pcb export gerbers -o fab/gerbers/ --no-protel-ext \
    --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts $P.kicad_pcb
$CLI pcb export drill -o fab/gerbers/ --format excellon --excellon-units mm --generate-map --map-format pdf $P.kicad_pcb
(cd fab/gerbers && zip -q ../$P-gerbers.zip *)
$CLI pcb export pos -o fab/$P-positions.csv --format csv --units mm --side both $P.kicad_pcb
$CLI sch export bom -o fab/$P-bom.csv --fields 'Reference,Value,Footprint,MPN,${QUANTITY}' \
    --labels 'Reference,Value,Footprint,MPN,Qty' --group-by 'Value,Footprint,MPN' --ref-range-delimiter '' $P.kicad_sch
$CLI sch export pdf -o fab/$P-schematic.pdf $P.kicad_sch
$CLI pcb export pdf -o fab/$P-assembly.pdf --layers F.Fab,F.SilkS,Edge.Cuts --mode-single $P.kicad_pcb
$CLI pcb render --side top --width 2000 --height 1400 -o fab/$P-top.png $P.kicad_pcb
$CLI pcb render --side bottom --width 2000 --height 1400 -o fab/$P-bottom.png $P.kicad_pcb
