# -*- coding: utf-8 -*-
"""Berechnete Plantagen echt bauen und messen, ob die Ware ankommt (M13b, 04.10.2026).

1. Baut jede Stelle der Liste (Bau-Befehl wie ein Klick). Steht gerade eine Einheit auf der
   Flaeche, sperrt das Spiel den Bau (gemessen 04.10., Daniel bestaetigt) - dann bis zu
   5 Versuche mit 20 Ticks Abstand. Jeder Fehlschlag steht in der Ausgabe.
2. Schreibt danach alle 200 Ticks mit: Ware im Lager, Beliebtheit, Essenswert, Arbeiter.
Kauft NICHTS dazu - die Plantagen allein sollen das Essen bringen.

Aufruf:  python plantagen_lauf.py <typ> <ware> <ticks> x,y x,y ...
         z.B. python plantagen_lauf.py 32 13 6000 203,112 201,102
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import befehl, peek
from steuerkarte import laufe, tick
from bauen import NACH_TYP, gebaeude_von, vorrat, kosten

ARBEITER = {30: 11, 31: 12, 32: 13, 33: 14}          # Farm-Gebaeudetyp -> Einheitentyp des Bauern
SP = 1

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def lage(sp, ware):
    b = 0x0115BDF8 + sp * 0x39F4
    t = re.findall(r"S%d:T(\d+)=(\d+)" % sp, " ".join(befehl({"typen": {"spieler": sp}}, 1.0)))
    return {"tick": tick(), "ware": peek(b + 0x4D0 + ware * 4)[0], "beliebt": s32(peek(b + 0x60)[0]) / 100.0,
            "essen": s32(peek(b + 0x2160)[0]), "typen": {int(a): int(n) for a, n in t}}

def baue_alle(typ, stellen, sp=SP):
    g = NACH_TYP[typ]
    gebaut, fehl = [], []
    for x, y in stellen:
        vorher = {n for n, _, _ in gebaeude_von(sp, typ)}
        neu = []
        for versuch in range(5):
            befehl({"baue": {"mapper": g["mapper"], "x": x, "y": y, "groesse": g["b"], "richtung": 0}}, 0.6)
            laufe(5)
            neu = [e for e in gebaeude_von(sp, typ) if e[0] not in vorher]
            if neu:
                break
            laufe(20)
        if neu:
            gebaut.append(neu[0]); print("  gebaut (%d,%d) als Nr %d, Versuch %d" % (x, y, neu[0][0], versuch + 1))
        else:
            fehl.append((x, y)); print("  NICHT gebaut (%d,%d) nach 5 Versuchen" % (x, y))
    return gebaut, fehl

def main():
    typ, ware, ticks = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    stellen = [tuple(int(v) for v in a.split(",")) for a in sys.argv[4:]]
    befehl({"tempo": 1000}, 0.5)
    # Fehlerkontrolle vorab (Daniel 04.10.): laeuft das Gefecht, ist der Mensch eingetragen?
    zustand = {"Ansicht": peek(0x01FE7D1C)[0], "gameOver": peek(0x0117D500)[0],
               "Mensch": s32(peek(0x0191DE10 + SP * 4)[0]), "Platz": peek(0x01A275DC)[0]}
    if zustand != {"Ansicht": 14, "gameOver": 0, "Mensch": 1, "Platz": SP}:
        raise SystemExit("TESTBEDINGUNG FEHLT: %s - erst laden und eigenerPlatz schicken" % zustand)
    print("Vorab-Kontrolle gut: %s" % zustand)
    v0 = vorrat(SP)
    print("%s x %d, Kosten je Stueck %s; Vorrat vorher Holz %d Gold %d" % (
        NACH_TYP[typ]["name"], len(stellen), kosten(typ), v0["holz"], v0["gold"]))
    gebaut, fehl = baue_alle(typ, stellen)
    v1 = vorrat(SP)
    print("GEBAUT %d von %d; Holz %d -> %d, Gold %d -> %d" % (len(gebaut), len(stellen), v0["holz"], v1["holz"],
                                                            v0["gold"], v1["gold"]))
    arb = ARBEITER.get(typ)
    print("Tick | Ware | Beliebtheit | Essen | Bauern | freie Leute")
    for i in range(ticks // 200 + 1):
        l = lage(SP, ware)
        print("%5d | %4d | %6.2f | %5d | %3d | %3d" % (l["tick"], l["ware"], l["beliebt"], l["essen"],
              l["typen"].get(arb, 0), l["typen"].get(1, 0)))
        if i < ticks // 200:
            laufe(200)
    befehl({"pause": True}, 0.5)

if __name__ == "__main__":
    main()
