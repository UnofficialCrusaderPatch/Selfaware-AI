# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer den gemeinsamen Lord-Angriff (Daniel 05.10. 23:51: ausser Schussweite sammeln, bis klar
ueberlegen, dann alle gleichzeitig). Vorher festgelegt, was gelten muss:
  1. Unter LORD_SAMMELN_AB lebende Assassinen -> weiter raiden, kein Sammeln
  2. Ab LORD_SAMMELN_AB -> alle an einen begehbaren Punkt ausser 40 Feldern Schussweite, kein Lord-Befehl
  3. Neue Assassinen schliessen sich der Sammlung an; unter LORD_KRITISCH greift niemand den Lord an
  4. LORD_KRITISCH Assassinen greifen erst an, wenn alle am Sammelpunkt angekommen sind
  5. waehrend des Angriffs vergibt die Raid-Logik keinem Angreifer ein Gebaeude
  6. wer nicht den Lord angreift, bekommt den Lord-Befehl in der naechsten Runde neu
  7. Messung: am Lord (<= 3 Felder, greift ihn an) wird gezaehlt, Ablenkung nach Einheitentyp
  8. weniger als LORD_REST uebrig -> Angriff vorbei; neuer Angriff erst wieder ab LORD_SAMMELN_AB lebenden
Aufruf: python werkzeug/lordtrupp_pruefen.py [andere_assassinen.py]   (Rueckgabe 0 = gruen)
"""
import importlib.util, os, subprocess, sys, types
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
if len(sys.argv) > 1 and sys.argv[1] == "HEAD":       # rote Gegenprobe gegen den eingecheckten Stand vor dem Umbau
    quelle = subprocess.check_output(["git", "-C", os.path.dirname(HIER), "show", "HEAD:werkzeug/assassinen.py"], text=True)
    A = types.ModuleType("assassinen_alt")
    exec(compile(quelle, "HEAD:werkzeug/assassinen.py", "exec"), A.__dict__)
elif len(sys.argv) > 1:                                 # Gegenprobe gegen eine andere Fassung
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


def sammel_befehle(bef):
    return [b for b in bef if b.get("halten", {}).get("nr")]


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))
    S = getattr(A.Einzeln, "LORD_SAMMELN_AB", 20)
    K = getattr(A.Einzeln, "LORD_KRITISCH", 40)
    L = {500: einheit(55, 2, *LORD), 600: einheit(22, 2, LORD[0] + 2, LORD[1]), 601: einheit(24, 2, 200, 280)}
    G = {900: {"besitzer": 2, "typ": 32, "x": 190, "y": 250, "leben": 500, "uid": 1, "erreichbar": 1}}
    for i in range(S - 1):                                            # knapp unter der Sammelgrenze
        L[100 + i] = einheit(73, 1, 150 + 3 * i, 260 + (i % 5) * 4)
    t.aufnehmen([n for n in L if L[n]["typ"] == 73])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    pruefe(1, "%d lebende -> weiter raiden, nicht sammeln" % (S - 1),
           not lord_befehle(bef) and t.lordtrupp.get("phase") is None)
    L[100 + S - 1] = einheit(73, 1, 120, 300)                       # Sammelgrenze erreicht, weit verteilt
    t.aufnehmen([100 + S - 1])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    sb = sammel_befehle(bef)
    punkt = t.lordtrupp.get("sammelpunkt")
    sammeln = sorted(n for n in L if L[n]["typ"] == 73)
    pruefe(2, "%d lebende -> sammeln ausser Schussweite, noch kein Lord-Befehl" % S,
           len(sb) == 1 and sb[0]["halten"]["nr"] == sammeln and punkt is not None
           and A.schach(punkt, LORD) > A.SCHUSSWEITE and not lord_befehle(bef))
    # Bis zur belegten Uebermacht auffuellen; die Neuen stehen noch nicht am Sammelpunkt.
    for i in range(S, K):
        L[100 + i] = einheit(73, 1, 110 + i, 310 + (i % 3))
    t.aufnehmen([100 + i for i in range(S, K)])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    alle = sorted(n for n in L if L[n]["typ"] == 73)
    sb = sammel_befehle(bef)
    neu = set(alle[S:])
    pruefe(3, "%d lebende, aber verstreut -> alle gehoeren zur Sammlung, die Neuen laufen hin, niemand greift an" % K,
           set(t.lordtrupp["mitglieder"]) == set(alle) and sb
           and any(neu <= set(b["halten"]["nr"]) for b in sb) and not lord_befehle(bef))
    sammelort = punkt or HEIM                    # bei der roten Gegenprobe kennt der alte Stand noch keinen Treffpunkt
    for n in alle:
        L[n].update(x=sammelort[0], y=sammelort[1], laufx=sammelort[0], laufy=sammelort[1])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    lb = lord_befehle(bef)
    pruefe(4, "%d gemeinsam angekommen -> EIN Befehl mit allen auf den Lord" % K,
           len(lb) == 1 and lb[0]["angriff"]["einheiten"] == alle)
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    raid = [b for b in bef if b.get("angriff", {}).get("gebaeude")]
    pruefe(5, "waehrend des Angriffs kein Gebaeude-Ziel fuer Angreifer", not raid)
    for n in alle[:5]:                                                # 5 am Lord und greifen ihn an
        L[n].update(x=LORD[0] + 1, y=LORD[1], zielart=4, zieleinheit=500)
    for n in alle[5:8]:                                               # 3 abgelenkt von einem Speertraeger (Typ 24)
        L[n].update(zielart=4, zieleinheit=601)
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])     # S2a: schon in der NAECHSTEN Runde
    lb = lord_befehle(bef)
    pruefe(6, "schon in der naechsten Runde die Abgelenkten neu auf den Lord", lb and set(alle[5:8]) <= set(lb[0]["angriff"]["einheiten"]))
    a = t.angriffe[-1] if getattr(t, "angriffe", None) else {}
    pruefe(7, "Messung: am Lord %s (soll 5), abgelenkt %s (soll Typ 24: 3)" % (a.get("am_lord_max"), a.get("anderes")),
           a.get("am_lord_max") == 5 and a.get("anderes", {}).get(24) == 3)
    for n in alle[2:]:                                                # nur 2 ueberleben
        del L[n]
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    vorbei = not t.lordtrupp["mitglieder"]
    for i in range(S - 3):                                           # 2 alte + (S-3) neue = S-1 -> noch kein Sammeln
        L[300 + i] = einheit(73, 1, 150, 270 + i)
    t.aufnehmen([300 + i for i in range(S - 3)])
    erg, bef = t.schritt(L, G, sichere_orte=[(94, 280), HEIM])
    pruefe(8, "unter %d uebrig -> vorbei; mit %d lebenden noch keine neue Sammlung" % (
           getattr(A.Einzeln, "LORD_REST", 3), S - 1), vorbei and not lord_befehle(bef) and t.lordtrupp.get("phase") is None)
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
