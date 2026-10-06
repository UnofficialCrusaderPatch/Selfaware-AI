# -*- coding: utf-8 -*-
"""Lernkreis (Daniel 06.10. 23:13: "das End-End-Ziel ... es geht darum, dass die KI selbst lernt, nicht wir fuer sie";
23:12: "es waere schoen, wenn solche Punkte dir auch auffallen wuerden nach jedem Run").

Die KI spielt, misst und entscheidet selbst, welcher Versuch als naechstes kommt:
  1. Strategie = Wert je Knopf (KNOEPFE). Erster Lauf: Grundstrategie; danach immer von der BESTEN bisherigen Strategie
     aus genau EIN Knopf anders - nie eine Kombination, die schon gespielt wurde (Daniel 21:59: keine gleichen Laeufe).
  2. Lauf: erstes_spiel.py bis zum Ziel (10 Streitkolbenkaempfer) oder bis_tick.
  3. Nachschau aus dem Lageprotokoll (jede Runde): Ticks mit vollem Wohnraum, mit >= 4 untaetigen Bauern, ohne Holz,
     mit liegendem Gold (>= 100) bei fehlendem Holz; erste Holz- und Steinlieferung; Abbruchgrund.
  4. Note (kleiner = besser): Tick des 10. Kaempfers; sonst bis_tick + fehlendes Gold / Zuwachs der letzten 2.000 Ticks
     (geschaetzte Restzeit, im Ergebnis als "geschaetzt" markiert); Fruehabbruch = 30.000.
  5. Wahl des naechsten Knopfs: Gewicht 1 fuer jeden Knopf, +3 fuer Knoepfe, die zum groessten Verlust der Nachschau
     passen (VERLUST_KNOEPFE); Wert des Knopfs zufaellig unter den noch nicht gespielten.
  6. Alles in daten/lernen.jsonl (je Lauf: Strategie, Note, Nachschau, Datei) und daten/lernen_wissen.json (je Knopfwert:
     beobachtete Notenaenderung gegen die Ausgangsstrategie).
Aufruf: python lernen.py laeufe=5 [bis_tick=14000] [start=grund|bester]
"""
import json
import os
import random
import re
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
sys.path.insert(0, HIER)

KNOEPFE = {
    "v14": ["ja", "nein"],               # nein = Aufbau wie v5 (Bestzeit 11.930): Lager am Bergfried, Planer allein
    "umzug": ["frueh", "nachb", "nein"],
    "holzfaeller_vorab": [0, 4, 8, 14],
    "holz_spam": [0, 10, 20, 30],
    "holzfaeller_je_baum": [1, 2, 4],
    "holzfaeller_max": [20, 30, 45, 70],
    "steinbruch_zuerst": ["ja", "nein"],
    "stein_parallel": ["ja", "nein"],
    "joch_nach_stein": ["ja", "nein"],
    "huetten_voraus": ["ja", "nein"],
    "holz_kaufen": ["ja", "nein"],
    "je_arbeiter": ["ja", "nein"],
    "vollbeschaeftigung": ["ja", "nein"],
}
GRUND = {"v14": "ja", "umzug": "frueh", "holzfaeller_vorab": 4, "holz_spam": 20, "holzfaeller_je_baum": 4, "holzfaeller_max": 30,
         "steinbruch_zuerst": "nein", "stein_parallel": "ja", "joch_nach_stein": "ja", "huetten_voraus": "ja",
         "holz_kaufen": "ja", "je_arbeiter": "ja", "vollbeschaeftigung": "nein"}
FEST = ["leere_ki=ja", "tempo=100", "minuten=60", "streitkolben=10", "weg=bilanz", "experiment=ja"]
REFERENZ = dict(GRUND, v14="nein")      # zweiter Lauf: die bisher schnellste Bauweise (v5) als Messlatte im selben Code
# welche Knoepfe zu welchem gemessenen Verlust gehoeren (Vorwissen; die Wirkung misst der Kreis selbst)
VERLUST_KNOEPFE = {
    "wohnraum_voll": ["huetten_voraus", "holz_kaufen"],
    "bauern_untaetig": ["vollbeschaeftigung", "holz_kaufen", "holz_spam", "holzfaeller_je_baum", "je_arbeiter"],
    "gold_liegt_holz_fehlt": ["holz_kaufen", "holz_spam"],
    "ohne_holz": ["holz_spam", "holzfaeller_vorab", "holzfaeller_je_baum", "holzfaeller_max", "umzug"],
    "stein_spaet": ["steinbruch_zuerst", "stein_parallel", "joch_nach_stein", "umzug"],
}


