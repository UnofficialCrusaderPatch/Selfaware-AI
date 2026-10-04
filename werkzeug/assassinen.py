# -*- coding: utf-8 -*-
"""Angriff mit Assassinen: in kleine Trupps aufteilen, moeglichst viele Gebaeude zerstoeren, ohne Verluste
(M16, Daniel 04.10.2026 21:54, 22:54, 23:13: "wirklich splitten und maximale Gebaeude kaputt machen, besonders auf
die Bogenschuetzen aufpassen").

Gelernt aus Partie 2 (23:12): ein grosser Trupp zerstoerte 11 Gebaeude, verlor aber 76 von 90 Assassinen - fast alle
nach Zielen 90-212 Felder tief im Feindgebiet und beim Rueckzug quer durch das Feindheer.

Je Runde (Lagebild + Gebaeudeliste aus EINEM Aufruf, siehe erstes_spiel.runde_lesen):
  - Mitglieder werden auf Trupps zu GROESSE verteilt (neue Anwerbungen fuellen den kleinsten Trupp auf).
  - Gefahr je Feind nach Art: Fernkaempfer (Bogen, Armbrust, Schleuder, Pferdebogen) FERN Felder, sonst NAH.
  - Jeder Trupp: Feind zu nah oder ein Mitglied verletzt -> ganzer Trupp zum NAECHSTEN sicheren Ort.
    Sonst ohne Ziel: Gebaeude mit bestem Wert / (Abstand + 20), hoechstens MAX_WEG Felder weg, Ziel und Weg frei von
    Gefahr, und nicht schon Ziel eines anderen Trupps. Alle Mitglieder des Trupps gebuendelt auf dieses Gebaeude.
Grenzen (offen): Reichweiten FERN/NAH sind Startwerte, nicht gemessen; Tuerme nicht beruecksichtigt.
"""
from laden import befehl
from waechter import sicherster_ort

ASSASSINE = 73
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
WERT = {19: 100, 20: 60, 3: 50, 4: 40, 5: 40, 6: 30, 30: 30, 31: 30, 32: 25, 33: 25,
        17: 20, 18: 20, 34: 20, 1: 10, 7: 10, 26: 5}
GROESSE, FERN, NAH, MAX_WEG = 4, 16, 8, 30   # 4 statt 6: mehr verschiedene Ziele gleichzeitig (Daniel 23:22)

def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def feinde(L, sp):
    return [((e["x"], e["y"]), FERN if e["typ"] in FERNKAMPF else NAH)
            for e in L.values() if e["besitzer"] not in (0, sp) and e["typ"] in TRUPPE]

def gefaehrdet(p, fe, zuschlag=0):
    return any(schach(p, f) < r + zuschlag for f, r in fe)

