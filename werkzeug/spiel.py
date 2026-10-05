# -*- coding: utf-8 -*-
"""Stronghold beenden - in drei Stufen, mit eingebautem Test.

Warum es das gibt: Das Spiel laeuft auf hoher Rechtestufe. Von einer normalen
Sitzung aus ist es weder zu beenden noch zu lesen (Fehler 5). Gemessen am
30.09.2026: Auf diesem Rechner erhoeht Windows ohne Nachfrage
(ConsentPromptBehaviorAdmin = 0, Konto in der Gruppe Administratoren) - ein
Helfer, der hohe Rechte anfordert, bekommt sie still, ohne Dialog.

Die drei Stufen, von sanft nach hart:
  1. unser Modul im Spiel beendet es selbst ({"beenden": true}) - nur wenn es geladen ist
  2. ein erhoehter Helfer bittet das Fenster zu schliessen (wie ein Klick aufs X)
  3. ein erhoehter Helfer beendet den Prozess hart

Aufruf:
  python spiel.py status
  python spiel.py beenden
  (SHC_INSTANZ=2 davor: die zweite Spielkopie)

Rueckgabe: 0 = geschafft, 1 = nicht geschafft (Grund steht in der Ausgabe).

Zwei Instanzen (05.10.2026): Stufe 2 und 3 suchten frueher alle Prozesse
namens "Stronghold Crusader" - mit zwei Instanzen haette das Beenden der einen
die andere mitgerissen. Jetzt zaehlt nur der Prozess der gewaehlten Instanz.
"""
import base64, io, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from befehl import SPIEL, BEFEHL, LOG, INSTANZ


def ps(befehl):
    return subprocess.run(["powershell", "-NoProfile", "-Command", befehl],
                          capture_output=True, text=True, errors="replace").stdout.strip()


def erhoeht(befehl, warte_s=20):
    """Fuehrt einen PowerShell-Befehl mit hoher Rechtestufe aus (still, ohne Fenster)."""
    kodiert = base64.b64encode(befehl.encode("utf-16-le")).decode()
    ps("$p = Start-Process powershell -Verb RunAs -WindowStyle Hidden -PassThru "
       "-ArgumentList '-NoProfile','-EncodedCommand','%s'; "
       "[void]$p.WaitForExit(%d)" % (kodiert, warte_s * 1000))


def spiel_pids():
    """Prozesse DIESER Instanz. UCP legt beim Start "ucp-pid-<nummer>" in den
    Spielordner (gemessen 0,06-0,12 s nach Prozessstart). Nach einem Absturz
    bleibt die Datei liegen; vergibt Windows die Nummer neu, zeigte sie auf
    einen fremden Prozess. Darum zaehlt eine Nummer nur, wenn ein Spielprozess
    mit ihr lebt UND hoechstens 30 s vor der Datei gestartet ist."""
    dateien = {}
    for f in os.listdir(SPIEL):
        if f.startswith("ucp-pid-") and f[8:].isdigit():
            dateien[int(f[8:])] = os.path.getctime(os.path.join(SPIEL, f))
    if not dateien:
        return []
    aus = ps("Get-Process -Name 'Stronghold Crusader' -ErrorAction SilentlyContinue | "
             "ForEach-Object { '{0} {1}' -f $_.Id, ([DateTimeOffset]$_.StartTime).ToUnixTimeMilliseconds() }")
    pids = []
    for z in aus.splitlines():
        teile = z.split()
        if len(teile) == 2 and teile[0].isdigit() and int(teile[0]) in dateien:
            if abs(dateien[int(teile[0])] - int(teile[1]) / 1000.0) <= 30:
                pids.append(int(teile[0]))
    return pids


def modul_geladen():
    """True, wenn im aktuellen Log (wird bei jedem Spielstart neu angelegt) unser Modul aktiv ist."""
    try:
        return "villagestudio aktiv" in io.open(LOG, encoding="utf-8", errors="replace").read()
    except OSError:
        return False


def warte_bis_weg(sekunden):
    ende = time.time() + sekunden
    while time.time() < ende:
        if not spiel_pids():
            return True
        time.sleep(0.5)
    return not spiel_pids()


def status():
    pids = spiel_pids()
    print("Instanz %d: %s" % (INSTANZ, SPIEL))
    if not pids:
        print("Spiel: laeuft nicht")
        return
    lesbar = ps("[bool](Get-Process -Id %d).Path" % pids[0]) == "True"
    print("Spiel: laeuft (PID %s)" % ", ".join(map(str, pids)))
    print("Rechtestufe: %s" % ("gleich wie diese Sitzung" if lesbar else "hoeher - nur mit erhoehtem Helfer erreichbar"))
    print("Unser Modul: %s" % ("geladen (villagestudio aktiv)" if modul_geladen() else "NICHT geladen"))


def beenden():
    pids = spiel_pids()
    print("Instanz %d: %s" % (INSTANZ, SPIEL))
    if not pids:
        print("GESCHAFFT: das Spiel lief gar nicht.")
        return 0
    nur_diese = "Get-Process -Id %s -ErrorAction SilentlyContinue | " % ",".join(map(str, pids))
    if modul_geladen():
        kennung = int(time.time())
        io.open(BEFEHL, "wb").write(json.dumps({"id": kennung, "player": 1, "beenden": True}).encode("utf-8"))
        if warte_bis_weg(10):
            print("GESCHAFFT mit Stufe 1: unser Modul hat das Spiel beendet.")
            return 0
        print("Stufe 1 ohne Wirkung (Modul geladen, aber das Spiel laeuft noch) - weiter mit Stufe 2.")
    else:
        print("Stufe 1 entfaellt: unser Modul ist in diesem Spiel nicht geladen.")

    erhoeht(nur_diese + "ForEach-Object { [void]$_.CloseMainWindow() }")
    if warte_bis_weg(10):
        print("GESCHAFFT mit Stufe 2: das Fenster wurde gebeten zu schliessen und hat es getan.")
        return 0
    print("Stufe 2 ohne Wirkung nach 10 s (das Spiel reagiert nicht auf 'Fenster schliessen') - Stufe 3.")

    erhoeht(nur_diese + "Stop-Process -Force")
    if warte_bis_weg(5):
        print("GESCHAFFT mit Stufe 3: der Prozess wurde hart beendet.")
        return 0
    print("NICHT GESCHAFFT: das Spiel laeuft nach allen drei Stufen noch (PID %s)." % ", ".join(map(str, spiel_pids())))
    print("Moegliche Gruende: der erhoehte Helfer wurde nicht gestartet (Windows fragt jetzt doch nach?) "
          "oder der Prozess haengt im Kern fest.")
    return 1


if __name__ == "__main__":
    was = sys.argv[1] if len(sys.argv) > 1 else "status"
    if was == "status":
        status(); sys.exit(0)
    if was == "beenden":
        sys.exit(beenden())
    print(__doc__); sys.exit(2)
