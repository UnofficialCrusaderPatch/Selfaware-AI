# -*- coding: utf-8 -*-
"""Erstes Spiel (M14, Daniel 04.10.2026 21:54): Eroeffnung nach Plan, dann Echtzeit mit Tempo 40.

Phase 1 (Spiel steht bei Tick 600): Startholz nach daten/eroeffnung_plan.json verbauen (Holzfaeller, Kornspeicher,
Apfelplantagen, Steinbruch + Ochsenjoch, Huetten), dann das leere Lager abreissen und am geplanten Platz neu
setzen (Daniels Regel). Jeder Bau mit Erfolgskontrolle; Stand wird gesichert.
Phase 2 (Echtzeit): Tempo 40, laeuft. Alle paar Sekunden: Lage mitschreiben und zwei Regeln anwenden -
  - Haeuser (Daniel): liegt die Zahl der Arbeiter, die alle eigenen Betriebe brauchen, ueber den Wohnplaetzen,
    wird eine Huette gebaut (5 Holz), so nah wie moeglich am Bergfried.
  - Lager (Daniel): ein Lagerteil fasst je Rohstoff ~48; wird der Platz knapp, wird ein 4er-Block angebaut
    (kostet nichts), damit kein Traeger warten muss oder seine Ware verliert.
Fehlerkontrolle (Daniel): vorab Gefecht/Mensch/gameOver; laufend: steht die Spielzeit oder ist gameOver 1 -> Abbruch.

Aufruf:  python erstes_spiel.py [minuten=10] [tempo=40] [nur_phase2=nein]
Stop von aussen: Datei werkzeug/STOP anlegen.
"""
import json, math, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import lade_stand, befehl, peek
from steuerkarte import laufe, tick, spielzustand
from bauen import NACH_TYP, gebaeude_von, vorrat, baue_irgendwo
from plantagen_lauf import baue_alle, vorab
from speichern import speichere

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
SP = 1
PD = 0x0115BDF8 + SP * 0x39F4
ARBEITER_JE = {3: 1, 32: 1, 30: 1, 31: 1, 33: 1, 20: 3, 4: 1, 5: 2, 7: 1, 6: 1}   # Betrieb -> Arbeiter (Steinbruch 3, Mine 2: Annahme)
LAGERWAREN = ("holz", "hopfen", "stein", "eisen", "pech", "weizen", "mehl")
LOG = os.path.join(D, "erstes_spiel_log.txt")

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def schreib(text):
    print(text)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + text + "\n")

def phase1(plan):
    schreib("== Phase 1: Eroeffnung nach Plan (%s)" % os.path.basename(plan["_datei"]))
    print("Tick", lade_stand("M7-04 Mensch Grumpy T600", mit_bild=False))
    befehl({"eigenerPlatz": SP}, 0.8)
    vorab()
    v0 = vorrat(SP)
    auftrag = [(3, p) for p in plan["holzfaeller"]] + [(19, plan["kornspeicher"])] + [(32, p) for p in plan["aepfel"]]
    if plan.get("stein"):
        auftrag += [(20, plan["stein"]["steinbruch"]), (4, plan["stein"]["ochsen"])]
    auftrag += [(1, p) for p in plan["huetten"]]
    gebaut, fehl = 0, []
    for typ, (x, y) in auftrag:
        g, f = baue_alle(typ, [(x, y)])
        gebaut += len(g); fehl += [(NACH_TYP[typ]["name"], x, y) for (x, y) in f]
    v1 = vorrat(SP)
    schreib("GEBAUT %d von %d; Fehlschlaege: %s; Holz %d -> %d, Gold %d -> %d" % (gebaut, len(auftrag), fehl or "keine",
            v0["holz"], v1["holz"], v0["gold"], v1["gold"]))
    alt = gebaeude_von(SP, 10)
    for nr, x, y in alt:
        befehl({"abreissen": {"nr": nr}}, 0.5)
    laufe(1)
    neu = baue_irgendwo(10, [tuple(plan["lager"])], SP)
    schreib("Lager: alt %d Teile abgerissen (Inhalt: %s), neu bei %s -> %s; jetzt %d Teile" % (
        len(alt), {k: v1[k] for k in LAGERWAREN if v1.get(k)}, plan["lager"], neu, len(gebaeude_von(SP, 10))))
    speichere("M14 Eroeffnung Grumpy T%d" % tick())
    befehl({"eigenerPlatz": SP}, 0.8)

