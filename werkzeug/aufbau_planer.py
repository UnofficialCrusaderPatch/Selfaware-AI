# -*- coding: utf-8 -*-
"""Aufbauplaner Streitkolben-Kette (Daniel 06.10. 20:29: "maximal effektiver Laufweg fuer 30 Schwertmacher und 30
Lederharnischmacher ... erst 5 von beidem, dann 15, dann 30").

Grundlage (Wissensregister): Laufen 24 Ticks je Feld, gerade = schraeg (G1); Schmied: Rundgang Schmiede -> Lager (Eisen)
-> Waffenlager -> Schmiede, 927 Ticks Arbeit (G3, G4); Gerber: 3 Leder je Kuh in einem Gang zum Waffenlager (G5), Kuh vom
Milchviehhof (G7 offen); Eingang je Bau-Richtung (G10); Werkstaetten sind keine Ecksperre, Waffenlager schon (W3/W4,
ungeprueft); Arbeiter treten zum Abholen auf Lagerteile (W9 widerlegt -> Lagerteile sind Ziel, kein Durchgang).

Rechnet auf der Weg-Ebene des Spiels (wegkarte) plus den geplanten Gebaeuden; setzt gierig eins nach dem anderen an die
Stelle mit dem kuerzesten Gang und prueft nach jedem, dass alle Eingaenge erreichbar bleiben. Ergebnis ist ein PLAN
(ungeprueft), das Spiel bestaetigt ihn erst beim Bauen und Messen.
"""
import os
import sys
from collections import deque

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import wegkarte as W

TICKS_JE_FELD = 24                  # G1
ARBEIT_SCHMIED = 927                # G3
EINGANG = {0: (2, 4), 2: (-1, 2), 4: (1, -1), 6: (4, 1)}     # G10, 4x4-Gebaeude
LAGER, WAFFENLAGER, SCHMIEDE, GERBEREI = 10, 11, 13, 16


class Plan:
    def __init__(self, k):
        self.k = k
        self.belegt = {}             # Feld -> geplante Art
        self.eingaenge = []          # (art, feld)
        self.bauten = []             # (art, x, y, richtung, eingang)

    # --- Gelaende -------------------------------------------------------------------------------------------------
    def boden(self, p):
        """Begehbarer Boden: in der Weg-Ebene begehbar, kein Lagerteil, nicht geplant belegt."""
        v = self.k["f"].get(p)
        return v is not None and v[0] != 0 and v[5] != LAGER and p not in self.belegt

    def eckensperre(self, p):
        if p in self.belegt:
            return self.belegt[p] in W.ECKSPERRE
        v = self.k["f"].get(p)
        return v is not None and v[0] == 0 and (v[5] in W.ECKSPERRE or v[3] & 0x30)

    def schritte(self, p):
        """Geplante Gebaeude nehmen Wege nur weg, nie hinzu: erlaubt ist ein Schritt, wenn die Weg-Ebene ihn heute
        erlaubt, das Ziel freier Boden bleibt und schraeg nicht zwei Ecksperren (auch geplante Waffenlager) daneben sind."""
        v = self.k["f"][p]
        for bit, (dx, dy) in W.RICHTUNG.items():
            n = (p[0] + dx, p[1] + dy)
            if not v[0] & bit or not self.boden(n):
                continue
            if dx and dy and self.eckensperre((p[0] + dx, p[1])) and self.eckensperre((p[0], p[1] + dy)):
                continue
            yield n

    def abstand(self, start):
        """Felder-Abstand von start (Feld oder Liste) zu allem Boden."""
        q = deque(start if isinstance(start, list) else [start])
        d = {p: 0 for p in q}
        while q:
            p = q.popleft()
            for n in self.schritte(p):
                if n not in d:
                    d[n] = d[p] + 1
                    q.append(n)
        return d

    def lager_abstand(self):
        """Abstand jedes Bodenfelds zum naechsten Lagerteil (ein Schritt auf das Teil gehoert dazu)."""
        teile = [p for p, v in self.k["f"].items() if v[5] == LAGER]
        start = {n for t in teile for n in ((t[0] + dx, t[1] + dy) for dx, dy in W.RICHTUNG.values()) if self.boden(n)}
        d = self.abstand(sorted(start))
        return {p: v + 1 for p, v in d.items()}

    # --- Bauen ----------------------------------------------------------------------------------------------------
    def frei(self, x, y, b=4):
        return all(self.boden((x + i, y + j)) and self.k["f"][(x + i, y + j)][0] == 0xFF
                   and (x + i, y + j) not in [e for _, e in self.eingaenge] for i in range(b) for j in range(b))

    def setze(self, art, x, y, r, b=4):
        for i in range(b):
            for j in range(b):
                self.belegt[(x + i, y + j)] = art
        e = (x + EINGANG[r][0], y + EINGANG[r][1])
        self.eingaenge.append((art, e))
        self.bauten.append((art, x, y, r, e))
        return e

    def zuruecknehmen(self):
        art, x, y, r, e = self.bauten.pop()
        self.eingaenge.pop()
        for i in range(4):
            for j in range(4):
                self.belegt.pop((x + i, y + j), None)

    def alle_erreichbar(self, ziel):
        d = self.abstand(ziel)
        return all(e in d for _, e in self.eingaenge)

    def kandidaten(self, mitte, r_max):
        for x in range(mitte[0] - r_max, mitte[0] + r_max):
            for y in range(mitte[1] - r_max, mitte[1] + r_max):
                for r in (0, 2, 4, 6):
                    if self.frei(x, y):
                        e = (x + EINGANG[r][0], y + EINGANG[r][1])
                        if self.boden(e) and all(not (x <= e2[0] < x + 4 and y <= e2[1] < y + 4) for _, e2 in self.eingaenge):
                            yield x, y, r, e