def nachschau(lage):
    """Verluste und Marken aus dem Lageprotokoll (jede Runde)."""
    from lageprotokoll import runden
    m = {"wohnraum_voll": 0, "bauern_untaetig": 0, "ohne_holz": 0, "gold_liegt_holz_fehlt": 0,
         "erstes_holz_geliefert": None, "erster_stein": None, "ticks": 0}
    vor, lad_vor = None, {}
    for t, st, E, G in runden(lage):
        if vor is not None:
            dt = t - vor
            m["ticks"] += dt
            if st.get("leute", 0) >= st.get("platz", 0):
                m["wohnraum_voll"] += dt
            if st.get("feuer", 0) >= 4:
                m["bauern_untaetig"] += dt
            if st.get("holz", 0) < 5:
                m["ohne_holz"] += dt
                if st.get("gold", 0) >= 100:
                    m["gold_liegt_holz_fehlt"] += dt
        lad = {e["nr"]: e.get("ladung", 0) for e in E if e["besitzer"] == 1 and e["typ"] == 3}
        if m["erstes_holz_geliefert"] is None and any(lad_vor.get(n, 0) > l for n, l in lad.items()):
            m["erstes_holz_geliefert"] = t
        lad_vor = lad
        if m["erster_stein"] is None and st.get("stein", 0) > 0:
            m["erster_stein"] = t
        vor = t
    return m


def note_aus(text, bis_tick):
    r = re.search(r"KAEMPFER 10 bei Tick (\d+)", text) or re.search(r"ZIEL 10 Streitkolbenkaempfer erreicht bei Tick (\d+)", text)
    if r:
        return int(r.group(1)), "erreicht"
    if re.search(r"FRUEHABBRUCH|ABBRUCH - Spiel angehalten|Traceback", text):
        return 30000, "abgebrochen"
    bil = [(int(t), int(h), int(b)) for t, h, b in re.findall(r"^\s*(\d+) \|.*BILANZ .*= (\d+) \| Bedarf (\d+)", text, re.M)]
    if not bil:
        return 30000, "keine Bilanz"
    t1, h1, b1 = bil[-1]
    frueh = [x for x in bil if x[0] <= t1 - 2000] or bil[:1]
    t0, h0, _ = frueh[-1]
    rate = max(1.0, (h1 - h0) * 1000.0 / max(1, t1 - t0))
    return int(t1 + 1000.0 * max(0, b1 - h1) / rate), "geschaetzt (fehlt %d, Zuwachs %.0f je 1.000)" % (b1 - h1, rate)


def lauf(strategie, bis_tick, nr):
    stempel = time.strftime("%Y%m%d_%H%M%S")
    aus = os.path.join(D, "lernen_lauf_%s_%d.txt" % (stempel, nr))
    args = [sys.executable, os.path.join(HIER, "erstes_spiel.py")] + FEST + ["bis_tick=%d" % bis_tick] + \
        ["%s=%s" % kv for kv in sorted(strategie.items())]
    env = dict(os.environ, SHC_INSTANZ="1")
    with open(aus, "w", encoding="utf-8") as f:
        subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=HIER, timeout=3600)
    text = open(aus, encoding="utf-8", errors="replace").read()
    note, art = note_aus(text, bis_tick)
    lp = re.search(r"Lageprotokoll \(jede Runde komplett\): (.+?\.jsonl\.gz)", text)   # Pfad hat Leerzeichen (Lauf 1: Nachschau leer)
    ns = nachschau(lp.group(1)) if lp and os.path.exists(lp.group(1)) else {}
    abbruch = re.search(r"FRUEHABBRUCH bei Tick \d+: [^\n]*", text)
    return {"nr": nr, "zeit": stempel, "strategie": strategie, "note": note, "art": art, "nachschau": ns,
            "abbruch": abbruch.group(0) if abbruch else None, "datei": os.path.basename(aus)}


