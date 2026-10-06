# -*- coding: utf-8 -*-
"""Recherche fuer die Streitkolben-Challenge (Daniel 06.10. 19:45/19:49): was kostet und liefert jedes Glied der Kette?
Messpartie, KEIN Benchmark - Gold und Waren werden direkt gesetzt, damit nur die Gebaeude gemessen werden.

Gemessen (vorher festgelegt, Plan_Streitkolben.md):
  1. Markt: Stueck und Gold je Kauf/Verkauf fuer Keule (21) und Leder (23)
  2. Kaserne: was ein Streitkolbenkaempfer (Typ 26) abzieht - Gold, Keule, Leder, Bauer am Feuer
  3. Abriss: was eine abgerissene Schmiede zurueckgibt
  4. Produktion je Zeit: Kuehe (Milchviehhof), Leder je Kuh (Gerberei), Keulen je Eisen (Schmiede)
Ergebnis: daten/streitkolben_messung_<zeit>.json + Zeilen im Log.
Aufruf: python werkzeug/streitkolben_messen.py [ticks=6000] [tempo=300]
"""
import json
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
from bauen import vorrat
from laden import befehl, peek, TICK

D = os.path.join(HIER, "..", "daten")
SP = 1
KEULE, LEDER, GOLD, HOLZ, STEIN, EISEN = 21, 23, 15, 2, 4, 6
MILCH, GERBER, SCHMIEDE, WAFFENLAGER, KASERNE, LAGER, MARKT, HUETTE = 33, 16, 13, 11, 9, 10, 26, 1


def setze(art, menge):
    befehl({"ware": {"typ": art, "menge": menge}}, 1.0, bis="WARE")


def bestand():
    v = vorrat(SP)
    st = E.runde_lesen()[0]
    return {"t": st.get("t"), "gold": v.get("gold"), "keule": v.get("keule"), "leder": v.get("leder"), "eisen": v.get("eisen"),
            "holz": v.get("holz"), "stein": v.get("stein"), "feuer": st.get("feuer"), "kaempfer": st.get("T26", 0),
            "einheiten": {k: v2 for k, v2 in st.items() if re.match(r"T\d+$", k)}}


def differenz(a, b):
    return {k: b[k] - a[k] for k in ("gold", "keule", "leder", "eisen", "holz", "stein", "feuer", "kaempfer") if a.get(k) is not None and b.get(k) is not None}


def warte_ticks(n):
    t0 = peek(TICK)[0]
    while peek(TICK)[0] - t0 < n:
        time.sleep(0.05)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, tempo = int(arg.get("ticks", 6000)), int(arg.get("tempo", 300))
    plan = json.load(open(os.path.join(D, "eroeffnung_plan_M19.json"), encoding="utf-8"))
    lx, ly = plan["lager"]
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    erg = {"ablauf": [], "proben": []}
    for art, menge in ((GOLD, 20000), (HOLZ, 600), (STEIN, 300)):
        setze(art, menge)
    # Bauen nah am Lager (Daniel: Kaserne naeher zum Vorratslager, minimale Laufwege)
    orte = {}
    # Messpartie 1 (19:51): nach 5 Ticks war das vorige Gebaeude noch nicht eingetragen - die Platzsuche gab Schmiede,
    # Gerberei und Huette denselben Platz (90, 276); Milchviehhoefe (10x10) fanden im Umkreis 25 keinen Platz.
    # Darum: nach jedem Bau warten, bis das Gebaeude in der Liste steht; grosse Hoefe weiter weg suchen.
    for typ, r in ((LAGER, 6), (WAFFENLAGER, 10), (KASERNE, 12), (MARKT, 20), (SCHMIEDE, 12), (GERBER, 12),
                   (MILCH, 45), (MILCH, 45), (HUETTE, 20), (HUETTE, 20), (HUETTE, 20), (SCHMIEDE, 20)):
        vorher = sum(1 for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == typ)
        o = E.baue_schnell(typ, lx, ly, r)
        for _ in range(40):
            warte_ticks(3)
            if sum(1 for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == typ) > vorher:
                break
        else:
            o = ("nicht gebaut", o)
        orte.setdefault(typ, []).append(o)
    erg["ablauf"].append({"gebaut": {str(k): v for k, v in orte.items()}, "t": peek(TICK)[0]})
    print("gebaut:", orte, flush=True)
    warte_ticks(200)                                   # Gebaeude fertig, Arbeiter unterwegs
    G = E.runde_lesen()[2]
    eigen = {n: g for n, g in G.items() if g["besitzer"] == SP}
    kaserne = [n for n, g in eigen.items() if g["typ"] == KASERNE]
    schmieden = [n for n, g in eigen.items() if g["typ"] == SCHMIEDE]
    # 1. Markt
    for name, art in (("keule", KEULE), ("leder", LEDER)):
        a = bestand()
        befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
        warte_ticks(3)
        b = bestand()
        befehl({"spielbefehl": {"nr": 38, "werte": [1, art]}}, 1.0, bis="SPIELBEFEHL")
        warte_ticks(3)
        c = bestand()
        erg["ablauf"].append({"markt": name, "kauf": differenz(a, b), "verkauf": differenz(b, c)})
        print("MARKT %s: Kauf %s | Verkauf %s" % (name, differenz(a, b), differenz(b, c)), flush=True)
    # 2. Kaserne: ein Kaempfer mit gesetzter Keule und Leder
    setze(KEULE, 5); setze(LEDER, 5)
    a = bestand()
    if kaserne:
        befehl({"werbe": {"typ": 26, "gebaeude": kaserne[0]}}, 1.0, bis="WERBE")
        warte_ticks(30)
    b = bestand()
    erg["ablauf"].append({"kaserne": kaserne, "werben": differenz(a, b)})
    print("KASERNE: ein Streitkolbenkaempfer zieht ab %s" % differenz(a, b), flush=True)
    # 3. Abriss der zweiten Schmiede
    if len(schmieden) >= 2:
        a = bestand()
        befehl({"abreissen": {"nr": schmieden[-1]}}, 0.8, bis="ABREISSEN")
        warte_ticks(10)
        b = bestand()
        erg["ablauf"].append({"abriss_schmiede": differenz(a, b)})
        print("ABRISS Schmiede: %s" % differenz(a, b), flush=True)
    # 4. Produktion: Eisen fuer die Schmiede, Keule/Leder auf 0, dann laufen lassen und mitschreiben
    setze(KEULE, 0); setze(LEDER, 0); setze(EISEN, 20)
    t0 = peek(TICK)[0]
    while peek(TICK)[0] - t0 < dauer:
        p = bestand()
        erg["proben"].append(p)
        time.sleep(0.3)
    letzte = erg["proben"][-1]
    print("PRODUKTION in %d Ticks: Keulen %s (Eisen 20 -> %s), Leder %s; Einheiten %s" % (
        letzte["t"] - t0, letzte["keule"], letzte["eisen"], letzte["leder"], letzte["einheiten"]), flush=True)
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "streitkolben_messung_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1)
    print("Daten:", pfad)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
