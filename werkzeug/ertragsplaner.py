# -*- coding: utf-8 -*-
"""Ertrags-Planer (Daniel 05.10. 19:11 "keine Fixes, sondern ein schlaues System, das abhaengig von der Umgebung
handelt; beliebig erweitern; am meisten Geld geben Stein und Eisen"; 19:33 "ja, bau den Ertrags-Planer").

Jede PLANEN-te Runde:
  1. Voraussetzungen: Lagerteil fast voll fuer eine Ware -> Lager erweitern (kostet nichts); zu wenig freie Leute fuer
     den besten Kandidaten -> erst eine Huette.
  2. Kandidaten: jede Gebaeudeart an ihrem besten Platz auf unserer Seite (Rohstoff-Feld bzw. Rehe, nahe am Lager /
     Kornspeicher). Wert = Ertrag (Startwert aus der Messpartie, korrigiert nach Weg) * Preis.
     Amortisation = Kosten in Gold (Holz 3, Stein 5 = Kaufpreise) / Gold je Tick.
  3. Gebaut wird der Kandidat mit der schnellsten Amortisation, wenn bezahlbar; sonst wird darauf gespart
     (braucht_gold -> keine Assassinen), ausser ein bezahlbarer ist hoechstens 1,5-mal langsamer.
Ohne feste Stueckzahlen - der Platz, die Rohstoffe und das Gold bestimmen, wie weit ausgebaut wird.
STARTWERTE (Messpartie 05.10., daten/ertrag_messung.json, wenige Lieferungen): Ertrag je 1.000 Ticks bei Weg D0 -
Eisen 0,9 @ 40, Stein 5,6 @ 8 (2,4 @ 23 war durch volles Lager gedeckelt), Apfel 2,5 @ 5, Fleisch 6 @ 53, Holz 5,5 @ 10.
Wegkorrektur (vermutet, nicht gemessen): Ertrag * (D0 + 20) / (D + 20).
Grenze: der Planer lernt noch nicht aus der laufenden Partie nach (Backlog: Selbstlernen).
"""
import json, os
from laden import befehl

def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

# Typ: (Ware, Ertrag je 1000 Ticks, Weg bei der Messung, Preis je Stueck, Arbeiter, Kosten Holz, Stein, Gold, Ziel)
ERTRAG = {
    5:  ("eisen", 0.9, 40, 27, 2, 20, 6, 0, "lager"),
    20: ("stein", 5.6, 8, 5, 4, 30, 0, 0, "lager"),        # Steinbruch + Ochsenjoch zusammen (3 + 1 Arbeiter)
    32: ("apfel", 2.5, 5, 3, 1, 3, 0, 15, "kornspeicher"),
    7:  ("fleisch", 6.0, 53, 1, 1, 3, 0, 60, "kornspeicher"),
    3:  ("holz", 5.5, 10, 3, 1, 5, 0, 0, "lager"),          # Holz zum Kaufpreis bewertet: es spart Zukauf
}
NAME = {5: "Eisenmine", 20: "Steinbruch+Ochsenjoch", 32: "Apfelplantage", 7: "Jaegerhuette", 3: "Holzfaeller"}
JE_TEIL = 48

