# -*- coding: utf-8 -*-
"""Spielstand speichern ohne Klick (M7.01) - mit Beweis: die neue .sav-Datei.

Weg (gemessen/abgelesen 30.09.2026): {"optionen": 3} oeffnet im laufenden Spiel
den Speichern-Dialog; der Knopf {"laden": 3} speichert nur, wenn im aktiven
Textfeld ein Name mit Laenge > 0 steht. Die Textablage des Spiels:
  DAT_UserTextHandlerState = 0x01652740   (+0x0 textArrayIndex)
  textContentLengthArray   = 0x016527D0   (int[16])
  textCursorIndexArray     = 0x01652810   (int[16])
  textArray                = 0x01652890   (char[16][250])
Namensregel (Daniel): <Meilenstein> <Was getestet wird> <Karte> T<Tick>, <= 32 Zeichen.
Gibt es den Namen schon, fragt das Spiel "Datei ueberschreiben?" - {"dialogJa": true}
beantwortet das (gemessen). Jede gespeicherte Fassung wird mit Uhrzeit nach
daten/spielstaende/ kopiert.

Aufruf:  python speichern.py "M7-01 Speichertest Grumpy T1100"
"""
import os, re, shutil, struct, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from befehl import sende

TEXT_INDEX, LAENGEN, CURSOR, TEXTE = 0x01652740, 0x016527D0, 0x01652810, 0x01652890
ORDNER = os.path.expandvars(r"%USERPROFILE%\Documents\Stronghold Crusader\Saves")
SAMMLUNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "spielstaende")

def lies(adr):
    for z in sende({"player": 1, "peek": adr, "worte": 1}, 0.6):
        m = re.search(r"PEEK 0x%08X: (\S+)" % adr, z)
        if m:
            return int(m.group(1), 16) & 0xFFFFFFFF
    return None

def main():
    name = sys.argv[1]
    roh = name.encode("latin-1") + b"\0"
    if len(roh) > 33:
        print("NICHT GESCHAFFT: Name zu lang (%d Zeichen, hoechstens 32)" % (len(roh) - 1)); sys.exit(1)
    ziel = os.path.join(ORDNER, name + ".sav")
    vorher = os.path.getmtime(ziel) if os.path.exists(ziel) else None

    print(sende({"player": 1, "optionen": 3}, 1.5))                   # Dialog oeffnen
    idx = lies(TEXT_INDEX)
    print("aktives Textfeld:", idx)
    if idx is None or idx > 15:
        print("NICHT GESCHAFFT: aktives Textfeld unbrauchbar (%s)" % idx); sys.exit(1)
    basis = TEXTE + idx * 250
    roh += b"\0" * (-len(roh) % 4)
    for i in range(0, len(roh), 4):                                   # Name wortweise schreiben
        sende({"player": 1, "poke": basis + i, "wert": struct.unpack("<i", roh[i:i + 4])[0]}, 0.5)
    laenge = len(name)
    sende({"player": 1, "poke": LAENGEN + idx * 4, "wert": laenge}, 0.5)
    sende({"player": 1, "poke": CURSOR + idx * 4, "wert": laenge}, 0.5)
    print("Laenge im Feld jetzt:", lies(LAENGEN + idx * 4))
    print(sende({"player": 1, "laden": 3}, 3.0))                      # Knopf Speichern
    if vorher is not None:                                            # Name gibt es: Spiel fragt "Ueberschreiben?"
        print(sende({"player": 1, "dialogJa": True}, 3.0))

    for _ in range(10):
        if os.path.exists(ziel) and os.path.getmtime(ziel) != vorher:
            time.sleep(1)                                             # Schreiben abwarten
            kopie = os.path.join(SAMMLUNG, "%s_%s.sav" % (name, time.strftime("%Y%m%d-%H%M%S")))
            os.makedirs(SAMMLUNG, exist_ok=True)
            shutil.copy2(ziel, kopie)                                 # jede Fassung aufheben, auch beim Ueberschreiben
            print("GESCHAFFT: %s (%d Byte), Kopie %s" % (ziel, os.path.getsize(ziel), kopie)); return
        time.sleep(1)
    print("NICHT GESCHAFFT: keine neue Datei %s nach 10 s" % ziel); sys.exit(1)

if __name__ == "__main__":
    main()
