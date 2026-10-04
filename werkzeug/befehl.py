# -*- coding: utf-8 -*-
"""Einen Befehl an unser Modul schicken und die Antwort aus dem Log lesen.

Die Nummern-Regel ist fest eingebaut (Meilenstein M2.03): Das Modul
ueberspringt jeden Befehl, dessen 'id' es schon kennt. Darum vergibt dieses
Werkzeug jede Nummer nur einmal - stetig steigend ueber alle Laeufe hinweg,
die letzte vergebene steht in .letzte_id neben diesem Skript.

Aufruf:    python befehl.py '<json>' [wartesekunden]
Beispiel:  python befehl.py '{"player": 1, "tempo": 90}' 3
Als Baustein:  from befehl import sende; zeilen = sende({"zeit": True})
"""
import io, json, os, re, sys, time

SPIEL  = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
BEFEHL = os.path.join(SPIEL, "ucp", "villagestudio", "befehl.json")
LOG    = os.path.join(SPIEL, "ucp3.log")
MERKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".letzte_id")


def neue_id():
    try:
        letzte = int(io.open(MERKER).read().strip())
    except (OSError, ValueError):
        letzte = 0
    nummer = max(int(time.time()), letzte + 1)
    io.open(MERKER, "w").write(str(nummer))
    return nummer


STRENG = False   # True (z. B. im Lenker): Modulfehler in der Antwort brechen sofort laut ab (Daniel 23:48)
# Lua-Fehler meldet das Modul als "logik: <ort>:<zeile>: <text>" (pcall), eine Befehlsliste mit
# "logik: <gut> von <alle> Befehlen ausgefuehrt" - weniger gut als alle heisst: mindestens einer ist gescheitert.
# Anlass 04.10.2026: eine globale Variable liess jeden Angriffsbefehl scheitern, vier Partien lang unbemerkt.
LUA_FEHLER = re.compile(r"logik: .*:\d+: ")
BILANZ = re.compile(r"logik: (\d+) von (\d+) Befehlen ausgefuehrt")

def pruefe(zeilen):
    for z in zeilen:
        b = BILANZ.search(z)
        if LUA_FEHLER.search(z) or (b and int(b.group(1)) < int(b.group(2))):
            raise RuntimeError("MODULFEHLER (Antwort des Moduls): " + z[:240])
    return zeilen

LAUF = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lauf")   # Kanal belegt: "<pid>" - der Lenker frischt sie je Runde auf

def belege():
    """Der Lenker meldet sich als Besitzer des Kanals (je Runde aufrufen). 05.10.: eine Nebenabfrage aus einem zweiten
    Prozess lief mitten in Partie 9f in den Kanal - zwei Schreiber auf befehl.json verlieren Befehle."""
    io.open(LAUF, "w").write(str(os.getpid()))

def freigeben():
    try:
        if io.open(LAUF).read().strip() == str(os.getpid()):
            os.remove(LAUF)
    except OSError:
        pass

def _kanal_frei():
    try:
        pid = io.open(LAUF).read().strip()
        alter = time.time() - os.path.getmtime(LAUF)
    except OSError:
        return
    if pid != str(os.getpid()) and alter < 15:
        raise RuntimeError("KANAL BELEGT: ein Lauf (Prozess %s) benutzt den Befehlskanal gerade (vor %.0f s gemeldet)" % (pid, alter))

def sende(befehl, warte=3.0, bis=None):
    """Schickt den Befehl (dict) und gibt die neuen Modul-Logzeilen zurueck.
    bis = Text, auf den gewartet wird (alle 20 ms nachsehen, hoechstens <warte> s) - statt fest zu warten
    (04.10.2026: feste Wartezeit machte eine Lenker-Runde 1,1 s lang)."""
    _kanal_frei()
    befehl = dict(befehl)
    befehl["id"] = neue_id()
    vorher = os.path.getsize(LOG)
    io.open(BEFEHL, "wb").write(json.dumps(befehl).encode("utf-8"))
    if bis is None:
        time.sleep(warte)
    else:
        ende = time.time() + warte
        while time.time() < ende:
            time.sleep(0.02)
            if os.path.getsize(LOG) > vorher:
                with io.open(LOG, encoding="utf-8", errors="replace") as f:
                    f.seek(vorher)
                    if bis in f.read():
                        break
    with io.open(LOG, encoding="utf-8", errors="replace") as f:
        f.seek(vorher)
        neu = f.read()
    zeilen = [z.split("| ", 1)[-1].strip() for z in neu.splitlines()
              if "villagestudio" in z and "ZUSTAND" not in z]
    return pruefe(zeilen) if STRENG else zeilen


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    zeilen = sende(json.loads(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 3.0)
    for z in zeilen:
        print(z)
    if not zeilen:
        print("(keine Antwort im Log)")
        sys.exit(1)
