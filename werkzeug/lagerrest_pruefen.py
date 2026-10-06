# -*- coding: utf-8 -*-
"""Gegenprobe: Beim Umsetzen des alten Lagers verschwindet kein verkaufbares Restholz."""
import wirtschaft as W


def lauf(holz):
    befehle = []
    alt = W.befehl
    W.befehl = lambda b, *a, **k: befehle.append(b) or []
    try:
        plan = {"aepfel": [], "lager": [20, 20]}
        w = W.Wirtschaft(plan, 1, lambda *a: None, [10])
        st = {"t": 1000, "holz": holz}
        G = {10: {"besitzer": 1, "typ": W.LAGER, "x": 1, "y": 1}}
        ev = w.schritt(st, {}, G)
        return befehle, ev
    finally:
        W.befehl = alt


def main():
    b20, e20 = lauf(20)
    b4, e4 = lauf(4)
    pruefungen = [
        ("20 Holz werden verkauft, nicht vernichtet",
         any("spielbefehl" in b for b in b20) and not any("abreissen" in b for b in b20)),
        ("nur technisch unverwertbarer Rest 1-4 darf fallen",
         any("abreissen" in b for b in b4) and any("Rest {'holz': 4}" in e for e in e4)),
    ]
    for text, ok in pruefungen:
        print(("OK  " if ok else "ROT ") + text)
    print("%d von %d gruen" % (sum(ok for _, ok in pruefungen), len(pruefungen)))
    return 0 if all(ok for _, ok in pruefungen) else 1


if __name__ == "__main__":
    raise SystemExit(main())
