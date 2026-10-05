# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer 4a "Ausweichen bei Uebermacht" (Daniel 05.10. 22:16: erst weggehen, bis sie nicht mehr
verfolgen, dann weiter angreifen). Vorher festgelegt, was gelten muss:
  1. 1 eigener gegen 3 feindliche Assassinen (2 Felder) -> AUSWEICHEN, wartet an einem Ort weiter weg, KEIN neues Ziel
  2. naechste Runde, Verfolger weiter 2 Felder nah -> bleibt auf der Flucht, kein Ziel
  3. Verfolger 15 Felder weg (> SICHER_NAH): nach FLUCHT_RUHE Runden "AUSWEICHEN vorbei" und wieder eine ZIELWAHL
  4. 3 eigene gegen 3 feindliche -> kein Ausweichen (nicht unterlegen)
  5. 1 gegen 1 -> kein Ausweichen
Aufruf: python werkzeug/ausweichen_pruefen.py [andere_assassinen.py]   (Rueckgabe 0 = gruen)
"""
import importlib.util, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
if len(sys.argv) > 1:                                   # Gegenprobe gegen eine andere Fassung
    spec = importlib.util.spec_from_file_location("assassinen", sys.argv[1])
    A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
else:
    import assassinen as A

ORTE = [(94, 280), (141, 269)]


def einheit(typ, besitzer, x, y, leben=12500, **k):
    e = {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben, "zustand": 0, "zielart": 0, "zieleinheit": 0,
         "zieluid": 0, "zielgebaeude": 0, "ziel": 0, "zielx": 0, "ziely": 0, "laufx": x, "laufy": y, "auswahlvon": 0,
         "auswahlmarke": 0, "gruppe": 0, "gruppenuid": 0, "ladung": 0, "arbeitsplatz": 0, "erreichbar": 1}
    e.update(k)
    return e


def neu():
    return A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))


def hat(ereignis, wort, n):
    return any(z.startswith(wort) and (" %d:" % n in z or " %d " % n in z or z.split()[1].rstrip(":") == str(n)) for z in ereignis)


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    G = {900: {"besitzer": 2, "typ": 32, "x": 200, "y": 270, "leben": 100, "uid": 1, "erreichbar": 1}}
    # 1.-3. einer gegen drei
    t = neu()
    L = {100: einheit(73, 1, 198, 270), 501: einheit(73, 2, 200, 270), 502: einheit(73, 2, 200, 271), 503: einheit(73, 2, 199, 272)}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    flucht = getattr(t, "flucht", {})
    pruefe(1, "1 gegen 3: ausweichen, wartet weiter weg, kein Ziel (Flucht %s, wartet %s, Ziel %s)" % (
        100 in flucht, t.warte.get(100), t.ziel.get(100)),
        100 in flucht and t.warte.get(100) and max(abs(t.warte[100][0] - 200), abs(t.warte[100][1] - 270)) > 5 and 100 not in t.ziel)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(2, "Verfolger bleiben nah: weiter auf der Flucht, kein Ziel", 100 in getattr(t, "flucht", {}) and 100 not in t.ziel)
    for f in (501, 502, 503):                                     # Verfolger geben auf: 15+ Felder weg
        L[f].update(x=L[f]["x"] + 20)
    L[100].update(x=180, y=270)
    runden = []
    for _ in range(getattr(A.Einzeln, "FLUCHT_RUHE", 2) + 1):
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        runden.append((100 in getattr(t, "flucht", {}), 100 in t.ziel, [z for z in erg if "AUSWEICHEN vorbei" in z or "ZIELWAHL 100" in z]))
    pruefe(3, "Verfolger weg -> nach FLUCHT_RUHE Runden wieder angreifen: %s" % runden,
           runden and not runden[-1][0] and runden[-1][1] and any("AUSWEICHEN vorbei" in z for r in runden for z in r[2]))
    # 4. drei gegen drei
    t = neu()
    L = {100: einheit(73, 1, 198, 270), 101: einheit(73, 1, 198, 271), 102: einheit(73, 1, 197, 270),
         501: einheit(73, 2, 200, 270), 502: einheit(73, 2, 200, 271), 503: einheit(73, 2, 199, 272)}
    t.aufnehmen([100, 101, 102])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(4, "3 gegen 3: kein Ausweichen", not any("AUSWEICHEN" in z for z in erg))
    # 5. einer gegen einen
    t = neu()
    L = {100: einheit(73, 1, 198, 270), 501: einheit(73, 2, 200, 270)}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(5, "1 gegen 1: kein Ausweichen", not any("AUSWEICHEN" in z for z in erg))
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
