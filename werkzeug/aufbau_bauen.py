# -*- coding: utf-8 -*-
"""Plan aus aufbau_planer.py im Spiel bauen und messen (Daniel 06.10. 20:29: "wenn alles maximal effektiv geht nach
Theorie, baue es im Spiel ... erst 5 von beidem, dann 15, dann 30").

Messpartie, KEIN Benchmark ab Tick 0: Gold gesetzt, Baukosten 0 (Rueckweg im finally), Eisen am Markt gekauft.
Ablauf: Lager erweitern und Markt ZUERST (Messpartie 5: sonst sperrt der Aufbau den Anbau), Wegkarte lesen, planen,
Waffenlager/Schmieden/Gerbereien genau nach Plan (Ort + Richtung), Milchviehhoefe per Platzsuche nahe den Gerbereien,
Eisen kaufen, Schmieden auf Keulen. Dann mitschreiben: alle Arbeiter (einheitwacht alle 2 Ticks), Kuehe (Typ 51) und
Bestand alle 50 Ticks.
Vergleich danach: gemessener Rundgang je Schmiede gegen den geplanten (arbeitsgang_auswerten + plan in der Datei).
Aufruf: python werkzeug/aufbau_bauen.py [n=5] [ticks=12000] [hoefe=3] [tempo=300]
"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
import wegkarte as W
import aufbau_planer as P
from laden import befehl, peek, TICK
from streitkolben_messen import setze, bestand, warte_ticks, GOLD, EISEN, KEULE
from wege_abstand import kosten_nullen, kosten_zurueck, ART
from arbeitsgang_messen import log_ab
import messumgebung as M

D = os.path.join(HIER, "..", "daten")
SP = 1
MAPPER = {P.WAFFENLAGER: 81, P.SCHMIEDE: 83, P.GERBEREI: 85}
ARBEITER = {19: "Schmied", 21: "Gerber", 14: "Milchbauer"}


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    n, dauer, hoefe, tempo = int(arg.get("n", 5)), int(arg.get("ticks", 12000)), int(arg.get("hoefe", 3)), int(arg.get("tempo", 300))
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    alt = kosten_nullen()
    stempel = time.strftime("%Y%m%d_%H%M%S")
    erg = {"n": n, "kosten_alt": {"0x%08X" % a: v for a, v in alt.items()}, "bestand": [], "kuehe": [], "gebaut": []}
    try:
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == P.LAGER]
        lx, ly = teile[0]["x"], teile[0]["y"]
        for typ, r in ((P.LAGER, 8), (26, 20)):              # Lager anbauen und Markt zuerst
            erg["gebaut"].append(["vorab", typ, E.baue_schnell(typ, lx, ly, r)])
            warte_ticks(8)
        k = W.holen(max(lx - 30, 0), max(ly - 30, 0), min(lx + 30, 399), min(ly + 30, 399))
        plan, bericht = P.plane(k, n, n)
        erg["plan"] = bericht
        P.zeichne_plan(plan, os.path.join(D, "aufbau_%s_plan.png" % stempel), "Plan %d+%d" % (n, n))
        for art, x, y, r, e in plan.bauten:
            befehl({"baue": {"mapper": MAPPER[art], "x": x, "y": y, "groesse": 4, "richtung": r}}, 0.8, bis="BAUE")
            warte_ticks(3)
        warte_ticks(5)
        k2 = W.holen(k["x0"], k["y0"], k["x1"], k["y1"])
        steht = [(art, x, y, r) for art, x, y, r, e in plan.bauten if k2["f"].get((x, y), (0,) * 6)[5] == art]
        erg["plan_gebaut"] = "%d von %d" % (len(steht), len(plan.bauten))
        print("Plan gebaut: %s" % erg["plan_gebaut"], flush=True)
        # Milchviehhoefe nahe den Gerbereien (Gruenland: Platzsuche des Spiels)
        ger = [(x, y) for art, x, y, r, e in plan.bauten if art == P.GERBEREI] or [(lx, ly)]
        gx, gy = sum(p[0] for p in ger) // len(ger), sum(p[1] for p in ger) // len(ger)
        for _ in range(hoefe):
            erg["gebaut"].append(["hof", 33, E.baue_schnell(33, gx, gy, 45)])
            warte_ticks(8)
        print("Hoefe:", [g[2] for g in erg["gebaut"] if g[0] == "hof"], flush=True)
        # Messumgebung (Daniel 20:41): Beliebtheit 100 halten - Kornspeicher und Huetten ABSEITS des Plans
        bx0 = min(x for _, x, _, _, _ in plan.bauten)
        by1 = max(y for _, _, y, _, _ in plan.bauten)
        erg["messumgebung"] = M.vorbereiten(bx0 - 10, by1 + 10)
        warte_ticks(10)
        k4 = W.holen(k["x0"], k["y0"], k["x1"], k["y1"])
        p4 = P.Plan(k4)
        we = next(e for art, x, y, r, e in plan.bauten if art == P.WAFFENLAGER)
        dw = p4.abstand(we)
        zu = [e for art, x, y, r, e in plan.bauten if e not in dw]
        erg["eingaenge_unerreichbar"] = zu
        print("Messumgebung:", erg["messumgebung"], "| Eingaenge unerreichbar:", zu or "keine", flush=True)
        for _ in range(6):                                    # 30 Eisen
            befehl({"spielbefehl": {"nr": 38, "werte": [0, EISEN]}}, 1.0, bis="SPIELBEFEHL")
        G = E.runde_lesen()[2]
        for nr, g in G.items():
            if g["besitzer"] == SP and g["typ"] == P.SCHMIEDE:
                befehl({"spielbefehl": {"nr": 33, "werte": [nr, KEULE, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
        erg["gebaeude_liste"] = {nr: g for nr, g in G.items() if g["besitzer"] == SP}
        nummern = {}
        for _ in range(80):                                   # Arbeiter abwarten
            L = E.runde_lesen()[1]
            nummern = {u: e["typ"] for u, e in L.items() if e["besitzer"] == SP and e["typ"] in ARBEITER}
            if sum(1 for t in nummern.values() if t == 19) >= n and sum(1 for t in nummern.values() if t == 21) >= n                     and sum(1 for t in nummern.values() if t == 14) >= hoefe:
                break
            M.pflegen()
            warte_ticks(30)
        erg["arbeiter"] = {str(u): ARBEITER[t] for u, t in nummern.items()}
        print("Arbeiter:", sorted(erg["arbeiter"].values()), flush=True)
        befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
        t0 = peek(TICK)[0]
        erg["t0"] = t0
        while peek(TICK)[0] - t0 < dauer:
            b = bestand()
            erg["bestand"].append({k3: b[k3] for k3 in ("t", "keule", "leder", "eisen")})
            erg["kuehe"].append([b["t"], b["einheiten"].get("T51", 0)])
            if len(erg["bestand"]) % 10 == 0:
                erg.setdefault("beliebt", []).append([b["t"], M.pflegen()])
            warte_ticks(50)
        befehl({"einheitwacht": False}, 1.0, bis="EINHEITWACHT")
        erg["ew"] = [z.split("INFO|", 1)[-1] for z in log_ab("EINHEITWACHT: scharf") if "EW " in z]
        k3 = W.holen(k["x0"], k["y0"], k["x1"], k["y1"])
        W.zeichnen(k3, os.path.join(D, "aufbau_%s_spiel.png" % stempel), W.gebaeude_typen_aus(k3, {}), zelle=14,
                   titel="Aufbau %d+%d im Spiel (Ende)" % (n, n))
        print("EW-Zeilen:", len(erg["ew"]), "Bestand Ende:", erg["bestand"][-1], "Beliebtheit:",
              [x[1]["beliebt"] for x in erg.get("beliebt", [])][::4], flush=True)
    finally:
        kosten_zurueck(alt)
        befehl({"pause": True}, 0.5)
        pfad = os.path.join(D, "aufbau_%s.json" % stempel)
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        import shutil
        shutil.copy(os.path.join(kanal.ABZUG, "wegkarte.txt"), pfad.replace(".json", "_wegkarte.txt"))
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
