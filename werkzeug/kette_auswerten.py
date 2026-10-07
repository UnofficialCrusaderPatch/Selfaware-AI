# -*- coding: utf-8 -*-
"""Auswertung der Messpartie Eisen/Schmiede/Leder (streitkolben_messen.py teil=kette, Daniel 08.10. 00:18).

Je Mine aus dem Lageprotokoll (jede Runde): Arbeiter = Einheiten mit arbeitsplatz = Minennummer; eine Lieferung = die
Ladung eines Arbeiters faellt von >0 auf 0. Rate = gelieferte Stuecke je 1.000 Ticks ab der ersten Lieferung.
Schmiede/Leder/Kuehe aus den Proben (Vorrat) und dem Status (T51 = Kuh).
Aufruf: python kette_auswerten.py daten/kette_messung_<zeit>.json
"""
import gzip
import json
import os
import sys


def tabelle(text, kopfzeile):
    z = text.strip().split("\n")[kopfzeile:]
    k = z[0].split()
    return [dict(zip(k, map(int, l.split()))) for l in z[1:] if l.strip()]


def auswerten(pfad):
    erg = json.load(open(pfad, encoding="utf-8"))
    minen = {b["nr"]: b for b in erg["bauten"] if b["typ"] == 5 and b["nr"]}
    lager = [b for b in erg["bauten"] if b["typ"] == 10 and b["nr"]]
    je = {n: {"arbeiter_ab": None, "lieferungen": [], "arbeiter": set()} for n in minen}
    ladung_vor, t_erst, t_letzt, kuehe = {}, None, None, []
    for zeile in gzip.open(erg["lageprotokoll"], "rt", encoding="utf-8"):
        d = json.loads(zeile)
        t = d["t"]
        t_erst = t if t_erst is None else t_erst
        t_letzt = t
        E = tabelle(d["einheiten"], 1)
        kuehe.append((t, d["st"].get("T51", 0)))
        for e in E:
            ap = e.get("arbeitsplatz")
            if e["besitzer"] != 1 or ap not in je:
                continue
            m = je[ap]
            m["arbeiter"].add(e["nr"])
            if m["arbeiter_ab"] is None:
                m["arbeiter_ab"] = t
            vor = ladung_vor.get(e["nr"], 0)
            if vor > 0 and e.get("ladung", 0) == 0:
                m["lieferungen"].append((t, vor))
            ladung_vor[e["nr"]] = e.get("ladung", 0)
    aus = {"messdauer": [t_erst, t_letzt], "minen": []}
    for n, b in minen.items():
        m = je[n]
        l = m["lieferungen"]
        stueck = sum(s for _, s in l)
        rate = None
        if len(l) >= 2:
            stueck_ab_zweiter = sum(s for _, s in l[1:])
            rate = round(1000.0 * stueck_ab_zweiter / max(1, t_letzt - l[0][0]), 2)
        aus["minen"].append({"name": b["name"], "nr": n, "weg_luftlinie": b.get("weg_luftlinie"), "gebaut": b["t"],
                             "arbeiter": len(m["arbeiter"]), "arbeiter_ab": m["arbeiter_ab"],
                             "erste_lieferung": l[0][0] if l else None, "lieferungen": len(l), "stueck": stueck,
                             "je_gang": sorted({s for _, s in l}), "eisen_je_1000_ab_erster": rate})
    proben = erg["proben"]
    if proben:
        a, z = proben[0], proben[-1]
        aus["schmiede"] = {"keulen": [a["keule"], z["keule"]], "eisen": [a["eisen"], z["eisen"]], "ticks": [a["t"], z["t"]]}
        aus["leder"] = {"leder": [a["leder"], z["leder"]], "ticks": [a["t"], z["t"]]}
        # Zeitpunkte jeder neuen Keule / jedes neuen Leders
        for w in ("keule", "leder"):
            spr = []
            for p, q in zip(proben, proben[1:]):
                if (q.get(w) or 0) > (p.get(w) or 0):
                    spr.append((q["t"], q[w] - p[w]))
            aus["%s_zugang" % w] = spr
    aus["kuehe_max"] = max((k for _, k in kuehe), default=0)
    aus["erste_kuh"] = next((t for t, k in kuehe if k > 0), None)
    aus["lager"] = [(b["x"], b["y"]) for b in lager]
    return aus


if __name__ == "__main__":
    print(json.dumps(auswerten(sys.argv[1]), indent=1, ensure_ascii=False))
