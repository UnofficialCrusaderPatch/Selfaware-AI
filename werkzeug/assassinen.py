# -*- coding: utf-8 -*-
"""Angriffstrupp (Assassinen + Speertraeger) - moeglichst viel beim Gegner zerstoeren, ohne Verluste
(M16, Daniel 04.10.2026 21:54 und 22:54).

Je Runde (Lagebild + Gebaeudeliste aus EINEM Aufruf, siehe erstes_spiel.runde_lesen):
  1. Verletzte Mitglieder (Leben unter ihrem Hoechstwert) gehen allein zum Rueckzugsort und bleiben dort.
  2. Kommt eine feindliche Truppe naeher als GEFAHR an ein Mitglied: der ganze Trupp zieht sich zurueck.
  3. Sonst, ohne Ziel: Ziel = feindliches Gebaeude mit dem besten Wert / (Abstand + 20), an dem im Umkreis
     SICHER keine feindliche Truppe steht. Werte nach Daniel (22:54): Kornspeicher am meisten (meist viel drin),
     dann Steinbruch, Holzfaeller, Ochsenjoch, Eisenmine. Alle Mitglieder gebuendelt auf dieses eine Ziel
     ("angriff", Spielbefehl 36 Art 9) - perfektes Stacken (Daniel 22:52).
  4. Bilanz: zerstoerte Gebaeude (nach Typ), eigene Verluste.
Grenzen (offen): Sichtweite der Gegner, Reichweite von Bogenschuetzen und Tuermen nicht gemessen; GEFAHR/SICHER
sind Startwerte. Einheiten heilen vermutlich nicht von selbst (nicht gemessen).
"""
from laden import befehl

ASSASSINE = 73
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}
WERT = {19: 100, 20: 60, 3: 50, 4: 40, 5: 40, 6: 30, 30: 30, 31: 30, 32: 25, 33: 25,
        17: 20, 18: 20, 34: 20, 1: 10, 7: 10, 26: 5}
GEFAHR, SICHER = 12, 18

def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

class Angriffstrupp:
    def __init__(self, sp=1, mitglieder=(), rueckzug=(125, 155)):
        self.sp, self.rueckzug = sp, tuple(rueckzug)
        self.mitglieder = set(mitglieder)      # Einheitennummern; Assassinen kommen beim Anwerben dazu
        self.leben_max, self.daheim = {}, set()
        self.ziel, self.zurueck = None, False
        self.bilanz = {"gebaeude": {}, "verluste": set()}

    def aufnehmen(self, nummern):
        self.mitglieder |= set(nummern)

    def schritt(self, L, G):
        ereignis = []
        for n in list(self.mitglieder):
            if n not in L or L[n]["besitzer"] != self.sp:
                self.bilanz["verluste"].add(n); self.mitglieder.discard(n); self.daheim.discard(n)
                ereignis.append("VERLUST: Mitglied %d" % n)
        for n in self.mitglieder:
            self.leben_max[n] = max(self.leben_max.get(n, 0), L[n]["leben"])
        verletzt = [n for n in self.mitglieder if L[n]["leben"] < self.leben_max[n] and n not in self.daheim]
        if verletzt:
            befehl({"halten": {"nr": verletzt, "x": self.rueckzug[0], "y": self.rueckzug[1]}}, 1.0, bis="HALTEN")
            self.daheim |= set(verletzt)
            ereignis.append("verletzt heim: %s" % verletzt)
        aktiv = [n for n in self.mitglieder if n not in self.daheim]
        if self.ziel is not None and self.ziel not in G:
            typ = self.ziel_typ
            self.bilanz["gebaeude"][typ] = self.bilanz["gebaeude"].get(typ, 0) + 1
            ereignis.append("Gebaeude %d (Typ %d) zerstoert" % (self.ziel, typ)); self.ziel = None
        if not aktiv:
            return ereignis
        feind = [(e["x"], e["y"]) for e in L.values() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE]
        gefahr = min((schach((L[n]["x"], L[n]["y"]), t) for n in aktiv for t in feind), default=999)
        mitte = (sum(L[n]["x"] for n in aktiv) / len(aktiv), sum(L[n]["y"] for n in aktiv) / len(aktiv))
        if gefahr < GEFAHR:
            if not self.zurueck:
                befehl({"halten": {"nr": aktiv, "x": self.rueckzug[0], "y": self.rueckzug[1]}}, 1.0, bis="HALTEN")
                self.zurueck, self.ziel = True, None
                ereignis.append("RUECKZUG: Feind %d Felder vom Trupp" % gefahr)
            return ereignis
        if self.zurueck:
            if gefahr >= SICHER:
                befehl({"halten": {"los": aktiv}}, 1.0, bis="HALTEN")
                self.zurueck = False
                ereignis.append("Trupp wieder bereit (%d)" % len(aktiv))
            else:
                return ereignis
        if self.ziel is None:
            kand = []
            for n, g in G.items():
                if g["besitzer"] in (0, self.sp) or g["typ"] not in WERT:
                    continue
                if min((schach((g["x"], g["y"]), t) for t in feind), default=999) < SICHER:
                    continue
                d = schach(mitte, (g["x"], g["y"]))
                kand.append((WERT[g["typ"]] / (d + 20.0), n, g, d))
            if kand:
                w, n, g, d = max(kand)
                befehl({"halten": {"los": aktiv}}, 1.0, bis="HALTEN")
                befehl({"angriff": {"einheiten": aktiv, "gebaeude": n}}, 1.0, bis="ANGRIFF")
                self.ziel, self.ziel_typ = n, g["typ"]
                ereignis.append("Ziel: Gebaeude %d Typ %d bei (%d,%d), %d Felder, Wert %d - %d Mitglieder gebuendelt" % (
                    n, g["typ"], g["x"], g["y"], d, WERT[g["typ"]], len(aktiv)))
        return ereignis

    def bericht(self):
        b = self.bilanz
        return "zerstoert %d Gebaeude %s, eigene Verluste %d" % (sum(b["gebaeude"].values()), b["gebaeude"], len(b["verluste"]))
