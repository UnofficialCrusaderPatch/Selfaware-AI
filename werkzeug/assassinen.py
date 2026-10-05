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
import math
from laden import befehl
from waechter import sicherster_ort

ASSASSINE = 73
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
WERT = {
    # Daniel 05.10. 19:05: Ausbildungslager, Steinbrueche, Haeuser usw. sind mehr wert als Apfelplantagen und, wenn
    # nicht allzu schwer bewacht, fast noch bessere Ziele. Kornspeicher-Bonus (04.10. 22:54). STARTWERTE, Rangfolge von Daniel.
    9: 100, 8: 100,                     # Kaserne, Soeldnerlager (Ausbildungslager)
    19: 100,                            # Kornspeicher
    20: 80, 21: 60, 5: 70, 6: 60,       # Steinbruch, Steinlager am Bruch, Eisenmine, Pechgrube
    11: 70, 12: 70, 13: 70, 14: 70, 15: 70,  # Waffenkammer und Waffenbauer
    24: 60, 25: 50, 35: 40,             # Ingenieurs-, Tunnelgraebergilde, Stall
    1: 60,                              # Huetten (Wohnraum = Arbeiter)
    4: 50, 3: 50,                       # Ochsenjoch, Holzfaeller
    22: 40, 18: 40, 17: 35, 34: 35, 33: 40, 30: 30, 36: 40, 37: 40, 38: 40,  # Wirtshaus, Brauerei, Baeckerei, Muehle, Milch, Weizen, Kirchen
    32: 30, 7: 30,                      # Apfelplantage, Jaegerhuette
    26: 20}
GROESSE, FERN, NAH, MAX_WEG = 1, 16, 8, 30   # 1: jeder Assassine einzeln, eigene Gruppe (Daniel 23:32; Modul reserviert Gruppen je Takt)

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
                # Kaempfen statt fliehen (Daniel 23:32): Fernkaempfer direkt daneben erledigen; gegen Nahkaempfer nur in
                # Ueberzahl (eigene Assassinen im Umkreis 6 mindestens doppelt so viele wie feindliche Nahkaempfer im Umkreis 8)
                fern_nah = sorted((schach(mitte, (e["x"], e["y"])), m) for m, e in L.items()
                                  if e["besitzer"] not in (0, self.sp) and e["typ"] in FERNKAMPF and schach(mitte, (e["x"], e["y"])) <= 6)
                nah_feinde = [m for m, e in L.items() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE
                              and e["typ"] not in FERNKAMPF and schach(mitte, (e["x"], e["y"])) <= 8]
                freunde = sum(1 for e in L.values() if e["besitzer"] == self.sp and e["typ"] == ASSASSINE and schach(mitte, (e["x"], e["y"])) <= 6)
                ziel_einheit = fern_nah[0][1] if fern_nah else (min(nah_feinde, key=lambda m: schach(mitte, (L[m]["x"], L[m]["y"])))
                                                                 if nah_feinde and freunde >= 2 * len(nah_feinde) else None)
                if ziel_einheit is not None:
                    befehl({"angriff": {"einheiten": aktiv, "ziel": ziel_einheit}}, 1.0, bis="ANGRIFF")
                    belegt.discard(t.ziel); t.ziel = None
                    ereignis.append("Trupp %d kaempft gegen Einheit %d Typ %d (Freunde %d, Nahkaempfer %d)" % (
                        t.nr, ziel_einheit, L[ziel_einheit]["typ"], freunde, len(nah_feinde)))
                    continue
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


