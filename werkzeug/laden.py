# -*- coding: utf-8 -*-
"""Spielstand laden ohne Klick (M7.02) - per Name, mit Beleg: Spielzeit und Bild.

Weg (Menue-Handbuch 02.09. + gemessen 30.09.2026):
  {"optionen": 2} oeffnet im laufenden Spiel den Lade-Dialog.
  Liste im Speicher: Anzahl 0x0112661C; Eintrag n (0 = oben) ist die Namens-
  nummer k = [0x01126E28 + 4n]; der Name steht bei 0x11BFCF8 + k*0x3E9
  (getLoadedMapNameForIndex, 0x0046C2E0). Geladen wird Eintrag
  n = markierte Zeile [0x01126624] + Scrollstand [0x01126628], dann {"laden": 2}.
  Alles in EINEM Auftrag, sonst greift der Poll dazwischen.
Laden hebt die Pause auf: vorher die Lade-Pause scharf machen ({"ladepause": true},
haelt beim ersten Tick nach einem Sprung der Spielzeit - in beide Richtungen),
danach zur Sicherheit noch einmal pausieren und pruefen, dass die Spielzeit steht.
(Eine Tick-Pause auf "jetzt + 1" greift nur, wenn der geladene Stand spaeter liegt.)

Aufruf:  python laden.py "<Name>"      (Name wie in der Liste, ohne .sav)
         python laden.py --liste       (nur die Liste zeigen)
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from befehl import sende, neue_id

ANZAHL, MARKIERT, SCROLL, SICHTBAR = 0x0112661C, 0x01126624, 0x01126628, 0x0112662C
LISTE, NAMEN, NAMENSLAENGE = 0x01126E28, 0x11BFCF8, 0x3E9
TICK, PAUSE = 0x0117CADC, 0x01FEA054
SPIEL = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
BILDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "bilder")

def peek(adr, n=1):
    for z in sende({"player": 1, "peek": adr, "worte": n}, 0.6):
        if "PEEK" in z:
            return [int(x, 16) & 0xFFFFFFFF for x in z.split(": ", 2)[-1].split()]
    raise RuntimeError("keine Antwort auf peek 0x%08X" % adr)

def liste():
    anz = peek(ANZAHL)[0]
    if not 0 < anz <= 500:
        raise RuntimeError("Liste unplausibel (Anzahl %d) - ist der Lade-Dialog offen?" % anz)
    nummern = peek(LISTE, anz)
    namen = []
    for k in nummern:
        roh = b"".join(w.to_bytes(4, "little") for w in peek(NAMEN + k * NAMENSLAENGE, 10))
        namen.append(roh.split(b"\0")[0].decode("latin-1"))
    return namen

def bild(datei):
    sende({"player": 1, "bild": "karte"}, 2.0)
    from PIL import Image
    os.makedirs(BILDER, exist_ok=True)
    Image.open(os.path.join(SPIEL, "ucp", "villagestudio", "vs_karte.bmp")).save(os.path.join(BILDER, datei))
    return os.path.join(BILDER, datei)

def main():
    sende({"player": 1, "optionen": 2}, 1.5)                          # Lade-Dialog oeffnen
    namen = liste()
    if sys.argv[1] == "--liste":
        for n, name in enumerate(namen):
            print(n, name)
        return
    ziel = sys.argv[1]
    if ziel not in namen:
        print("NICHT GESCHAFFT: '%s' steht nicht in der Liste (%d Eintraege)" % (ziel, len(namen))); sys.exit(1)
    n = namen.index(ziel)
    scroll = max(0, n - 15)
    zeile = n - scroll
    vorher = peek(TICK)[0]
    print("Eintrag %d '%s' -> Scrollstand %d, Zeile %d; Spielzeit vorher %d" % (n, ziel, scroll, zeile, vorher))

    print(sende({"player": 1, "ladepause": True}, 0.8))               # haelt beim ersten Tick nach dem Laden
    antwort = sende({"befehle": [
        {"id": neue_id(), "player": 1, "poke": SCROLL, "wert": scroll},
        {"id": neue_id(), "player": 1, "poke": MARKIERT, "wert": zeile},
        {"id": neue_id(), "player": 1, "laden": 2}]}, 4.0)
    print(antwort)
    sende({"player": 1, "pause": True}, 0.8)                          # Sicherheitsnetz
    sende({"player": 1, "ladepause": "aus"}, 0.8)                     # nichts scharf zuruecklassen
    if not any("LADEPAUSE: Spielzeit sprang" in z for z in antwort):
        print("WARNUNG: die Lade-Pause hat keinen Sprung gesehen")
    t1 = peek(TICK)[0]; time.sleep(1.0); t2 = peek(TICK)[0]
    pause = peek(PAUSE)[0]
    print("Spielzeit nachher %d / %d, Pause %d" % (t1, t2, pause))
    datei = bild("m7-02_%s_t%d.png" % (ziel.replace(" ", "_"), t2))
    if t1 != t2 or pause != 1:
        print("WARNUNG: Spiel steht nicht still")
    if t2 == vorher:
        print("NICHT GESCHAFFT: Spielzeit unveraendert (%d) - nichts geladen" % t2); sys.exit(1)
    print("GELADEN: '%s' bei Tick %d, Bild %s" % (ziel, t2, datei))

if __name__ == "__main__":
    main()
