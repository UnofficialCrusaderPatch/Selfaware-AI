# -*- coding: utf-8 -*-
"""Wirtschaft im laufenden Spiel (Daniel 05.10.2026 00:06: "beachte gleich auch seasoning/vorratslager"):

1. Apfel-Seasoning (Daniel 04.10.: nebeneinanderliegende Plantagen genau dann setzen, wenn eine von Fruehling in
   Sommer wechselt - dann holen sie sich gegenseitig Aepfel, fast doppelt so produktiv).
   Belegt am 05.10. (Spielcode + Messung):
     - Ein Apfelbaum durchlaeuft die Stufen 0-5 im Kreis; Dauer je Stufe 500, 300, 200, 1000, 40, 40 Ticks
       (Tabelle 0x00B484C0, ein Schritt je Spieltick gemessen). Geerntet wird NUR in Stufe 3 - 1000 von 2080 Ticks.
     - Die Baeume einer Plantage werden beim Bau gepflanzt und starten in Stufe 0 (Zaehler 0-31 zufaellig).
     - Der Apfelbauer nimmt JEDEN reifen Apfelbaum naeher als 30 Felder (selectClosestTree 0x004F3610 prueft weder
       Plantage noch Besitzer); findet er keinen, steht er untaetig (Zustand 1).
   Darum: Gruppe A in der Eroeffnung, Gruppe B, sobald die Baeume von A in Stufe 3 springen. B braucht dann genau
   1000 Ticks bis zur Reife - so lange, wie A reif ist. Die Gruppen wechseln sich ab, jeder Bauer findet fast immer
   einen reifen Baum.
2. Lager erst, wenn der erste Traeger abliefern WILL (Daniel 04.10.). Abgelesen (UpdateWoodcutter 0x0054C710):
   ein Holzfaeller mit fertigem Holz steht in Zustand 7 und fragt alle 21 Ticks nach einem Lager; ohne Lager bleibt
   er in Zustand 7. Gemessen am Eroeffnungsstand: erster Zustand 7 bei Tick ~4.500.
   Das alte Lager behaelt bis zum Bau von B dessen Holz (3 je Plantage) und wird danach leer abgerissen.
3. Lager rechtzeitig erweitern (Daniel 04.10.: wird es voll, WAEHREND Traeger unterwegs sind, verfallen ihre Waren -
   abgelesen: Ladung wird auf 0 gesetzt). Gezaehlt wird, was die Traeger bringen: Ladung (+904) der Einheiten in
   Zustand 8 plus Holzfaeller in Zustand 7 mal der groessten bisher gemessenen Ladung.
"""
import math
from laden import befehl, peek

APFEL, HOLZFAELLER, LAGER, BAUER = 32, 3, 10, 13
SUCHRADIUS_BAUER = 30                       # abgelesen: selectClosestTree nimmt Baeume naeher als 0x1E Felder
BAUM_BASIS, BAUM_SCHRITT, BAUM_STUFE = 0xF2CC54, 156, 0x80
REIF = 3
JE_TEIL = 48                                # Lagerteil fasst je Ware 48 (abgelesen: addResourceToStockpile(..., 0x30))
LAGERWAREN = ("holz", "hopfen", "stein", "eisen", "pech", "weizen", "mehl")


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def apfel_gruppen(orte, radius=SUCHRADIUS_BAUER):
    """Teilt Apfelplantagen (Ankerpunkte) in A (sofort bauen) und B (bauen, wenn A reif wird).
    Haufen = Plantagen, die einander ueber hoechstens <radius> Felder erreichen (Suchkreis des Bauern).
    Im Haufen abwechselnd A/B, vom Haufen-Mittelpunkt nach aussen; Einzelstuecke -> A (kein Partner)."""
    orte = [tuple(o) for o in orte]
    rest, haufen = list(orte), []
    while rest:
        h = [rest.pop(0)]
        neu = True
        while neu:
            neu = False
            for o in list(rest):
                if any(schach(o, p) <= radius for p in h):
                    h.append(o); rest.remove(o); neu = True
        haufen.append(h)
    A, B = [], []
    for h in haufen:
        if len(h) == 1:
            A += h
            continue
        mx, my = sum(o[0] for o in h) / len(h), sum(o[1] for o in h) / len(h)
        for i, o in enumerate(sorted(h, key=lambda o: (abs(o[0] - mx) + abs(o[1] - my), o))):
            (A if i % 2 == 0 else B).append(o)
    return A, B