def plane(k, n_schmiede, n_gerber, hof=None, r_max=16):
    """Gibt (plan, bericht). hof = Feld am Milchviehhof (Kuh holen), sonst nur Waffenlager-Weg fuer Gerber."""
    p = Plan(k)
    teile = [q for q, v in k["f"].items() if v[5] == LAGER]
    mitte = (sum(q[0] for q in teile) // len(teile), sum(q[1] for q in teile) // len(teile))
    bericht = {"mitte": mitte, "schmiede": [], "gerber": []}
    # 1. Waffenlager: Eingang so nah wie moeglich am Lager
    dl = p.lager_abstand()
    best = None
    for x, y, r, e in p.kandidaten(mitte, 10):
        if e in dl and (best is None or dl[e] < best[0]):
            best = (dl[e], x, y, r)
    if best is None:
        raise RuntimeError("kein Platz fuer das Waffenlager")
    we = p.setze(WAFFENLAGER, best[1], best[2], best[3])
    bericht["waffenlager"] = {"ort": best[1:3], "richtung": best[3], "eingang": we, "zum_lager": best[0]}
    # 2. Schmieden: Rundgang Eingang -> Lager -> Waffenlager-Eingang -> Eingang
    for _ in range(n_schmiede):
        dl, dw = p.lager_abstand(), p.abstand(we)
        lager_zu_w = min((dw.get(n, 999) + 1) for t in teile for n in
                         ((t[0] + dx, t[1] + dy) for dx, dy in W.RICHTUNG.values()) if p.boden(n))
        best = None
        for x, y, r, e in p.kandidaten(mitte, r_max):
            if e not in dl or e not in dw:
                continue
            gang = dl[e] + lager_zu_w + dw[e]
            if best is None or gang < best[0]:
                p.setze(SCHMIEDE, x, y, r)
                dl2 = p.lager_abstand()
                ok = p.alle_erreichbar(we) and all(e2 in dl2 for _, e2 in p.eingaenge)
                p.zuruecknehmen()
                if ok:
                    best = (gang, x, y, r)
        if best is None:
            bericht["schmiede"].append({"fehlt": "kein Platz"})
            continue
        e = p.setze(SCHMIEDE, best[1], best[2], best[3])
        bericht["schmiede"].append({"ort": best[1:3], "richtung": best[3], "eingang": e, "gang_felder": best[0],
                                    "gang_ticks": best[0] * TICKS_JE_FELD,
                                    "zyklus_ticks": ARBEIT_SCHMIED + best[0] * TICKS_JE_FELD})
    # 3. Gerbereien: Weg zum Waffenlager hin und zurueck (+ zum Hof, falls bekannt)
    for _ in range(n_gerber):
        dw = p.abstand(we)
        dh = p.abstand(hof) if hof else {}
        best = None
        for x, y, r, e in p.kandidaten(mitte, r_max + 6):
            if e not in dw or (hof and e not in dh):
                continue
            gang = 2 * dw[e] + (2 * dh[e] if hof else 0)
            if best is None or gang < best[0]:
                p.setze(GERBEREI, x, y, r)
                dl2 = p.lager_abstand()
                ok = p.alle_erreichbar(we) and all(e2 in dl2 for a, e2 in p.eingaenge if a == SCHMIEDE)
                p.zuruecknehmen()
                if ok:
                    best = (gang, x, y, r)
        if best is None:
            bericht["gerber"].append({"fehlt": "kein Platz"})
            continue
        e = p.setze(GERBEREI, best[1], best[2], best[3])
        bericht["gerber"].append({"ort": best[1:3], "richtung": best[3], "eingang": e, "gang_felder": best[0],
                                  "gang_ticks": best[0] * TICKS_JE_FELD})
    return p, bericht


def zeichne_plan(plan, pfad, titel=""):
    """Plan als Bild: geplante Gebaeude als belegte Felder (eigene Nummern ab 900), Eingaenge als begehbare Felder."""
    k = dict(plan.k)
    f = dict(k["f"])
    nummer = {}
    for i, (art, x, y, r, e) in enumerate(plan.bauten):
        for a in range(4):
            for b in range(4):
                q = (x + a, y + b)
                if q in f:
                    v = f[q]
                    f[q] = (0, 900 + i, v[2], v[3] | 0x400, v[4], art)
    k["f"] = f
    x0 = min(x for _, x, _, _, _ in plan.bauten) - 6
    y0 = min(y for _, _, y, _, _ in plan.bauten) - 6
    x1 = max(x for _, x, _, _, _ in plan.bauten) + 10
    y1 = max(y for _, _, y, _, _ in plan.bauten) + 10
    k.update(x0=max(x0, k["x0"]), y0=max(y0, k["y0"]), x1=min(x1, k["x1"]), y1=min(y1, k["y1"]))
    k["f"] = {q: v for q, v in f.items() if k["x0"] <= q[0] <= k["x1"] and k["y0"] <= q[1] <= k["y1"]}
    return W.zeichnen(k, pfad, W.gebaeude_typen_aus(k, {}), zelle=20, titel=titel)


if __name__ == "__main__":
    import glob
    import json
    pfad = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(HIER, "..", "daten", "arbeitsgang_*_wegkarte.txt")))[-1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    k = W.lesen(pfad)
    # geplante/vorhandene Werkstaetten der Messpartie aus der Karte nehmen: nur Lager bleiben als Bestand
    plan, bericht = plane(k, n, n)
    w = bericht["waffenlager"]
    print("Waffenlager", w["ort"], "Richtung", w["richtung"], "Eingang", w["eingang"], "zum Lager", w["zum_lager"], "Felder")
    for s2 in bericht["schmiede"]:
        print("Schmiede", s2.get("ort"), "R", s2.get("richtung"), "Rundgang", s2.get("gang_felder"), "Felder =",
              s2.get("gang_ticks"), "Ticks, Zyklus", s2.get("zyklus_ticks"))
    for s2 in bericht["gerber"]:
        print("Gerberei", s2.get("ort"), "R", s2.get("richtung"), "Gang", s2.get("gang_felder"), "Felder =", s2.get("gang_ticks"), "Ticks")
    print(zeichne_plan(plan, os.path.join(HIER, "..", "daten", "plan_%d_%d.png" % (n, n)), "Plan %d Schmieden + %d Gerbereien" % (n, n)))
