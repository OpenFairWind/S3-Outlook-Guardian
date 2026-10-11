#!/usr/bin/env python3
"""Specctra round trip for the autorouter: dsn.py export | dsn.py import.

export writes build/outlook_guardian.dsn from the board; import reads
build/outlook_guardian.ses back, restores the plane nets, adds and fills the
zones and saves the board.
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_pcb  # noqa: E402

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
pcb = os.path.join(out, "outlook_guardian.kicad_pcb")
board = pcbnew.LoadBoard(pcb)
if sys.argv[1] == "export":
    dsn = os.path.join(out, "build", "outlook_guardian.dsn")
    print("export:", pcbnew.ExportSpecctraDSN(board, dsn))
else:
    print("import:", pcbnew.ImportSpecctraSES(board, os.path.join(out, "build", "outlook_guardian.ses")))
    gen_pcb.planes(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(pcb, board)
    print("tracks:", len(board.GetTracks()))