def weg_sicher(von, nach, fe):
    n = max(1, int(schach(von, nach) // 4))
    return not any(gefaehrdet((von[0] + (nach[0] - von[0]) * i / n, von[1] + (nach[1] - von[1]) * i / n), fe)
                   for i in range(n + 1))

def naechster_sicherer(L, orte, von, fe, sp=1):
    gut = [o for o in orte if not gefaehrdet(o, fe, 4)]
    return min(gut, key=lambda o: schach(o, von)) if gut else sicherster_ort(L, orte, sp)

class Trupp:
    def __init__(self, nr):
        self.nr, self.mitglieder, self.ziel, self.ziel_typ, self.zurueck, self.daheim = nr, set(), None, None, False, set()
        self.bereit = None     # Bereitstellungsplatz, zu dem der Trupp gerade laeuft
        self.bereit_ziel = None  # das feindliche Gebaeude, vor dem er bereitsteht

class Angriffstrupp:
    def __init__(self, sp=1, mitglieder=(), rueckzug=(125, 155)):
        self.sp, self.rueckzug = sp, tuple(rueckzug)
        self.trupps, self.leben_max = [], {}
        self.bilanz = {"gebaeude": {}, "verluste": set()}
        self.aufnehmen(mitglieder)

    @property
    def mitglieder(self):
        return set().union(*[t.mitglieder for t in self.trupps]) if self.trupps else set()

    def aufnehmen(self, nummern):
        schon = self.mitglieder
        for n in nummern:
            if n in schon or n in self.bilanz["verluste"]:
                continue
            frei = [t for t in self.trupps if len(t.mitglieder) < GROESSE]
            if not frei:
                self.trupps.append(Trupp(len(self.trupps) + 1)); frei = [self.trupps[-1]]
            min(frei, key=lambda t: len(t.mitglieder)).mitglieder.add(n)
            schon.add(n)

    def schritt(self, L, G, sichere_orte=None):
        ereignis = []
        fe = feinde(L, self.sp)
        orte = list(sichere_orte or [self.rueckzug])
        belegt = {t.ziel for t in self.trupps if t.ziel is not None}
        for t in self.trupps:
            for n in list(t.mitglieder):
                if n not in L or L[n]["besitzer"] != self.sp:
                    self.bilanz["verluste"].add(n); t.mitglieder.discard(n); t.daheim.discard(n)
                    ereignis.append("VERLUST: Trupp %d Mitglied %d" % (t.nr, n))
            for n in t.mitglieder:
                self.leben_max[n] = max(self.leben_max.get(n, 0), L[n]["leben"])
            if t.ziel is not None and t.ziel not in G:
                self.bilanz["gebaeude"][t.ziel_typ] = self.bilanz["gebaeude"].get(t.ziel_typ, 0) + 1
                ereignis.append("Trupp %d: Gebaeude %d (Typ %d) zerstoert" % (t.nr, t.ziel, t.ziel_typ))
                belegt.discard(t.ziel); t.ziel = None
            aktiv = [n for n in t.mitglieder if n not in t.daheim]
            if not aktiv or (len(t.mitglieder) < GROESSE and t.ziel is None and t.bereit is None and not t.zurueck):
                continue      # Trupp waechst noch - ab 6 geht er los (Daniel 23:18)
            mitte = (sum(L[n]["x"] for n in aktiv) / len(aktiv), sum(L[n]["y"] for n in aktiv) / len(aktiv))
            # erst unter 60 % zurueck (Partie 6: jeder Kratzer schickte den Trupp heim, Schaden kam oft von Feinden
            # 17-29 Felder weg - Quelle offen, vermutlich Tuerme)
            verletzt = [n for n in aktiv if L[n]["leben"] < 0.6 * self.leben_max[n]]
            in_gefahr = any(gefaehrdet((L[n]["x"], L[n]["y"]), fe) for n in aktiv)
            if verletzt and not in_gefahr and not t.zurueck:
                # nur die Schwerverletzten heim, der Rest macht weiter
                ort = naechster_sicherer(L, orte, mitte, fe, self.sp)
                befehl({"halten": {"nr": verletzt, "x": ort[0], "y": ort[1]}}, 1.0, bis="HALTEN")
                t.daheim |= set(verletzt)
                ereignis.append("Trupp %d: %d unter 60 %% heim nach %s" % (t.nr, len(verletzt), tuple(ort)))
                aktiv = [n for n in aktiv if n not in t.daheim]
                if not aktiv:
                    continue
                verletzt = []
            if in_gefahr and not t.zurueck:
                # naechster Feind (Art, Abstand) - Messung der echten Reichweite (Daniel 23:22: einverstanden)
                feind_e = [(schach(mitte, (e["x"], e["y"])), e["typ"]) for e in L.values()
                           if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE]
                nf = min(feind_e) if feind_e else (999, 0)
                # weg vom Angreifer: 15 Felder in Gegenrichtung, wenn dort sicher - sonst naechster sicherer Ort
                fx, fy = min(((e["x"], e["y"]) for e in L.values() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE),
                             key=lambda f: schach(mitte, f), default=(mitte[0], mitte[1]))
                dx, dy = mitte[0] - fx, mitte[1] - fy
                lang = max(abs(dx), abs(dy), 1)
                weg = (int(mitte[0] + 15 * dx / lang), int(mitte[1] + 15 * dy / lang))
                ort = weg if (0 < weg[0] < 400 and 0 < weg[1] < 400 and not gefaehrdet(weg, fe)) else naechster_sicherer(L, orte, mitte, fe, self.sp)
                ereignis.append("MESSUNG Trupp %d: naechster Feind Typ %d in %d Feldern, verletzt %d" % (t.nr, nf[1], nf[0], len(verletzt)))
                befehl({"halten": {"nr": list(t.mitglieder), "x": ort[0], "y": ort[1]}}, 1.0, bis="HALTEN")
                t.daheim |= set(verletzt); t.zurueck = True; t.bereit, t.bereit_ziel = None, None
                belegt.discard(t.ziel); t.ziel = None
                ereignis.append("Trupp %d zurueck nach %s (%s)" % (t.nr, tuple(ort), ("verletzt %s" % verletzt) if verletzt else "Feind nah"))
                continue
            if t.zurueck:
                if in_gefahr:
                    continue
                aktiv = [n for n in t.mitglieder if n not in t.daheim]
                if not aktiv:
                    continue
                befehl({"halten": {"los": aktiv}}, 1.0, bis="HALTEN")
                t.zurueck = False
            if t.ziel is None:
                # sofort das naechste Ziel (Daniel 23:14: nicht stehenbleiben) - Suchkreis stufenweise 30 / 45 / 60
                kand = []
                for weite in (MAX_WEG, 45, 60):
                    for n, g in G.items():
                        if g["besitzer"] in (0, self.sp) or g["typ"] not in WERT or n in belegt or not g.get("erreichbar", 1):
                            continue
                        ort = (g["x"], g["y"])
                        d = schach(mitte, ort)
                        if d > weite or gefaehrdet(ort, fe, 2) or not weg_sicher(mitte, ort, fe):
                            continue
                        kand.append((WERT[g["typ"]] / (d + 20.0), n, g, d))
                    if kand:
                        break
                if not kand:
                    # Bereitstellung (Daniel 23:18: ab 6 sofort nach vorne, nicht am Soeldnerlager warten): sicher bis
                    # 12 Felder vor das naechste ungeschuetzte, erreichbare feindliche Gebaeude laufen
                    if t.bereit is not None and schach(mitte, t.bereit) > 3:
                        continue
                    andere = [o.bereit_ziel for o in self.trupps if o is not t and o.bereit_ziel is not None]
                    ziele = sorted(((schach(mitte, (g["x"], g["y"])), (g["x"], g["y"])) for n, g in G.items()
                                    if g["besitzer"] not in (0, self.sp) and g["typ"] in WERT and g.get("erreichbar", 1)
                                    and n not in belegt and not gefaehrdet((g["x"], g["y"]), fe, 4)
                                    and all(schach((g["x"], g["y"]), a) > 10 for a in andere)))
                    for d, (gx, gy) in ziele:
                        f = max(0.0, (d - 12.0) / d) if d else 0.0
                        platz = (int(mitte[0] + (gx - mitte[0]) * f), int(mitte[1] + (gy - mitte[1]) * f))
                        if weg_sicher(mitte, platz, fe) and not gefaehrdet(platz, fe, 4):
                            befehl({"halten": {"nr": aktiv, "x": platz[0], "y": platz[1]}}, 1.0, bis="HALTEN")
                            t.bereit, t.bereit_ziel = platz, (gx, gy)
                            ereignis.append("Trupp %d (%d) rueckt vor nach %s (Ziel-Gebiet %s)" % (t.nr, len(aktiv), platz, (gx, gy)))
                            break
                    continue
                if t.bereit is not None:
                    befehl({"halten": {"los": aktiv}}, 1.0, bis="HALTEN")
                    t.bereit, t.bereit_ziel = None, None
                if kand:
                    w, n, g, d = max(kand)
                    befehl({"angriff": {"einheiten": aktiv, "gebaeude": n}}, 1.0, bis="ANGRIFF")
                    t.ziel, t.ziel_typ = n, g["typ"]; belegt.add(n)
                    ereignis.append("Trupp %d (%d) -> Gebaeude %d Typ %d bei (%d,%d), %d Felder" % (t.nr, len(aktiv), n, g["typ"], g["x"], g["y"], d))
        return ereignis

    def bericht(self):
        b = self.bilanz
        return "zerstoert %d Gebaeude %s, eigene Verluste %d, Trupps %d" % (
            sum(b["gebaeude"].values()), b["gebaeude"], len(b["verluste"]), len(self.trupps))
