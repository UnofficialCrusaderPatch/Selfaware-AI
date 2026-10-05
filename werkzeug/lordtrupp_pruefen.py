# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer "Alle auf den Lord" (Daniel 05.10. 21:34: raiden, bei kritischer Menge auf dem ganzen Feld
greifen ALLE zugleich den Lord an). Vorher festgelegt, was gelten muss:
  1. 19 lebende Assassinen -> kein Lord-Befehl
  2. 20 lebende, ueber das Feld verteilt, einige mitten im Raid -> EIN Angriffsbefehl mit allen 20 auf den Lord
  3. waehrend des Angriffs vergibt die Raid-Logik keinem Angreifer ein Gebaeude
  4. wer nicht den Lord angreift, bekommt den Lord-Befehl in der naechsten Runde neu (S2a, vorher erst nach NEU_NACH)
  5. Messung: am Lord (<= 3 Felder, greift ihn an) wird gezaehlt, Ablenkung nach Einheitentyp
  6. weniger als LORD_REST uebrig -> Angriff vorbei; neuer Angriff erst wieder ab LORD_KRITISCH lebenden
Aufruf: python werkzeug/lordtrupp_pruefen.py [andere_assassinen.py]   (Rueckgabe 0 = gruen)
"""
import importlib.util, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
if len(sys.argv) > 1:                                   # Gegenprobe gegen eine andere Fassung
    spec = importlib.util.spec_from_file_location("assassinen", sys.argv[1])
    A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
else:
    import assassinen as A

HEIM, LORD = (141, 269), (230, 287)


def einheit(typ, besitzer, x, y, leben=12500, **k):
    e = {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben, "zustand": 0, "zielart": 0, "zieleinheit": 0,
         "zieluid": 0, "zielgebaeude": 0, "ziel": 0, "zielx": 0, "ziely": 0, "laufx": x, "laufy": y, "auswahlvon": 0,
         "auswahlmarke": 0, "gruppe": 0, "gruppenuid": 0, "ladung": 0, "arbeitsplatz": 0, "erreichbar": 1}
    e.update(k)
    return e


def lord_befehle(bef):
    return [b for b in bef if b.get("angriff", {}).get("ziel") == 500]


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))
    K = getattr(A.Einzeln, "LORD_KRITISCH", 20)
    L = {500: einheit(55, 2, *LORD), 600: einheit(22, 2, LORD[0] + 2, LORD[1]), 601: einheit(24, 2, 200, 280)}
    G = {900: {"besitzer": 2, "typ": 32, "x": 190, "y": 250, "leben": 500, "uid": 1, "erreichbar": 1}}
    for i in range(K - 1):                                            # 19 verteilt
        L[100 + i] = einheit(73, 1, 150 + 3 * i, 260 + (i % 5) * 4)
    t.aufnehmen([n for n in L if L[n]["typ"] == 73])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    pruefe(1, "%d lebende -> kein Lord-Befehl" % (K - 1), not lord_befehle(bef))
    L[100 + K - 1] = einheit(73, 1, 120, 300)                       # der 20., weit weg
    t.aufnehmen([100 + K - 1])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    lb = lord_befehle(bef)
    alle = sorted(n for n in L if L[n]["typ"] == 73)
    pruefe(2, "%d lebende -> EIN Befehl mit allen %d auf den Lord" % (K, K), len(lb) == 1 and lb[0]["angriff"]["einheiten"] == alle)
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    raid = [b for b in bef if b.get("angriff", {}).get("gebaeude")]
    pruefe(3, "waehrend des Angriffs kein Gebaeude-Ziel fuer Angreifer", not raid)
    for n in alle[:5]:                                                # 5 am Lord und greifen ihn an
        L[n].update(x=LORD[0] + 1, y=LORD[1], zielart=4, zieleinheit=500)
    for n in alle[5:8]:                                               # 3 abgelenkt von einem Speertraeger (Typ 24)
        L[n].update(zielart=4, zieleinheit=601)
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])     # S2a: schon in der NAECHSTEN Runde
    lb = lord_befehle(bef)
    pruefe(4, "schon in der naechsten Runde die Abgelenkten neu auf den Lord", lb and set(alle[5:8]) <= set(lb[0]["angriff"]["einheiten"]))
    a = t.angriffe[-1] if getattr(t, "angriffe", None) else {}
    pruefe(5, "Messung: am Lord %s (soll 5), abgelenkt %s (soll Typ 24: 3)" % (a.get("am_lord_max"), a.get("anderes")),
           a.get("am_lord_max") == 5 and a.get("anderes", {}).get(24) == 3)
    for n in alle[2:]:                                                # nur 2 ueberleben
        del L[n]
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    vorbei = not t.lordtrupp["mitglieder"]
    for i in range(K - 3):                                           # 2 alte + 17 neue = 19 -> noch kein neuer Angriff
        L[300 + i] = einheit(73, 1, 150, 270 + i)
    t.aufnehmen([300 + i for i in range(K - 3)])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    pruefe(6, "unter %d uebrig -> vorbei; mit 19 lebenden noch kein neuer Angriff" % getattr(A.Einzeln, "LORD_REST", 3),
           vorbei and not lord_befehle(bef))
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
