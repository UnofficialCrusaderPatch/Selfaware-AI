# -*- coding: utf-8 -*-
"""Gehorcht jede Einheitenart? (01.10.2026, Daniels Fragen: alle Arten, Bauern, fremde Spieler)

Je Typ und Spieler eine Einheit; Ziel = naechstes gueltige Feld 12 Felder neben ihr
(zielsuche). Zwei Laeufe aus DEMSELBEN Spielstand (Laden ist wiederholbar, M7.03):
  Kontrolle: 300 Ticks ohne Befehl.     Versuch: Befehl, dann 300 Ticks.
Vorher festgelegt - "gehorcht", wenn sie im Versuch mindestens 5 Felder naeher am
Ziel steht als in der Kontrolle (oder hoechstens 2 Felder davon entfernt ist).

Aufruf:  python einheiten_steuern.py "<Spielstand>" spieler:typ [spieler:typ ...]
"""
import io, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import lade_stand, befehl
from steuerkarte import laufe

LAUF = 300
EINTRAG = re.compile(r"(\d+):T(\d+)@\((\d+),(\d+)\)")

def liste(**g):
    z = " ".join(befehl({"gruppe": g}, 1.0))
    return [(int(a), int(b), int(c), int(d)) for a, b, c, d in EINTRAG.findall(z)]

def orte(nummern):
    return {nr: (x, y) for nr, _, x, y in liste(nr=nummern)}

def abstand(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def main():
    stand, paare = sys.argv[1], [tuple(int(v) for v in p.split(":")) for p in sys.argv[2:]]
    lade_stand(stand, mit_bild=False)
    proben = []
    for sp, typ in paare:
        l = liste(spieler=sp, typ=typ)
        if l:
            proben.append({"spieler": sp, "typ": typ, "nr": l[0][0], "start": (l[0][2], l[0][3])})
        else:
            print("kein Typ %d bei Spieler %d" % (typ, sp))
    nummern = [p["nr"] for p in proben]
    # Kontrolle
    t0 = laufe(LAUF)
    kontrolle = orte(nummern)
    # Versuch
    lade_stand(stand, mit_bild=False)
    for p in proben:
        z = " ".join(befehl({"zielsuche": {"nr": p["nr"], "x": p["start"][0] + 12, "y": p["start"][1], "r": 6}}, 0.8))
        m = re.search(r"\((\d+),(\d+)\) gueltig", z)
        p["ziel"] = (int(m.group(1)), int(m.group(2))) if m else None
    laufe(LAUF)
    versuch = orte(nummern)
    print("%-6s %-5s %-5s %-11s %-11s %-11s %-11s %s" % ("Spieler", "Typ", "Nr", "Start", "Ziel", "ohne Bef.", "mit Bef.", "Urteil"))
    for p in proben:
        k, v, z = kontrolle.get(p["nr"]), versuch.get(p["nr"]), p["ziel"]
        if z is None or k is None or v is None:
            p["urteil"] = "keine Aussage (Ziel/Ort fehlt)"
        else:
            dk, dv = abstand(k, z), abstand(v, z)
            p.update(ohne=k, mit=v, abstand_ohne=dk, abstand_mit=dv)
            p["urteil"] = "GEHORCHT" if (dv + 5 <= dk or dv <= 2) else "NICHT"
        print("%-6d %-5d %-5d %-11s %-11s %-11s %-11s %s" % (p["spieler"], p["typ"], p["nr"], p["start"], z,
              k, v, p["urteil"]), flush=True)
    io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten",
            "einheiten_steuern_%s.json" % time.strftime("%H%M%S")), "w", encoding="utf-8").write(
        json.dumps({"stand": stand, "lauf": LAUF, "proben": proben}, indent=1, default=list))

if __name__ == "__main__":
    main()
