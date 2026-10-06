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
ARBEITER_JE = {3: 1, 32: 1, 30: 1, 31: 1, 33: 1, 20: 3, 4: 1, 5: 2, 7: 1, 6: 1}   # Betrieb -> Arbeiter (Steinbruch 3, Mine 2: Annahme)
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
    holz_bauten = [(19, tuple(plan["kornspeicher"])), (26, MARKT)] + [(3, tuple(p)) for p in plan["holzfaeller"]]
    if plan.get("stein"):
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
        if warte_bis(lambda: vorrat(SP)["gold"] >= 190, "Gold fuer Posten + Assassine", 5, pflicht=False):
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
    nach = rest + [r for r in fp if r[0] == 32]
    g2, f2 = baue_viele(nach, SP, live=True) if nach else ([], [])
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

def verkaufen(st, stein_reserve=None, messer=None, holz_verkaufen=False):
    """Je Runde hoechstens ein Verkauf je Ware (Spielbefehl 38, verkaufen=1). Gibt Text oder None.
    stein_reserve: Bedarf der naechsten geplanten Eisenmine (Daniel 05.10. 19:44: Stein bis darauf verkaufen);
    messer: Ertragsmesser - bekommt jedes verkaufte Los (fuer die Buchfuehrung Zugang = Bestand + Verkauft + Verbaut)."""
    teile = []
    # Holz nur, solange Gold das Anwerben bremst (holz_verkaufen); sonst geht der Ueberschuss in Holzfaeller. Daniel
    # 06.10.: erst "statt Holz verkaufen mehr Holzfaeller", nach holz_partie_1/2 (20. Assassine ~4.000 Ticks spaeter,
    # kein Sieg) 19:33 "ja, vorerst" - gegen mehrere Gegner braucht es spaeter stabiles Wachstum statt Verkauf.
    holz = (("holz", HOLZ_RESERVE),) if holz_verkaufen else ()
    for ware, reserve in holz + (("stein", STEIN_RESERVE if stein_reserve is None else stein_reserve), ("eisen", 0),
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

def phase2(plan, minuten, tempo, mit_waechter=False, bis_tick=None, assassinen=0, trainingsstand=None, trainingsstand_ab=40,
           gold_ziel=None):
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
    ausbau = Ertragsplaner(plan, SP, baue_schnell, wirt, s32(peek(PD + 0x2188)[0]), ende=bis_tick, protokoll=lernlog, wegtest=wegtest)   # lernt im Spiel (Daniel 19:44)

    def gold_bremst(st, G):
        """Es sollen Assassinen her, aber das Gold reicht nicht fuer den naechsten (70 + B-Ruecklage)."""
        return bool(assassinen) and (assassinen < 0 or geworben < assassinen) and st.get("gold", 0) < 70 + wirt.ruecklage(G)["gold"]

    def holz_verwerten(st, L, G):
        """Altes Lager: Holz verkaufen, solange Gold das Anwerben bremst (Daniel 06.10. 19:33, vorerst); sonst Holzfaeller."""
        if gold_bremst(st, G):
            befehl({"spielbefehl": {"nr": 38, "werte": [1, WAREN_NR["holz"]]}}, 1.0, bis="SPIELBEFEHL")
            ausbau.messer.verkauft("holz")
            return "verkauft", "Gold bremst das Anwerben"
        return ausbau.holzfaeller_statt_verkauf(st, L, G)
    wirt.holz_verbauen = holz_verwerten
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
    while time.time() < ende and not os.path.exists(os.path.join(HIER, "STOP")):
        tz = time.time()
        befehlskanal.belege()
        st, L, G = runde_lesen()
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
        ausbau.beobachte(st, L, G)        # Buchfuehrung des Planers: Zugang je Ware seit der letzten Runde
        eig = [g for g in G.values() if g["besitzer"] == SP]
        gebs = [(g["x"] + NACH_TYP.get(g["typ"], {"b": 2})["b"] // 2, g["y"] + NACH_TYP.get(g["typ"], {"b": 2})["b"] // 2)
                for g in eig if g["typ"] in EIGENE_ARTEN]
        tz = time.time()
        ereignis = w.schritt(L, gebs, ausgenommen=trupp.mitglieder if trupp else ()) if w is not None else []
        tz = uhr("waechter", tz)
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
            if not [n for n, g in G.items() if g["besitzer"] == SP and g["typ"] == 26] and runde % 20 == 2:
                ereignis.append("Markt gesetzt %s" % (baue_schnell(26, BERGFRIED[0], BERGFRIED[1], 25),))
            elif runde % 3 == 0:
                bremst = gold_bremst(st, G)
                v = verkaufen(st, ausbau.reserve()["stein"], ausbau.messer, holz_verkaufen=bremst)
                if v:
                    ereignis.append(v)
                if not bremst and st["holz"] > HOLZ_RESERVE + 4:     # Gold reicht: Holzueberschuss -> Holzfaeller
                    ort, text = ausbau.holzfaeller_statt_verkauf(st, L, G)
                    if ort:
                        ereignis.append("Holzfaeller statt Holzverkauf bei %s (Holz %d; %s)" % (ort, st["holz"], text))
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
        ereignis += ausbau.schritt(st, L, G, runde)
        tz = uhr("wirtschaft", tz)
        bedarf = sum(ARBEITER_JE[t] * st.get("G%d" % t, 0) for t in ARBEITER_JE)
        if st["holz"] >= 5 + wirt.ruecklage(G)["holz"] and (bedarf > st["platz"] or (trupp is not None and st["feuer"] == 0 and st["platz"] - st["leute"] <= 2)):
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
    global LEERE_KI
    LEERE_KI = arg.get("leere_ki", "nein") == "ja"
    if arg.get("start"):
        print("Tick", lade_stand(arg["start"], mit_bild=False))
        befehl({"eigenerPlatz": SP}, 0.8)
    elif arg.get("nur_phase2", "nein") != "ja":
        phase1(plan, int(arg.get("tempo", 40)), mit_posten=int(arg.get("assassinen", 0)) != 0)   # Daniel 22:52: jede Partie ab Tick 0
    try:
        phase2(plan, int(arg.get("minuten", 10)), int(arg.get("tempo", 40)), arg.get("waechter", "nein") == "ja",
               int(arg["bis_tick"]) if arg.get("bis_tick") else None, int(arg.get("assassinen", 0)), arg.get("trainingsstand"),
               int(arg.get("trainingsstand_ab", 40)), int(arg["gold_ziel"]) if arg.get("gold_ziel") else None)
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
