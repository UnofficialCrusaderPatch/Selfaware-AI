# -*- coding: utf-8 -*-
"""Kausalmodell (Daniel 06.10. 23:27: "da wirklich alles Kausalketten hat, aber diese dynamisch sein muessen, heisst es auch,
es muss dynamische Antworten fuer alles geben"; 23:13: "die KI lernt selbst").

Statt fester Schwellen ("Huette, wenn < 6 frei", "Joch nach dem ersten Stein") rechnet der Entscheider fuer jede moegliche
Handlung die Wirkungskette bis zum Zieltick aus der AKTUELLEN Lage und baut, was dort am meisten Gold-Wert bringt:

  Bauer verfuegbar   -> sofort (am Feuer) oder nach Spawn (SPAWN Ticks je Bauer, nur wenn Wohnraum frei)
  Weg zum Arbeitsort -> Abstand Feuer -> Platz x GEHEN Ticks
  erster Ertrag      -> Anlauf der Art (gemessen) + Weg zum Abgabeort
  Ertrag bis Ziel    -> Zyklen bis zum Zieltick x Menge x Verkaufswert
  Wert der Handlung  = Ertrag bis Ziel + Abrissrueckgabe (Haelfte) - Kosten

Huette: Wert = Wert der Arbeit, die die dadurch frueher gespawnten Bauern bis zum Ziel noch leisten - 0, wenn schon Bauern
untaetig sind (die Arbeit braucht keinen neuen Menschen) oder kein Arbeitsplatz auf sie wartet.

Alle Groessen kommen aus MODELL (gemessene Werte, Wissensregister). Der Lernkreis vergleicht nach jedem Lauf Vorhersage
und Wirklichkeit (erste Lieferung, Ertrag) und schreibt korrigierte Werte nach daten/kausal_modell.json - der naechste
Lauf rechnet damit.
"""
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
DATEI = os.path.join(HIER, "..", "daten", "kausal_modell.json")

# gemessene Startwerte (Wissensregister, 06.10.) - werden durch daten/kausal_modell.json ersetzt, sobald gelernt
MODELL = {
    "spawn_ticks": 52,            # L7: ~1 Bauer je 52 Ticks (Wohnraum frei, Beliebtheit hoch)
    "gehen_ticks": 24,            # G1/L1: 24-26 Ticks je Feld
    "huette_platz": 8,            # +8 Wohnplaetze je Huette (Platz 26 -> 34 -> 42 ...)
    # Art: (Anlauf ohne Wege, Zyklus ohne Wege, Menge je Zyklus, Gold je Stueck, Abgabe-Wege je Zyklus)
    3: {"anlauf": 2240, "zyklus": 1860, "menge": 18, "wert": 1.0},     # L10/L9 Holzfaeller: 3 Staemme + 3x Saegen, 18 Holz
    32: {"anlauf": 2224, "zyklus": 790, "menge": 3, "wert": 3.0},      # Apfel: Startwert Anlauf, 3,8 je 1.000 (23/1000 fuer 6)
    7: {"anlauf": 4427, "zyklus": 1000, "menge": 3, "wert": 1.0},      # Jaeger: Startwert 3,07 je 1.000, Fleisch 1 Gold
}