class Einzeln:
    """Jeder Assassine einzeln (Daniel 04.10. 23:35): Befehl auf das NAECHSTE erreichbare feindliche
    Wirtschaftsgebaeude; hoechstens JE_GEBAEUDE auf eines (Daniel 05.10. 00:00), sonst sofort das naechste.
    schritt() gibt (ereignisse, befehle) - alle Befehle einer Runde gehen gesammelt in EINEM Aufruf ans Spiel,
    das Modul setzt sie nacheinander ab.

    Gefahr (05.10., gemessen in Partie 9e: 21 von 25 Toten hatten KEIN Ziel und standen untaetig im Schussfeld,
    meist ~10 Bogenschuetzen 9-19 Felder weg; bei 223 Verletzungen stand der naechste Fernkaempfer meist 9-30 Felder weg):
      1. Ohne Ziel wartet ein Assassine ausser Reichweite (eigener Ort ohne Fernkaempfer bis SICHER_FERN).
      2. Verletzt und Fernkaempfer bis RUECKZUG_FERN: Rueckzug - ausser ein Fernkaempfer steht direkt daneben
         (bis ZUSCHLAGEN Felder) und hoechstens 1 Nahkaempfer im Umkreis 5: dann ihn angreifen (Daniel 04.10. 23:4x).
      3. Zielwahl: Gebaeude mit mehr als ZIEL_FERN_MAX Fernkaempfern im Umkreis ZIEL_FERN auslassen; wer unter
         SCHWACH Leben hat, nimmt nur Ziele ganz ohne Fernkaempfer bis SCHWACH_FERN.
    Die Zahlen sind STARTWERTE aus dieser Messung, nicht geeicht - jede Zielwahl schreibt ihre Gefahrenzahlen mit
    (ZIELWAHL-Zeilen), jede Verletzung und jeder Tod ihr Umfeld (MESSUNG-Zeilen), damit die naechste Partie sie eicht.
    Gegenprobe je Runde: laeuft ein Assassine nicht zu seinem Gebaeude (Laufziel im Lagebild weiter als ZIEL_NAH),
    bekommt er den Befehl neu - der Plan im Kopf zaehlt nicht, nur das Laufziel im Spiel."""
    JE_GEBAEUDE = 6
    ZIEL_NAH = 8           # gemessen 05.10.: Gebaeudeangriff -> Laufziel 1-2 Felder neben dem Gebaeude
    NEU_NACH = 4           # Runden (je ~30 Ticks bei Tempo 1000), bis ein Befehl im Spiel sichtbar sein muss
    VOLL = 12500           # gemessen 05.10.: Leben eines frisch angeworbenen Assassinen
    SICHER_FERN, SICHER_NAH = 30, 10
    RUECKZUG_FERN = 20
    ZUSCHLAGEN = 3
    ZIEL_FERN, ZIEL_FERN_MAX = 20, 2
    SCHWACH, SCHWACH_FERN = 0.6, 25
    VORAUS_FERN, VORAUS_ANZAHL = 10, 3   # Startwert aus Partie 9f: Tote standen 2-9 Felder neben ~7 Bogenschuetzen
    STAPEL_AB = 12         # Daniel 05.10. 00:30: "oben stehen noch so 30 Assassinen, die nichts machen" - ab so vielen
                           # Wartenden greifen ALLE gebuendelt einen erreichbaren Fernkaempfer am Boden an (perfekt stapeln)
    STAPEL_RUECKZUG = 0.3  # im Stapel erst unter 30 % Leben zurueck (Daniel: manchmal ist kein Rueckzug besser)
    # Lord-Trupp (Daniel 05.10. 00:52): nebenher immer wieder pruefen; freie Raid-Assassinen gebuendelt auf den Lord -
    # meist reichen 10, steht er allein sogar 5, bei Bogenschuetzen mehr, je nach Feindmenge noch viel mehr.
    # STARTWERTE aus dieser Regel: 5 allein, sonst 10 + 2 je Fernkaempfer + 1 je Nahkaempfer im Umkreis LORD_UMKREIS.
    LORD_ALLEIN, LORD_NORMAL, LORD_JE_FERN, LORD_JE_NAH, LORD_UMKREIS = 5, 10, 2, 1, 15
    LORD_PRUEFEN = 5       # alle 5 Runden (~150 Ticks bei Tempo 1000)
    LORD_WENIG_FEINDE = 5  # Daniel: "auf jeden Fall, wenn keine oder nur noch ein paar Einheiten im Spiel sind"

    def __init__(self, sp=1, pruefe_begehbar=None, wegtest=None):
        self.sp = sp
        self.wegtest = wegtest                     # Funktion(nr, punkte) -> [bool] (Modulbefehl "wegtest", Wegfinder des Spiels)
        self.lordtrupp = {"lord": None, "mitglieder": set(), "seit": 0}
        self.pruefe_begehbar = pruefe_begehbar     # Funktion(punkte) -> Menge begehbarer Punkte (Modulbefehl "begehbar")
        self._kand, self._begehbar = {}, set()
        self.mitglieder = set()
        self.ziel, self.ziel_typ, self.jagd, self.warte, self.befohlen = {}, {}, {}, {}, {}
        self.warte_seit = {}
        self.schlechte_orte = set()          # Warteplaetze, an die keiner hinlief (9g: Gebaeudemitten)
        self.stapel = {"ziel": None, "mitglieder": set()}
        self.leben, self.umfeld = {}, {}
        self.runde, self.gemessen, self.ohne_ziel_zuletzt = 0, 0, None
        self.bilanz = {"gebaeude": {}, "verluste": set(), "neu_befohlen": 0, "rueckzug": 0, "zuschlagen": 0}

    def aufnehmen(self, nummern):
        self.mitglieder |= set(n for n in nummern if n not in self.bilanz["verluste"])

    # --- Hilfen ---------------------------------------------------------------------------------------------------
    def _feinde(self, L):
        fern, nah = [], []
        for nr, e in L.items():
            if e["besitzer"] in (0, self.sp) or e["typ"] not in TRUPPE:
                continue
            (fern if e["typ"] in FERNKAMPF else nah).append((nr, (e["x"], e["y"]), e["typ"]))
        return fern, nah

    @staticmethod
    def _naechster(ort, liste):
        return min(((schach(ort, p), nr, typ) for nr, p, typ in liste), default=(999, 0, 0))

    @staticmethod
    def _anzahl(ort, liste, r):
        return sum(1 for _, p, _ in liste if schach(ort, p) <= r)

    def _sicherer_ort(self, ort, orte, fern, nah, n=None):
        """Zuerst KURZ weg vom Feind (begehbar laut Modul, der Punkt mit dem groessten Abstand zum naechsten Fernkaempfer);
        nur wenn das nicht geht: naechster begehbarer eigener Ort ohne Fernkaempfer bis SICHER_FERN und Nahkaempfer bis
        SICHER_NAH, sonst der Ort mit dem groessten Abstand zum naechsten Feind. Gesperrte Orte nie."""
        kurz = [p for p in self._kand.get(n, []) if p in self._begehbar and p not in self.schlechte_orte]
        if kurz:
            return max(kurz, key=lambda p: (self._naechster(p, fern)[0], -schach(ort, p)))
        orte = [o for o in orte if o not in self.schlechte_orte]
        gut = [o for o in orte if self._naechster(o, fern)[0] > self.SICHER_FERN and self._naechster(o, nah)[0] > self.SICHER_NAH]
        if gut:
            return min(gut, key=lambda o: schach(ort, o))
        return max(orte, key=lambda o: min(self._naechster(o, fern)[0], self._naechster(o, nah)[0])) if orte else None

    def _weg_vom_feind(self, ort, fern, nah):
        """Kandidaten fuer einen KURZEN Rueckzug: 15/20/25 Felder weg vom Schwerpunkt der nahen Feinde, geradeaus und
        30 Grad links/rechts (Partie 9h: 210 Rueckzuege quer ueber die Karte nach Hause, 37 Assassinen starben im Laufen;
        Partie 2/5: kurz vom Angreifer weg war das Beste)."""
        nahe = [p for _, p, _ in fern if schach(ort, p) <= self.RUECKZUG_FERN] + [p for _, p, _ in nah if schach(ort, p) <= self.SICHER_NAH]
        if not nahe:
            return []
        cx, cy = sum(p[0] for p in nahe) / len(nahe), sum(p[1] for p in nahe) / len(nahe)
        dx, dy = ort[0] - cx, ort[1] - cy
        lang = math.hypot(dx, dy) or 1.0
        dx, dy = dx / lang, dy / lang
        aus = []
        for k in (20, 15, 25):
            for w in (0.0, 0.52, -0.52):
                rx = dx * math.cos(w) - dy * math.sin(w)
                ry = dx * math.sin(w) + dy * math.cos(w)
                x, y = int(round(ort[0] + rx * k)), int(round(ort[1] + ry * k))
                if 2 <= x <= 397 and 2 <= y <= 397:
                    aus.append((x, y))
        return aus

    def umgebung(self, n, L, G, fern, nah):
        """Umfeld fuer die MESSUNG-Zeilen."""
        ort = (L[n]["x"], L[n]["y"])
        nf, nn = self._naechster(ort, fern), self._naechster(ort, nah)
        feind = min(nf, nn)
        gb = min(((schach(ort, (g["x"], g["y"])), g["typ"]) for g in G.values() if g["besitzer"] not in (0, self.sp)),
                 default=(999, 0))
        z = self.ziel.get(n)
        zd = schach(ort, (G[z]["x"], G[z]["y"])) if z in G else -1
        return ("ort (%d,%d) zustand %d | naechster Feind Typ %d in %d | naechster Fernkaempfer Typ %d in %d | "
                "Fern<=%d: %d | Nah<=%d: %d | naechstes Feindgebaeude Typ %d in %d | Ziel %s in %d" % (
                    ort[0], ort[1], L[n]["zustand"], feind[2], feind[0], nf[2], nf[0],
                    FERN, self._anzahl(ort, fern, FERN), NAH, self._anzahl(ort, nah, NAH), gb[1], gb[0], z, zd))

    def _vergessen(self, n):
        self.ziel.pop(n, None); self.jagd.pop(n, None); self.warte.pop(n, None); self.warte_seit.pop(n, None)

    def _warten(self, n, ort_sicher, halten):
        self.warte[n] = ort_sicher
        self.warte_seit[n] = self.runde
        halten.setdefault(ort_sicher, []).append(n)

    # --- eine Runde -----------------------------------------------------------------------------------------------
    def schritt(self, L, G, sichere_orte=None):
        ereignis, angriffe, jagen, halten = [], [], [], {}
        self.runde += 1
        # begehbare Warteplaetze: wo gerade eine eigene Nicht-Kampfeinheit steht, ist begehbarer Boden
        orte = list(sichere_orte or []) + sorted({(e["x"], e["y"]) for e in L.values()
                                                  if e["besitzer"] == self.sp and e["typ"] not in TRUPPE and e["typ"] != ASSASSINE})
        if self.pruefe_begehbar and orte:
            gut = self.pruefe_begehbar(orte)
            orte = [o for o in orte if o in gut] or orte
        fern, nah = self._feinde(L)
        # Rueckzugs-Kandidaten fuer alle, die Feinde nah haben - EIN Modulaufruf prueft, welche begehbar sind
        self._kand = {}
        for n in self.mitglieder:
            if n in L:
                c = self._weg_vom_feind((L[n]["x"], L[n]["y"]), fern, nah)
                if c:
                    self._kand[n] = c
        punkte = sorted({p for c in self._kand.values() for p in c})
        self._begehbar = (self.pruefe_begehbar(punkte) if self.pruefe_begehbar else set(punkte)) if punkte else set()
        # 1. Verluste und Verletzungen messen
        for n in list(self.mitglieder):
            if n not in L or L[n]["besitzer"] != self.sp:
                self.bilanz["verluste"].add(n); self.mitglieder.discard(n); self._vergessen(n)
                ereignis.append("MESSUNG tot %d: zuletzt %s" % (n, self.umfeld.pop(n, "unbekannt")))
                self.leben.pop(n, None)
        verletzt = set()
        for n in self.mitglieder:
            u = self.umgebung(n, L, G, fern, nah)
            alt = self.leben.get(n)
            if alt is not None and L[n]["leben"] < alt:
                verletzt.add(n)
                ereignis.append("MESSUNG verletzt %d: leben %d -> %d | %s" % (n, alt, L[n]["leben"], u))
            self.leben[n], self.umfeld[n] = L[n]["leben"], u
        # 2. Erledigte Ziele, erledigte Jagd
        for n, z in list(self.ziel.items()):
            if z not in G:
                typ = self.ziel_typ.pop(z, None)
                if typ is not None:
                    self.bilanz["gebaeude"][typ] = self.bilanz["gebaeude"].get(typ, 0) + 1
                    ereignis.append("Gebaeude %d (Typ %d) zerstoert" % (z, typ))
                del self.ziel[n]
        for n, f in list(self.jagd.items()):
            if f not in L or L[f]["besitzer"] in (0, self.sp):
                del self.jagd[n]
        # 3. Gegenprobe: laeuft er wirklich zu seinem Gebaeude?
        wirklich, abweichler = set(), 0
        for n, z in list(self.ziel.items()):
            if schach((L[n]["laufx"], L[n]["laufy"]), (G[z]["x"], G[z]["y"])) <= self.ZIEL_NAH:
                wirklich.add(z)
            elif self.runde - self.befohlen.get(n, 0) >= self.NEU_NACH:
                abweichler += 1
                del self.ziel[n]
        self.gemessen = len(wirklich)
        if abweichler:
            self.bilanz["neu_befohlen"] += abweichler
            ereignis.append("%d Assassinen liefen nicht zu ihrem Ziel - neu befohlen" % abweichler)
        # 4. Verletzt im Schussfeld: Rueckzug oder zuschlagen
        for n in verletzt:
            ort = (L[n]["x"], L[n]["y"])
            nf = self._naechster(ort, fern)
            if nf[0] > self.RUECKZUG_FERN:
                continue
            if n in self.lordtrupp["mitglieder"]:
                continue                   # der Lord-Trupp bleibt dran (gebuendelt; Daniel: nur die letzten Lebenspunkte zaehlen)
            if n in self.stapel["mitglieder"]:
                if L[n]["leben"] >= self.STAPEL_RUECKZUG * self.VOLL:
                    continue
                self.stapel["mitglieder"].discard(n)
            if nf[0] <= self.ZUSCHLAGEN and self._anzahl(ort, nah, 5) <= 1:
                if self.jagd.get(n) != nf[1]:
                    self.ziel.pop(n, None); self.warte.pop(n, None)
                    self.jagd[n] = nf[1]
                    jagen.append((n, nf[1]))
                    self.bilanz["zuschlagen"] += 1
                continue
            sicher = self._sicherer_ort(ort, orte, fern, nah, n)
            if sicher and self.warte.get(n) != sicher:
                self._vergessen(n)
                self._warten(n, sicher, halten)
                self.bilanz["rueckzug"] += 1
        # 4b. Ausweichen, bevor es weh tut: rueckt eine Gruppe Fernkaempfer heran, Ziel aufgeben
        for n in self.mitglieder:
            if n in verletzt or n in self.jagd or n in self.warte or n in self.stapel["mitglieder"] or n in self.lordtrupp["mitglieder"]:
                continue
            ort = (L[n]["x"], L[n]["y"])
            if self._anzahl(ort, fern, self.VORAUS_FERN) >= self.VORAUS_ANZAHL:
                sicher = self._sicherer_ort(ort, orte, fern, nah, n)
                if sicher:
                    self._vergessen(n)
                    self._warten(n, sicher, halten)
                    self.bilanz["ausgewichen"] = self.bilanz.get("ausgewichen", 0) + 1
        # 4c. Gegenprobe Warten: laeuft er nach NEU_NACH Runden nicht zu seinem sicheren Ort, neu schicken (mit Messzeile)
        for n, o in list(self.warte.items()):
            if self.runde - self.warte_seit.get(n, self.runde) < self.NEU_NACH or n in halten.get(o, []):
                continue
            ort, lauf = (L[n]["x"], L[n]["y"]), (L[n]["laufx"], L[n]["laufy"])
            if schach(ort, o) > 4 and schach(lauf, o) > 4:
                ereignis.append("MESSUNG warten klappt nicht %d: ort %s lauf %s Platz %s zustand %d zielart %d - Platz gesperrt" % (
                    n, ort, lauf, o, L[n]["zustand"], L[n]["zielart"]))
                self.schlechte_orte.add(o)
                neu_o = self._sicherer_ort(ort, orte, fern, nah, n)
                if neu_o:
                    self._warten(n, neu_o, halten)
                self.bilanz["warten_neu"] = self.bilanz.get("warten_neu", 0) + 1
        # 5. Ziele verteilen (Gefahr am Gebaeude beachten); wer keins bekommt, wartet ausser Reichweite
        zahl = {}
        for z in self.ziel.values():
            zahl[z] = zahl.get(z, 0) + 1
        kand = []
        for gn, g in G.items():
            if g["besitzer"] in (0, self.sp) or g["typ"] not in WERT:
                continue
            p = (g["x"], g["y"])
            kand.append((gn, p, g["typ"], g.get("erreichbar", 1), self._anzahl(p, fern, 10),
                         self._anzahl(p, fern, self.ZIEL_FERN), self._anzahl(p, fern, 30), self._anzahl(p, fern, self.SCHWACH_FERN)))
        gruende = {"keins erreichbar": 0, "alle voll": 0, "alle gefaehrlich": 0}
        ohne = 0
        for n in sorted(self.mitglieder):
            if n in self.ziel or n in self.jagd or n in self.stapel["mitglieder"] or n in self.lordtrupp["mitglieder"] \
                    or (n in self.warte and n in verletzt):
                continue
            ort = (L[n]["x"], L[n]["y"])
            schwach = L[n]["leben"] < self.SCHWACH * self.VOLL
            erreichbar = [k for k in kand if k[3]]
            frei = [k for k in erreichbar if zahl.get(k[0], 0) < self.JE_GEBAEUDE]
            sicher = [k for k in frei if (k[7] == 0 if schwach else k[5] <= self.ZIEL_FERN_MAX)]
            if sicher:
                # Wert je Weg, abgeschwaecht durch Fernkaempfer am Ziel (Daniel 19:05: wertvoll UND nicht allzu schwer bewacht)
                gn, p, typ, _, f10, f20, f30, _ = max(sicher, key=lambda k: WERT.get(k[2], 10) / ((schach(ort, k[1]) + 20.0) * (1 + k[5])))
                self.ziel[n] = gn
                self.ziel_typ[gn] = typ
                zahl[gn] = zahl.get(gn, 0) + 1
                self.befohlen[n] = self.runde
                self.warte.pop(n, None); self.warte_seit.pop(n, None)
                angriffe.append((n, gn))
                ereignis.append("ZIELWAHL %d -> %d Typ %d in %d: Fern<=10 %d, <=20 %d, <=30 %d, Leben %d" % (
                    n, gn, typ, schach(ort, p), f10, f20, f30, L[n]["leben"]))
                continue
            ohne += 1
            gruende["keins erreichbar" if not erreichbar else "alle voll" if not frei else "alle gefaehrlich"] += 1
            nf, nn = self._naechster(ort, fern)[0], self._naechster(ort, nah)[0]
            if nf <= self.SICHER_FERN or nn <= self.SICHER_NAH:
                sicher_ort = self._sicherer_ort(ort, orte, fern, nah, n)
                if sicher_ort and self.warte.get(n) != sicher_ort:
                    self._warten(n, sicher_ort, halten)
        # 5b. Lord-Trupp (Daniel 05.10. 00:52)
        lord_befehl = None
        lt = self.lordtrupp
        lt["mitglieder"] = {n for n in lt["mitglieder"] if n in self.mitglieder}
        lords = [(n, e) for n, e in L.items() if e["typ"] == 55 and e["besitzer"] not in (0, self.sp)]
        if not lords:
            if lt["mitglieder"]:
                ereignis.append("LORD-TRUPP aufgeloest: kein feindlicher Lord mehr (%d frei)" % len(lt["mitglieder"]))
            lt["mitglieder"], lt["lord"] = set(), None
        else:
            ln, le = lords[0]
            lp = (le["x"], le["y"])
            fern_l = self._anzahl(lp, fern, self.LORD_UMKREIS)
            nah_l = self._anzahl(lp, nah, self.LORD_UMKREIS)
            noetig = self.LORD_ALLEIN if fern_l + nah_l == 0 else self.LORD_NORMAL + self.LORD_JE_FERN * fern_l + self.LORD_JE_NAH * nah_l
            feinde_gesamt = len(fern) + len(nah)
            if lt["mitglieder"]:
                # Gegenprobe: wer nicht (mehr) den Lord angreift, bekommt den Befehl neu; zu wenige -> aufloesen
                if len(lt["mitglieder"]) < 3:
                    ereignis.append("LORD-TRUPP aufgeloest: nur noch %d (Lord-Leben %d)" % (len(lt["mitglieder"]), le["leben"]))
                    lt["mitglieder"], lt["lord"] = set(), None
                elif self.runde - lt["seit"] >= self.NEU_NACH:
                    abseits = [n for n in lt["mitglieder"] if not (L[n]["zielart"] == 4 and L[n].get("zieleinheit") == ln)]
                    if abseits:
                        lord_befehl = {"angriff": {"einheiten": sorted(lt["mitglieder"]), "ziel": ln}}
                        lt["seit"] = self.runde
                        ereignis.append("LORD-TRUPP neu befohlen: %d von %d griffen den Lord nicht an" % (len(abseits), len(lt["mitglieder"])))
            elif self.runde % self.LORD_PRUEFEN == 0:
                frei = [n for n in self.mitglieder if n not in self.ziel and n not in self.jagd and n not in self.stapel["mitglieder"]
                        and L[n]["leben"] >= self.SCHWACH * self.VOLL]
                # Truppgroesse gilt immer (9l: "wenig Feinde" schickte 7 statt der noetigen 15 - 5 starben, der Lord ueberlebte);
                # wenige Feinde heisst nur: dann alle Freien mitschicken, nicht mit weniger losgehen
                genug = len(frei) >= noetig
                if genug:
                    frei.sort(key=lambda n: schach((L[n]["x"], L[n]["y"]), lp))
                    weg = self.wegtest(frei[0], [lp])[0] if self.wegtest else True
                    ereignis.append("LORD-PRUEFUNG: Lord %d bei %s Leben %d, Fern %d / Nah %d im Umkreis %d, Feinde gesamt %d -> noetig %d, frei %d, Weg %s" % (
                        ln, lp, le["leben"], fern_l, nah_l, self.LORD_UMKREIS, feinde_gesamt, noetig, len(frei), "ja" if weg else "NEIN"))
                    if weg:
                        anzahl = len(frei) if feinde_gesamt <= self.LORD_WENIG_FEINDE else max(noetig, min(len(frei), 2 * noetig))
                        lt["mitglieder"] = set(frei[:anzahl])
                        lt["lord"], lt["seit"] = ln, self.runde
                        for n in lt["mitglieder"]:
                            self.warte.pop(n, None)
                            self.warte_seit.pop(n, None)
                        lord_befehl = {"angriff": {"einheiten": sorted(lt["mitglieder"]), "ziel": ln}}
                        self.bilanz["lordtrupps"] = self.bilanz.get("lordtrupps", 0) + 1
                        ereignis.append("LORD-TRUPP: %d Assassinen gebuendelt auf den Lord" % anzahl)
        # 6. Stapel: viele Wartende -> alle gebuendelt auf EINEN erreichbaren Fernkaempfer am Boden, dann den naechsten
        stapel_befehl = None
        stp = self.stapel
        stp["mitglieder"] = {n for n in stp["mitglieder"] if n in self.mitglieder}
        ziel_lebt = stp["ziel"] in L and L[stp["ziel"]]["besitzer"] not in (0, self.sp)
        wartende = [n for n in self.mitglieder if n not in self.ziel and n not in self.jagd and n not in stp["mitglieder"]
                    and n not in self.lordtrupp["mitglieder"] and L[n]["leben"] >= self.SCHWACH * self.VOLL]
        if stp["mitglieder"] or len(wartende) >= self.STAPEL_AB:
            if not stp["mitglieder"]:
                stp["mitglieder"] = set(wartende)
                for n in wartende:
                    self.warte.pop(n, None)
                    self.warte_seit.pop(n, None)
            if not ziel_lebt:
                # 9h: der naechste Schuetze stand inmitten von 17 weiteren - jetzt nur Schuetzen, um die hoechstens
                # (Stapelgroesse - 4) / 2 weitere Fernkaempfer im Umkreis 10 stehen; davon der einsamste, dann der naechste
                mx = sum(L[n]["x"] for n in stp["mitglieder"]) / len(stp["mitglieder"])
                my = sum(L[n]["y"] for n in stp["mitglieder"]) / len(stp["mitglieder"])
                erreichbar = []
                for f in fern:
                    if L[f[0]].get("erreichbar", -1) != 1:
                        continue
                    um = self._anzahl(f[1], fern, 10) - 1
                    if len(stp["mitglieder"]) >= 2 * um + 4:
                        erreichbar.append((um, schach((mx, my), f[1]), f))
                if erreichbar:
                    um, d, (f, _, typ) = min(erreichbar)
                    stp["ziel"] = f
                    stapel_befehl = {"angriff": {"einheiten": sorted(stp["mitglieder"]), "ziel": f}}
                    self.bilanz["stapel_ziele"] = self.bilanz.get("stapel_ziele", 0) + 1
                    ereignis.append("STAPEL: %d Assassinen gebuendelt auf Fernkaempfer %d (Typ %d, %d Felder vom Stapel, Fern<=10 dort %d)" % (
                        len(stp["mitglieder"]), f, typ, d, self._anzahl((L[f]["x"], L[f]["y"]), fern, 10)))
                else:
                    ereignis.append("STAPEL aufgeloest: kein erreichbarer Fernkaempfer, den %d schlagen koennen (zurueck ins Warten)" % len(stp["mitglieder"]))
                    stp["mitglieder"], stp["ziel"] = set(), None
        if ohne != self.ohne_ziel_zuletzt:
            self.ohne_ziel_zuletzt = ohne
            ereignis.append("%d Assassinen ohne Ziel (%s)" % (ohne, ", ".join("%s %d" % kv for kv in gruende.items() if kv[1])))
        befehle = [{"angriff": {"einheiten": [n], "gebaeude": gn}} for n, gn in angriffe]
        befehle += [{"angriff": {"einheiten": [n], "ziel": f}} for n, f in jagen]
        befehle += [{"halten": {"nr": ns, "x": o[0], "y": o[1]}} for o, ns in halten.items()]
        if stapel_befehl:
            befehle.append(stapel_befehl)
        if lord_befehl:
            befehle.append(lord_befehl)
        if angriffe:
            ereignis.append("%d Assassinen auf %d Gebaeude verteilt (im Spiel gemessen: %d Gebaeude gleichzeitig angelaufen)" % (
                len(angriffe), len(set(g for _, g in angriffe)), self.gemessen))
        if jagen:
            ereignis.append("%d Assassinen greifen Fernkaempfer direkt daneben an" % len(jagen))
        if halten:
            ereignis.append("%d Assassinen warten/ziehen sich zurueck ausser Reichweite" % sum(len(v) for v in halten.values()))
        return ereignis, befehle

    def bericht(self):
        b = self.bilanz
        return ("zerstoert %d Gebaeude %s, eigene Verluste %d, im Spiel gleichzeitig angelaufen zuletzt %d, neu befohlen %d, "
                "Rueckzuege %d, ausgewichen %d, Fernkaempfer angegriffen %d, Warten neu geschickt %d, Stapel-Ziele %d, "
                "gesperrte Warteplaetze %d" % (
                    sum(b["gebaeude"].values()), b["gebaeude"], len(b["verluste"]), self.gemessen, b["neu_befohlen"],
                    b["rueckzug"], b.get("ausgewichen", 0), b["zuschlagen"], b.get("warten_neu", 0),
                    b.get("stapel_ziele", 0), len(self.schlechte_orte)) + ", Lord-Trupps %d" % b.get("lordtrupps", 0))