class Wirtschaft:
    def __init__(self, plan, sp, baue_schnell, alte_lager):
        self.sp, self.baue_schnell = sp, baue_schnell
        self.A, self.B = apfel_gruppen(plan["aepfel"])
        self.B_offen = list(self.B)
        self.lager_ort = tuple(plan["lager"])
        self.alt = set(alte_lager)               # Lagerteile aus der Eroeffnung (behalten B-Holz bis B steht)
        self.apfelbaum, self.B_tick, self.A_reif_tick = None, None, None
        self.lager_tick, self.ladung_max = None, {}
        self.bauern = []                          # (tick, Bauern, untaetig)
        self.versuche_B = 0
        # Baum gleich jetzt suchen, solange das Spiel noch steht (9g: die Kartensuche mitten im Lauf kostete ~600 Ticks)
        if self.B:
            self.apfelbaum = self._a_baum() or -1

    # ---- Messen ---------------------------------------------------------------------------------------------------
    def _a_baum(self):
        """Einen Apfelbaum einer A-Plantage suchen (einmal, ueber die Baumliste des Moduls)."""
        befehl({"rohstoffkarte": {}}, 5.0, bis="ROHSTOFF")
        datei = "C:/Program Files (x86)/Steam/steamapps/common/Stronghold Crusader Extreme/ucp/villagestudio/abzug/baeume.txt"
        for z in open(datei).read().splitlines()[1:]:
            w = z.split()
            if len(w) >= 6 and w[1] == "15" and any(schach((int(w[3]), int(w[4])), (a[0] + 5, a[1] + 5)) <= 8 for a in self.A):
                return int(w[0])
        return None

    def stufe_a(self):
        if self.apfelbaum is None:
            self.apfelbaum = self._a_baum() or -1
        if self.apfelbaum <= 0:
            return None
        return peek(BAUM_BASIS + self.apfelbaum * BAUM_SCHRITT + BAUM_STUFE)[0]

    # ---- eine Runde -----------------------------------------------------------------------------------------------
    def schritt(self, st, L, G):
        ev = []
        t = st.get("t", 0)
        eigen = {n: g for n, g in G.items() if g["besitzer"] == self.sp}
        einheiten = {n: e for n, e in L.items() if e["besitzer"] == self.sp}
        # Messung: Apfelbauern untaetig?
        bauern = [e for e in einheiten.values() if e["typ"] == BAUER]
        if bauern:
            self.bauern.append((t, len(bauern), sum(1 for e in bauern if e["zustand"] == 1)))
        # 1. Seasoning: B setzen, sobald A reif wird
        if self.B_offen:
            stufe = self.stufe_a() if self.B_tick is None else REIF
            if stufe == REIF:
                if self.A_reif_tick is None:
                    self.A_reif_tick = t
                    ev.append("Seasoning: A-Plantagen reif bei Tick %d (Baum %d) - setze %d B-Plantagen" % (t, self.apfelbaum, len(self.B_offen)))
                stehen = [(g["x"], g["y"]) for g in eigen.values() if g["typ"] == APFEL]
                for o in list(self.B_offen):
                    if any(schach(o, s) <= 2 for s in stehen):
                        self.B_offen.remove(o)
                        continue
                    if st.get("holz", 0) >= 3 and st.get("gold", 0) >= 15:
                        self.baue_schnell(APFEL, o[0], o[1], 2)
                    elif st.get("holz", 0) < 3 and st.get("gold", 0) >= 60:
                        # 9g: der Markt verbaute das zurueckgelegte B-Holz - dann kaufen (Spielbefehl 38, kaufen = 0, Holz = 2)
                        befehl({"spielbefehl": {"nr": 38, "werte": [0, 2]}}, 1.0, bis="SPIELBEFEHL")
                        ev.append("Holz fuer B gekauft (Holz %d, Gold %d)" % (st.get("holz", 0), st.get("gold", 0)))
                        break
                self.versuche_B += 1
                if not self.B_offen:
                    self.B_tick = t
                    ev.append("Seasoning: alle %d B-Plantagen stehen (Tick %d, %d Ticks nach A-Reife)" % (len(self.B), t, t - self.A_reif_tick))
                elif self.versuche_B % 10 == 0:
                    ev.append("Seasoning: %d B-Plantagen noch offen (Holz %d, Gold %d)" % (len(self.B_offen), st.get("holz", 0), st.get("gold", 0)))
        # 2. Altes Lager abreissen, wenn B steht (oder keins geplant) und es leer ist
        alt_da = [n for n in self.alt if n in eigen]
        if alt_da and not self.B_offen:
            inhalt = sum(st.get(k, 0) for k in LAGERWAREN)
            if inhalt == 0:
                for n in alt_da:
                    befehl({"abreissen": {"nr": n}}, 0.8, bis="ABREISSEN")
                ev.append("Altes Lager abgerissen (%d Teile, leer) bei Tick %d" % (len(alt_da), t))
                self.alt.clear()
        # 3. Neues Lager erst, wenn ein Holzfaeller abliefern will (Zustand 7)
        teile = [n for n, g in eigen.items() if g["typ"] == LAGER]
        wollen = [n for n, e in einheiten.items() if e["typ"] == HOLZFAELLER and e["zustand"] == 7]
        if not teile and wollen and (self.lager_tick is None or t - self.lager_tick > 60):
            ort = self.baue_schnell(LAGER, self.lager_ort[0], self.lager_ort[1], 8)
            self.lager_tick = t
            ev.append("Lager gesetzt bei %s - %d Holzfaeller wollen abliefern (Tick %d)" % (ort, len(wollen), t))
        # 4. Rechtzeitig erweitern: Bestand + was unterwegs ist
        for e in einheiten.values():
            if e["zustand"] == 8 and e.get("ladung", 0) > 0:
                self.ladung_max[e["typ"]] = max(self.ladung_max.get(e["typ"], 0), e["ladung"])
        if teile and not alt_da:
            unterwegs = sum(e.get("ladung", 0) for e in einheiten.values() if e["typ"] == HOLZFAELLER and e["zustand"] == 8)
            bald = len(wollen) * self.ladung_max.get(HOLZFAELLER, 0)
            bestand = {k: st.get(k, 0) for k in LAGERWAREN}
            noetig = sum(math.ceil(v / JE_TEIL) for k, v in bestand.items() if k != "holz") + \
                math.ceil((bestand["holz"] + unterwegs + bald) / JE_TEIL)
            menge = sum(bestand.values())
            # Rueckfall solange keine Ladung gemessen ist: alte Reserve (60) wie bisher
            if noetig > len(teile) or (not self.ladung_max and menge >= JE_TEIL * len(teile) - 60):
                ort = self.baue_schnell(LAGER, self.lager_ort[0], self.lager_ort[1], 10)
                ev.append("Lager erweitert %s: Bestand %d, Holz unterwegs %d + bald %d, Teile %d -> noetig %d" % (
                    ort, menge, unterwegs, bald, len(teile), noetig))
        return ev

    def bericht(self):
        def anteil(von, bis):
            r = [(n, u) for t, n, u in self.bauern if von <= t < bis]
            n = sum(x[0] for x in r)
            return "%.0f %% (%d Messungen)" % (100.0 * sum(x[1] for x in r) / n, len(r)) if n else "keine Messung"
        b = self.B_tick or 10 ** 9
        return ("Seasoning: A %d / B %d Plantagen, A reif bei %s, B gesetzt bei %s; Apfelbauern untaetig vor B %s, "
                "B bis B+1000 %s, danach %s; FESTES FENSTER Tick 5000-12000 (zum Vergleich zwischen Partien): %s; "
                "Lager gesetzt bei %s, gemessene Ladung je Gang %s" % (
                    len(self.A), len(self.B), self.A_reif_tick, self.B_tick, anteil(0, b), anteil(b, b + 1000),
                    anteil(b + 1000, 10 ** 9), anteil(5000, 12000), self.lager_tick, self.ladung_max or "keine"))