def lade():
    if os.path.exists(DATEI):
        try:
            MODELL.update({int(k) if k.isdigit() else k: v for k, v in json.load(open(DATEI, encoding="utf-8")).items()})
        except Exception:
            pass
    return MODELL


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ertrag_bis(typ, t_start, ziel, weg_abgabe):
    """Gold-Wert, den ein Betrieb der Art typ, dessen Arbeiter bei t_start an seinem Platz steht, bis ziel abliefert."""
    m = MODELL[typ]
    g = MODELL["gehen_ticks"]
    t1 = t_start + m["anlauf"] + weg_abgabe * g                      # erste Lieferung
    if t1 > ziel:
        return 0.0, t1
    zyklus = m["zyklus"] + 2 * weg_abgabe * g
    n = 1 + int((ziel - t1) // max(1, zyklus))
    return n * m["menge"] * m["wert"], t1


def wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_ort, kosten, bauer_ab):
    """Netto-Wert bis ziel: Ertrag + halbe Kosten zurueck (Abriss im Endspiel) - Kosten. bauer_ab: Tick, ab dem ein Bauer
    fuer diesen Betrieb frei ist (jetzt, wenn einer am Feuer steht; sonst nach Spawn)."""
    g = MODELL["gehen_ticks"]
    an_ort = bauer_ab + schach(feuer_ort, ort) * g
    ertrag, t1 = ertrag_bis(typ, an_ort, ziel, schach(ort, abgabe_ort))
    k = sum(kosten.get(w, 0) * (1 if w != "stein" else 5) for w in ("holz", "stein", "gold"))
    return ertrag + k / 2.0 - k, t1


def bauer_ab(jetzt, feuer, frei_wohn, rang):
    """Wann ist der rang-te zusaetzliche Bauer (0 = erster) verfuegbar? Am Feuer sofort; dann Spawn, solange Wohnraum frei;
    sonst nie (None)."""
    if rang < feuer:
        return jetzt
    k = rang - feuer
    if k < frei_wohn:
        return jetzt + (k + 1) * MODELL["spawn_ticks"]
    return None


def entscheide(jetzt, ziel, st, kandidaten, feuer_ort, abgabe_orte, huette_kosten):
    """kandidaten: [(typ, ort, kosten, arbeiter)] - die besten Plaetze je Art (vom Planer). Gibt eine Liste von Handlungen
    [(wert, art, ort, text)] in Wertfolge, nur mit positivem Wert und im Rahmen von Holz/Gold."""
    feuer, frei_wohn = st.get("feuer", 0), max(0, st.get("platz", 0) - st.get("leute", 0))
    holz, gold, stein = st.get("holz", 0), st.get("gold", 0), st.get("stein", 0)
    handlungen = []
    rang = 0
    bewertet = []
    for typ, ort, kosten, arbeiter in kandidaten:
        if typ not in MODELL:
            continue
        ab = bauer_ab(jetzt, feuer, frei_wohn, rang)
        if ab is None:
            bewertet.append((typ, ort, kosten, None, None))
            continue
        w, t1 = wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_orte.get(typ, ort), kosten, ab)
        bewertet.append((typ, ort, kosten, w, t1))
    bewertet.sort(key=lambda x: -(x[3] if x[3] is not None else -1e9))
    for typ, ort, kosten, w, t1 in bewertet:
        if w is None or w <= 0:
            continue
        if holz < kosten.get("holz", 0) or gold < kosten.get("gold", 0) or stein < kosten.get("stein", 0):
            continue
        holz -= kosten.get("holz", 0)
        gold -= kosten.get("gold", 0)
        stein -= kosten.get("stein", 0)
        handlungen.append((w, typ, ort, "Wert %.0f bis Tick %d, erste Lieferung %d" % (w, ziel, t1)))
        rang += 1
    # Huette: lohnt nur, wenn ein Arbeitsplatz mit positivem Wert auf einen Bauern wartet, den es ohne Wohnraum nicht gibt
    wartet = [x for x in bewertet if x[3] is None]
    if wartet and feuer == 0 and holz >= huette_kosten:
        # Wert: der beste wartende Betrieb, gerechnet mit Spawn nach dem Bau (Huette ~ sofort, Spawn danach)
        best = None
        for typ, ort, kosten, _, _ in wartet:
            w, t1 = wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_orte.get(typ, ort), kosten, jetzt + MODELL["spawn_ticks"])
            if best is None or w > best[0]:
                best = (w, typ, t1)
        if best and best[0] > huette_kosten:
            handlungen.append((best[0] - huette_kosten, 1, None, "Huette: wartender Betrieb Art %d bringt %.0f bis Tick %d" % (
                best[1], best[0], ziel)))
    return handlungen
