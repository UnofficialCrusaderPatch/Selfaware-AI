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
    # Messpartie 4: Schmiede ~55 Felder vom Lager am Bergfried -> ~4.100 Ticks je Eisen. Darum alles direkt an dieses Lager
    # (Daniel: Kaserne naeher zum Vorratslager, minimale Laufwege).
    teile0 = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == LAGER]
    if teile0:
        lx, ly = teile0[0]["x"], teile0[0]["y"]
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    erg = {"ablauf": [], "proben": []}
    # Nur Gold ist eine reine Zahl. Stein/Holz/Eisen/Waffen liegen in Lagern: ein gesetzter Zaehler wird vom Spiel neu
    # gezaehlt (Messpartie 2: Stein 0 -> 300 gesetzt, kurz darauf 0) - darum fehlte Kaserne (12 Stein), Schmiede (8),
    # Gerberei (3), Daniel 19:54: "du brauchst gewisse Gueter, siehe Balance". Waren werden echt am Markt gekauft.
    setze(GOLD, 20000)
    # Bauen nah am Lager (Daniel: Kaserne naeher zum Vorratslager, minimale Laufwege)
    orte = {}
    # Messpartie 1 (19:51): nach 5 Ticks war das vorige Gebaeude noch nicht eingetragen - die Platzsuche gab Schmiede,
    # Gerberei und Huette denselben Platz (90, 276); Milchviehhoefe (10x10) fanden im Umkreis 25 keinen Platz.
    # Darum: nach jedem Bau warten, bis das Gebaeude in der Liste steht; grosse Hoefe weiter weg suchen.
    # Messpartie 5: alles direkt ans Lager gebaut -> kein Platz zum Anbauen, Eisenkauf und Abriss-Rueckgabe scheiterten
    # (jedes Teil nur eine Warenart, 48). Darum ZUERST zwei Lagerbloecke anbauen, dann den Rest drumherum.
    for typ, r in ((LAGER, 8), (LAGER, 10), (MARKT, 20), (WAFFENLAGER, 10), ("kaufen", 0), (KASERNE, 12), (SCHMIEDE, 12), (GERBER, 12),
                   (MILCH, 45), (MILCH, 45), (HUETTE, 20), (HUETTE, 20), (HUETTE, 20), (SCHMIEDE, 20)):
        if typ == "kaufen":                       # nach dem Markt: Stein und Holz echt kaufen
            for art, lose in ((STEIN, 10), (HOLZ, 10)):
                for _ in range(lose):
                    befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
            warte_ticks(10)
            orte["gekauft"] = [bestand()]
            continue
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
    # Schmiede auf Keulen stellen: Spielbefehl 33 ClickSetBuildingProductionType (Gebaeude, Art, UID) ->
    # SetBuildingProductionType setzt producedItemType, wenn die UID passt (dekomp_produktionstyp*.c). Art 21 = Keule.
    for n, g in eigen.items():
        if g["typ"] == SCHMIEDE:
            befehl({"spielbefehl": {"nr": 33, "werte": [n, KEULE, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
            erg["ablauf"].append({"schmiede_auf_keule": [n, g.get("uid")]})
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
    for art in (KEULE, LEDER):                     # Waffen liegen im Waffenlager: echt kaufen statt setzen
        befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(5)
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
        # rueckgabe=1: Spielbefehl 29 {nr, rueckgabe, uid}; ohne kam 3-mal 0 zurueck. Daniel 20:06: Abriss gibt normalerweise die
        # Haelfte zurueck, egal in welchem Zustand (giveBackResourceForDestroyedBuilding, daten/dekomp_abriss_rueckgabe.c)
        befehl({"abreissen": {"nr": schmieden[-1], "rueckgabe": 1}}, 0.8, bis="ABREISSEN")
        warte_ticks(150)      # Messpartie 3: nach 10 Ticks noch nichts
        b = bestand()
        erg["ablauf"].append({"abriss_schmiede": differenz(a, b)})
        print("ABRISS Schmiede: %s" % differenz(a, b), flush=True)
    # 4. Produktion: Eisen fuer die Schmiede, Keule/Leder auf 0, dann laufen lassen und mitschreiben
    # Jedes Lagerteil fasst nur eine Warenart (Messung 19:58, Tipp Daniel); die 4 Startteile waren mit Holz und Stein
    # belegt, Eisen fand keinen Platz. Darum vorher einen Lagerblock anbauen (kostet nichts).
    teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == LAGER]
    if teile:
        erg["ablauf"].append({"lager_anbau": E.baue_schnell(LAGER, teile[0]["x"], teile[0]["y"], 8)})
        warte_ticks(40)
    vor_eisen = bestand()
    for _ in range(4):                              # Eisen fuer die Schmiede echt kaufen (Los zu 270 Gold)
        befehl({"spielbefehl": {"nr": 38, "werte": [0, EISEN]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(5)
    erg["ablauf"].append({"eisenkauf": differenz(vor_eisen, bestand())})
    print("EISENKAUF 4 Lose: %s" % erg["ablauf"][-1]["eisenkauf"], flush=True)
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