class Ertragsplaner:
    PLANEN = 10

    def __init__(self, plan, sp, baue_schnell, wirt, steuerstufe):
        self.sp, self.plan, self.baue, self.wirt = sp, plan, baue_schnell, wirt
        self.K = tuple(plan.get("bergfried_eingang", (165, 111)))
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
        info = json.load(open(os.path.join(d, "start_%s.json" % plan["start"]), encoding="utf-8"))
        self.feinde = [tuple(v["eingang"]) for v in info["feind_bergfried"].values()]
        z = open(os.path.join(d, "rohstoffe_%s.txt" % plan["start"])).read().splitlines()[1:]
        self.felder = {"b": [], "i": []}
        for y, r in enumerate(z):
            for x, c in enumerate(r):
                if c in self.felder and self.eigene_seite((x, y)):
                    self.felder[c].append((x, y))
        self.baeume = []
        for w in open(os.path.join(d, "baeume_%s.txt" % plan["start"])).read().splitlines()[1:]:
            w = w.split()
            if len(w) >= 7 and w[2] == "2" and int(w[5]) < 4 and int(w[6]) > 0 and self.eigene_seite((int(w[3]), int(w[4]))):
                self.baeume.append((int(w[3]), int(w[4])))
        self.steuer, self.steuer_runde = steuerstufe, -99
        self.braucht_gold, self.letzte_wahl, self.bilanz = False, None, {}
        self.fehlschlag = {}
        from farmen_mischen import lies_karte
        self.anker = {}
        for typ, name in ((5, "eisenmine"), (20, "steinbruch")):
            pfad = os.path.join(d, "start_%s_platz_%s.txt" % (plan["start"], name))
            if os.path.exists(pfad):
                self.anker[typ] = [p for p in lies_karte(pfad) if self.eigene_seite(p)]

    def eigene_seite(self, p):
        d = schach(p, self.K)
        return all(d < schach(p, f) for f in self.feinde)

    # ---- Kandidaten ------------------------------------------------------------------------------------------------
    def _ziel_orte(self, eigen):
        # das alte Startlager zaehlt nicht (wird abgerissen) - sonst baut der Planer an den Bergfried statt ans Holz (9s)
        lager = [(g["x"] + 2, g["y"] + 2) for g in eigen if g["typ"] == 10 and g.get("nr") not in self.wirt.alt] or [tuple(self.plan["lager"])]
        speicher = [(g["x"] + 2, g["y"] + 2) for g in eigen if g["typ"] == 19] or [tuple(self.plan["kornspeicher"])]
        return lager, speicher

    def _platz(self, typ, L, eigen, lager, speicher):
        """Bester Ort fuer typ: am Rohstoff, moeglichst nahe am Ziel (Lager bzw. Kornspeicher). Gibt (ort, weg) oder None."""
        ziele = lager if ERTRAG[typ][8] == "lager" else speicher
        weg = lambda p: min(schach(p, z) for z in ziele)
        belegt = [(g["x"], g["y"]) for g in eigen if g["typ"] == typ]
        # 9s: die Eisenmine scheiterte 7-mal an Nachbarfeldern - ein Fehlschlag sperrt den Umkreis 8 fuer diese Art
        frei = lambda p: all(schach(p, b) > 6 for b in belegt) and not any(t == typ and schach(p, q) <= 8 for (t, q) in self.fehlschlag)
        # gueltige Ankerpunkte laut Spielpruefung, falls karten_holen sie geholt hat (start_<kurz>_platz_eisenmine/steinbruch)
        anker = self.anker.get(typ)
        if typ in (5, 20) and anker:
            kand = anker
        elif typ == 5:
            kand = self.felder["i"]
        elif typ == 20:
            kand = self.felder["b"]
        elif typ == 3:
            kand = self.baeume
        elif typ == 7:
            rehe = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 44 and e["besitzer"] == 0 and self.eigene_seite((e["x"], e["y"]))]
            kand = [p for p in rehe if sum(1 for q in rehe if schach(p, q) <= 15) >= 5]
        else:
            kand = [tuple(p) for p in self.plan.get("aepfel", [])] + [(s[0] + dx, s[1] + dy) for s in speicher for dx in (-20, -10, 10, 20) for dy in (-20, -10, 10, 20)]
        kand = [p for p in kand if frei(p) and weg(p) <= 70]
        if not kand:
            return None
        p = min(kand, key=weg)
        return p, weg(p)

    def kandidaten(self, L, eigen, st=None):
        lager, speicher = self._ziel_orte(eigen)
        # Holz je nach Lage: fehlt es, spart es Zukauf (3 Gold); liegt reichlich da, bringt es nur den Verkauf (1 Gold)
        holz_wert = 3 if (st or {}).get("holz", 0) < 60 else 1
        aus = []
        for typ, (ware, rate, d0, preis, arb, h, s, g, _) in ERTRAG.items():
            pl = self._platz(typ, L, eigen, lager, speicher)
            if not pl:
                continue
            ort, weg = pl
            gold_je_tick = rate * (d0 + 20.0) / (weg + 20.0) * (holz_wert if ware == "holz" else preis) / 1000.0
            kosten = 3 * h + 5 * s + g
            aus.append({"typ": typ, "ort": ort, "weg": weg, "gold_je_1000": round(1000 * gold_je_tick, 1),
                        "amort": kosten / gold_je_tick if gold_je_tick > 0 else 10 ** 9, "holz": h, "stein": s, "gold": g, "arbeiter": arb})
        return sorted(aus, key=lambda k: k["amort"])

    # ---- eine Planungsrunde ----------------------------------------------------------------------------------------
    def schritt(self, st, L, G, runde):
        if runde % self.PLANEN:
            return []
        ev, self.braucht_gold = [], bool(self.wirt.B_offen)     # Seasoning-B hat beim Gold Vorrang
        eigen = [dict(g, nr=n) for n, g in G.items() if g["besitzer"] == self.sp]
        holz, stein, gold = st.get("holz", 0), st.get("stein", 0), st.get("gold", 0)
        # Steuern nach Beliebtheit (Regel bleibt, bis der Planer sie mitrechnet)
        b = st.get("beliebt", 0) / 100.0
        if runde - self.steuer_runde >= 2 * self.PLANEN:
            neu = self.steuer + 1 if (b >= 97 and self.steuer < 8 and st.get("leute", 0) >= 15) else self.steuer - 1 if (b < 95 and self.steuer > 3) else self.steuer
            if neu != self.steuer:
                befehl({"spielbefehl": {"nr": 34, "werte": [neu]}}, 1.0, bis="SPIELBEFEHL")
                ev.append("STEUER %d -> %d (Beliebtheit %.2f)" % (self.steuer, neu, b))
                self.steuer, self.steuer_runde = neu, runde
        # Voraussetzung Lager: eine Ware nahe am Teil-Deckel (48 je Teil) -> anbauen
        teile = sum(1 for g in eigen if g["typ"] == 10)
        if teile and not [n for n in self.wirt.alt if n in G]:
            belegt = sum(-(-st.get(w, 0) // JE_TEIL) for w in ("holz", "stein", "eisen", "pech", "hopfen", "weizen", "mehl"))
            voll = [w for w in ("holz", "stein", "eisen") if st.get(w, 0) % JE_TEIL >= JE_TEIL - 8]
            if voll and belegt >= teile:
                lager, _ = self._ziel_orte(eigen)
                ev.append("PLANER Lager anbauen (%s fast voll, %d Teile) -> %s" % (voll, teile, self.baue(10, lager[0][0], lager[0][1], 10)))
        kand = self.kandidaten(L, eigen, st)
        if not kand:
            return ev
        beste = kand[0]
        self.letzte_wahl = beste
        # Voraussetzung Arbeiter: zu wenig freie Leute am Feuer -> erst Huette
        if st.get("feuer", 0) < beste["arbeiter"] and holz >= 5 and st.get("leute", 0) >= st.get("platz", 0) - 2:
            ev.append("PLANER Huette zuerst (Feuer %d, %s braucht %d) -> %s" % (st.get("feuer", 0), NAME[beste["typ"]], beste["arbeiter"],
                                                                              self.baue(1, self.K[0] - 7, self.K[1] - 2, 25)))
            return ev
        bezahlbar = lambda k: holz >= k["holz"] and stein >= k["stein"] and gold >= k["gold"] + (15 if self.wirt.B_offen else 0)
        wahl = beste if bezahlbar(beste) else next((k for k in kand[1:] if bezahlbar(k) and k["amort"] <= 1.5 * beste["amort"]), None)
        if wahl is None:
            self.braucht_gold = True
            if runde % (5 * self.PLANEN) == 0:
                ev.append("PLANER spart auf %s (Amortisation %.0f Ticks, %.1f Gold/1000)" % (NAME[beste["typ"]], beste["amort"], beste["gold_je_1000"]))
            return ev
        ort = self.baue(wahl["typ"], wahl["ort"][0], wahl["ort"][1], 10)
        if ort is None:
            self.fehlschlag[(wahl["typ"], wahl["ort"])] = self.fehlschlag.get((wahl["typ"], wahl["ort"]), 0) + 1
        elif wahl["typ"] == 20:
            self.baue(4, ort[0] + 3, ort[1] - 4, 8)                # Ochsenjoch direkt dazu (Daniels Regel)
        self.bilanz[NAME[wahl["typ"]]] = self.bilanz.get(NAME[wahl["typ"]], 0) + (1 if ort else 0)
        ev.append("PLANER %s bei %s (Weg %d, %.1f Gold/1000, Amortisation %.0f Ticks) -> %s" % (
            NAME[wahl["typ"]], wahl["ort"], wahl["weg"], wahl["gold_je_1000"], wahl["amort"], ort))
        return ev

    def bericht(self):
        return "Ertrags-Planer: gebaut %s, Steuerstufe %d, zuletzt bester Kandidat %s" % (
            self.bilanz or "nichts", self.steuer, (NAME[self.letzte_wahl["typ"]], round(self.letzte_wahl["amort"])) if self.letzte_wahl else None)
