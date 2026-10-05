# -*- coding: utf-8 -*-
"""Totschlagtest fuer den Lord-Trupp Stand 2 (Daniel 05.10. 20:39: 5 gestapelt, Schwache zurueck, sofort wieder drauf) -
an einer Attrappe ohne Spiel. Vorher festgelegt, was gelten muss:
  1. freie Assassinen kommen in den Trupp (hoechstens LORD_MAX) und laufen zum Sammelpunkt (halten-Befehl)
  2. Sammelpunkt: kein feindlicher Fernkaempfer naeher als LORD_SAMMEL_FERN
  3. erst ab LORD_MIN Angekommenen EIN Angriffsbefehl mit allen zugleich (= gestapelt); mit 4 noch keiner
  4. schwach UND gerade getroffen -> Rueckzug (halten), nicht schwach oder nicht getroffen -> bleibt
  5. eine Runde spaeter wieder auf den Lord, zusammen in einem Befehl
Aufruf: python werkzeug/lordtrupp_pruefen.py   (Rueckgabe 0 = gruen)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assassinen as A

HEIM = (141, 269)
LORD = (230, 287)


def einheit(typ, besitzer, x, y, leben=12500, **k):
    e = {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben, "zustand": 0, "zielart": 0, "zieleinheit": 0,
         "zieluid": 0, "zielgebaeude": 0, "ziel": 0, "zielx": 0, "ziely": 0, "laufx": x, "laufy": y, "auswahlvon": 0,
         "auswahlmarke": 0, "gruppe": 0, "gruppenuid": 0, "ladung": 0, "arbeitsplatz": 0, "erreichbar": 1}
    e.update(k)
    return e


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bed)
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))
    L = {500: einheit(55, 2, *LORD)}
    for i, (dx, dy) in enumerate([(0, 0), (2, 0), (-2, 1), (0, -2), (4, 0), (6, 6)]):
        L[600 + i] = einheit(22, 2, LORD[0] + dx, LORD[1] + dy)          # 6 Bogenschuetzen um den Lord
    MIN = A.Einzeln.LORD_MIN
    for i in range(A.Einzeln.LORD_MAX + 2):
        L[100 + i] = einheit(73, 1, 150 + i, 270)                        # 12 eigene Assassinen daheim
    G = {}
    t.aufnehmen([n for n in L if L[n]["typ"] == 73])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    lt = t.lordtrupp
    P = lt.get("punkt")
    halten = [b for b in bef if "halten" in b]
    pruefe(1, "freie in den Trupp (hoechstens %d), alle auf dem Weg zum Sammelpunkt" % t.LORD_MAX,
           len(lt["mitglieder"]) == t.LORD_MAX and any(b["halten"]["x"] == P[0] and b["halten"]["y"] == P[1] for b in halten))
    nf = min(A.schach(P, (L[n]["x"], L[n]["y"])) for n in L if L[n]["typ"] == 22)
    pruefe(2, "Sammelpunkt %s hat %d Felder Abstand zum naechsten Bogenschuetzen (>= %d)" % (P, nf, t.LORD_SAMMEL_FERN), nf >= t.LORD_SAMMEL_FERN)
    # 4 angekommen -> noch kein Angriff
    mitgl = sorted(lt["mitglieder"])
    for n in mitgl[:MIN - 1]:
        L[n]["x"], L[n]["y"] = P
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    pruefe(3, "mit %d Angekommenen noch kein Lord-Angriff" % (MIN - 1), not any(b.get("angriff", {}).get("ziel") == 500 for b in bef))
    for n in mitgl[:MIN + 2]:
        L[n]["x"], L[n]["y"] = P
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    lb = [b for b in bef if b.get("angriff", {}).get("ziel") == 500]
    pruefe(3, "ab %d Angekommenen EIN Befehl mit allen %d zugleich" % (MIN, min(MIN + 2, len(mitgl))), len(lb) == 1 and lb[0]["angriff"]["einheiten"] == mitgl[:MIN + 2])
    # Angriff laeuft: n0 schwach + getroffen, n1 nur getroffen (stark), n2 schwach aber nicht getroffen
    for n in mitgl[:MIN + 2]:
        L[n]["x"], L[n]["y"], L[n]["zielart"], L[n]["zieleinheit"] = LORD[0] + 1, LORD[1], 4, 500
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])          # Leben merken
    n0, n1, n2 = mitgl[0], mitgl[1], mitgl[2]
    L[n0]["leben"] = int(0.4 * t.VOLL); L[n1]["leben"] = int(0.9 * t.VOLL)
    t.leben[n2] = int(0.4 * t.VOLL); L[n2]["leben"] = int(0.4 * t.VOLL)
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    zurueck = [n for b in bef if "halten" in b for n in b["halten"]["nr"]]
    pruefe(4, "schwach+getroffen zurueck, stark oder ungetroffen bleibt", n0 in zurueck and n1 not in zurueck and n2 not in zurueck
           and t.lordtrupp["status"][n0].startswith("zurueck"))
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    lb = [b for b in bef if b.get("angriff", {}).get("ziel") == 500]
    pruefe(5, "eine Runde spaeter sofort wieder auf den Lord", len(lb) == 1 and n0 in lb[0]["angriff"]["einheiten"]
           and t.lordtrupp["status"][n0] == "angriff")
    # 6 - beim Sammeln getroffen -> Punkt gesperrt, neuer Punkt naeher an daheim (z1: 13 starben stehend am Sammelpunkt)
    t2 = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))
    L2 = {500: einheit(55, 2, *LORD), 600: einheit(22, 2, LORD[0], LORD[1])}
    for i in range(3):
        L2[100 + i] = einheit(73, 1, 150 + i, 270)
    t2.aufnehmen([100, 101, 102])
    t2.schritt(L2, {}, sichere_orte=[(94, 280), HEIM])
    P1 = t2.lordtrupp["punkt"]
    for n in (100, 101, 102):
        L2[n]["x"], L2[n]["y"] = P1
    t2.schritt(L2, {}, sichere_orte=[(94, 280), HEIM])
    L2[100]["leben"] -= 2000
    t2.schritt(L2, {}, sichere_orte=[(94, 280), HEIM])
    P2 = t2.lordtrupp["punkt"]
    pruefe(6, "getroffen am Sammelpunkt %s -> gesperrt, neuer Punkt %s naeher an daheim" % (P1, P2),
           P1 in t2.lord_schlecht and A.schach(P2, HEIM) < A.schach(P1, HEIM))
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