def schluessel(s):
    return json.dumps(s, sort_keys=True)


def naechste(beste, gespielt, ns):
    """23:24: nicht wuerfeln. Die Verluste der besten Strategie der Groesse nach; je Verlust seine Knoepfe in Rangfolge;
    der erste Knopf mit einem noch nicht gespielten Wert gewinnt (logische Konsequenz aus der Nachschau). Erst wenn alle
    passenden Knoepfe durch sind, zufaellig."""
    if ns:
        anteil = {v: ns.get(v, 0) / float(max(1, ns.get("ticks", 1))) for v in VERLUST_KNOEPFE}
        for verlust in sorted(anteil, key=anteil.get, reverse=True):
            if anteil[verlust] <= 0.1:
                break
            for k in VERLUST_KNOEPFE[verlust]:
                for w in KNOEPFE[k]:
                    if w != beste[k]:
                        s = dict(beste, **{k: w})
                        if schluessel(s) not in gespielt:
                            return s, k
    gewicht = {k: 1.0 for k in KNOEPFE}
    for _ in range(200):
        k = random.choices(list(gewicht), weights=list(gewicht.values()))[0]
        werte = [w for w in KNOEPFE[k] if w != beste[k]]
        random.shuffle(werte)
        for w in werte:
            s = dict(beste, **{k: w})
            if schluessel(s) not in gespielt:
                return s, k
    return None, None


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    laeufe, bis_tick = int(arg.get("laeufe", 5)), int(arg.get("bis_tick", 14000))
    pfad = os.path.join(D, "lernen.jsonl")
    alle = [json.loads(z) for z in open(pfad, encoding="utf-8")] if os.path.exists(pfad) else []
    gespielt = {schluessel(r["strategie"]) for r in alle}
    beste = min(alle, key=lambda r: r["note"]) if alle else None
    for i in range(laeufe):
        if beste is None:
            s, knopf = dict(GRUND), None
        elif schluessel(REFERENZ) not in gespielt:
            s, knopf = dict(REFERENZ), "v14"
        else:
            s, knopf = naechste(beste["strategie"], gespielt, beste.get("nachschau"))
            if s is None:
                print("Alle Nachbarn der besten Strategie gespielt - Ende", flush=True)
                break
        print("LERNEN Lauf %d: %s%s" % (len(alle) + 1, "Grundstrategie" if knopf is None else "%s = %s (statt %s)" % (
            knopf, s[knopf], beste["strategie"][knopf]), "" if beste is None else ", beste Note bisher %d" % beste["note"]), flush=True)
        r = lauf(s, bis_tick, len(alle) + 1)
        r["geaendert"] = knopf
        r["vergleich"] = None if beste is None else {"gegen": beste["nr"], "note_vorher": beste["note"], "differenz": r["note"] - beste["note"]}
        alle.append(r)
        gespielt.add(schluessel(s))
        with open(pfad, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("LERNEN Ergebnis Lauf %d: Note %d (%s)%s | Nachschau %s" % (
            r["nr"], r["note"], r["art"], "" if r["vergleich"] is None else ", %+d gegen Lauf %d" % (r["vergleich"]["differenz"], beste["nr"]),
            {k: v for k, v in r["nachschau"].items() if v}), flush=True)
        if beste is None or r["note"] < beste["note"]:
            beste = r
            print("LERNEN neue beste Strategie (Lauf %d)" % r["nr"], flush=True)
        # Wissen: je Knopfwert die beobachteten Differenzen
        wissen = {}
        for x in alle:
            if x.get("geaendert") and x.get("vergleich"):
                k = "%s=%s" % (x["geaendert"], x["strategie"][x["geaendert"]])
                wissen.setdefault(k, []).append(x["vergleich"]["differenz"])
        json.dump({"beste": beste, "wirkung_je_knopfwert": wissen}, open(os.path.join(D, "lernen_wissen.json"), "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)
    print("LERNEN fertig: beste Note %s (Lauf %s, %s)" % (beste["note"], beste["nr"], beste["strategie"]), flush=True)


if __name__ == "__main__":
    main()
