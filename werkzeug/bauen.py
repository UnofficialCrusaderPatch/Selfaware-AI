# -*- coding: utf-8 -*-
"""Bauen und Anwerben wie ein Klick des Menschen - Bausteine und Probe (M11/M12, 04.10.2026).

Modulbefehle: "eigenerPlatz" (ohne ihn baut man still fuer den neutralen Spieler 0!), "baue",
"werbe", "vorrat", "gebaeude", "typen". Bau-Nummer und Groesse je Gebaeude aus
VillageStudio lib/gebaeude.json, Kosten aus der Tabelle im Spiel (0x01124CF4, int[110][5]:
Holz, Stein, Eisen, Pech, Gold; Index = Gebaeudetyp).
Gemessen 04.10.: 5 Holzfaellerhuetten -> Holz 150 -> 125 (5 x 5 laut Tabelle); Soeldnerposten
-> Gold -120; angeworben 1 arabischer Bogenschuetze (Typ 70). Belegter Platz -> nichts, kein Abzug.

Aufruf (Probe):  python bauen.py "<Spielstand>" [spieler=1]
Als Baustein:    from bauen import baue_irgendwo, werbe, vorrat, kosten
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import lade_stand, befehl, peek
from steuerkarte import laufe

GEBAEUDE = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "VillageStudio",
                                           "lib", "gebaeude.json"), encoding="utf-8"))["gebaeude"]
NACH_TYP = {g["laufzeit"]: g for g in GEBAEUDE.values() if "laufzeit" in g and "mapper" in g}

def kosten(typ):
    return dict(zip(("holz", "stein", "eisen", "pech", "gold"), peek(0x01124CF4 + typ * 20, 5)))

def vorrat(sp=1):
    z = " ".join(befehl({"vorrat": sp}, 1.0))
    return {k.lower(): int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", z.split(": ", 2)[-1])}

def gebaeude_von(sp, typ):
    z = " ".join(befehl({"gebaeude": {"spieler": sp, "typ": typ}}, 1.0))
    return [(int(n), int(x), int(y)) for n, x, y in re.findall(r"GEBAEUDE (\d+): Typ \d+, Spieler \d+, Ort \((\d+),(\d+)\)", z)]

def baue_irgendwo(typ, kandidaten, sp=1):
    """Versucht die Stellen der Reihe nach, bis das Spiel baut. Gibt (Nummer, x, y) oder None."""
    g = NACH_TYP[typ]
    vorher = {n for n, _, _ in gebaeude_von(sp, typ)}
    for x, y in kandidaten:
        befehl({"baue": {"mapper": g["mapper"], "x": x, "y": y, "groesse": g["b"], "richtung": 0}}, 0.8)
        laufe(5)
        neu = [e for e in gebaeude_von(sp, typ) if e[0] not in vorher]
        if neu:
            return neu[0]
    return None

def werbe(einheitentyp, gebaeude_nr):
    befehl({"werbe": {"typ": einheitentyp, "gebaeude": gebaeude_nr}}, 0.8)

def probe(stand, sp):
    lade_stand(stand, mit_bild=False)
    befehl({"eigenerPlatz": sp}, 0.8)
    befehl({"tempo": 300}, 0.5)
    v0 = vorrat(sp)
    k = kosten(3)
    print("Holzfaellerhuette kostet %s; Holz vorher %d" % (k, v0["holz"]))
    # Gegenlauf: belegter Platz (Lager) - darf nichts bauen und nichts kosten
    lager = gebaeude_von(sp, 10)
    if lager:
        befehl({"baue": {"mapper": 51, "x": lager[0][1], "y": lager[0][2], "groesse": 3, "richtung": 0}}, 0.8)
        laufe(10)
        print("GEGENLAUF (auf dem Lager): Holz %d -> %d, Huetten %d -> %s" % (
            v0["holz"], vorrat(sp)["holz"], 0, len(gebaeude_von(sp, 3))))
    v1 = vorrat(sp)
    h = baue_irgendwo(3, [(186, 116), (190, 105), (180, 125)], sp)
    v2 = vorrat(sp)
    print("BAUEN: Huette %s; Holz %d -> %d (Soll -%d) -> %s" % (h, v1["holz"], v2["holz"], k["holz"],
          "GILT" if h and v1["holz"] - v2["holz"] == k["holz"] else "NICHT"))
    p = baue_irgendwo(8, [(195, 100), (200, 116), (170, 128)], sp)
    print("SOELDNERPOSTEN: %s, Gold %d -> %d" % (p, v2["gold"], vorrat(sp)["gold"]))
    if p:
        t0 = re.search(r"S%d:T70=(\d+)" % sp, " ".join(befehl({"typen": {"spieler": sp}}, 1.0)))
        werbe(70, p[0])
        laufe(50)
        t1 = re.search(r"S%d:T70=(\d+)" % sp, " ".join(befehl({"typen": {"spieler": sp}}, 1.0)))
        a, b = int(t0.group(1)) if t0 else 0, int(t1.group(1)) if t1 else 0
        print("ANWERBEN: arabische Bogenschuetzen %d -> %d -> %s" % (a, b, "GILT" if b == a + 1 else "NICHT"))

if __name__ == "__main__":
    probe(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
