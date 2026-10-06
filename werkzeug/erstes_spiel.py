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
Aufruf:  python erstes_spiel.py [minuten=10] [tempo=40] [nur_phase2=nein] [waechter=nein] [start=<Spielstand>] [bis_tick=N] [assassinen=N; -1 = ohne Grenze] [trainingsstand=<Name>] [trainingsstand_ab=40]
         Tests mit Hoechstgeschwindigkeit (Daniel 22:55): tempo=1000 bis_tick=...
Stop von aussen: Datei werkzeug/STOP anlegen.
"""
import json, math, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import lade_stand, befehl, peek
from steuerkarte import laufe, tick, spielzustand
from bauen import NACH_TYP, gebaeude_von, vorrat, baue_irgendwo
from waechter import Waechter, lies_lagebild, lies_gebaeude
from assassinen import Angriffstrupp, Einzeln
from befehl import sende, neue_id, ABZUG, INSTANZ
from wirtschaft import Wirtschaft, apfel_gruppen
from ertragsplaner import Ertragsplaner

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
SP = 1
PD = 0x0115BDF8 + SP * 0x39F4
ARBEITER_JE = {3: 1, 32: 1, 30: 1, 31: 1, 33: 1, 20: 3, 4: 1, 5: 2, 7: 1, 6: 1, 16: 1, 13: 1}   # Betrieb -> Arbeiter (Steinbruch 3, Mine 2: Annahme)
LAGERWAREN = ("holz", "hopfen", "stein", "eisen", "pech", "weizen", "mehl")
LOG = os.path.join(D, "erstes_spiel_log%s.txt" % ("" if INSTANZ == 1 else INSTANZ))   # je Instanz ein Protokoll

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def schreib(text):
    print(text)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + text + "\n")

def partie_pruefen():
    """Fehlerkontrolle (Daniel 04.10.) OHNE Tempo zu aendern: laeuft das Gefecht, ist der Mensch eingetragen, gameOver 0?
    (plantagen_lauf.vorab() stellt Tempo 1000 - in einer Live-Partie ein sichtbarer Sprung, Daniel 22:54.)"""
    zustand = {"Ansicht": peek(0x01FE7D1C)[0], "gameOver": peek(0x0117D500)[0],
               "Mensch": s32(peek(0x0191DE10 + SP * 4)[0]), "Platz": peek(0x01A275DC)[0]}
    if zustand != {"Ansicht": 14, "gameOver": 0, "Mensch": 1, "Platz": SP}:
        raise SystemExit("TESTBEDINGUNG FEHLT: %s" % zustand)
    return zustand

def warte_bis(bedingung, text, sekunden=90, pflicht=True):
    """Bei LAUFENDEM Spiel warten, bis bedingung() wahr ist (keine Tick-Pause - Daniel 22:54 "ohne komische Pausen").
    pflicht=False: bei Zeitablauf None statt Abbruch."""
    ende = time.time() + sekunden
    while time.time() < ende:
        if bedingung():
            return tick()
        time.sleep(0.02)        # unter einem Tick (Daniel 23:01: keine festen Wartezeiten)
    if not pflicht:
        return None
    raise SystemExit("ZEIT UM beim Warten auf: %s (Tick %s)" % (text, tick()))

def lords():
    return [tuple(int(v) for v in m) for m in re.findall(r"LORD \d+: Spieler (\d+) bei \((\d+),(\d+)\)",
                                                          " ".join(befehl({"lords": True}, 1.0, bis="LORDS")))]

SAAT_DATEI = os.path.join(D, "saat_liga.json")
SAAT_FELDER = ("karte", "partie", "wert1", "wert2", "zaehler1", "zaehler2")
LIGA_GEFECHT = {"eigenesGefecht": True, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 1, "ausgleich": 3,
                "startliste": [0, 1, 246, 246, 246, 246, 246, 246]}   # aus dem M19-Stand gelesen: Mensch Platz 0, Rotkaeppchen 1

def saat_laden(datei=SAAT_DATEI):
    """Feste Saat (Daniel 23:13): gleiche Zufallswerte bei jedem Start -> gleiche Partie, solange unser Lenker gleich spielt."""
    return json.load(open(datei, encoding="utf-8")) if os.path.exists(datei) else None

def saat_lesen(zeilen):
    """Die SAAT-Zeile des Moduls (jeder Gefecht-Start schreibt sie) als dict, sonst None."""
    m = re.search(r"SAAT " + " ".join(f + r"=(-?\d+)" for f in SAAT_FELDER), " ".join(zeilen))
    return dict(zip(SAAT_FELDER, map(int, m.groups()))) if m else None

def saat_merken(gelesen, datei=SAAT_DATEI):
    """Die erste Partie legt die Saat fest; die Karten-Saat liest der Start nicht mit - die Partie-Saat dient fuer beide."""
    saat = dict(gelesen, karte=gelesen["partie"])
    json.dump(saat, open(datei, "w", encoding="utf-8"), indent=1)
    return saat

LEERE_KI = False      # leere_ki=ja: Rotkaeppchen (Spieler 2) bekommt jede Runde alle Waren und Gold auf 0 (Modul leereKI)

def gefecht_starten(tempo):
    """Frisches Liga-Gefecht ab Tick 0 mit festem Tempo und fester Saat, ohne Pausen (Daniel 22:52-23:13). Wartet bei
    laufendem Spiel auf beide Lords und prueft Startplatz + Testbedingung. Gibt den Tick, ab dem beide Lords da sind.
    Tempo VOR dem Start (live_1: das Gefecht startete mit altem Tempo, erst bei Tick 3.250 kam unser erster Befehl)."""
    import befehl as kanal
    from serie import zuruecksetzen       # Endbildschirm/laufende Partie -> Hauptmenue (bremse_1: "Menue 41" allein beendete die alte Partie nicht)
    schreib("Zuruecksetzen: %s" % zuruecksetzen())
    befehl({"tempo": tempo}, 1.0, bis="TEMPO")
    kanal.sende({"player": SP, "pause": False}, 0.5)
    if LEERE_KI:
        # Daniel 06.10.: Testpartie gegen eine leere KI (ohne Gegner endet das Gefecht sofort als Sieg, gemessen).
        # Als Befehlsliste: im Hauptmenue reicht der UCP-Haken (villagestudio init.lua) nur bestimmte Befehle und Listen
        # an die Logik durch, einen einzelnen leereKI-Befehl verwirft er still (gemessen 06.10.: keine Quittung).
        z = kanal.sende({"befehle": [{"player": SP, "id": kanal.neue_id(), "leereKI": [2]}]}, 3.0, bis="LEERE KI")
        if not any("LEERE KI" in x for x in z):
            raise SystemExit("LEERE KI nicht bestaetigt: %s" % z[-3:])
        schreib("LEERE KI: Spieler 2 ohne Waren und Gold (jede Runde)")
    else:
        # der Modulzustand ueberdauert das Gefecht - sonst haette die naechste normale Partie eine leere Rotkaeppchen
        kanal.sende({"befehle": [{"player": SP, "id": kanal.neue_id(), "leereKI": False}]}, 3.0, bis="LEERE KI")
    saat = saat_laden()
    zeilen = kanal.sende(dict(LIGA_GEFECHT, **({"saat": saat} if saat else {})), 4, bis="LaunchSkirmishGame zurueck")
    gelesen = saat_lesen(zeilen)
    if saat:
        schreib("SAAT fest aus %s (Modul meldet %s)" % (os.path.basename(SAAT_DATEI), gelesen))
    elif gelesen:
        schreib("SAAT neu festgelegt: %s -> %s" % (saat_merken(gelesen), os.path.basename(SAAT_DATEI)))
    else:
        schreib("SAAT nicht gelesen: %s" % zeilen[-3:])
    befehl({"tempo": tempo}, 1.0, bis="TEMPO")
    t_lords = warte_bis(lambda: len(lords()) >= 2, "beide Lords")
    zustand = partie_pruefen()
    eigener = [(x, y) for sp, x, y in lords() if sp == SP]
    if not eigener or max(abs(eigener[0][0] - BERGFRIED[0]), abs(eigener[0][1] - BERGFRIED[1])) > 8:
        raise SystemExit("STARTPLATZ FALSCH: unser Lord bei %s, Plan erwartet den Bergfried-Eingang %s" % (eigener, BERGFRIED))
    schreib("Partie laeuft seit Tick %d: Lords da, unser Lord bei %s, %s" % (t_lords, eigener[0], zustand))
    return t_lords

def phase1(plan, tempo, mit_posten=True):
    """Neue Partie ab Tick 0 (Daniel 05.10. 22:52: "warum laesst du der KI so einen Vorlauf? starte das Spiel bei Tick 0",
    "Neustart komplett"; 22:54: "ohne komische Pausen, ein Spiel, das live mit gleicher Geschwindigkeit laeuft").
    Vorher: jede Partie lud den Startstand "M19 Liga Start Grumpy T600" - Rotkaeppchen hatte 600 Ticks Vorsprung, dazu
    Tick-Pausen in der Eroeffnung und ein Speichern. Jetzt: gefecht_starten(), dann die Eroeffnung bei laufendem Spiel."""
    schreib("== Phase 1: neue Partie ab Tick 0, Tempo %d durchgehend, ohne Pausen (Plan %s)" % (tempo, os.path.basename(plan["_datei"])))
    gefecht_starten(tempo)
    from bauen import baue_viele
    # Daniel 22:59: "immer noch zu langsam, und dann ploeppt er ploetzlich seine Wirtschaft hin". Gemessen live_2: Markt
    # erst 200 Ticks nach dem Kornspeicher (Platzsuche), Posten + Assassine erst bei 976, die Wirtschaft (21 Bauten) auf
    # einen Schlag bei 2.504 - jede Abfrage wartete fest 1 s (= 40 Ticks bei Tempo 40), dazu Kontrolle je Gebaeudeart.
    # Jetzt: ALLES, was nur Holz kostet, in EINEM Befehl gleich beim Start (Kornspeicher, Markt, Holzfaeller, Steinbruch,
    # Ochsenjoch, Huetten) an festen Plaetzen; sobald das Essen da ist verkaufen, Posten, Assassine; dann die Apfelplantagen
    # (die kosten Gold). Kontrolle einmal, waehrend wir sowieso aufs Essen warten.
    A, B = apfel_gruppen(plan["aepfel"])
    if V14 and HOLZ_SPAM:
        # E3 (Daniel 22:57: "als Spieler erstmal alle Baeume vollspammen im Umkreis vom Vorratslager"): das Startholz zuerst in
        # Holzfaeller - Steinbrueche/Joche erst, wenn HOLZ_SPAM Holzfaeller stehen (Phase 2)
        holz_bauten = [(19, tuple(plan["kornspeicher"])), (26, MARKT)] + [(3, tuple(p)) for p in v16_holzfaeller(plan)]
    elif V14:
        # Daniel 22:05: "zwei Steinbrueche direkt neben dem Vorratslager, sofort gebaut, wenn die Ressourcen da sind" -
        # vor den Holzfaellern (die Reihenfolge entscheidet, was beim ersten Holz (30 bei Tick 120) noch geht)
        holz_bauten = [(19, tuple(plan["kornspeicher"])), (26, MARKT)] + [(20, q) for q in V14["brueche"]] + \
                      ([] if JOCH_NACH_STEIN else [(4, j) for j in V14["joche"]]) + \
                      [(3, tuple(p)) for p in (v16_holzfaeller(plan) if HF_VORAB is None else v16_holzfaeller(plan)[:HF_VORAB])]
    else:
        holz_bauten = [(19, tuple(plan["kornspeicher"])), (26, MARKT)] + [(3, tuple(p)) for p in plan["holzfaeller"]]
    if plan.get("stein") and not V14:
        holz_bauten += [(20, tuple(plan["stein"]["steinbruch"])), (4, tuple(plan["stein"]["ochsen"]))]
    holz_bauten += [(1, tuple(p)) for p in plan["huetten"]]
    t_bau = tick()
    g1, f1 = baue_viele([(typ, x, y) for typ, (x, y) in holz_bauten], SP, live=True)
    schreib("ERSTE BAUBEFEHLE bei Tick %d: %d von %d Holz-Bauten stehen bei Tick %d (Kornspeicher, Markt, Holzfaeller, "
            "Steinbruch, Ochsenjoch, Huetten); nicht gebaut: %s" % (t_bau, len(g1), len(holz_bauten), tick(),
            [(NACH_TYP[t]["name"], x, y) for t, x, y in f1] or "keine"))
    if any(t == 26 for t, _, _ in f1):                # Markt-Platz belegt (z. B. Einheit drauf): Platz suchen
        schreib("Markt am festen Platz nicht moeglich - gesucht: %s" % (baue_schnell(26, BERGFRIED[0], BERGFRIED[1], 25),))
    rest = [r for r in f1 if r[0] != 26]
    # live_3: sofort beim ersten Essen verkauft - es kommt nach und nach an, verkauft wurde 1 Los Kaese (30 Gold), dann
    # Abbruch "Gold aus dem Verkauf". Jetzt: warten, bis alle 4 Sorten da sind; reicht das Gold nicht, nochmal verkaufen.
    t_essen = warte_bis(lambda: all(vorrat(SP).get(k, 0) > 0 for k in NAHRUNG_PREIS), "alle 4 Sorten Start-Nahrung")
    lose = {}
    for versuch in range(3):
        vk = vorrat(SP)
        for w, k in nahrung_auf_kante({k: vk.get(k, 0) for k in NAHRUNG_PREIS}, 15).items():
            lose[w] = lose.get(w, 0) + k
        # ohne Posten (Streitkolben) reicht Gold fuer die 3 A-Plantagen (3 x 15) - Daniel 21:48 "warum wartet er am Anfang?":
        # v9 wartete bis Tick ~708 auf 190 Gold (Posten + Assassine), A erst danach -> gut 500 Ticks verloren
        if warte_bis(lambda: vorrat(SP)["gold"] >= (190 if mit_posten else 45), "Gold fuer Posten + Assassine" if mit_posten
                     else "Gold fuer die A-Plantagen", 5, pflicht=False):
            break
    schreib("VERKAUFT bis Tick %d: %s Lose, Gold %d" % (tick(), lose, vorrat(SP)["gold"]))
    # Daniel 23:41: "Seasoning am Anfang ist eine gute Investition, da Nahrung fuer Beliebtheit und Verkauf unersetzlich
    # ist". gewinn_3: A-Plantagen erst nach Posten + Assassine versucht (Tick 783, Gold 5 - alle gescheitert), erste A bei
    # 1.315, letzte nach 3.865; ohne eigenes Essen fiel die Beliebtheit 98 -> 58. Jetzt: Posten und A-Plantagen in EINEM
    # Befehl, sobald das Verkaufsgold da ist (Posten zuerst in der Liste, 120 + 3 x 15 von ~195 Gold).
    gp, fp = baue_viele(([(8, POSTEN[0], POSTEN[1])] if mit_posten else []) + [(32, x, y) for (x, y) in A], SP, live=True)
    posten = (POSTEN if any(r[0] == 8 for r in gp) else baue_schnell(8, BERGFRIED[0], BERGFRIED[1], 25)) if mit_posten else None
    schreib("SEASONING FRUEH: %d von %d A-Plantagen mit dem Posten bei Tick %d, Gold jetzt %d" % (
        sum(1 for r in gp if r[0] == 32), len(A), tick(), vorrat(SP)["gold"]))
    if mit_posten:
        warte_bis(lambda: gebaeude_von(SP, 8), "Soeldnerposten", 20)
    geworben = 0
    nr_posten = [n for n, _, _ in gebaeude_von(SP, 8)]
    while nr_posten and vorrat(SP)["gold"] >= 70 and s32(peek(PD + 136)[0]) >= 1:
        vorher = vorrat(SP)["gold"]
        befehl({"werbe": {"typ": 73, "gebaeude": nr_posten[0]}}, 1.0, bis="WERBE")
        geworben += 1
        warte_bis(lambda: vorrat(SP)["gold"] < vorher, "Gold fuer den Assassinen abgebucht", 10)
    v0 = vorrat(SP)
    schreib("RAID ZUERST: Nahrung da bei Tick %d, %s verkauft (Lose zu 5); Soeldnerposten %s; %d Assassinen angeworben "
            "(freie Leute am Feuer jetzt %d) -> Gold %d, Nahrung uebrig %s, Tick %d" % (t_essen, lose, posten, geworben,
            s32(peek(PD + 136)[0]), v0["gold"], {k: v0.get(k, 0) for k in NAHRUNG_PREIS if v0.get(k, 0)}, tick()))
    # Apfelplantagen (Gold) und was beim ersten Befehl nicht ging - einmal nachholen; den Rest setzen Planer/Wirtschaft
    if V14:
        # erst die A-Plantagen (Seasoning), dann Steinbrueche/Joche, dann der Rest - in der Reihenfolge von holz_bauten
        nach = [r for r in fp if r[0] == 32] + sorted(rest, key=lambda r: [t for t, _ in holz_bauten].index(r[0]))
    else:
        nach = rest + [r for r in fp if r[0] == 32]
    g2, f2 = baue_viele(nach, SP, live=True) if nach else ([], [])
    if not V14:
        # Steinbruch/Ochsenjoch am festen Platz gescheitert -> im Umkreis 8 weitersuchen (v9: (80,271) nie gebaut)
        # v14: NICHT - (81,268) aus dieser Suche nahm beiden festen Plaetzen den Boden; die Pflicht in Phase 2 baut genau
        for typ, x, y in [r for r in f2 if r[0] in (20, 4)]:
            schreib("Ersatzplatz %s bei (%d,%d): %s" % (NACH_TYP[typ]["name"], x, y, baue_schnell(typ, x, y, 8)))
        f2 = [r for r in f2 if r[0] not in (20, 4)]
    v1 = vorrat(SP)
    schreib("NACHGEHOLT bei Tick %d: %d von %d (Apfelplantagen A + Rest); nicht gebaut: %s; Holz %d, Gold %d" % (
        tick(), len(g2), len(nach), [(NACH_TYP[t]["name"], x, y) for t, x, y in f2] or "keine", v1["holz"], v1["gold"]))
    schreib("Apfelplantagen A %d, B %d spaeter %s; altes Lager bleibt mit %s" % (
        len(A), len(B), B, {k: v1[k] for k in LAGERWAREN if v1.get(k)}))

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

RESERVIERT = []      # 07.10. (Lauf 29): B-Plantagen-Flaechen (x0, y0, x1, y1 einschliesslich, Anker) - kein anderer Bau darf hinein
BUCH = None          # Auftragsbuch (phase2): jeder Bau wird vorher gegen den Bestand geprueft und danach bestaetigt
_KOSTEN_SPIEL = {}

def kosten_spiel(typ):
    if typ not in _KOSTEN_SPIEL:
        from bauen import kosten
        _KOSTEN_SPIEL[typ] = kosten(typ)
    return _KOSTEN_SPIEL[typ]

GROESSE_IST = {10: 6, 20: 6, 21: 3, 4: 2}     # tatsaechliche Flaeche: Lagerplatz = 4 Teile 3x3 (L6), Steinhaufen ~3x3

def platz_sauber(typ, frei, eigen=None):
    """Daniel 23:34: (1) "der Ochsenjoch-Arbeiter ist vom Vorratslager geblockt ... ein Abstand von eins wuerde helfen";
    (2) "ein Ochsenjoch, das gebaut wurde, hat einen Mitarbeiter ueberbaut - worst case".
    Aus den Plaetzen der Platzsuche (naechste zuerst) den ersten nehmen, auf dem keine eigene Einheit steht und - fuer Lager
    und Joche - mit 1 Feld Gang zu Steinbruch, Steinhaufen, Joch und Lager (je nach Art). Gibt die Liste gefiltert zurueck."""
    try:
        L = lies_lagebild(neu_holen=False)
        G = lies_gebaeude()
    except Exception:
        return frei
    b = GROESSE_IST.get(typ, NACH_TYP[typ]["b"])
    # Daniel 23:35: "nicht nur gerade steht, sondern zum Zeitpunkt des Bauens stehen wird" - jede eigene Einheit mit ihrem
    # ganzen Weg bis zum Laufziel (laufx/laufy aus dem Lagebild), Feld fuer Feld auf der Geraden
    leute = []
    for e in L.values():
        if e["besitzer"] != SP:
            continue
        x0, y0 = e["x"], e["y"]
        x1, y1 = (e["laufx"], e["laufy"]) if e.get("laufx", 0) > 0 and e.get("laufy", 0) > 0 else (x0, y0)
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        leute += [(x0 + round((x1 - x0) * i / float(n)), y0 + round((y1 - y0) * i / float(n))) for i in range(n + 1)]
    gang_zu = {10: (20, 21, 4), 4: (10, 20)}.get(typ, ())
    hindernis = [(gg["x"], gg["y"], GROESSE_IST.get(gg["typ"], NACH_TYP.get(gg["typ"], {"b": 3})["b"]))
                 for gg in G.values() if gg["besitzer"] == SP and gg["typ"] in gang_zu]
    gut = []
    for (px, py) in frei:
        if any(px <= ux < px + b and py <= uy < py + b for ux, uy in leute):
            continue
        # Lauf 29: ein Holzfaeller (kausal) stand bei (89,236) auf dem Platz der B-Plantage oben -> B oben wich auf B Mitte aus,
        # B Mitte auf B unten, B unten fand 43-mal keinen Platz. Reservierte B-Flaechen sind tabu, ausser fuer ihr eigenes B
        # fremde Bauten mit 1 Feld Rand; die B untereinander nur mit ihrer Flaeche (sie beruehren sich an den Ecken)
        rand = 0 if eigen is not None else 1
        if any(px <= r[2] + rand and px + b - 1 >= r[0] - rand and py <= r[3] + rand and py + b - 1 >= r[1] - rand
               for r, anker in RESERVIERT if anker != eigen):
            continue
        if any(px - 1 <= hx + hb - 1 and hx <= px + b and py - 1 <= hy + hb - 1 and hy <= py + b for hx, hy, hb in hindernis):
            continue
        gut.append((px, py))
    return gut

def baue_schnell(typ, x, y, r, mapper=None, zweck=""):
    """Im laufenden Spiel: Platz suchen und bauen OHNE zu blockieren (04.10.: das alte Bauwerkzeug wartete fest und
    auf einen genauen Tick - bei Tempo 1000 hing die Schleife ~20.000 Ticks, der Waechter kam nie dran).
    Ob es steht, prueft das Auftragsbuch in den naechsten Runden (Gebaeudeliste). Daniel 22:08: "wie kann es sein, dass
    irgendein Gebaeude ohne Pruefung gebaut wird?" - vorher kam der Platz zurueck, auch wenn das Holz fehlte (Serie:
    "Ersatzplatz Steinbruch (80,271)" bei 8 Holz). Jetzt: reicht der Bestand nicht, wird gar nicht gesendet."""
    g = NACH_TYP[typ]
    if BUCH is not None:
        k, v = kosten_spiel(typ), vorrat(SP)
        fehlt = ["%s %d" % (w, k[w] - v.get(w, 0)) for w in ("holz", "stein", "gold") if k.get(w, 0) > v.get(w, 0)]
        if fehlt:
            BUCH.ablehnen(typ, (x, y), "fehlt " + ", ".join(fehlt))
            return None
    z = " ".join(befehl({"platzsuche": {"spieler": SP, "mapper": g["mapper"], "groesse": g["b"], "x": x, "y": y, "r": r,
                                        "max": 12 if BUCH is not None else 1}}, 1.0, bis="PLATZSUCHE"))
    frei = [tuple(map(int, p)) for p in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    if BUCH is not None and frei:
        frei = platz_sauber(typ, frei, eigen=(x, y) if zweck == "B" else None)
    if not frei:
        if BUCH is not None:
            BUCH.ablehnen(typ, (x, y), "kein Platz im Umkreis %d" % r)
        return None
    befehl({"baue": {"mapper": g["mapper"], "x": frei[0][0], "y": frei[0][1], "groesse": g["b"], "richtung": 0}}, 1.0, bis="BAUE")
    if BUCH is not None:
        BUCH.vormerken(typ, frei[0], zweck)
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

ROHSTOFFE = os.path.join(ABZUG, "rohstoffe.txt")
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

ESSEN_RESERVE, HOLZ_RESERVE, STEIN_RESERVE, GOLD_RESERVE = 60, 30, 10, 30   # Daniel 23:06: alles ueber dem Minimum verkaufen
BASIS = "M19 Liga Start Grumpy T600"     # Liga-Bedingung: 0 Gold, 150 Holz (Daniel 05.10. 00:55; gemessen 18:38)
MARKT, POSTEN = (145, 269), (145, 274)   # feste Plaetze, gemessen live_2 (dort gebaut); belegt -> Platzsuche
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

def verkaufen(st, stein_reserve=None, messer=None, holz_verkaufen=False, eisen_reserve=0):
    """Je Runde hoechstens ein Verkauf je Ware (Spielbefehl 38, verkaufen=1). Gibt Text oder None.
    stein_reserve: Bedarf der naechsten geplanten Eisenmine (Daniel 05.10. 19:44: Stein bis darauf verkaufen);
    messer: Ertragsmesser - bekommt jedes verkaufte Los (fuer die Buchfuehrung Zugang = Bestand + Verkauft + Verbaut)."""
    teile = []
    # Holz nur, solange Gold das Anwerben bremst (holz_verkaufen); sonst geht der Ueberschuss in Holzfaeller. Daniel
    # 06.10.: erst "statt Holz verkaufen mehr Holzfaeller", nach holz_partie_1/2 (20. Assassine ~4.000 Ticks spaeter,
    # kein Sieg) 19:33 "ja, vorerst" - gegen mehrere Gegner braucht es spaeter stabiles Wachstum statt Verkauf.
    holz = (("holz", HOLZ_RESERVE),) if holz_verkaufen else ()
    for ware, reserve in holz + (("stein", STEIN_RESERVE if stein_reserve is None else stein_reserve), ("eisen", eisen_reserve),
                          ("pech", 0), ("weizen", 0), ("hopfen", 0), ("mehl", 0)):
        if st.get(ware, 0) > reserve + 4:
            befehl({"spielbefehl": {"nr": 38, "werte": [1, WAREN_NR[ware]]}}, 1.0, bis="SPIELBEFEHL"); teile.append(ware)
            if messer is not None:
                messer.verkauft(ware)
    lose = nahrung_auf_kante({k: st.get(k, 0) for k in NAHRUNG_PREIS}, nahrung_puffer(st.get("leute", 10)))
    if messer is not None:
        for w, k in lose.items():
            messer.verkauft(w, k)
    teile += ["%s x%d" % (w, k) for w, k in lose.items()]
    return ("verkauft: " + ",".join(teile)) if teile else None

KAEMPFER_GOLD = 20          # Anwerben (Liga goldCost)
FRUEH_TICK = 2500           # bis hierhin muessen Steinbruch, Lagerumzug und B-Seasoning stehen (Fruehabbruch)
BASIS_LAGER = (145, 264)    # Startlager am Bergfried (Teil 6, gemessen) - steht dort noch ein Teil, ist das Lager nicht umgezogen
LOS_PREIS = {21: 300, 23: 160}   # 5 Keulen / 5 Lederharnische am Markt (gemessen 06.10. Messpartie 8)

# v14 (Daniel 22:04 "ja bau v14", 22:05 "zwei Steinbrueche direkt neben dem Vorratslager, sofort gebaut"). Plaetze aus den
# Platzkarten des Spiels (start_M19_platz_*.txt, Rechnung scratchpad steinplatz.py/lederplatz.py 22:07-22:16):
#  - auf das Steinfeld passen GENAU zwei Steinbrueche (Anker x 77-81, y 265-271): (80,265) + (80,271). Der Planer setzte
#    in v12/v13 einen auf (81,268) - danach war fuer keinen zweiten mehr Platz.
#  - Lager 5x5 bei (87,268): 1 Feld Gang zu beiden Steinbruechen (B4); Erweiterung nach Osten (93,268), (98,268) frei.
#  - Joche 2x2 noerdlich/suedlich vom Lager, 1 Feld Abstand.
#  - Leder (Plan_Streitkolben Bewertungskette, Daniel 22:04): Hof-Boden gibt es am Lager nicht (im Umkreis 30 kein
#    Platz); der Gerber laeuft nur Hof <-> Gerberei <-> Waffenlager, das Lager braucht er nicht. Zwei Hoefe 8 Felder
#    auseinander, Gerberei dazwischen (2 Felder zu beiden), Waffenlager 1 Feld neben der Gerberei.
V14 = None
HF_VORAB = None          # v15: so viele Holzfaeller aus dem Eroeffnungsplan in Phase 1, der Rest erst nach den Steinbruechen
UMZUG = "nachb"          # E1/E2 (06.10. 22:55): "frueh" = gleich nach Phase 1, "nachb" = wenn B steht, "nein" = Lager bleibt am Bergfried
EXPERIMENT = False       # Versuch: keine Tempo-Regel gegen die Bestzeit (er soll die erste Lieferung erleben), nur harte Fehler brechen ab
HF_MAX = None            # v16: Holzfaeller nur bis so viele Felder vom neuen Lager (L9: weit weg ~3, nah ~11 Holz je 1.000)
JE_ARBEITER = False      # v16: Planer bewertet Gewinn je Arbeiter (Bauern sind der Engpass, L7)
HUETTEN_JE_BAUM = None   # v17: bis zu so viele Holzfaeller je Baum (Daniel 22:57); None = alte Regel (einer je Baum, 7 Felder Sperre)
HOLZ_KAUFEN = False      # v17: Holz kaufen, wenn >= 4 Bauern untaetig sind und Holz fehlt
HOLZ_SPAM = 0            # E3: erst so viele Holzfaeller rund ums Lager, dann Steinbrueche und Leder
STEIN_MAX = False        # E4: Steinbrueche erst nach der ersten Holzlieferung, dann alle (2 am Lager + 3 am zweiten Steinfeld)
JOCH_NACH_STEIN = False  # v18: Joch erst, wenn der Steinhaufen seines Steinbruchs Stein hat (Daniel 23:10, Punkte 4+5)
STEIN_PARALLEL = False   # v18: Steinbrueche sofort (vor allem), Holzfaeller-Spam mit dem Rest - nicht erst nach dem Spam
HUETTEN_VORAUS = False   # v18: Huetten vor dem Bedarf (Daniel 23:10 Punkt 3: Bauern brauchen Spawnzeit)
VOLLBESCHAEFTIGUNG = False   # Lernkreis: jeder Bauer am Feuer bekommt sofort einen Arbeitsplatz (Lernlauf 1: 93 % untaetig)
ENTSCHEIDER = "regeln"   # "kausal" (Daniel 23:27 "dynamische Antworten fuer alles"): Kausalmodell entscheidet Betriebe + Huetten
B_VERSATZ = None         # Lernkreis: B-Plantagen so viele Ticks nach "alle A stehen" (None = erst bei A-Reife)
STEUER_RUNTER = 95       # Lernkreis: Steuer senken unter dieser Beliebtheit (Daniel 06.10. 23:53: Steuern als Geldquelle)
BEV_ZIEL = 0             # Lernkreis: Huetten bauen, bis so viele Wohnplaetze stehen (0 = aus; Daniel 07.10. 00:17 "60-70")
EINZELKAUF = False       # Lernkreis: fehlende 1-4 Waffen einzeln gutschreiben statt 5er kaufen (Daniel 01:35)
AUFLOESEN = False        # Lernkreis: eigene Soldaten (ausser Streitkolbenkaempfern) zu Bauern aufloesen (Daniel 01:29)
SCHUB = False            # Lernkreis: die ersten 5 Kaempfer schon waehrend der Kasse anwerben (Lauf 45/46: Verlust im Endspiel)
KASSE_STUFE = 11         # Lernkreis: Steuerstufe der Kasse (11 = -40, 9 = -20, 7 = -11; Liga 4,00 / 2,00 / 1,30 Gold je Kopf)
PENNER = 20              # Lernkreis: Wachstums-Holzfaeller erst ab so vielen Wartenden am Feuer (hoechstens 24 moeglich)
KASSE_GRENZE = 50        # Lernkreis: Kasse nur, solange die Beliebtheit darueber liegt (Lauf 26: bei 0 Massen-Wegzug)
KASSE = "nein"           # Lernkreis: "steuer" / "steuer_essen" - ab Ziel-Bevoelkerung (oder wenn nichts mehr lohnt) Stufe 11 bis zum Ende
STEUER_ENDE = "nein"     # Lernkreis: Hoechststeuer (Stufe 11), sobald sich nichts mehr amortisiert (Daniel 07.10. 00:0x)
ZIEL_TICK = 9400         # Zieltick, bis zu dem das Kausalmodell Ertraege rechnet (unter 1 Jahr = 9.600, Endspiel davor)
                         # 07.10.: Lernkreis setzt ihn auf das gemessene Ende der besten Strategie; gilt auch fuer den Planer
                         # (vorher Planer bis bis_tick=13.000, Kausal bis 9.400 - zwei Zeitraeume fuer dieselbe Frage)

def v16_holzfaeller(plan):
    """Plan-Holzfaeller nach Abstand zum neuen Lager, ohne die jenseits von HF_MAX."""
    if not V14:
        return list(plan["holzfaeller"])
    lg = BASIS_LAGER if UMZUG == "nein" else V14_PLAN["lager"]      # E2: Lager bleibt am Bergfried
    m = (lg[0] + 3, lg[1] + 3)
    ab = lambda p: max(abs(p[0] + 1 - m[0]), abs(p[1] + 1 - m[1]))
    return [p for p in sorted(plan["holzfaeller"], key=ab) if HF_MAX is None or ab(p) <= HF_MAX]
STEIN_ZUERST = False     # v15: Planer baut nichts mit Arbeitern, bis beide Steinbrueche + Joche besetzt sind
# Lager (89,270) statt (87,268) (v15, 22:45): die Steinbrueche legen ihre Steinhaufen (Typ 21) selbst daneben - gemessen
# bei (87,267) und (87,276); (87,268) war damit belegt, die Platzkarte von Tick 0 kannte die Haufen nicht. (89,270) ist
# laut Platzkarte bei Tick 1.650 frei und liegt 1 Feld neben beiden Haufen (kurzer Ochsenweg).
V14_PLAN = {"brueche": [(80, 265), (80, 271)], "joche": [(87, 265), (87, 274)], "lager": (89, 270),
            "erweiterung": [(89, 265), (94, 265)], "hoefe": [(172, 297), (181, 279)], "gerberei": (175, 291),
            "waffenlager": (176, 286)}
V14_GROESSE = {20: 6, 4: 2, 10: 5, 33: 10, 16: 4, 11: 4}
V14_STEIN_BIS, V14_LAGER_BIS, V14_UMZUG_AB = 500, 800, 650   # Fruehabbruch-Marken; Startholz ist ab ~650 komplett da

def v14_sperrflaechen():
    """Rechtecke (x0, y0, x1, y1), die Planer und Wirtschaft nicht bebauen duerfen (1 Feld Rand)."""
    p, r = V14_PLAN, []
    for typ, orte in ((20, p["brueche"]), (4, p["joche"]), (10, [p["lager"]] + p["erweiterung"]), (33, p["hoefe"]),
                      (16, [p["gerberei"]]), (11, [p["waffenlager"]])):
        b = V14_GROESSE[typ]
        r += [(x - 1, y - 1, x + b, y + b) for x, y in orte]
    if STEIN_MAX:
        r += [(x - 1, y - 1, x + 9, y + 6) for x, y in E4_BRUECHE]     # Steinbruch 6x6 + Haufen/Joch rechts daneben
    return r

def steht_bei(G, typ, ort, r=1):
    return [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == typ and max(abs(g["x"] - ort[0]), abs(g["y"] - ort[1])) <= r]

def wohnraum_fehlt(st, G):
    """Daniel 23:21 "du baust Haeuser ohne Ende ohne Grund": eine Huette bringt nur etwas, wenn es fuer den neuen Bauern
    Arbeit gibt. Bedarf = offene Arbeitsplaetze - Bauern am Feuer (die koennen sofort arbeiten). Huette, wenn Bedarf + 2
    (Spawnzeit, Daniel 23:10 Punkt 3) groesser ist als der freie Wohnraum. Vorher: "weniger als 6 frei" -> Schleife aus
    Huetten, untaetigen Bauern und neuen Huetten."""
    offene = sum(max(0, ARBEITER_JE.get(g["typ"], 0) - (BUCH.hat.get(n, 0) if BUCH is not None else 0))
                 for n, g in G.items() if g["besitzer"] == SP)
    # 23:27 (Lernlauf 3: Wohnraum 83 % der Zeit voll): ohne untaetige Bauern immer 2 Plaetze Wachstum frei halten - sonst
    # warten Huetten auf Arbeit und Arbeit (Vollbeschaeftigung) auf Bauern, und nichts waechst
    feuer = st.get("feuer", 0)
    return feuer < 2 and max(0, offene - feuer) + 2 > st.get("platz", 0) - st.get("leute", 0), offene

def haufen_hat_stein(G, q):
    """Liegt auf dem Steinhaufen (Verbund) des Steinbruchs bei q schon Stein?"""
    n = steht_bei(G, 20, q)
    if not n:
        return False
    h = G.get(G[n[0]].get("verbund") or -1)
    return bool(h and (h.get("vorrat") or 0) > 0)

E4_BRUECHE = [(61, 213), (72, 210), (84, 206)]   # zweites Steinfeld (61,212), 57 Felder vom Lager - 3 passen (Platzkarte Tick 0)

def v14_steinpflicht(st, G, wirt):
    """Beide Steinbrueche, dann beide Joche, genau an ihren Plaetzen (Umkreis 0), sobald das Holz reicht - vor allem
    anderen in der Runde. Was noch fehlt, liegt als Ruecklage in wirt.extra (Planer, Huetten, Holzfaeller halten es frei).
    E4 (Daniel 23:03 "so viele Steinbrueche wie geht"): danach die 3 vom zweiten Steinfeld, je mit Joch daneben."""
    ev, holz, offen = [], st.get("holz", 0), 0
    if JOCH_NACH_STEIN:
        # v18 (Daniel 23:10: "erst Steinbrueche, dann Ochsen, auch wenn Holz fuer Ochsen da ist ... Ochsen erst, wenn Stein
        # produziert wird"): Joch i erst, wenn Steinbruch i steht UND auf seinem Steinhaufen (Verbund) Stein liegt
        auftraege = [(20, q, 0) for q in V14_PLAN["brueche"]]
        for q, j in zip(V14_PLAN["brueche"], V14_PLAN["joche"]):
            # 23:51 (Daniel: "der Timer zwischen Steinbruch und Ochsenjoch stimmt noch nicht"): Joch, sobald der Steinbruch voll
            # BESETZT ist - der Ochsentreiber bekommt dann den naechsten Bauern und laeuft fast gleichzeitig mit den Steinmetzen
            # (gleicher Weg ~1.200 Ticks); nach "erster Stein" kam er ~1.200 Ticks zu spaet
            q_nr = steht_bei(G, 20, q)
            besetzt = bool(q_nr) and BUCH is not None and BUCH.hat.get(q_nr[0], 0) >= ARBEITER_JE[20]
            if besetzt or haufen_hat_stein(G, q) or steht_bei(G, 4, j, 3):
                # Umkreis 3: kommt das Joch nach dem ersten Stein, liegt der Steinhaufen schon - Lernlauf 1 (23:18): Haufen
                # bei (87,273) belegte den festen Joch-Platz (87,274), 501 Fehlversuche, 26 Steine nie abgeholt
                auftraege.append((4, j, 3))
    else:
        auftraege = [(20, q, 0) for q in V14_PLAN["brueche"]] + [(4, j, 0) for j in V14_PLAN["joche"]]
    if STEIN_MAX:
        for q in E4_BRUECHE:
            auftraege += [(20, q, 0)]
            if steht_bei(G, 20, q):
                auftraege += [(4, (q[0] + 7, q[1] + 2), 6)]    # Joch neben den Steinhaufen (der liegt bei x+7, y+2)
    for typ, ort, r in auftraege:
        if steht_bei(G, typ, ort, 1 if r == 0 else r) or BUCH.offen_bei(typ, ort, 2 if r == 0 else r):
            continue
        k = kosten_spiel(typ)["holz"]
        if holz >= k:
            o = baue_schnell(typ, ort[0], ort[1], r, zweck="Steinpflicht")
            ev.append("PFLICHT %s bei %s gesendet: %s (Holz %d)" % (NACH_TYP[typ]["name"], ort, o, holz))
            if o:
                holz -= k
                continue
        offen += k
    wirt.extra = {"holz": offen, "gold": 0}
    return ev

class LederKette:
    """v14: eigenes Leder statt 2 Lose (320 Gold) - Bewertungskette 22:03: netto ~80, spart 320.
    Stufe 0: warten bis das B-Seasoning steht -> 2 Milchviehhoefe (7 H 15 G je Hof).
    Stufe 1: Gerberei (15 H 3 S 75 G), sobald beide Hoefe bestaetigt stehen und der Bestand reicht.
    Stufe 2: Waffenlager (5 H) erst, wenn die erste Kuh da ist (Daniel B13: nicht frueher als noetig) - vor dem
             ersten Leder (Gerber braucht ~1.550 Ticks je Kuh).
    Jeder Bau ueber baue_schnell -> Auftragsbuch; genau an den Plaetzen (Umkreis 2, Plaetze sind gesperrt)."""

    def __init__(self, marken):
        self.marken = marken

    def schritt(self, st, G, wirt):
        ev, p, t = [], V14_PLAN, st.get("t", 0)
        if wirt.B_offen:
            return ev
        R = wirt.ruecklage(G)
        habe = {w: st.get(w, 0) - R.get(w, 0) for w in ("holz", "stein", "gold")}
        reicht = lambda typ: all(habe[w] >= kosten_spiel(typ).get(w, 0) for w in habe)
        def bau(typ, ort):
            if steht_bei(G, typ, ort, 2) or BUCH.offen_bei(typ, ort) or not reicht(typ):
                return
            o = baue_schnell(typ, ort[0], ort[1], 2, zweck="v14 Leder")
            ev.append("LEDER %s bei %s gesendet: %s (Holz %d, Stein %d, Gold %d)" % (
                NACH_TYP[typ]["name"], ort, o, st.get("holz", 0), st.get("stein", 0), st.get("gold", 0)))
            if o:
                for w in habe:
                    habe[w] -= kosten_spiel(typ).get(w, 0)
        for h in p["hoefe"]:
            bau(33, h)
        hoefe = sum(1 for h in p["hoefe"] if steht_bei(G, 33, h, 2))
        if hoefe == 2:
            bau(16, p["gerberei"])
        if steht_bei(G, 16, p["gerberei"], 2) and st.get("T51", 0) >= 1:
            bau(11, p["waffenlager"])
        for name, ok in (("erste Kuh", st.get("T51", 0) >= 1), ("beide Hoefe", hoefe == 2),
                         ("Gerberei steht", bool(steht_bei(G, 16, p["gerberei"], 2)))):
            if ok and name not in self.marken:
                self.marken[name] = t
                ev.append("MARKE %s bei Tick %d" % (name, t))
        return ev

def ruestung_kaufen(st, G, wirt, ausbau, ziel, marken):
    """v2 (Daniel 06.10. 21:05: erst maximale Wirtschaft, den Rest kaufen): Waffenlager + Kaserne weit weg (B3), Keulen und
    Leder in 5er-Losen am Markt kaufen, sobald das Gold ueber der Ruecklage reicht, und anwerben (20 Gold, Bauer am Feuer).
    Keine eigenen Werkstaetten - das ist v3."""
    aus = []
    eig = {n: g for n, g in G.items() if g["besitzer"] == SP}
    waf = [n for n, g in eig.items() if g["typ"] == 11]
    kas = [n for n, g in eig.items() if g["typ"] == 9]
    rl = wirt.ruecklage(G)
    # Daniel 21:07 (Bild v2, Tick ~2.600): "macht keinen Sinn, so frueh eine Waffenkammer zu bauen, die hat jetzt keinen
    # Wert, bevor nicht Waffen reinkommen" - Waffenlager und Kaserne erst, wenn das Gold fuer das erste Los Keulen + Leder
    # + Anwerben ueber der Ruecklage liegt; gekauft wird in der Runde danach.
    erstes_los = LOS_PREIS[21] + LOS_PREIS[23] + KAEMPFER_GOLD + rl["gold"]
    if st["gold"] >= erstes_los or (waf and kas):
        if not waf and st["holz"] >= 5 + rl["holz"]:
            aus.append("Waffenlager gesetzt %s (Gold %d)" % (baue_schnell(11, BERGFRIED[0] - 14, BERGFRIED[1] + 14, 25), st["gold"]))
        if not kas and st["stein"] >= 12:
            aus.append("Kaserne gesetzt %s (Gold %d)" % (baue_schnell(9, BERGFRIED[0] - 16, BERGFRIED[1] + 18, 30), st["gold"]))
    if not (waf and kas) or not [n for n, g in eig.items() if g["typ"] == 26]:
        return aus
    v = vorrat(SP)
    gold = st["gold"] - rl["gold"]
    for ware, name in ((21, "keule"), (23, "leder")):
        # Kipppunkt (Daniel 21:07 B12): ab hier hat das Militaer Vorrang - nicht mehr auf ausbau.braucht_gold warten
        # (v2: B-Plantagen die ganze Partie "offen" -> braucht_gold immer True -> bei bis zu 2.220 Gold nie gekauft);
        # die Ruecklage rl (B-Plantagen) ist oben schon abgezogen.
        if v.get(name, 0) == 0 and gold >= LOS_PREIS[ware] + KAEMPFER_GOLD:
            befehl({"spielbefehl": {"nr": 38, "werte": [0, ware]}}, 1.0, bis="SPIELBEFEHL")
            gold -= LOS_PREIS[ware]
            v[name] = 5
            aus.append("5 %s gekauft (%d Gold)" % (name, LOS_PREIS[ware]))
    werben = min(v.get("keule", 0), v.get("leder", 0), st.get("feuer", 0), max(gold, 0) // KAEMPFER_GOLD,
                 ziel - st.get("T26", 0))
    for _ in range(max(werben, 0)):
        befehl({"werbe": {"typ": 26, "gebaeude": kas[0]}}, 1.0, bis="WERBE")
    if werben > 0:
        aus.append("%d Streitkolbenkaempfer angeworben" % werben)
    for n in range(1, ziel + 1):
        if st.get("T26", 0) >= n and n not in marken:
            marken[n] = st["t"]
            aus.append("KAEMPFER %d bei Tick %d" % (n, st["t"]))
    return aus

def kaserne_am_feuer(G):
    """Kaserne so nah wie moeglich am Lagerfeuer (Typ 55): die Bauern laufen vom Feuer zur Kaserne (v5: weit weg gebaut)."""
    feuer = next((g for g in G.values() if g["besitzer"] == SP and g["typ"] == 55), None)
    x, y = (feuer["x"] + 3, feuer["y"] + 3) if feuer else (BERGFRIED[0], BERGFRIED[1] + 6)
    return baue_schnell(9, x, y, 20)

_SPLITS = []
ZIEL_FAKTOR = 11930 / 9600.0      # Bestzeit v5 -> Ziel unter 1 Jahr (9.600 Ticks)

def bestzeit_split(tick_jetzt):
    """Fortschritt der Bestzeit (v5) beim letzten Tick <= tick_jetzt: Bilanz-Wert / Bedarf (BILANZ-Zeilen ihres Protokolls).
    v14: als Anteil statt in Gold - eigene Leder-Kette senkt den Bedarf um 2 Lose, kostet aber frueh ~150 (sonst bricht
    der absolute Vergleich einen Lauf ab, der in Wahrheit vorne liegt)."""
    if not _SPLITS:
        pfad = os.path.join(D, "haertetest_v5_20261006.txt")
        if os.path.exists(pfad):
            for z in open(pfad, encoding="utf-8", errors="replace"):
                m = re.match(r"\s*(\d+) \|.*BILANZ .*= (\d+) \| Bedarf (\d+)", z)
                if m:
                    _SPLITS.append((int(m.group(1)), int(m.group(2)) / float(max(1, int(m.group(3))))))
        _SPLITS.append((0, 0.0))
        _SPLITS.sort()
    frueher = [h for t, h in _SPLITS if t <= tick_jetzt]
    return frueher[-1] if frueher else None

_KOSTEN = {}

def kosten_aller(typ, ausbau):
    """Baukosten jeder Art (v4 21:25: KeyError 21 - der Steinhaufen fehlt in der Tabelle des Planers): erst der Planer,
    sonst einmal aus der Kostentabelle des Spiels (bauen.kosten), danach gemerkt."""
    if typ not in _KOSTEN:
        from bauen import kosten
        _KOSTEN[typ] = ausbau.kosten_von(typ) if typ in ausbau.kosten else kosten(typ)
    return _KOSTEN[typ]

def bilanz_schritt(st, L, G, ausbau, ziel, endspiel, runde, marken):
    """Daniel 21:21: komplette Tabelle - was ist drin, was kommt, was braucht man WIRKLICH - und dann abreissen und das
    Ziel erfuellen. Rechnung in bilanz.py; hier: Tabelle ins Protokoll, Endspiel ausfuehren, danach anwerben."""
    import bilanz as BZ
    aus = []
    v = vorrat(SP)
    eig = {n: g for n, g in G.items() if g["besitzer"] == SP}
    kommt, behalten = 0, ()
    if V14:
        # eigenes Leder: naechste Kuh je Gerber = 3 Leder. Nimmt der Gerber die Kuh, faellt sie aus der Zaehlung, bevor
        # ihr Leder im Waffenlager ist -> Deckung (Leder + kommt + schon angeworben) ueber 1.600 Ticks (1 Gerber-Gang) glaetten
        gerber = len(steht_bei(G, 16, V14_PLAN["gerberei"], 2))
        deckung = v.get("leder", 0) + 3 * min(st.get("T51", 0), gerber) + st.get("T26", 0)
        hist = endspiel.setdefault("deckung", [])
        hist.append((st["t"], deckung))
        hist[:] = [(tt, d) for tt, d in hist if st["t"] - tt <= 1600]
        kommt = max(0, max(d for _, d in hist) - v.get("leder", 0) - st.get("T26", 0)) if gerber else 0
        if v.get("leder", 0) < ziel - st.get("T26", 0):
            behalten = (33, 16)                    # Hoefe + Gerberei liefern noch
    endspiel["leder_kommt"] = kommt
    if not endspiel["fertig"]:
        t = BZ.rechne(st, v, G, L, SP, ziel, lambda typ: kosten_aller(typ, ausbau), kommt, behalten)
        endspiel["tabelle"] = t
        # Zwischenzeiten wie beim TAS: Fortschritt (Bilanz-Wert / Bedarf) gegen die Bestzeit zum selben Tick; ab 3.000 mehr
        # als 10 % dahinter -> Abbruch. Ziel unter 1 Jahr (Daniel 21:58): Tempo von v5 * 11.930/9.600 noetig
        split = bestzeit_split(st["t"] * ZIEL_FAKTOR)
        anteil = t["habe_gold"] / float(max(1, t["bedarf_gold"]))
        if split and st["t"] >= 3000 and anteil < 0.9 * split and not EXPERIMENT:
            endspiel["abbruch"] = "Fortschritt %.2f (%d von %d) < 90 %% des Ziel-Tempos (%.2f) bei Tick %d" % (
                anteil, t["habe_gold"], t["bedarf_gold"], split, st["t"])
        if runde % 10 == 0 or t["jetzt_erreichbar"]:
            aus.append(BZ.text(t))
        if not t["jetzt_erreichbar"]:
            # kurz vor dem Endspiel (90 % der Bilanz) Kaserne am Feuer und Waffenlager setzen (v5: erst im Endspiel gebaut,
            # weit weg - erster Kaempfer 450 Ticks nach dem Endspiel; Daniel B13: nicht frueher als noetig)
            if t["habe_gold"] >= 0.9 * t["bedarf_gold"]:
                if not any(g["typ"] == 9 for g in eig.values()) and st.get("stein", 0) >= 12:
                    aus.append("VORBEREITUNG Kaserne am Feuer %s" % (kaserne_am_feuer(G),))
                if not any(g["typ"] == 11 for g in eig.values()) and st.get("holz", 0) >= 5:
                    aus.append("VORBEREITUNG Waffenlager %s" % (baue_schnell(11, BERGFRIED[0] - 14, BERGFRIED[1] + 14, 25),))
            return aus
        # ENDSPIEL: Kaserne/Waffenlager sichern, abreissen, alles verkaufen, kaufen
        aus.append("ENDSPIEL bei Tick %d: %d Betriebe abreissen, alles verkaufen, %d+%d Lose kaufen" % (
            st["t"], len(t["abriss_liste"]), t["lose_keule"], t["lose_leder"]))
        if not any(g["typ"] == 9 for g in eig.values()):
            for _ in range(max(0, -(-(12 - st.get("stein", 0)) // 5))):
                befehl({"spielbefehl": {"nr": 38, "werte": [0, 4]}}, 1.0, bis="SPIELBEFEHL")
            aus.append("Kaserne %s" % (kaserne_am_feuer(G),))
        if not any(g["typ"] == 11 for g in eig.values()):
            aus.append("Waffenlager %s" % (baue_schnell(11, BERGFRIED[0] - 14, BERGFRIED[1] + 14, 25),))
        # Reihenfolge (Daniel 21:24: "sie geht verloren, wenn du abreisst und kein Platz ist"): ERST alles verkaufen,
        # damit die Lagerteile leer sind, DANN abreissen, dann die Rueckgabe noch einmal verkaufen
        # gebuendelt in EINEM Befehl je Schritt (v6: 34 Verkaeufe + 47 Abrisse einzeln -> die Runde dauerte 427 Ticks)
        verkauft = {}
        def alles_verkaufen():
            vk = vorrat(SP)
            liste = []
            for w, los in BZ.LOS.items():
                k = min(vk.get(w, 0) // los, 60)
                liste += [{"spielbefehl": {"nr": 38, "werte": [1, BZ.WARE_NR[w]]}}] * k
                if k:
                    verkauft[w] = verkauft.get(w, 0) + k
            if liste:
                sende({"befehle": [dict(b, player=1, id=neue_id()) for b in liste]}, 2.0, bis="SPIELBEFEHL")
        alles_verkaufen()
        # Stufe 2 (v8: nach dem Endspiel fehlte Gold fuer das 2. Leder-Los - Kaempfer 6-10 erst 3.800 Ticks spaeter):
        # mit dem ECHTEN Gold nach dem Verkauf nachrechnen; reicht es nicht sicher, NICHT abreissen - Wirtschaft laeuft weiter
        gold_echt = vorrat(SP)["gold"]
        n_rest = max(0, ziel - st.get("T26", 0))
        noch = (-(-max(0, n_rest - v.get("keule", 0)) // 5)) * LOS_PREIS[21] + (-(-max(0, n_rest - v.get("leder", 0) - kommt) // 5)) * LOS_PREIS[23]             + n_rest * KAEMPFER_GOLD
        # Abriss nur zur Haelfte zaehlen + 20 Sicherheit (v9: 904 + 179 schien zu reichen, nach dem Abriss waren es 1.086
        # gegen 1.120 - das Abriss-Holz kommt beim Verkauf nicht voll an)
        # 07.10. 01:18: Abriss mit 80 % - gemessen kommen 82-114 % an (Gold vor/nach Endspiel-Verkauf: Lauf 12 +111/136,
        # 15 +109/128, 18 +116/128, 52 +211/186, 54 ~+205/182). Die Drittel-Rechnung beruhte auf einem Messfehler (L16 zaehlte
        # nur das nach dem Verkauf uebrige Holz) und liess Lauf 54 ~270 Ticks auf Gold warten
        if gold_echt + int(t["abriss_wert"] * 0.8) < noch + 20:
            aus.append("ENDSPIEL VERSCHOBEN: Gold nach Verkauf %d + Abriss %d < %d - Wirtschaft laeuft weiter" % (
                gold_echt, t["abriss_wert"], noch))
            return aus
        if t["abriss_liste"]:
            sende({"befehle": [{"player": 1, "id": neue_id(), "abreissen": {"nr": nr}} for nr in t["abriss_liste"]]}, 2.0,
                  bis="ABREISSEN")
        tick0 = tick()
        while tick() - tick0 < 10:                     # Abriss-Rueckgabe ins Lager
            time.sleep(0.05)
        alles_verkaufen()
        aus.append("ENDSPIEL verkauft (Lose): %s, Gold jetzt %d" % (verkauft, vorrat(SP)["gold"]))
        endspiel["fertig"] = True
        marken["endspiel"] = st["t"]
    # nach dem Endspiel: fehlende Lose kaufen, anwerben
    v = vorrat(SP)
    kas = [n for n, g in eig.items() if g["typ"] == 9]
    n = ziel - st.get("T26", 0)
    # Einzelkauf (Daniel 01:35: "wie eine KI im Backend, nicht ueber den Weg eines Spielers"): fehlen 1-4 Stueck, genau so
    # viele gutschreiben (Warenzelle PlayerData +0x4D0 + Ware*4, Gold +0x50C) zum Stueckpreis des Marktes (300/5, 160/5)
    # statt 5 zu kaufen. Ungeprueft, ob das Anwerben diese Waffen nimmt - EINZELKAUF-Zeile + KAEMPFER-Zeilen zeigen es
    ek = marken.get("einzelkauf")
    if ek and not marken.get("einzelkauf_aus") and st["t"] - ek["t"] > 200 and st.get("T26", 0) <= ek["t26"]:
        # Rueckweg: 200 Ticks kein neuer Kaempfer -> Anwerben nimmt die gutgeschriebenen Waffen nicht. Zellen und Gold
        # zurueck auf den Stand davor, ab jetzt wieder 5er kaufen
        for ware, (name, vorher) in ek["vorher"].items():
            sende({"player": 1, "poke": PD + 0x4D0 + ware * 4, "wert": vorher}, 0.5)
            v[name] = vorher
        sende({"player": 1, "poke": PD + 0x50C, "wert": v.get("gold", 0) + ek["gold"]}, 0.5)
        v["gold"] = v.get("gold", 0) + ek["gold"]
        marken["einzelkauf_aus"] = True
        aus.append("EINZELKAUF GESCHEITERT (kein Kaempfer in 200 Ticks) - zurueckgesetzt, %d Gold zurueck" % ek["gold"])
    if EINZELKAUF and n > 0 and not ek and not marken.get("einzelkauf_aus"):
        neu_ek = {"t": st["t"], "t26": st.get("T26", 0), "vorher": {}, "gold": 0}
        for ware, name in ((21, "keule"), (23, "leder")):
            fehlt = n - v.get(name, 0) - (kommt if name == "leder" else 0)
            stueck = LOS_PREIS[ware] // 5
            if 1 <= fehlt <= 4 and v.get("gold", 0) >= fehlt * stueck + n * KAEMPFER_GOLD:
                neu_ek["vorher"][ware] = (name, v.get(name, 0))
                sende({"player": 1, "poke": PD + 0x4D0 + ware * 4, "wert": v.get(name, 0) + fehlt}, 0.5)
                sende({"player": 1, "poke": PD + 0x50C, "wert": v.get("gold", 0) - fehlt * stueck}, 0.5)
                v[name] = v.get(name, 0) + fehlt
                v["gold"] -= fehlt * stueck
                neu_ek["gold"] += fehlt * stueck
                aus.append("EINZELKAUF %d %s fuer %d Gold" % (fehlt, name, fehlt * stueck))
        if neu_ek["vorher"]:
            marken["einzelkauf"] = neu_ek
    # alle noetigen Lose auf einmal (v6 kaufte nur eines je Ware und wartete dann), Gold fuer das Anwerben bleibt
    for ware, name in ((21, "keule"), (23, "leder")):
        while v.get(name, 0) + (kommt if name == "leder" else 0) < n and v.get("gold", 0) >= LOS_PREIS[ware] + n * KAEMPFER_GOLD:
            befehl({"spielbefehl": {"nr": 38, "werte": [0, ware]}}, 1.0, bis="SPIELBEFEHL")
            v[name] = v.get(name, 0) + 5
            v["gold"] -= LOS_PREIS[ware]
            aus.append("5 %s gekauft" % name)
    if not kas and n > 0 and endspiel["fertig"]:
        # Absicherung (v6/v7: Kaserne nach dem Endspiel weg, Lauf hing still bei 2-4 Kaempfern): sofort neu bauen
        if st.get("stein", 0) < 12:
            for _ in range(-(-(12 - st.get("stein", 0)) // 5)):
                befehl({"spielbefehl": {"nr": 38, "werte": [0, 4]}}, 1.0, bis="SPIELBEFEHL")
        aus.append("WARNUNG Kaserne fehlt nach dem Endspiel - neu gebaut: %s" % (kaserne_am_feuer(G),))
    if endspiel["fertig"] and v.get("holz", 0) >= 5:
        # Lauf 14: Gold reichte fuer 9 Kaempfer, 59 Holz lagen - im Endspiel ist Holz nur Gold
        for _ in range(v["holz"] // 5):
            befehl({"spielbefehl": {"nr": 38, "werte": [1, 2]}}, 1.0, bis="SPIELBEFEHL")
        aus.append("ENDSPIEL Holz verkauft (%d Holz)" % v["holz"])
    if kas:
        werben = min(v.get("keule", 0), v.get("leder", 0), st.get("feuer", 0), v.get("gold", 0) // KAEMPFER_GOLD, n)
        # 07.10. 01:25: hoechstens EINE Anwerbung je Runde (~11 Ticks). Lauf 45/46/52/57: von 5 gleichzeitig bezahlten kamen
        # oft nur 4 an (Waffen weg, Bauer nie losgelaufen) - Vermutung: zwei Befehle im selben Tick waehlen denselben Bauern.
        # Die Waffen werden beim Befehl abgezogen, darum zaehlt die naechste Runde richtig weiter
        werben = min(werben, 1)
        for _ in range(max(werben, 0)):
            befehl({"werbe": {"typ": 26, "gebaeude": kas[0]}}, 1.0, bis="WERBE")
        if werben > 0:
            aus.append("%d Streitkolbenkaempfer angeworben" % werben)
    for k in range(1, ziel + 1):
        if st.get("T26", 0) >= k and k not in marken:
            marken[k] = st["t"]
            aus.append("KAEMPFER %d bei Tick %d" % (k, st["t"]))
    return aus

class Produktion:
    """v3 (Daniel 06.10. 21:11-21:14): eigene Waffenproduktion moeglichst frueh, aber nicht fruehestmoeglich - erst wenn das
    Seasoning (B) steht; Kauf nur aus echtem Ueberschuss (B19); Anwerben erst, wenn Waffen da sind (B21: fruehes Anwerben
    nimmt der Wirtschaft das Gold); Kaserne erst bei Bedarf (B13). Eisen der Minen wird behalten (verkaufen eisen_reserve).
    Stufen: 0 warten -> 1 zwei Milchviehhoefe (Kuehe brauchen Zeit) -> 2 Gerberei + Schmiede + Waffenlager nach dem
    Aufbauplaner (Eisenteil, Hoftore, 1 Feld vom Lager) -> anwerben."""
    UEBERSCHUSS = 800              # Gold ueber der Ruecklage, ab dem ein fehlendes Los gekauft werden darf

    def __init__(self, ziel, marken, plan_lager=None):
        self.ziel, self.marken, self.stufe, self.umgestellt = ziel, marken, 0, set()
        self.plan_lager = tuple(plan_lager) if plan_lager else None

    def stein_bedarf(self):
        return {0: 0, 1: 11, 2: 12}.get(self.stufe, 0)

    def lager(self, G, wirt):
        # ueber die LAGE, nicht die Nummer (v3, 21:20: das neue Lager bekam nach dem Abriss wieder die Nummern 6-9, der
        # Filter "nicht in wirt.alt" fand nie ein Lager - die Produktion startete die ganze Partie nicht)
        teile = [g for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 10]
        if self.plan_lager:
            nah = [g for g in teile if max(abs(g["x"] - self.plan_lager[0]), abs(g["y"] - self.plan_lager[1])) <= 10]
            teile = nah or teile
        if not teile:
            return None
        return (sum(g["x"] for g in teile) // len(teile) + 1, sum(g["y"] for g in teile) // len(teile) + 1)

    def schritt(self, st, G, wirt):
        import aufbau_planer as P
        import wegkarte as W
        aus = []
        eig = {n: g for n, g in G.items() if g["besitzer"] == SP}
        rl = wirt.ruecklage(G)
        gold, holz, stein, feuer = st["gold"] - rl["gold"], st["holz"] - rl["holz"], st["stein"], st.get("feuer", 0)
        mitte = self.lager(G, wirt)
        hoefe = [g for g in eig.values() if g["typ"] == 33]
        if self.stufe == 0 and mitte and not wirt.B_offen and gold >= 30 and holz >= 14 and feuer >= 1:
            for _ in range(2):
                aus.append("PRODUKTION Milchviehhof %s" % (baue_schnell(33, mitte[0], mitte[1], 45),))
            self.stufe = 1
        elif self.stufe == 1 and len(hoefe) >= 2 and gold >= 75 and holz >= 40 and stein >= 11 and feuer >= 2 and mitte:
            k = W.holen(max(mitte[0] - 30, 0), max(mitte[1] - 30, 0), min(mitte[0] + 30, 399), min(mitte[1] + 30, 399))
            eisen = next((n for n, g in eig.items() if g["typ"] == 10 and g.get("ware") == 6), None)
            plan, bericht = P.plane(k, 1, 1, eisen, [(g["x"], g["y"]) for g in hoefe])
            for art, x, y, r, e in plan.bauten:
                befehl({"baue": {"mapper": {11: 81, 13: 83, 16: 85}[art], "x": x, "y": y, "groesse": 4, "richtung": r}}, 0.8, bis="BAUE")
            aus.append("PRODUKTION Werkstaetten nach Plan: %s" % [(NACH_TYP[a]["name"], x, y, r) for a, x, y, r, e in plan.bauten])
            self.stufe = 2
        if self.stufe < 2:
            return aus
        for n, g in eig.items():
            if g["typ"] == 13 and n not in self.umgestellt:
                befehl({"spielbefehl": {"nr": 33, "werte": [n, 21, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
                self.umgestellt.add(n)
        v = vorrat(SP)
        kas = [n for n, g in eig.items() if g["typ"] == 9]
        if not kas and v.get("keule", 0) and v.get("leder", 0) and stein >= 12:
            aus.append("PRODUKTION Kaserne %s" % (baue_schnell(9, BERGFRIED[0] - 16, BERGFRIED[1] + 18, 30),))
        if kas:
            for ware, name in ((21, "keule"), (23, "leder")):
                if v.get(name, 0) == 0 and gold >= self.UEBERSCHUSS + LOS_PREIS[ware]:
                    befehl({"spielbefehl": {"nr": 38, "werte": [0, ware]}}, 1.0, bis="SPIELBEFEHL")
                    gold -= LOS_PREIS[ware]
                    v[name] = 5
                    aus.append("PRODUKTION 5 %s aus Ueberschuss gekauft" % name)
            werben = min(v.get("keule", 0), v.get("leder", 0), feuer, max(gold, 0) // KAEMPFER_GOLD, self.ziel - st.get("T26", 0))
            for _ in range(max(werben, 0)):
                befehl({"werbe": {"typ": 26, "gebaeude": kas[0]}}, 1.0, bis="WERBE")
            if werben > 0:
                aus.append("%d Streitkolbenkaempfer angeworben" % werben)
        for n in range(1, self.ziel + 1):
            if st.get("T26", 0) >= n and n not in self.marken:
                self.marken[n] = st["t"]
                aus.append("KAEMPFER %d bei Tick %d" % (n, st["t"]))
        for name, wert in (("erste Keule", v.get("keule", 0)), ("erstes Leder", v.get("leder", 0))):
            if wert and name not in self.marken:
                self.marken[name] = st["t"]
                aus.append("MARKE %s bei Tick %d" % (name, st["t"]))
        return aus

def phase2(plan, minuten, tempo, mit_waechter=False, bis_tick=None, assassinen=0, trainingsstand=None, trainingsstand_ab=40,
           gold_ziel=None, streitkolben=0, weg="kauf"):
    schreib("== Phase 2: Echtzeit, Tempo %d, %d Minuten, Waechter %s" % (tempo, minuten, "an" if mit_waechter else "aus"))
    partie_pruefen()
    # Halte-Liste des Moduls ueberlebt das Laden einer Partie (04.10.: alte Eintraege zogen neue Assassinen mit
    # gleicher Nummer an fremde Plaetze zurueck - "sie sammeln sich nur und machen nichts")
    befehl({"halten": False}, 1.0, bis="HALTEN")
    import befehl as befehlskanal
    befehlskanal.STRENG = True     # ab hier bricht jeder Modulfehler den Lauf laut ab
    w = Waechter(SP, posten=plan["lager_mitte"]) if mit_waechter else None
    trupp = Einzeln(SP, pruefe_begehbar=pruefe_begehbar, wegtest=wegtest) if assassinen else None
    if trupp is not None and trainingsstand:
        # Kein Angriff: erst einen wiederholbaren Stand mit mindestens 40 gemeinsam angekommenen Assassinen sichern.
        trupp.angriff_aus = True
    if trupp is not None:   # S1 (Plan_Lord.md): was tut der Angriff auf den Lord, Runde fuer Runde
        trupp.wellen_protokoll = os.path.join(D, "angriff_live_%s_i%d.jsonl" % (time.strftime("%Y%m%d_%H%M%S"), INSTANZ))
    wirt = Wirtschaft(plan, SP, baue_schnell, [nr for nr, _, _ in gebaeude_von(SP, 10)])
    karte_laden()        # Begehbarkeit fuer kurze Rueckzuege - jetzt, solange das Spiel noch steht
    if trupp is not None:
        trupp.gelaende = list(_KARTE)   # einmal im Angriffsprotokoll: Gelände darf als Einfluss nicht vorab verschwinden
    lernlog = os.path.join(D, "ertrag_live_%s_i%d.jsonl" % (time.strftime("%Y%m%d_%H%M%S"), INSTANZ))   # je Instanz: Serien laufen parallel
    # Daniel 22:39: jede Runde die ganze Lage (jede Einheit, jedes Gebaeude der Karte) - abfragbar mit lageprotokoll.py
    from lageprotokoll import Lageprotokoll
    lage = Lageprotokoll(os.path.join(D, "lage_%s_i%d.jsonl.gz" % (time.strftime("%Y%m%d_%H%M%S"), INSTANZ)))
    schreib("Lageprotokoll (jede Runde komplett): %s" % lage.pfad)
    ausbau = Ertragsplaner(plan, SP, baue_schnell, wirt, s32(peek(PD + 0x2188)[0]), ende=ZIEL_TICK, protokoll=lernlog, wegtest=wegtest)   # lernt im Spiel (Daniel 19:44)

    def gold_bremst(st, G):
        """Es sollen Assassinen her, aber das Gold reicht nicht fuer den naechsten (70 + B-Ruecklage) - oder Gold ist selbst
        das Ziel (gold_ziel, Testpartie gegen die leere KI)."""
        if gold_ziel and st.get("gold", 0) < gold_ziel:
            return True
        if streitkolben and st.get("T26", 0) < streitkolben and st.get("gold", 0) < KAEMPFER_GOLD + wirt.ruecklage(G)["gold"]:
            return True
        return bool(assassinen) and (assassinen < 0 or geworben < assassinen) and st.get("gold", 0) < 70 + wirt.ruecklage(G)["gold"]

    def holz_verwerten(st, L, G):
        """Altes Lager: Holz verkaufen, solange Gold das Anwerben bremst (Daniel 06.10. 19:33, vorerst); sonst Holzfaeller."""
        if gold_bremst(st, G) and not V14:
            # v14+ nicht: E4 (23:06) verkaufte so beim Lagerumzug bei Tick 353 Startholz - am Anfang wird nicht angeworben
            befehl({"spielbefehl": {"nr": 38, "werte": [1, WAREN_NR["holz"]]}}, 1.0, bis="SPIELBEFEHL")
            ausbau.messer.verkauft("holz")
            return "verkauft", "Gold bremst das Anwerben"
        ort, text = ausbau.holzfaeller_statt_verkauf(st, L, G)
        if ort is None and streitkolben:          # 23:21: auch in der v5-Bauweise keine Huette als Holz-Abfluss
            # v15 (Daniel 22:29: "10 Haeuser helfen nur bedingt"; v14 baute 11 Huetten fuer 15 Leute, Platz 98): keine Huette
            # als Holz-Abfluss - Huetten nur als Puffer (Platz - Leute < 6). Holz bleibt fuer B (Seasoning vor der ersten
            # Holzlieferung), ein volles 20er-Los wird verkauft, wenn das Holz ueber der Ruecklage liegt.
            if st.get("holz", 0) - wirt.ruecklage(G)["holz"] >= 20:
                befehl({"spielbefehl": {"nr": 38, "werte": [1, WAREN_NR["holz"]]}}, 1.0, bis="SPIELBEFEHL")
                ausbau.messer.verkauft("holz")
                return "verkauft", "kein Holzfaeller-Platz (%s), Los ueber der Ruecklage" % text
            return None, text
        if ort is None and streitkolben:
            # v11: "kein erreichbarer Holzfaeller-Platz" -> das alte Lager wurde nie leer, der Umzug blieb bis 11.520 haengen.
            # Dann Huetten (Wohnplatz-Puffer, Daniel 21:55), sonst verkaufen - nie liegen lassen.
            if st.get("holz", 0) >= 5:
                h = baue_haus()
                if h:
                    return h, "Huette statt Holzfaeller (%s)" % text
            befehl({"spielbefehl": {"nr": 38, "werte": [1, WAREN_NR["holz"]]}}, 1.0, bis="SPIELBEFEHL")
            ausbau.messer.verkauft("holz")
            return "verkauft", "kein Holzfaeller-/Huettenplatz (%s)" % text
        return ort, text
    wirt.holz_verbauen = holz_verwerten
    wirt.b_versatz = B_VERSATZ
    global BUCH
    leder, hf_spaeter = None, []
    # Auftragsbuch und die allgemeinen Knoepfe in JEDER Bauweise (Lernkreis 23:20: sonst kann er nach einem Sieg der
    # v5-Bauweise nichts mehr verbessern; Daniel 22:08: jeder Bau wird geprueft - nicht nur in v14)
    from auftragsbuch import Auftragsbuch
    BUCH = Auftragsbuch(SP, ARBEITER_JE, NACH_TYP)
    ausbau.holz_max, ausbau.je_arbeiter, ausbau.huetten_je_baum = HF_MAX, JE_ARBEITER, HUETTEN_JE_BAUM
    ausbau.steuer_runter, ausbau.steuer_ende = STEUER_RUNTER, STEUER_ENDE
    ausbau.kasse, kasse = False, {"an": None}
    ausbau.kasse_grenze, ausbau.kasse_stufe = KASSE_GRENZE, KASSE_STUFE
    ausbau.kasse_modus = KASSE                       # ist die Kasse eingestellt, setzt NUR sie Stufe 11 (steuer_ende schweigt)
    ausbau.wachstum = bool(BEV_ZIEL)                 # bis zur Ziel-Bevoelkerung keine Steuer
    if V14:
        wirt.umzug_ab, wirt.lager_genau, wirt.lager_ort = None, True, tuple(V14_PLAN["lager"])
        wirt.umzug_nach_b = UMZUG == "nachb"
        if UMZUG == "frueh":
            wirt.umzug_ab = 0
        elif UMZUG == "nein":
            wirt.alt = set()                    # die Startteile SIND das Lager - kein Abriss, kein neues
            wirt.lager_ort = BASIS_LAGER
            plan["lager"] = list(BASIS_LAGER)   # Planer misst Wege zum Lager am Bergfried
        schreib("Versuch: Umzug %s, Experiment (ohne Tempo-Regel) %s" % (UMZUG, EXPERIMENT))
        ausbau.ohne, ausbau.sperr = ({3, 5, 7, 20, 32} if STEIN_ZUERST else {20}), v14_sperrflaechen()
        RESERVIERT[:] = [((x, y, x + 9, y + 9), (x, y)) for x, y in (tuple(o) for o in wirt.B)]   # Apfelplantage 10x10
        ausbau.sperr = ausbau.sperr + [(r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1) for r, _ in RESERVIERT]
        hf_spaeter = [tuple(p) for p in v16_holzfaeller(plan)[HF_VORAB:]] if HF_VORAB is not None else []
        ausbau.holz_max, ausbau.je_arbeiter = HF_MAX, JE_ARBEITER
        ausbau.huetten_je_baum = HUETTEN_JE_BAUM
        schreib("v17: Holzfaeller je Baum %s, Holz kaufen bei untaetigen Bauern %s" % (HUETTEN_JE_BAUM, HOLZ_KAUFEN))
        schreib("v16: Holzfaeller hoechstens %s Felder vom Lager (Plan: %s), Planer nach Gewinn je Arbeiter: %s" % (
            HF_MAX, v16_holzfaeller(plan), JE_ARBEITER))
        schreib("v15: Holzfaeller vorab %s, spaeter %d aus dem Plan; Steinbrueche zuerst besetzen: %s; Lagerumzug nach B" % (
            HF_VORAB, len(hf_spaeter), STEIN_ZUERST))
        leder = LederKette({})
        schreib("v14: Auftragsbuch an; Steinbrueche %s, Joche %s, Lager %s (Umzug ab Tick %d), Leder: Hoefe %s, Gerberei %s, "
                "Waffenlager %s; Fruehabbruch: Steinbrueche+Joche bis %d, neues Lager bis %d" % (
                    V14_PLAN["brueche"], V14_PLAN["joche"], V14_PLAN["lager"], V14_UMZUG_AB, V14_PLAN["hoefe"],
                    V14_PLAN["gerberei"], V14_PLAN["waffenlager"], V14_STEIN_BIS, V14_LAGER_BIS))
    schreib("Ertrags-Planer: Baukosten aus dem Spiel %s; Protokoll %s" % (
        {t: {w: v for w, v in k.items() if v} for t, k in ausbau.kosten.items()}, os.path.basename(lernlog)))
    schreib("Ertrags-Planer: " + ausbau.startwerte)
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
    gold_marke = 1000
    kaempfer_marken = {}
    prod = Produktion(streitkolben, kaempfer_marken, plan.get("lager")) if streitkolben and weg == "produktion" else None
    endspiel = {"fertig": False, "tabelle": None}
    fruehpruefung = {}
    while time.time() < ende and not os.path.exists(os.path.join(HIER, "STOP")):
        tz = time.time()
        befehlskanal.belege()
        st, L, G = runde_lesen()
        if st:
            lage.schreibe(st)
        tz = uhr("lesen", tz)
        if bis_tick and st.get("t", 0) >= bis_tick:
            break
        # Goldmarken (Daniel 06.10.: "wie man am schnellsten 10k Gold bekommt") - jede 1.000 einmal, am Ziel Schluss
        while gold_ziel and st.get("gold", 0) >= gold_marke and gold_marke <= gold_ziel:
            schreib("GOLD-MARKE %d bei Tick %d" % (gold_marke, st.get("t", 0)))
            gold_marke += 1000
        if gold_ziel and st.get("gold", 0) >= gold_ziel:
            schreib("GOLD-ZIEL %d erreicht bei Tick %d" % (gold_ziel, st.get("t", 0)))
            break
        runde += 1
        if not st:
            continue
        if st.get("over") == 0 and st.get("ansicht") not in (14, 16):
            # 07.10. (Lauf 24/27/50/51: Daniel schaut zu, Ansicht 16 bei pause 0 -> Abbruch, Lauf verloren): Ansicht 16 ist
            # Spiel mit offenem Menue (Spiel laeuft weiter) und zaehlt wie 14; andere Ansicht: warten, nach 120 s abbrechen
            if "ansicht_weg" not in fruehpruefung:
                fruehpruefung["ansicht_weg"] = time.time()
                schreib("ANSICHT %s bei Tick %s (von aussen?) - Lenker wartet" % (st.get("ansicht"), st.get("t")))
            if time.time() - fruehpruefung["ansicht_weg"] < 120:
                time.sleep(0.5)
                continue
        else:
            fruehpruefung.pop("ansicht_weg", None)
        if st.get("over") != 0 or st.get("ansicht") not in (14, 16):
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
        ausbau.beobachte(st, L, G)        # Buchfuehrung des Planers: Zugang je Ware seit der letzten Runde
        eig = [g for g in G.values() if g["besitzer"] == SP]
        gebs = [(g["x"] + NACH_TYP.get(g["typ"], {"b": 2})["b"] // 2, g["y"] + NACH_TYP.get(g["typ"], {"b": 2})["b"] // 2)
                for g in eig if g["typ"] in EIGENE_ARTEN]
        tz = time.time()
        ereignis = w.schritt(L, gebs, ausgenommen=trupp.mitglieder if trupp else ()) if w is not None else []
        tz = uhr("waechter", tz)
        if BUCH is not None:
            ereignis += BUCH.abgleich(G, L, st)            # jeder Bau bestaetigt oder gescheitert, jede Belegung
            while BUCH.unerreichbar:                        # v18: laut Spiel unerreichbar -> abreissen, Platz sperren
                n_u, typ_u, ort_u = BUCH.unerreichbar.pop()
                befehl({"abreissen": {"nr": n_u}}, 0.8, bis="ABREISSEN")
                ausbau.fehlschlag[(typ_u, ort_u)] = ausbau.fehlschlag.get((typ_u, ort_u), 0) + 1
            if ENTSCHEIDER == "kausal" and not endspiel["fertig"]:
                # Kausalmodell (kausal.py): fuer jede Handlung die Wirkungskette bis ZIEL_TICK aus der aktuellen Lage
                import kausal as KM
                ausbau.kausal = True
                feuer_g = next(((g["x"] + 1, g["y"] + 1) for g in G.values() if g["besitzer"] == SP and g["typ"] == 55), BERGFRIED)
                lager_m = tuple(plan["lager"])
                speicher_m = tuple(plan["kornspeicher"])
                # 23:48 (Daniel: "warum wird hier keine Plantage gebaut"): je Art die 4 naechsten Plaetze zur Abgabe bewerten -
                # vorher nur EINEN (den "besten" des Planers, (101,200) ganz oben); die Flaeche neben den Obstgaerten sah es nie
                abgabe_k = {3: lager_m, 32: speicher_m, 7: speicher_m}
                kand_k = []
                for typ_a in (3, 32, 7):
                    if typ_a in getattr(ausbau, "ohne", ()):
                        continue
                    b_a = ausbau.groesse.get(typ_a, 3) // 2
                    orte_a = sorted(ausbau._orte(typ_a, L, G), key=lambda p: max(abs(p[0] + b_a - abgabe_k[typ_a][0]), abs(p[1] + b_a - abgabe_k[typ_a][1])))
                    kand_k += [(typ_a, p, ausbau.kosten_von(typ_a), 1) for p in orte_a[:4]]
                R_k = wirt.ruecklage(G)
                st_k = dict(st, holz=st["holz"] - R_k["holz"], gold=st["gold"] - R_k["gold"])
                for w_k, typ_k, ort_k, text_k in KM.entscheide(st["t"], ZIEL_TICK, st_k, kand_k, feuer_g,
                                                                {3: lager_m, 32: speicher_m, 7: speicher_m}, kosten_spiel(1)["holz"]):
                    if typ_k == 1:
                        o_k = baue_haus()
                    else:
                        o_k = baue_schnell(typ_k, ort_k[0], ort_k[1], 3, zweck="kausal")
                        if not o_k:
                            ausbau.fehlschlag[(typ_k, ort_k)] = ausbau.fehlschlag.get((typ_k, ort_k), 0) + 1
                    ereignis.append("KAUSAL %s bei %s: %s -> %s" % (NACH_TYP[typ_k]["name"], ort_k, text_k, o_k))
                # Holz aus dem Modell (Daniel 23:48 "mach das direkt aus dem Modell, sofort"): hat keine Handlung mit Holz mehr
                # positiven Wert, ist Holz nur noch Verkaufsware -> alles ueber 20 verkaufen, Lager waechst nicht mehr
                bedarf_holz = KM.entscheide(st["t"], ZIEL_TICK, dict(st_k, holz=999, gold=999), kand_k, feuer_g, abgabe_k, kosten_spiel(1)["holz"])
                fruehpruefung["holz_ueberfluessig"] = not bedarf_holz
                ausbau.endphase = not bedarf_holz
            if V14 and not endspiel["fertig"] and fruehpruefung.get("holz_ueberfluessig"):
                # Daniel 23:46: gegen Ende Holz direkt verkaufen statt neue Lagerplaetze - Holzfaeller legen sofort ab
                ausbau.lager_stopp = wirt.lager_stopp = True
                lose_h = min(3, max(0, (st["holz"] - 20) // 20))
                if lose_h:
                    sende({"befehle": [{"player": 1, "id": neue_id(), "spielbefehl": {"nr": 38, "werte": [1, WAREN_NR["holz"]]}}
                                       for _ in range(lose_h)]}, 1.0, bis="SPIELBEFEHL")
                    ereignis.append("HOLZ VERKAUFT %d Lose (Holz %d, Lager waechst nicht mehr)" % (lose_h, st["holz"]))
            if HUETTEN_VORAUS and not endspiel["fertig"] and ENTSCHEIDER != "kausal":
                # v18 (Daniel 23:10 Punkt 3: "Haeuser bauen, bevor du Menschen brauchst, weil sie Spawnzeit brauchen"):
                # freie Wohnplaetze >= offene Arbeitsplaetze + 4 (mind. 6)
                fehlt_w, offene = wohnraum_fehlt(st, G)
                frei_wohn = st.get("platz", 0) - st.get("leute", 0)
                if fehlt_w and st["holz"] >= 5 and not any(a["typ"] == 1 for a in BUCH.offen):
                    ereignis.append("HUETTE VORAUS (frei %d, offene Arbeitsplaetze %d): %s" % (frei_wohn, offene, baue_haus()))
            # Daniel 07.10. 00:17/00:20: "maximal viel Bevoelkerung und Holzfaeller, dann relativ frueh bei 60-70 Leuten -40
            # Steuern, Essen stoppen und verkaufen". Wachstum: Huetten, bis BEV_ZIEL Plaetze stehen (nur wenn fast voll).
            # Daniel 00:48: "einfach maximal Bevoelkerung, aber bei 70 anfangen auf -40, dann kommen wir eher auf 80-90" -
            # das Wachstum laeuft nach dem Kasse-Start weiter, solange noch Leute zuziehen (Beliebtheit >= 50, Liga +5 bei 50-54)
            if BEV_ZIEL and not endspiel["fertig"] and (not kasse["an"] or st.get("beliebt", 0) >= 5000):
                # Daniel 00:40: "ohne ausreichend Holzfaeller werden niemals 70 erreicht, da maximal 24 Leute im Pennerhof sind" -
                # am Lagerfeuer warten hoechstens 24, dann zieht niemand mehr zu. Wartende bekommen sofort Arbeit: der billigste
                # Arbeitsplatz ist der Holzfaeller (3 Holz, 1 Arbeiter, liefert Holz fuer Huetten und Verkauf)
                # 00:44 (Daniel "er baut immer noch keine Holzfaeller"; Lauf 42: 2 Stueck, bei Tick 6.122 lagen 39 Holz bei 19
                # Wartenden): nicht ueber holzfaeller_statt_verkauf (haelt Holz fuer den "besten Bau" zurueck, Entfernungsgrenze),
                # sondern direkt: naechster Baum-Platz des Planers, sonst ein geplanter Holzfaeller-Platz; jede Absage mit Grund
                R_w = wirt.ruecklage(G)
                # Daniel 01:35: "Holz gekauft kurz bevor Holz reinkommt - unnoetig": was Holzfaeller gerade tragen, kommt gleich
                holz_kommt = sum(e.get("ladung", 0) for e in L.values() if e["besitzer"] == SP and e["typ"] == 3 and e.get("ladung", 0) > 0)
                # erst wenn die Steinbrueche besetzt sind (v15: Bauern nehmen Holzfaeller vor Steinbruch, Steinbrueche blieben 0/6)
                # Daniel 00:54: "es muss noch Platz fuer Penner sein - wenn alle direkt Holzfaeller werden, ist kein Platz": die
                # Wartenden sind der Puffer (sie gehen bei niedriger Beliebtheit zuerst, aus ihnen wird angeworben); Holzfaeller
                # erst, wenn das Feuer fast voll ist (hoechstens 24, dann kein Zuzug) - Knopf penner
                if st.get("feuer", 0) >= PENNER and "stein_besetzt" in fruehpruefung and not any(a["typ"] == 3 for a in BUCH.offen):
                    if st["holz"] - R_w["holz"] >= kosten_spiel(3)["holz"]:
                        ort_w, weg_w = ausbau._bester_ort(3, L, G)
                        # Daniel 01:03 (rote Marker = "ausserhalb gebaut", jenseits des Flusses): der Plan-Platz wurde nicht auf
                        # einen Weg geprueft und die Platzsuche durfte 3 Felder abweichen. Jetzt jeder Platz per Wegtest des
                        # Spiels, Abweichung hoechstens 1 Feld
                        if not ort_w:
                            ort_w = ausbau._erreichbarer([tuple(q) for q in v16_holzfaeller(plan) if not steht_bei(G, 3, tuple(q), 1)], L)
                        plaetze_w = [ort_w] if ort_w else []
                        if plaetze_w:
                            o_w = baue_schnell(3, plaetze_w[0][0], plaetze_w[0][1], 1, zweck="Wachstum")
                            if not o_w and ort_w:
                                ausbau.fehlschlag[(3, ort_w)] = ausbau.fehlschlag.get((3, ort_w), 0) + 1
                            ereignis.append("WACHSTUM Holzfaeller fuer %d Wartende bei %s (Weg %s): %s" % (
                                st["feuer"], plaetze_w[0], weg_w, o_w))
                        elif runde % 20 == 0:
                            ereignis.append("WACHSTUM kein Holzfaeller-Platz (Planer und Plan leer) bei %d Wartenden" % st["feuer"])
                    elif holz_kommt + st["holz"] - R_w["holz"] >= kosten_spiel(3)["holz"]:
                        if runde % 20 == 0:
                            ereignis.append("WACHSTUM wartet auf %d Holz unterwegs (statt kaufen)" % holz_kommt)
                    elif HOLZ_KAUFEN and st["gold"] - R_w["gold"] >= 15 and st["t"] - fruehpruefung.get("holz_gekauft_w", -999) >= 12:
                        # Daniel 00:44: "Gold am Anfang fuer Holz ausgeben, bis das erste Holz reinkommt, und noch mehr Holzfaeller"
                        # - 5 Holz fuer 15 Gold (L11) = ein Holzfaeller fuer einen Wartenden
                        lose_w = int(min((st["gold"] - R_w["gold"]) // 15, max(1, st["feuer"] // 2)))
                        sende({"befehle": [{"player": 1, "id": neue_id(), "spielbefehl": {"nr": 38, "werte": [0, WAREN_NR["holz"]]}}
                                           for _ in range(lose_w)]}, 1.0, bis="SPIELBEFEHL")
                        fruehpruefung["holz_gekauft_w"] = st["t"]
                        ereignis.append("WACHSTUM Holz gekauft: %d Lose fuer %d Wartende (Holz %d, Gold %d)" % (
                            lose_w, st["feuer"], st["holz"], st["gold"]))
                    elif runde % 20 == 0:
                        ereignis.append("WACHSTUM wartet: %d am Feuer, Holz %d (Ruecklage %d), Gold %d (Ruecklage %d)" % (
                            st["feuer"], st["holz"], R_w["holz"], st["gold"], R_w["gold"]))
                frei_w = st.get("platz", 0) - st.get("leute", 0)
                if frei_w <= 4 and st["holz"] >= kosten_spiel(1)["holz"]                         and not any(a["typ"] == 1 for a in BUCH.offen):
                    ereignis.append("WACHSTUM Huette (Platz %d, Ziel %d, frei %d): %s" % (st.get("platz", 0), BEV_ZIEL, frei_w, baue_haus()))
            # mit Ziel-Bevoelkerung wartet die Kasse auf das Ziel (Daniel 00:34 "erst 60-70, dann -40"); frueher nur, wenn die
            # Bevoelkerung einen Monat (~800 Ticks, L23) nicht mehr gewachsen ist und nichts mehr lohnt
            if st.get("leute", 0) > kasse.get("leute_max", -1):
                kasse["leute_max"], kasse["wuchs_tick"] = st.get("leute", 0), st["t"]
            stillstand = st["t"] - kasse.get("wuchs_tick", st["t"]) >= 800
            if KASSE != "nein" and not kasse["an"] and not endspiel["fertig"] and (
                    (BEV_ZIEL and st.get("leute", 0) >= BEV_ZIEL)
                    or (fruehpruefung.get("holz_ueberfluessig") and (not BEV_ZIEL or stillstand))):
                kasse["an"] = st["t"]
                ausbau.kasse, ausbau.wachstum = True, False
                ereignis.append("KASSE ab Tick %d (%s): Steuer 11 bis zum Ende, Leute %d, Beliebtheit %.1f%s" % (
                    st["t"], "Ziel-Bevoelkerung" if BEV_ZIEL and st.get("leute", 0) >= BEV_ZIEL else "nichts lohnt mehr" + (", Bevoelkerung steht seit Tick %d" % kasse["wuchs_tick"] if BEV_ZIEL else ""),
                    st.get("leute", 0), st.get("beliebt", 0) / 100.0, ", keine Rationen, Nahrung wird verkauft" if KASSE == "steuer_essen" else ""))
            if kasse["an"] and KASSE == "steuer_essen":
                # Lauf 38/39: unter der Grenze ging nur die Steuer aus, Rationen blieben 0 und Nahrung wurde weiter verkauft ->
                # Beliebtheit bis 0, Lauf 39 von 34 auf 4 Leute, kein Kaempfer. Jetzt: unter der Grenze Rationen normal (2) und
                # kein Nahrungsverkauf mehr, darueber Rationen 0 und alles verkaufen
                essen_aus = st.get("beliebt", 0) / 100.0 >= KASSE_GRENZE
                if essen_aus != kasse.get("essen_aus"):
                    befehl({"spielbefehl": {"nr": 35, "werte": [0 if essen_aus else 2]}}, 1.0, bis="SPIELBEFEHL")
                    kasse["essen_aus"] = essen_aus
                    ereignis.append("KASSE Rationen %s (Beliebtheit %.1f, Grenze %d)" % (
                        "aus, Nahrung wird verkauft" if essen_aus else "normal, kein Verkauf", st.get("beliebt", 0) / 100.0, KASSE_GRENZE))
            if kasse["an"] and KASSE == "steuer_essen" and kasse.get("essen_aus") and runde % 3 == 1:
                lose_n = [{"player": 1, "id": neue_id(), "spielbefehl": {"nr": 38, "werte": [1, WAREN_NR[w]]}}
                          for w in ("apfel", "brot", "kaese", "fleisch") for _ in range(st.get(w, 0) // 5)]
                if lose_n:
                    sende({"befehle": lose_n}, 1.0, bis="SPIELBEFEHL")
                    ereignis.append("KASSE Nahrung verkauft: %d Lose" % len(lose_n))
            # Schub (07.10., Daniel 01:07 "macht was ihr koennt"): Lauf 45/46 - im Endspiel bei Beliebtheit 0 ging der 10.
            # Angeworbene auf dem Weg verloren, Nachkauf 460 Gold = ~1.100 Ticks. Die ersten 5 Kaempfer darum schon waehrend
            # der Kasse, solange die Beliebtheit hoeher ist (Liga-Wegzug -5 bei 25-29 statt -40 bei 0-4)
            if SCHUB and kasse["an"] and not endspiel["fertig"] and (st.get("T26", 0) == 0 or kasse.get("schub") == "gekauft")                     and kasse.get("schub") != "geworben":
                v_s = vorrat(SP)
                kas_s = [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 9]
                wl_s = [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 11]
                bedarf_s = LOS_PREIS[21] + LOS_PREIS[23] + 5 * KAEMPFER_GOLD
                if kasse.get("schub") == "gekauft":
                    # eine Anwerbung je Runde, bis die Waffen aufgebraucht sind (siehe Endspiel, 01:25)
                    werben_s = min(v_s.get("keule", 0), v_s.get("leder", 0), st.get("feuer", 0), v_s.get("gold", 0) // KAEMPFER_GOLD)
                    if kas_s and werben_s > 0:
                        befehl({"werbe": {"typ": 26, "gebaeude": kas_s[0]}}, 1.0, bis="WERBE")
                        kasse["schub_n"] = kasse.get("schub_n", 0) + 1
                        ereignis.append("SCHUB %d. Streitkolbenkaempfer angeworben (Beliebtheit %.1f, Wartende %d)" % (
                            kasse["schub_n"], st.get("beliebt", 0) / 100.0, st.get("feuer", 0)))
                    elif kasse.get("schub_n"):
                        kasse["schub"] = "geworben"
                elif v_s.get("gold", 0) >= bedarf_s and st.get("feuer", 0) >= 5:
                    if not kas_s:
                        if st.get("stein", 0) < 12:
                            for _ in range(-(-(12 - st.get("stein", 0)) // 5)):
                                befehl({"spielbefehl": {"nr": 38, "werte": [0, 4]}}, 1.0, bis="SPIELBEFEHL")
                        elif not any(a["typ"] == 9 for a in BUCH.offen):
                            ereignis.append("SCHUB Kaserne am Feuer %s" % (kaserne_am_feuer(G),))
                    if not wl_s and not any(a["typ"] == 11 for a in BUCH.offen):
                        ereignis.append("SCHUB Waffenlager %s" % (baue_schnell(11, BERGFRIED[0] - 14, BERGFRIED[1] + 14, 25),))
                    if kas_s and wl_s:
                        for ware, name in ((21, "keule"), (23, "leder")):
                            if v_s.get(name, 0) < 5:
                                befehl({"spielbefehl": {"nr": 38, "werte": [0, ware]}}, 1.0, bis="SPIELBEFEHL")
                        kasse["schub"] = "gekauft"
                        ereignis.append("SCHUB je 1 Los Keulen + Leder gekauft (Gold %d, Beliebtheit %.1f)" % (v_s.get("gold", 0), st.get("beliebt", 0) / 100.0))
            # Daniel 01:29: "deine Starteinheiten einschlaefern - die werden dann zu Bevoelkerung". Gegen die leere KI nutzlos:
            # Bogenschuetzen (22, 5 ab Start), Speertraeger (24, 7 spaeter) usw. aufloesen (disbandUnit -> Bauer am Feuer,
            # M10.04); Streitkolbenkaempfer (26) und Lord (55) bleiben
            # 01:39 (Daniel: "die 12 Starteinheiten chillen dann nur und werden nicht zu Arbeitern - eleganter loesen"; Lauf 61:
            # alle 12 auf einmal fuellten den Wohnraum 26, 17 sassen am Feuer): nach Bedarf - ein Soldat wird erst Bauer, wenn
            # ein Arbeitsplatz offen ist und niemand am Feuer wartet (er ersetzt den Bauern, auf den man ~52 Ticks warten muesste)
            offene_a = wohnraum_fehlt(st, G)[1] if AUFLOESEN else 0
            if AUFLOESEN and not endspiel["fertig"] and st.get("feuer", 0) == 0 and offene_a > 0:
                opfer = [n for n, e in L.items() if e["besitzer"] == SP and 22 <= e["typ"] <= 30 and e["typ"] != 26][:min(offene_a, 2)]
                if opfer:
                    # das Modul erwartet eine LISTE von Nummern (aufloesen_ersetzen.py; Lauf 61: einzelne Nummer -> "0 Einheiten")
                    befehl({"aufloesen": {"nr": [int(n) for n in opfer[:12]]}}, 1.0)
                    ereignis.append("AUFGELOEST %d Soldaten fuer %d offene Arbeitsplaetze (Typen %s) -> Bauern" % (len(opfer[:12]), offene_a, 
                        sorted({L[n]["typ"] for n in opfer[:12]})))
            ausbau.nach_abriss = bool(endspiel["fertig"])
            if runde % 10 == 1:
                schreib(BUCH.stand(G, st))
            hf_jetzt = sum(1 for g in G.values() if g["besitzer"] == SP and g["typ"] == 3) + \
                sum(1 for a in BUCH.offen if a["typ"] == 3)
            # E4: erste ECHTE Holzlieferung = ein Holzfaeller (Typ 3) gibt Ladung ab (Lagebild), nicht "Holz im Lager steigt"
            # (23:06: der Kauf "Holz fuer B" bei Tick 1.190 galt als Lieferung)
            lad_jetzt = {n: e.get("ladung", 0) for n, e in L.items() if e["besitzer"] == SP and e["typ"] == 3}
            lad_vor = fruehpruefung.get("hf_ladung", {})
            if "holz_geliefert" not in fruehpruefung and any(lad_vor.get(n, 0) > l for n, l in lad_jetzt.items()):
                fruehpruefung["holz_geliefert"] = st["t"]
                ereignis.append("ERSTE HOLZLIEFERUNG bei Tick %d (Holzfaeller gibt Ladung ab; Holzfaeller %d, Holz %d)" % (
                    st["t"], hf_jetzt, st["holz"]))
            fruehpruefung["hf_ladung"] = lad_jetzt
            # Spam endet bei HOLZ_SPAM Holzfaellern ODER mit der ersten Lieferung (E4: 19 von 20 - die Steinbrueche kamen nie)
            spam_offen = bool(HOLZ_SPAM) and hf_jetzt < HOLZ_SPAM and "holz_geliefert" not in fruehpruefung
            holz_unterwegs = sum(e.get("ladung", 0) for e in L.values() if e["besitzer"] == SP and e["typ"] == 3 and e.get("ladung", 0) > 0)
            if HOLZ_KAUFEN and not endspiel["fertig"] and st.get("feuer", 0) >= 4 and st["holz"] + holz_unterwegs < 5 \
                    and st["gold"] >= 60 + wirt.ruecklage(G)["gold"] and st["t"] - fruehpruefung.get("holz_gekauft", -999) >= 100:
                # v17 (22:57): untaetige Bauern bringen 0 - 5 Holz fuer 15 Gold (L11) = ein Arbeitsplatz; in jeder Bauweise
                fruehpruefung["holz_gekauft"] = st["t"]
                vor = vorrat(SP)["gold"]
                befehl({"spielbefehl": {"nr": 38, "werte": [0, 2]}}, 1.0, bis="SPIELBEFEHL")
                ereignis.append("HOLZ GEKAUFT (Feuer %d untaetig, Holz %d): Gold %d -> %d" % (st["feuer"], st["holz"], vor, vorrat(SP)["gold"]))
            if VOLLBESCHAEFTIGUNG and ENTSCHEIDER != "kausal" and not endspiel["fertig"] and st.get("feuer", 0) >= 2:
                # Lernlauf 1 (23:22): 93 % der Zeit >= 4 Bauern untaetig, am Ende 448 Holz + 510 Gold ungenutzt - ein Bauer am
                # Feuer bringt 0. Jede freie Hand bekommt sofort einen Arbeitsplatz (beste Art je Platz laut Planer, ohne
                # Horizont-Pruefung), bis zu 3 je Runde, Kosten ueber den Ruecklagen
                frei_b = st["feuer"]
                R = wirt.ruecklage(G)
                habe_v = {"holz": st["holz"] - R["holz"], "stein": st["stein"], "gold": st["gold"] - R["gold"]}
                gebaut_v = 0
                for k in ausbau.kandidaten(st, L, G):
                    if k["typ"] not in (3, 32, 7) or k["arbeiter"] > frei_b or gebaut_v >= 3:
                        continue
                    if all(habe_v[w] >= k["kosten"][w] for w in habe_v):
                        o = baue_schnell(k["typ"], k["ort"][0], k["ort"][1], 3, zweck="Vollbeschaeftigung")
                        ereignis.append("VOLL %s bei %s: %s (Feuer %d)" % (NACH_TYP[k["typ"]]["name"], k["ort"], o, st["feuer"]))
                        if o:
                            for w_v in habe_v:
                                habe_v[w_v] -= k["kosten"][w_v]
                            frei_b -= k["arbeiter"]
                            gebaut_v += 1
                        else:
                            ausbau.fehlschlag[(k["typ"], k["ort"])] = ausbau.fehlschlag.get((k["typ"], k["ort"]), 0) + 1
            if spam_offen and not endspiel["fertig"]:
                # E3: so viele Holzfaeller wie das Holz hergibt (ueber der B-Ruecklage), naechste zum Lager, mehrere je Baum
                holz = st["holz"] - wirt.ruecklage(G)["holz"]
                for _ in range(3):
                    if holz < 5 or hf_jetzt >= HOLZ_SPAM:
                        break
                    ort, weg_hf = ausbau._bester_ort(3, L, G)     # NICHT w - das ist der Waechter (E3-Absturz 23:03)
                    if ort is None:
                        ereignis.append("HOLZ-SPAM: kein Platz mehr (%d Holzfaeller)" % hf_jetzt)
                        break
                    o = baue_schnell(3, ort[0], ort[1], 1, zweck="E3 Holz-Spam")
                    ereignis.append("HOLZ-SPAM %d/%d bei %s (Weg %d): %s" % (hf_jetzt + 1, HOLZ_SPAM, ort, weg_hf, o))
                    if not o:
                        ausbau.fehlschlag[(3, ort)] = ausbau.fehlschlag.get((3, ort), 0) + 1
                        break
                    holz -= 5
                    hf_jetzt += 1
            # E4 (Daniel 23:03: "wenn die ersten 20 Holzfaeller Holz geladen haben, direkt Steinbrueche, so viele wie geht")
            stein_frei = (STEIN_PARALLEL or not spam_offen) and (not STEIN_MAX or "holz_geliefert" in fruehpruefung)
            if V14 and not endspiel["fertig"] and stein_frei:
                ereignis += v14_steinpflicht(st, G, wirt)   # vor allem anderen (Daniel 22:05); E3: erst nach dem Holz-Spam
                if "stein_besetzt" not in fruehpruefung:
                    pruef = ((20, V14_PLAN["brueche"]),) if JOCH_NACH_STEIN else ((20, V14_PLAN["brueche"]), (4, V14_PLAN["joche"]))
                    voll = all(BUCH.hat.get(n, 0) >= ARBEITER_JE[typ] for typ, orte in pruef
                               for o in orte for n in (steht_bei(G, typ, o) or [None]))
                    if voll:
                        fruehpruefung["stein_besetzt"] = st["t"]
                        ausbau.ohne = {20}
                        ereignis.append("STEINBRUECHE BESETZT bei Tick %d (6/6 + Joche 2/2) - Planer und restliche Holzfaeller frei" % st["t"])
                if "stein_besetzt" in fruehpruefung and hf_spaeter and st["holz"] - wirt.ruecklage(G)["holz"] >= 5:
                    o = hf_spaeter.pop(0)
                    ereignis.append("HOLZFAELLER aus dem Plan nach den Steinbruechen bei %s: %s" % (o, baue_schnell(3, o[0], o[1], 1, zweck="Plan")))
            tz = uhr("auftragsbuch", tz)
        # Markt und Verkauf gehoeren zur Wirtschaft, nicht zu den Assassinen (gold10k_1: mit assassinen=0 wurde 60.000
        # Ticks lang nichts verkauft - der Block stand im Assassinen-Teil; Gold am Ende 1.013, nur aus Steuern)
        if not [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 26] and runde % 20 == 2:
            ereignis.append("Markt gesetzt %s" % (baue_schnell(26, BERGFRIED[0], BERGFRIED[1], 25),))
        elif runde % 3 == 0:
            bremst = gold_bremst(st, G)
            # 12 Stein fuer die Kaserne nicht verkaufen, solange sie fehlt (v2 Tick 5.246: "verkauft: stein" und "Kaserne
            # gesetzt" in derselben Runde - danach reichte der Stein nicht mehr)
            kas_fehlt = streitkolben and not [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 9]
            v = verkaufen(st, ausbau.reserve()["stein"] + (12 if kas_fehlt else 0) + (prod.stein_bedarf() if prod else 0),
                          ausbau.messer, holz_verkaufen=bremst, eisen_reserve=10 ** 6 if prod else 0)
            if v:
                ereignis.append(v)
            # Daniel 07.10. (Lauf 14: 9 statt 10 Kaempfer, "hier fehlt ein Arbeiter, schlecht kalkuliert"): nach dem Endspiel-
            # Abriss lagen 59 Holz, daraus wurde ein Holzfaeller statt Gold - im Endspiel und ohne Holzbedarf nie
            if (not bremst and st["holz"] > HOLZ_RESERVE + 4 and not endspiel["fertig"]
                    and not fruehpruefung.get("holz_ueberfluessig")):
                ort, text = ausbau.holzfaeller_statt_verkauf(st, L, G)
                if ort:
                    ereignis.append("Holzfaeller statt Holzverkauf bei %s (Holz %d; %s)" % (ort, st["holz"], text))
        if trupp is not None:
            # Soeldnerlager (120 Gold) einmal bauen, dann Assassinen (Typ 73) anwerben bis zur Zahl; Mitglieder = alle eigenen 73er
            posten = [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 8]
            if not posten and (soeldner is None or runde % 10 == 0) and not ausbau.braucht_gold:
                # nicht am Lagerplatz (9i: Markt/Soeldnerlager belegten ihn - 14 Holzfaeller warteten Tick 4500-9035)
                soeldner = baue_schnell(8, BERGFRIED[0], BERGFRIED[1], 25)
                ereignis.append("Soeldnerlager gesetzt %s (Gold %d)" % (soeldner, st["gold"]))
            elif posten and st["gold"] >= 70 + wirt.ruecklage(G)["gold"] and st["feuer"] >= 1 and (assassinen < 0 or geworben < assassinen) and not ausbau.braucht_gold \
                    and not wirt.a_offen(G):   # Daniel 23:09: Farmen nicht vergessen - erst die fehlenden A-Plantagen (45 Gold)   # erst rollen (Daniel 18:51/19:05)
                befehl({"werbe": {"typ": 73, "gebaeude": posten[0]}}, 1.0, bis="WERBE")
                geworben += 1
                if geworben == 1 or geworben % 5 == 0:     # der erste zaehlt einzeln (gewinn_5: Zeitpunkt fehlte)
                    ereignis.append("%d Assassinen angeworben (Gold jetzt %d)" % (geworben, st["gold"]))
            if posten and runde % 50 == 0:     # ganz_1: in 28.700 Ticks nur 1 Assassine - welche Bedingung bremst?
                ereignis.append("ANWERBEN-BREMSE: Gold %d (braucht %d), Feuer %d, Planer braucht Gold %s, A-Farmen offen %d" % (
                    st["gold"], 70 + wirt.ruecklage(G)["gold"], st["feuer"], bool(ausbau.braucht_gold), len(wirt.a_offen(G))))
            tz = uhr("bauen_werben_verkauf", tz)
            trupp.aufnehmen([n for n, e in L.items() if e["besitzer"] == SP and e["typ"] == 73])
            # nur begehbare Plaetze (9g: Gebaeudemitten waren nicht begehbar - die Wartenden blieben im Schussfeld)
            erg = trupp.schritt(L, G, sichere_orte=[tuple(plan["lager_mitte"]), BERGFRIED], tick=st.get("t"))
            if isinstance(erg, tuple):          # Einzeln: Befehle der Runde gesammelt in EINEM Aufruf
                erg, liste = erg
                if liste:
                    sende({"befehle": [dict(b, player=1, id=neue_id()) for b in liste]}, 1.0,
                          bis="ANGRIFF" if any("angriff" in b for b in liste) else "HALTEN")
            ereignis += erg
            if trainingsstand and trupp.lordtrupp.get("phase") == "sammeln":
                punkt = trupp.lordtrupp.get("sammelpunkt")
                angekommen = [n for n in trupp.lordtrupp["mitglieder"] if n in L and max(
                    abs(L[n]["x"] - punkt[0]), abs(L[n]["y"] - punkt[1])) <= trupp.LORD_SAMMEL_R]
                # trainingsstand_ab: so viele muessen am Treffpunkt stehen (bedarf_partie_2: in der ganzen Partie kamen nie
                # 40 zusammen, hoechstens 27 - die Lage, in der wirklich angegriffen wuerde, braucht einen eigenen Stand)
                if len(angekommen) >= trainingsstand_ab:
                    befehl({"pause": True}, 0.5)
                    from speichern import speichere
                    pfad = speichere(trainingsstand)
                    schreib("TRAININGSSTAND gesichert: %s mit %d gemeinsam angekommenen Assassinen bei Tick %d -> %s" % (
                        trainingsstand, len(angekommen), st["t"], pfad))
                    break
            tz = uhr("assassinen", tz)
        if V14 and streitkolben:
            # v14-Fruehabbruch (Daniel 22:05: "ich brauche nicht noch einen Run, wo nicht zwei Steinbrueche direkt neben dem
            # Vorratslager sind"): nach dem Holz-Zeitplan stehen beide Steinbrueche + Joche bei ~350 (30 Holz bei 120,
            # +28 je 110 Ticks; Kornspeicher 5, Steinbruch 25, A-Plantagen 9, Joch 5, Steinbruch 25, Joch 5)
            if st["t"] >= V14_STEIN_BIS and not fruehpruefung.get("stein") and not HOLZ_SPAM:   # E3: Steinbrueche absichtlich spaeter
                fehlt = ["%s %s" % (NACH_TYP[typ]["name"], o) for typ, o in [(20, q) for q in V14_PLAN["brueche"]] +
                         ([] if JOCH_NACH_STEIN else [(4, j) for j in V14_PLAN["joche"]]) if not steht_bei(G, typ, o)]
                if fehlt:
                    schreib("FRUEHABBRUCH bei Tick %d: fehlt %s" % (st["t"], ", ".join(fehlt)))
                    break
                fruehpruefung["stein"] = True
                schreib("PRUEFUNG bestanden bei Tick %d: beide Steinbrueche + Joche stehen an den Plan-Plaetzen" % st["t"])
            lager_bis = min(2000, wirt.B_tick + 400) if wirt.B_tick else 2000      # v15: Umzug erst nach B
            teile = [g for g in G.values() if g["besitzer"] == SP and g["typ"] == 10]
            if not teile:
                fruehpruefung.setdefault("ohne_lager_seit", st["t"])
                if st["t"] - fruehpruefung["ohne_lager_seit"] > 150:
                    schreib("FRUEHABBRUCH bei Tick %d: seit Tick %d kein Lager (Holz und Stein kommen nicht an)" % (
                        st["t"], fruehpruefung["ohne_lager_seit"]))
                    break
            else:
                fruehpruefung.pop("ohne_lager_seit", None)
            if STEIN_ZUERST and st["t"] >= 1500 and "stein_besetzt" not in fruehpruefung:
                schreib("FRUEHABBRUCH bei Tick %d: Steinbrueche + Joche nicht besetzt (%s)" % (st["t"], BUCH.stand(G, st)))
                break
            if st["t"] >= lager_bis and not fruehpruefung.get("lager") and UMZUG != "nein":
                neu = steht_bei(G, 10, V14_PLAN["lager"], 6)   # 23:40: Platzwahl haelt Abstand zum Steinhaufen -> (91,268) statt (89,270)
                alt = [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 10 and
                       max(abs(g["x"] - BASIS_LAGER[0]), abs(g["y"] - BASIS_LAGER[1])) <= 6]
                if not neu or alt:
                    schreib("FRUEHABBRUCH bei Tick %d: Lager nicht umgezogen (neu bei %s: %s, alt am Bergfried: %s)" % (
                        st["t"], V14_PLAN["lager"], neu or "keins", alt or "weg"))
                    break
                fruehpruefung["lager"] = True
                schreib("PRUEFUNG bestanden bei Tick %d: neues Lager steht bei %s, altes weg" % (st["t"], V14_PLAN["lager"]))
        if streitkolben and not V14 and not EXPERIMENT and not fruehpruefung.get("ok4000"):   # Lernkreis: diese Regel wuergte alle 4 1-Jahr-Versuche ab
            # schaerfer (Daniel 21:56: "er baut nur einen Steinbruch, hier wuerde ich auch abbrechen ... gleiches fuer
            # andere nicht optimal platzierte Gebaeude"): genug Steinbrueche, keiner weit vom Lager
            lager_teile = [g for g in G.values() if g["besitzer"] == SP and g["typ"] == 10]
            weit = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] == SP and g["typ"] == 20 and lager_teile and
                    min(max(abs(g["x"] - l["x"]), abs(g["y"] - l["y"])) for l in lager_teile) > 40]
            # strenger (Daniel 21:57: "wenn das so frueh passiert und die Gewinnmarge so gering ist, musst du strenger sein")
            soll = 3 if st["t"] >= FRUEH_TICK else 2 if st["t"] >= 1500 else 0
            if st.get("G20", 0) < soll or (weit and st["t"] >= FRUEH_TICK):
                schreib("FRUEHABBRUCH bei Tick %d: %d Steinbrueche (soll %d)%s" % (st["t"], st.get("G20", 0), soll,
                        ", weit vom Lager: %s" % weit if weit else ""))
                break
            if st["t"] >= FRUEH_TICK:
                fruehpruefung["ok4000"] = True
        if streitkolben and st["t"] >= FRUEH_TICK and not EXPERIMENT and not fruehpruefung.get("ok"):
            # Fruehabbruch (Daniel 21:55: "wenn du merkst, dass schon der Steinbruch nicht richtig gesetzt ist, muesstest du
            # eigentlich schon aufhoeren ... das sind alles verschwendete Zeiten/Versuche")
            fehlt = []
            if not st.get("G20", 0) and not HOLZ_SPAM:          # E3/E4: Steinbrueche absichtlich nach dem Holz
                fehlt.append("kein Steinbruch")
            if [n for n in wirt.alt if n in G and G[n]["typ"] == 10 and max(abs(G[n]["x"] - BASIS_LAGER[0]), abs(G[n]["y"] - BASIS_LAGER[1])) <= 6]:
                fehlt.append("Lager nicht umgezogen")
            if wirt.B_offen:
                fehlt.append("B-Seasoning offen")
            if fehlt:
                schreib("FRUEHABBRUCH bei Tick %d: %s" % (st["t"], ", ".join(fehlt)))
                break
            fruehpruefung["ok"] = True
            schreib("FRUEHPRUEFUNG bestanden bei Tick %d (Steinbruch, Lager umgezogen, B-Seasoning)" % st["t"])
        if streitkolben and endspiel.get("abbruch"):
            schreib("FRUEHABBRUCH bei Tick %d: %s" % (st["t"], endspiel["abbruch"]))
            break
        if streitkolben:
            # Daniel 00:54: "Gerber und Kaesereien machen keinen Sinn, wenn kein Platz fuer Bevoelkerung ist, wenn's als letztes
            # gebaut wird" - mit Kasse gehen die Leute am Ende weg; Leder wird im Endspiel gekauft
            if leder is not None and KASSE == "nein" and not endspiel["fertig"] and not (BUCH is not None and HOLZ_SPAM and
                    sum(1 for g in G.values() if g["besitzer"] == SP and g["typ"] == 3) < HOLZ_SPAM):
                ereignis += leder.schritt(st, G, wirt)
            ereignis += bilanz_schritt(st, L, G, ausbau, streitkolben, endspiel, runde, kaempfer_marken)
            if not endspiel["fertig"] and weg != "bilanz":     # weg=bilanz: nur Wirtschaft + Bilanz-Endspiel (v5)
                ereignis += prod.schritt(st, G, wirt) if prod else ruestung_kaufen(st, G, wirt, ausbau, streitkolben, kaempfer_marken)
            if st.get("T26", 0) >= streitkolben:
                schreib("ZIEL %d Streitkolbenkaempfer erreicht bei Tick %d" % (streitkolben, st["t"]))
                break
            tz = uhr("ruestung", tz)
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
        if not (streitkolben and endspiel["fertig"]):    # nach dem Endspiel ruht die Wirtschaft (v6: baute A-Plantagen nach)
            ereignis += wirt.schritt(st, L, G)
            ereignis += ausbau.schritt(st, L, G, runde)
        tz = uhr("wirtschaft", tz)
        bedarf = sum(ARBEITER_JE[t] * st.get("G%d" % t, 0) for t in ARBEITER_JE)
        puffer = streitkolben and not endspiel["fertig"] and ENTSCHEIDER != "kausal" and wohnraum_fehlt(st, G)[0]   # Huetten vorab, aber nur mit Arbeit (23:21)
        if st["holz"] >= 5 + wirt.ruecklage(G)["holz"] and ((bedarf > st["platz"] and st["feuer"] < 2) or puffer or (trupp is not None and st["feuer"] == 0 and st["platz"] - st["leute"] <= 2)):
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
    schreib(ausbau.bericht())
    if BUCH is not None:
        BUCH.abgleich(G, L, st)
        schreib(BUCH.stand(G, st))
    try:
        # Daniel 22:44: "ALLES festhalten" - jeder Lauf wird vermessen und sein Wissen an daten/wissen_ablauf.jsonl gehaengt
        import ablaufanalyse as AA
        erg, _ = AA.analyse(lage.pfad, SP)
        schreib(AA.text(erg))
        schreib("Wissen angehaengt: %s" % AA.wissen_anhaengen(erg))
    except Exception as ex:
        schreib("ABLAUFANALYSE fehlgeschlagen: %r" % ex)
    ausbau.sichern(os.path.join(D, "ertrag_gelernt_%s_i%d.json" % (time.strftime("%Y%m%d_%H%M%S"), INSTANZ)))

def main():
    arg = dict(a.split("=") for a in sys.argv[1:])
    import kennung                    # Daniel 20:46: sofort sehen, welcher Code-Stand diese Partie spielt
    schreib(kennung.zeile())
    # Plan je Startstand (Daniel 05.10. 18:55: erst schauen, wo der Bergfried steht) - karten_holen.py + eroeffnung.py start=...
    datei = os.path.join(D, arg.get("plan", "eroeffnung_plan_M19.json"))
    plan = json.load(open(datei, encoding="utf-8")); plan["_datei"] = datei
    global BASIS, BERGFRIED
    BASIS = plan.get("spielstand", BASIS)
    BERGFRIED = tuple(plan.get("bergfried_eingang", BERGFRIED))
    import waechter
    waechter.BERGFRIED_EINGANG = BERGFRIED
    global LEERE_KI, V14
    LEERE_KI = arg.get("leere_ki", "nein") == "ja"
    global HF_VORAB, STEIN_ZUERST, HF_MAX, JE_ARBEITER, UMZUG, EXPERIMENT, HUETTEN_JE_BAUM, HOLZ_KAUFEN
    HUETTEN_JE_BAUM = int(arg["holzfaeller_je_baum"]) if arg.get("holzfaeller_je_baum") else None
    HOLZ_KAUFEN = arg.get("holz_kaufen", "nein") == "ja"
    global HOLZ_SPAM, STEIN_MAX, JOCH_NACH_STEIN, STEIN_PARALLEL, HUETTEN_VORAUS, VOLLBESCHAEFTIGUNG
    VOLLBESCHAEFTIGUNG = arg.get("vollbeschaeftigung", "nein") == "ja"
    global ENTSCHEIDER, ZIEL_TICK, B_VERSATZ, STEUER_RUNTER, STEUER_ENDE, BEV_ZIEL, KASSE, KASSE_GRENZE, PENNER, KASSE_STUFE, SCHUB, AUFLOESEN, EINZELKAUF
    BEV_ZIEL = int(arg.get("bevoelkerung_ziel", 0))
    KASSE = arg.get("kasse", "nein")
    KASSE_GRENZE = int(arg.get("kasse_grenze", 50))
    PENNER = int(arg.get("penner", 20))
    KASSE_STUFE = int(arg.get("kasse_stufe", 11))
    SCHUB = arg.get("schub", "nein") == "ja"
    AUFLOESEN = arg.get("aufloesen", "nein") == "ja"
    EINZELKAUF = arg.get("einzelkauf", "nein") == "ja"
    STEUER_RUNTER = int(arg.get("steuer_runter", 95))
    STEUER_ENDE = arg.get("steuer_ende", "nein")
    B_VERSATZ = None if arg.get("b_versatz", "reif") == "reif" else int(arg["b_versatz"])
    ENTSCHEIDER = arg.get("entscheider", "regeln")
    ZIEL_TICK = int(arg.get("ziel_tick", 9400))
    HOLZ_SPAM = int(arg.get("holz_spam", 0))
    STEIN_MAX = arg.get("stein_max", "nein") == "ja"
    JOCH_NACH_STEIN = arg.get("joch_nach_stein", "nein") == "ja"
    STEIN_PARALLEL = arg.get("stein_parallel", "nein") == "ja"
    HUETTEN_VORAUS = arg.get("huetten_voraus", "nein") == "ja"
    UMZUG = arg.get("umzug", "nachb")
    EXPERIMENT = arg.get("experiment", "nein") == "ja"
    if arg.get("holzfaeller_vorab"):
        HF_VORAB = int(arg["holzfaeller_vorab"])
    if arg.get("holzfaeller_max"):
        HF_MAX = int(arg["holzfaeller_max"])
    JE_ARBEITER = arg.get("je_arbeiter", "nein") == "ja"
    STEIN_ZUERST = arg.get("steinbruch_zuerst", "nein") == "ja"
    if arg.get("v14", "nein") == "ja":
        V14 = V14_PLAN
        plan["lager"], plan["lager_mitte"] = list(V14_PLAN["lager"]), [V14_PLAN["lager"][0] + 2, V14_PLAN["lager"][1] + 2]
    if arg.get("start"):
        print("Tick", lade_stand(arg["start"], mit_bild=False))
        befehl({"eigenerPlatz": SP}, 0.8)
    elif arg.get("nur_phase2", "nein") != "ja":
        phase1(plan, int(arg.get("tempo", 40)), mit_posten=int(arg.get("assassinen", 0)) != 0)   # Daniel 22:52: jede Partie ab Tick 0
    try:
        phase2(plan, int(arg.get("minuten", 10)), int(arg.get("tempo", 40)), arg.get("waechter", "nein") == "ja",
               int(arg["bis_tick"]) if arg.get("bis_tick") else None, int(arg.get("assassinen", 0)), arg.get("trainingsstand"),
               int(arg.get("trainingsstand_ab", 40)), int(arg["gold_ziel"]) if arg.get("gold_ziel") else None,
               int(arg.get("streitkolben", 0)), arg.get("weg", "kauf"))
    except BaseException as e:
        # JEDER Abbruch haelt das Spiel an (06.10. 23:04, Daniel "Abbrechen funktioniert nicht": E3 stuerzte bei Tick 353 mit
        # einem AttributeError ab - gefangen wurde nur RuntimeError, das Spiel lief ohne Lenker bis 5.420 weiter)
        import traceback
        import befehl as befehlskanal
        befehlskanal.STRENG = False
        try:
            befehl({"pause": True}, 0.8)
        except Exception:
            pass
        traceback.print_exc()
        print("ABBRUCH - Spiel angehalten -", repr(e), flush=True)
        sys.exit(1)

if __name__ == "__main__":
    import befehl as befehlskanal
    befehlskanal.belege()
    try:
        main()
    finally:
        befehlskanal.freigeben()