def lage():
    v = vorrat(SP)
    t = {int(a): int(n) for a, n in re.findall(r"S%d:T(\d+)=(\d+)" % SP, " ".join(befehl({"typen": {"spieler": SP}}, 0.8)))}
    return {"tick": tick(), "v": v, "t": t, "beliebt": s32(peek(PD + 0x60)[0]) / 100.0, "platz": s32(peek(PD + 116)[0]),
            "leute": s32(peek(PD + 8576)[0]), "feuer": s32(peek(PD + 136)[0]), "essen": s32(peek(PD + 0x2160)[0])}

def betriebe():
    n = {}
    for typ in ARBEITER_JE:
        n[typ] = len(gebaeude_von(SP, typ))
    return n

def haus_noetig(l, b):
    bedarf = sum(ARBEITER_JE[t] * k for t, k in b.items())
    return bedarf, bedarf > l["platz"]

def baue_haus():
    z = " ".join(befehl({"platzsuche": {"spieler": SP, "mapper": NACH_TYP[1]["mapper"], "groesse": 4, "x": 158, "y": 109, "r": 20, "max": 4}}, 1.5))
    frei = [tuple(map(int, p)) for p in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    return baue_irgendwo(1, frei, SP) if frei else None

def lager_knapp(l, teile):
    menge = sum(l["v"].get(k, 0) for k in LAGERWAREN)
    sorten = sum(1 for k in LAGERWAREN if l["v"].get(k, 0) > 0)
    return menge >= 48 * teile - 60 or sorten >= teile

def baue_lager(plan):
    lx, ly = plan["lager_mitte"]
    z = " ".join(befehl({"platzsuche": {"spieler": SP, "mapper": NACH_TYP[10]["mapper"], "groesse": 5, "x": lx, "y": ly, "r": 10, "max": 6}}, 1.5))
    frei = [tuple(map(int, p)) for p in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    return baue_irgendwo(10, frei, SP) if frei else None

def phase2(plan, minuten, tempo):
    schreib("== Phase 2: Echtzeit, Tempo %d, %d Minuten" % (tempo, minuten))
    vorab()
    befehl({"kamera": list(plan["lager_mitte"])}, 0.8)
    befehl({"tempo": tempo}, 0.5)
    befehl({"pause": False}, 0.5)
    ende, letzter_tick, stand = time.time() + 60 * minuten, None, None
    schreib("Tick | Holz Stein Eisen | Aepfel Brot | Beliebt | Leute/Platz (Feuer) | Holzf. Apfelb. | Ereignis")
    while time.time() < ende and not os.path.exists(os.path.join(HIER, "STOP")):
        l = lage()
        z = spielzustand()
        if "gameOver 1" in z or "Ansicht 14" not in z:
            schreib("ABBRUCH - Testbedingung weg: %s" % z); break
        if l["tick"] == letzter_tick:
            stand = (stand or 0) + 1
            if stand >= 3:
                schreib("ABBRUCH - Spielzeit steht bei %s: %s" % (l["tick"], z)); break
        else:
            stand = 0
        letzter_tick = l["tick"]
        ereignis = []
        b = betriebe()
        bedarf, noetig = haus_noetig(l, b)
        if noetig and l["v"]["holz"] >= 5:
            ereignis.append("Huette %s (Bedarf %d > Platz %d)" % (baue_haus(), bedarf, l["platz"]))
        teile = len(gebaeude_von(SP, 10))
        if lager_knapp(l, teile):
            ereignis.append("Lager angebaut %s (%d Teile)" % (baue_lager(plan), teile))
        v = l["v"]
        schreib("%5d | %3d %3d %3d | %3d %3d | %6.2f | %d/%d (%d) | %d %d | %s" % (
            l["tick"], v["holz"], v["stein"], v["eisen"], v["apfel"], v["brot"], l["beliebt"], l["leute"], l["platz"],
            l["feuer"], l["t"].get(3, 0), l["t"].get(13, 0), "; ".join(ereignis) or "-"))
        time.sleep(1.0)
    befehl({"pause": True}, 0.5)
    schreib("Ende Phase 2 bei Tick %s, %s" % (tick(), spielzustand()))

def main():
    arg = dict(a.split("=") for a in sys.argv[1:])
    datei = os.path.join(D, "eroeffnung_plan.json")
    plan = json.load(open(datei, encoding="utf-8")); plan["_datei"] = datei
    if arg.get("nur_phase2", "nein") != "ja":
        phase1(plan)
    phase2(plan, int(arg.get("minuten", 10)), int(arg.get("tempo", 40)))

if __name__ == "__main__":
    main()
