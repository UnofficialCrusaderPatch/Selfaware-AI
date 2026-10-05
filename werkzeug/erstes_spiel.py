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

Waechter (M15, Daniel 22:42): mit waechter=ja liest jede Runde das Lagebild und schickt Verteidiger (waechter.py).
Aufruf:  python erstes_spiel.py [minuten=10] [tempo=40] [nur_phase2=nein] [waechter=nein] [start=<Spielstand>] [bis_tick=N] [assassinen=N; -1 = ohne Grenze]
         Tests mit Hoechstgeschwindigkeit (Daniel 22:55): tempo=1000 bis_tick=...
Stop von aussen: Datei werkzeug/STOP anlegen.
"""
import json, math, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import lade_stand, befehl, peek
from steuerkarte import laufe, tick, spielzustand
from bauen import NACH_TYP, gebaeude_von, vorrat, baue_irgendwo
from plantagen_lauf import baue_alle, vorab
from speichern import speichere
from waechter import Waechter, lies_lagebild, lies_gebaeude
from assassinen import Angriffstrupp, Einzeln
from befehl import sende, neue_id
from wirtschaft import Wirtschaft, apfel_gruppen

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
    print("Tick", lade_stand(BASIS, mit_bild=False))
    befehl({"eigenerPlatz": SP}, 0.8)
    vorab()
    from bauen import baue_viele
    # Liga-Start (0 Gold): Kornspeicher + Markt zuerst; die Start-Nahrung (je 15) erscheint erst mit dem Kornspeicher.
    # Dann alles bis auf den Puffer verkaufen, teuerste Sorte zuerst - das ist das Startgold fuer die Apfelplantagen.
    baue_viele([(19, plan["kornspeicher"][0], plan["kornspeicher"][1])], SP)
    markt = baue_schnell(26, BERGFRIED[0], BERGFRIED[1], 25)
    laufe(120)
    vk = vorrat(SP)
    lose = nahrung_auf_kante({k: vk.get(k, 0) for k in NAHRUNG_PREIS}, nahrung_puffer(10))
    laufe(5)
    v0 = vorrat(SP)
    schreib("Liga-Start: Kornspeicher + Markt %s; Start-Nahrung %s verkauft (Lose zu 5) -> Gold %d, Nahrung uebrig %s" % (
        markt, lose, v0["gold"], {k: v0.get(k, 0) for k in NAHRUNG_PREIS if v0.get(k, 0)}))
    # Seasoning (Daniel 04.10./05.10.): nur Gruppe A jetzt, B wenn A reif wird (wirtschaft.py); B-Holz bleibt im alten Lager
    A, B = apfel_gruppen(plan["aepfel"])
    auftrag = [(3, p) for p in plan["holzfaeller"]] + [(32, p) for p in A]
    if plan.get("stein"):
        auftrag += [(20, plan["stein"]["steinbruch"]), (4, plan["stein"]["ochsen"])]
    auftrag += [(1, p) for p in plan["huetten"]]
    g1, f1 = baue_viele([(typ, x, y) for typ, (x, y) in auftrag], SP)
    gebaut, fehl = len(g1), []
    for typ, x, y in f1:                      # Rest einzeln (z. B. stand gerade eine Einheit auf der Flaeche)
        g, f = baue_alle(typ, [(x, y)])
        gebaut += len(g); fehl += [(NACH_TYP[typ]["name"], x, y) for (x, y) in f]
    schreib("in einem Aufruf gebaut: %d von %d, einzeln nachgeholt: %d" % (len(g1), len(auftrag), len(f1)))
    v1 = vorrat(SP)
    schreib("GEBAUT %d von %d; Fehlschlaege: %s; Holz %d -> %d, Gold %d -> %d" % (gebaut, len(auftrag), fehl or "keine",
            v0["holz"], v1["holz"], v0["gold"], v1["gold"]))
    # Lager (Daniel 04.10.): das alte bleibt, bis B steht (haelt dessen Holz); das neue erst, wenn ein Holzfaeller
    # abliefern will - beides in Phase 2 (wirtschaft.py)
    schreib("Apfelplantagen A %d jetzt, B %d spaeter %s; altes Lager bleibt mit %s" % (
        len(A), len(B), B, {k: v1[k] for k in LAGERWAREN if v1.get(k)}))
    name = "M19 Liga Eroeffnung T%d" % tick()
    speichere(name)
    befehl({"eigenerPlatz": SP}, 0.8)
    return name

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

def baue_schnell(typ, x, y, r, mapper=None):
    """Im laufenden Spiel: Platz suchen und bauen OHNE zu blockieren (04.10.: das alte Bauwerkzeug wartete fest und
    auf einen genauen Tick - bei Tempo 1000 hing die Schleife ~20.000 Ticks, der Waechter kam nie dran).
    Ob es steht, zeigt die naechste Runde (Gebaeudeliste)."""
    g = NACH_TYP[typ]
    z = " ".join(befehl({"platzsuche": {"spieler": SP, "mapper": g["mapper"], "groesse": g["b"], "x": x, "y": y, "r": r, "max": 1}},
                        1.0, bis="PLATZSUCHE"))
    frei = [tuple(map(int, p)) for p in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    if not frei:
        return None
    befehl({"baue": {"mapper": g["mapper"], "x": frei[0][0], "y": frei[0][1], "groesse": g["b"], "richtung": 0}}, 1.0, bis="BAUE")
    return frei[0]

def baue_haus():
    return baue_schnell(1, BERGFRIED[0] - 7, BERGFRIED[1] - 2, 20)    # nahe am Bergfried (frueher fest 158,109 = 165-7, 111-2)

def lager_knapp(l, teile):
    menge = sum(l["v"].get(k, 0) for k in LAGERWAREN)
    sorten = sum(1 for k in LAGERWAREN if l["v"].get(k, 0) > 0)
    return menge >= 48 * teile - 60 or sorten >= teile

def baue_lager(plan):
    lx, ly = plan["lager_mitte"]
    return baue_schnell(10, lx, ly, 10)

EIGENE_ARTEN = (3, 19, 32, 20, 4, 1, 10, 30, 31, 33, 5)

ROHSTOFFE = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme\ucp\villagestudio\abzug\rohstoffe.txt"
_KARTE = []

def karte_laden():
    """Rohstoffkarte (Modulbefehl rohstoffkarte, einmal je Partie bei stehendem Spiel) fuer die Begehbarkeit."""
    befehl({"rohstoffkarte": {}}, 6.0, bis="ROHSTOFF")
    _KARTE[:] = open(ROHSTOFFE).read().splitlines()[1:]

def pruefe_begehbar(punkte):
    """Begehbar = das Feld und seine 8 Nachbarn sind Gruenland (G), Gestruepp (s) oder freier Boden (.) - nicht
    Wasser, Fluss, Rand, Gebaeude, Stein, Eisen, Pech. 05.10.: die Wegnetz-Pruefung des Spiels taugte dafuer nicht
    (Gegenprobe: Wasser, Rand und Gebaeudefelder galten als erreichbar). Gebaeude, die nach dem Kartenabzug
    entstehen, kennt die Karte nicht - dafuer sperrt der Assassinen-Lenker Plaetze, an die keiner hinlaeuft."""
    gut = set()
    for x, y in punkte:
        if all(0 <= y + dy < len(_KARTE) and 0 <= x + dx < len(_KARTE[y + dy]) and _KARTE[y + dy][x + dx] in "Gs."
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            gut.add((x, y))
    return gut

def wegtest(nr, punkte):
    """Modulbefehl wegtest: hat Einheit <nr> laut Wegfinder des Spiels einen Weg zu jedem Punkt? (05.10., Gegenprobe gruen:
    Wasser und Gebaeudefelder -> kein Weg, freies Feld -> Weg)"""
    z = " ".join(befehl({"wegtest": {"nr": nr, "punkte": [list(p) for p in punkte]}}, 1.0, bis="WEGTEST"))
    m = re.search(r"WEGTEST \d+: ([01]*)", z)
    return [c == "1" for c in m.group(1)] if m else [False] * len(punkte)

def runde_lesen():
    """EIN Aufruf fuer die ganze Runde (04.10.: einzelne Abfragen kosteten ~20 s = 800 Ticks je Runde):
    Modulbefehle status + lagebild in einer Liste. Gibt (status, einheiten, gebaeude)."""
    z = " ".join(sende({"befehle": [{"player": 1, "id": neue_id(), "status": SP},
                                    {"player": 1, "id": neue_id(), "lagebild": True}]}, 1.5, bis="LAGEBILD Tick"))
    m = re.search(r"STATUS (.*?)(?:\[villagestudio\]|$)", z)
    st = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", m.group(1))} if m else {}
    return st, lies_lagebild(neu_holen=False), lies_gebaeude()

def eigene_gebaeude():
    orte = []
    for t in EIGENE_ARTEN:
        orte += [(x + NACH_TYP[t]["b"] // 2, y + NACH_TYP[t]["b"] // 2) for _, x, y in gebaeude_von(SP, t)]
    return orte

ESSEN_RESERVE, HOLZ_RESERVE, STEIN_RESERVE, GOLD_RESERVE = 60, 15, 0, 30   # Daniel 23:06: alles ueber dem Minimum verkaufen
BASIS = "M19 Liga Start Grumpy T600"     # Liga-Bedingung: 0 Gold, 150 Holz (Daniel 05.10. 00:55; gemessen 18:38)
BERGFRIED = (141, 269)                    # wird in main() aus dem Plan gesetzt (Bergfried-Eingang dieses Starts)
# Verkaufspreise Liga, gemessen 05.10. 18:50 (daten/verkaufspreise_liga.txt), ein Verkauf = 5 Stueck
NAHRUNG_PREIS = {"kaese": 6, "brot": 4, "apfel": 3, "fleisch": 1}

def nahrung_puffer(leute):
    """Nahrung auf Kante (Daniel 05.10. 18:51): nur so viel behalten, dass bis zur naechsten Lieferung genau noch etwas
    da ist - alles andere ist Startgold. Gemessen 05.10.: 10 Leute assen bei normalen Rationen 1 Stueck in 1.000 Ticks.
    STARTWERT: 3 + 1 je 10 Leute (deckt mit Abstand die ~1.000 Ticks bis zu den ersten eigenen Aepfeln)."""
    return 3 + leute // 10

def nahrung_auf_kante(bestand, puffer, hoechstens=12):
    """Verkauft Nahrung in Losen zu 5, die teuerste Sorte zuerst, ohne unter <puffer> zu fallen; die billigste bleibt.
    bestand: dict Sorte -> Menge. Gibt dict Sorte -> verkaufte Lose."""
    rest = dict(bestand)
    lose = {}
    for ware in sorted(NAHRUNG_PREIS, key=lambda w: -NAHRUNG_PREIS[w]):
        while rest.get(ware, 0) >= 5 and sum(rest.values()) - 5 >= puffer and sum(lose.values()) < hoechstens:
            rest[ware] -= 5
            lose[ware] = lose.get(ware, 0) + 1
    if lose:
        sende({"befehle": [{"player": 1, "id": neue_id(), "spielbefehl": {"nr": 38, "werte": [1, WAREN_NR[w]]}}
                           for w, k in lose.items() for _ in range(k)]}, 1.5, bis="SPIELBEFEHL")
    return lose
WAREN_NR = {"holz": 2, "stein": 4, "eisen": 6, "pech": 7, "apfel": 13, "brot": 10, "kaese": 11, "fleisch": 12, "weizen": 9, "hopfen": 3, "mehl": 16}

def verkaufen(st):
    """Je Runde hoechstens ein Verkauf je Ware (Spielbefehl 38, verkaufen=1). Gibt Text oder None."""
    teile = []
    essen = sum(st.get(k, 0) for k in ("apfel", "brot", "kaese", "fleisch"))
    for ware, reserve in (("holz", HOLZ_RESERVE), ("stein", STEIN_RESERVE), ("eisen", 0), ("pech", 0),
                          ("weizen", 0), ("hopfen", 0), ("mehl", 0)):
        if st.get(ware, 0) > reserve + 4:
            befehl({"spielbefehl": {"nr": 38, "werte": [1, WAREN_NR[ware]]}}, 1.0, bis="SPIELBEFEHL"); teile.append(ware)
    lose = nahrung_auf_kante({k: st.get(k, 0) for k in NAHRUNG_PREIS}, nahrung_puffer(st.get("leute", 10)))
    teile += ["%s x%d" % (w, k) for w, k in lose.items()]
    return ("verkauft: " + ",".join(teile)) if teile else None

def phase2(plan, minuten, tempo, mit_waechter=False, bis_tick=None, assassinen=0):
    schreib("== Phase 2: Echtzeit, Tempo %d, %d Minuten, Waechter %s" % (tempo, minuten, "an" if mit_waechter else "aus"))
    vorab()
    # Halte-Liste des Moduls ueberlebt das Laden einer Partie (04.10.: alte Eintraege zogen neue Assassinen mit
    # gleicher Nummer an fremde Plaetze zurueck - "sie sammeln sich nur und machen nichts")
    befehl({"halten": False}, 1.0, bis="HALTEN")
    import befehl as befehlskanal
    befehlskanal.STRENG = True     # ab hier bricht jeder Modulfehler den Lauf laut ab
    w = Waechter(SP, posten=plan["lager_mitte"]) if mit_waechter else None
    trupp = Einzeln(SP, pruefe_begehbar=pruefe_begehbar, wegtest=wegtest) if assassinen else None
    wirt = Wirtschaft(plan, SP, baue_schnell, [nr for nr, _, _ in gebaeude_von(SP, 10)])
    karte_laden()        # Begehbarkeit fuer kurze Rueckzuege - jetzt, solange das Spiel noch steht
    schreib("Wirtschaft: Apfel A %s, B %s; alte Lagerteile %s" % (wirt.A, wirt.B, sorted(wirt.alt)))
    soeldner, geworben = None, 0
    befehl({"kamera": list(plan["lager_mitte"])}, 0.8)
    befehl({"tempo": tempo}, 0.5)
    befehl({"pause": False}, 0.5)
    ende, letzter_tick, stand, runde, t0 = time.time() + 60 * minuten, None, 0, 0, time.time()
    schreib("Tick | Holz Stein Eisen | Aepfel Brot | Beliebt | Leute/Platz (Feuer) | Holzf. Apfelb. | Ereignis")
    zeiten, diese_runde, feindlord = {}, {}, {}
    def uhr(name, t0):
        zeiten[name] = zeiten.get(name, 0.0) + time.time() - t0
        diese_runde[name] = time.time() - t0
        return time.time()
    while time.time() < ende and not os.path.exists(os.path.join(HIER, "STOP")):
        tz = time.time()
        befehlskanal.belege()
        st, L, G = runde_lesen()
        tz = uhr("lesen", tz)
        if bis_tick and st.get("t", 0) >= bis_tick:
            break
        runde += 1
        if not st:
            continue
        if st.get("over") != 0 or st.get("ansicht") != 14:
            # Spielende deutlich melden (Daniel 05.10. 00:44): wer hat wessen Lord getoetet? (PlayerData +8720)
            if st.get("over") == 1:
                getoetet = {sp: s32(peek(0x0115BDF8 + sp * 0x39F4 + 8720)[0]) for sp in (1, 2)}
                if getoetet[2] == SP:
                    schreib("SIEG bei Tick %d: Lord von Spieler 2 getoetet durch Spieler %d" % (st["t"], getoetet[2])); break
                if getoetet[1] > 0:
                    schreib("NIEDERLAGE bei Tick %d: unser Lord getoetet durch Spieler %d" % (st["t"], getoetet[1])); break
            schreib("ABBRUCH - Testbedingung weg: %s" % {k: st.get(k) for k in ("ansicht", "over", "pause", "t")}); break
        if letzter_tick is not None and st["t"] - letzter_tick > 400:
            schreib("WARNUNG: Runde dauerte %d Ticks (%d -> %d) - Waechter war so lange blind; Zeit der Runde davor: %s" % (
                st["t"] - letzter_tick, letzter_tick, st["t"], ", ".join("%s %.2f s" % kv for kv in sorted(diese_runde.items(), key=lambda kv: -kv[1]))))
        diese_runde.clear()
        stand = stand + 1 if st["t"] == letzter_tick else 0
        if stand >= 4:
            schreib("ABBRUCH - Spielzeit steht bei %d" % st["t"]); break
        letzter_tick = st["t"]
        eig = [g for g in G.values() if g["besitzer"] == SP]
        gebs = [(g["x"] + NACH_TYP.get(g["typ"], {"b": 2})["b"] // 2, g["y"] + NACH_TYP.get(g["typ"], {"b": 2})["b"] // 2)
                for g in eig if g["typ"] in EIGENE_ARTEN]
        tz = time.time()
        ereignis = w.schritt(L, gebs, ausgenommen=trupp.mitglieder if trupp else ()) if w is not None else []
        tz = uhr("waechter", tz)
        if trupp is not None:
            # Soeldnerlager (120 Gold) einmal bauen, dann Assassinen (Typ 73) anwerben bis zur Zahl; Mitglieder = alle eigenen 73er
            posten = [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 8]
            if not posten and (soeldner is None or runde % 10 == 0):
                # nicht am Lagerplatz (9i: Markt/Soeldnerlager belegten ihn - 14 Holzfaeller warteten Tick 4500-9035)
                soeldner = baue_schnell(8, BERGFRIED[0], BERGFRIED[1], 25)
                ereignis.append("Soeldnerlager gesetzt %s (Gold %d)" % (soeldner, st["gold"]))
            elif posten and st["gold"] >= 70 + GOLD_RESERVE and st["feuer"] >= 1 and (assassinen < 0 or geworben < assassinen):
                befehl({"werbe": {"typ": 73, "gebaeude": posten[0]}}, 1.0, bis="WERBE")
                geworben += 1
                if geworben % 5 == 0:
                    ereignis.append("%d Assassinen angeworben (Gold jetzt %d)" % (geworben, st["gold"]))
            if not [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 26] and runde % 20 == 2:
                ereignis.append("Markt gesetzt %s" % (baue_schnell(26, BERGFRIED[0], BERGFRIED[1], 25),))
            elif runde % 3 == 0:
                v = verkaufen(st)
                if v:
                    ereignis.append(v)
            tz = uhr("bauen_werben_verkauf", tz)
            trupp.aufnehmen([n for n, e in L.items() if e["besitzer"] == SP and e["typ"] == 73])
            # nur begehbare Plaetze (9g: Gebaeudemitten waren nicht begehbar - die Wartenden blieben im Schussfeld)
            erg = trupp.schritt(L, G, sichere_orte=[tuple(plan["lager_mitte"]), BERGFRIED])
            if isinstance(erg, tuple):          # Einzeln: Befehle der Runde gesammelt in EINEM Aufruf
                erg, liste = erg
                if liste:
                    sende({"befehle": [dict(b, player=1, id=neue_id()) for b in liste]}, 1.0,
                          bis="ANGRIFF" if any("angriff" in b for b in liste) else "HALTEN")
            ereignis += erg
            tz = uhr("assassinen", tz)
        # Feindlicher Lord: jede Runde mit Lebensverlust mitschreiben - wer steht bei ihm? (9i/9j: Sieg ohne Befehl auf ihn)
        for n, e in L.items():
            if e["typ"] == 55 and e["besitzer"] not in (0, SP):
                alt = feindlord.get(n)
                if alt is not None and e["leben"] < alt:
                    bei = {}
                    for m, u in L.items():
                        if u["besitzer"] == SP and max(abs(u["x"] - e["x"]), abs(u["y"] - e["y"])) <= 5:
                            bei[u["typ"]] = bei.get(u["typ"], 0) + 1
                    ereignis.append("MESSUNG Feindlord %d: leben %d -> %d bei (%d,%d), eigene in 5 Feldern %s" % (
                        n, alt, e["leben"], e["x"], e["y"], bei or "keine"))
                feindlord[n] = e["leben"]
        tz = time.time()
        ereignis += wirt.schritt(st, L, G)
        tz = uhr("wirtschaft", tz)
        bedarf = sum(ARBEITER_JE[t] * st.get("G%d" % t, 0) for t in ARBEITER_JE)
        if st["holz"] >= 5 + 3 * len(wirt.B_offen) and (bedarf > st["platz"] or (trupp is not None and st["feuer"] == 0 and st["platz"] - st["leute"] <= 2)):
            ereignis.append("Huette %s (Bedarf %d, Platz %d, Leute %d, Feuer %d)" % (baue_haus(), bedarf, st["platz"], st["leute"], st["feuer"]))
        zeile = "%5d | %3d %3d %3d | %3d %3d | %6.2f | %d/%d (%d) | %d %d | %s" % (
            st["t"], st["holz"], st["stein"], st["eisen"], st["apfel"], st["brot"], st["beliebt"] / 100.0, st["leute"],
            st["platz"], st["feuer"], st.get("T3", 0), st.get("T13", 0), "; ".join(ereignis) or "-")
        tz = uhr("haus_lager_zeile", tz)
        if ereignis or runde % 10 == 1:
            schreib(zeile)
        if runde % 10 == 0:
            schreib("ZEITEN nach %d Runden: %s" % (runde, ", ".join("%s %.2f s" % kv for kv in sorted(zeiten.items(), key=lambda kv: -kv[1]))))
    befehl({"pause": True}, 0.5)
    st, L, G = runde_lesen()
    schreib("Ende Phase 2 bei Tick %s nach %d Runden (%.1f s je Runde); Kornspeicher %d, Holzfaeller %d, Apfelplantagen %d%s" % (
        st.get("t"), runde, (time.time() - t0) / max(runde, 1), st.get("G19", 0), st.get("G3", 0), st.get("G32", 0),
        (("; Waechter: " + w.bericht()) if w else "") + (("; Angriff: " + trupp.bericht()) if trupp else "")))
    schreib("Wirtschaft: " + wirt.bericht())

def fingerabdruck(plan):
    """Alles, was die Eroeffnung bestimmt: Plan, Phase-1-Code, Gruppenteilung, Bauwerkzeug. Gleich -> gleicher Stand."""
    import hashlib, inspect, bauen, wirtschaft
    teile = [json.dumps({k: v for k, v in plan.items() if not k.startswith("_")}, sort_keys=True),
             inspect.getsource(phase1), inspect.getsource(wirtschaft.apfel_gruppen), inspect.getsource(bauen)]
    return hashlib.sha1("|".join(teile).encode("utf-8")).hexdigest()

def main():
    arg = dict(a.split("=") for a in sys.argv[1:])
    # Plan je Startstand (Daniel 05.10. 18:55: erst schauen, wo der Bergfried steht) - karten_holen.py + eroeffnung.py start=...
    datei = os.path.join(D, arg.get("plan", "eroeffnung_plan_M19.json"))
    plan = json.load(open(datei, encoding="utf-8")); plan["_datei"] = datei
    global BASIS, BERGFRIED
    BASIS = plan.get("spielstand", BASIS)
    BERGFRIED = tuple(plan.get("bergfried_eingang", BERGFRIED))
    import waechter
    waechter.BERGFRIED_EINGANG = BERGFRIED
    if arg.get("start"):
        print("Tick", lade_stand(arg["start"], mit_bild=False))
        befehl({"eigenerPlatz": SP}, 0.8)
    elif arg.get("nur_phase2", "nein") != "ja":
        # Eroeffnung nur neu bauen, wenn sie sich geaendert hat (Daniel 05.10. 00:18: "wenn du immer den gleichen
        # Speicherstand nutzt, musst du ihn nicht immer wieder erzeugen lassen")
        merk = os.path.join(D, "eroeffnung_stand.json")
        fp = fingerabdruck(plan)
        alt = json.load(open(merk, encoding="utf-8")) if os.path.exists(merk) else {}
        if alt.get("fingerabdruck") == fp and arg.get("neu", "nein") != "ja":
            schreib("Eroeffnung unveraendert (Fingerabdruck %s) - lade %s statt neu zu bauen" % (fp[:10], alt["spielstand"]))
            print("Tick", lade_stand(alt["spielstand"], mit_bild=False))
            befehl({"eigenerPlatz": SP}, 0.8)
        else:
            name = phase1(plan)
            json.dump({"fingerabdruck": fp, "spielstand": name, "erstellt": time.strftime("%d.%m.%Y %H:%M")},
                      open(merk, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    try:
        phase2(plan, int(arg.get("minuten", 10)), int(arg.get("tempo", 40)), arg.get("waechter", "nein") == "ja",
               int(arg["bis_tick"]) if arg.get("bis_tick") else None, int(arg.get("assassinen", 0)))
    except RuntimeError as e:
        # Modulfehler (befehl.pruefe): Spiel anhalten, damit der Zustand fuer die Ursachensuche stehen bleibt
        import befehl as befehlskanal
        befehlskanal.STRENG = False
        befehl({"pause": True}, 0.8)
        print("ABBRUCH -", e, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    import befehl as befehlskanal
    befehlskanal.belege()
    try:
        main()
    finally:
        befehlskanal.freigeben()
