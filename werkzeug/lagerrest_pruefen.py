# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel: Holz wird nicht mehr verkauft, sondern in Holzfaeller gesteckt (Daniel 06.10.: "statt Holz
verkaufen einfach mehr Holzfaeller, weil Holz kann man spaeter immer brauchen"). Vorher festgelegt:
  1. altes Lager mit 20 Holz -> Holzfaeller statt Verkauf (Rueckruf aufgerufen), kein Verkauf, kein Abriss
  2. altes Lager mit 20 Holz, Holzfaeller geht gerade nicht -> Holz bleibt liegen: kein Verkauf, kein Abriss
  3. nur ein unverwertbarer Rest 1-4 -> Abriss (wie bisher, Codex 06.10.)
  4. Stein im alten Lager wird weiter verkauft (nur Holz ist ausgenommen)
  5. der Rundenverkauf verkauft kein Holz mehr, auch nicht weit ueber der Ruecklage
Aufruf: python werkzeug/lagerrest_pruefen.py   (Rueckgabe 0 = gruen)
"""
import os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import wirtschaft as W


def lauf(bestand, verbauen=None):
    befehle, aufrufe = [], []
    alt = W.befehl
    W.befehl = lambda b, *a, **k: befehle.append(b) or []
    try:
        plan = {"aepfel": [], "lager": [20, 20]}
        w = W.Wirtschaft(plan, 1, lambda *a: None, [10])
        if verbauen is not None:
            w.holz_verbauen = lambda st, L, G: aufrufe.append(st.get("holz")) or verbauen
        st = dict({"t": 1000}, **bestand)
        G = {10: {"besitzer": 1, "typ": W.LAGER, "x": 1, "y": 1}}
        ev = w.schritt(st, {}, G)
        return befehle, ev, aufrufe
    finally:
        W.befehl = alt


def verkauft_holz(befehle):
    return any(b.get("spielbefehl", {}).get("werte") == [1, 2] for b in befehle)


def main():
    b1, e1, a1 = lauf({"holz": 20}, verbauen=((55, 60), "Platz (55, 60), Weg 9"))
    b2, e2, a2 = lauf({"holz": 20}, verbauen=(None, "kein freier Arbeiter am Feuer"))
    b3, e3, _ = lauf({"holz": 4}, verbauen=((55, 60), "x"))
    b4, e4, _ = lauf({"stein": 20}, verbauen=((55, 60), "x"))
    import erstes_spiel as E
    gesendet = []
    alt_b, alt_n = E.befehl, E.nahrung_auf_kante
    E.befehl = lambda b, *a, **k: gesendet.append(b) or []
    E.nahrung_auf_kante = lambda *a, **k: {}
    try:
        v = E.verkaufen({"holz": 200, "stein": 0, "eisen": 0, "leute": 10})
    finally:
        E.befehl, E.nahrung_auf_kante = alt_b, alt_n
    pruefungen = [
        ("20 Holz: Holzfaeller statt Verkauf, kein Abriss",
         a1 == [20] and not verkauft_holz(b1) and not any("abreissen" in b for b in b1)
         and any("Holzfaeller statt Verkauf" in e for e in e1)),
        ("20 Holz, Holzfaeller geht nicht: Holz bleibt (kein Verkauf, kein Abriss)",
         a2 == [20] and not verkauft_holz(b2) and not any("abreissen" in b for b in b2)),
        ("nur unverwertbarer Rest 1-4 -> Abriss", any("abreissen" in b for b in b3) and any("Rest {'holz': 4}" in e for e in e3)),
        ("Stein im alten Lager wird weiter verkauft", any(b.get("spielbefehl", {}).get("werte") == [1, 4] for b in b4)),
        ("Rundenverkauf: 200 Holz -> kein Holzverkauf (%s)" % v, not verkauft_holz(gesendet)),
    ]
    for text, ok in pruefungen:
        print(("OK  " if ok else "ROT ") + text)
    print("%d von %d gruen" % (sum(ok for _, ok in pruefungen), len(pruefungen)))
    return 0 if all(ok for _, ok in pruefungen) else 1


if __name__ == "__main__":
    raise SystemExit(main())
