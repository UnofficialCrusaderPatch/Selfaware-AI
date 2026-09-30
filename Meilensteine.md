# Meilensteine - Selfaware-AI

Der Katalog aller Meilensteine auf dem Weg zur selbstlernenden KI. Ein Meilenstein gilt erst als **erreicht**, wenn (1) er im Speicher oder Log belegt ist UND (2) Daniel ihn am laufenden Spiel gesehen und abgenommen hat. Ausnahme: was sich nicht sichtbar pruefen laesst, wird im Hintergrund abgenommen. Alle Dauern in **Ticks**.

Zwei Spalten, zwei Abnahmen: **Definition** = Daniel hat festgelegt, *was* geprueft wird. **Erreicht** = Daniel hat es am Spiel gesehen. Jede Abnahme wird hier mit Datum eingetragen; die Messung dazu steht in `doku/Wissensstand.md` des Village-Studio-Repos.

Diese Datei ist die eine Quelle des Katalogs und wird direkt gepflegt. Werkzeuge zu den Meilensteinen liegen in `werkzeug/`.

Lieferung 1 (30.09.2026): Bloecke M1 Grundlagen, M2 Spiel starten, M3 Gefecht steuern, M4 Spielende und Lord-Tod, M5 Ticks. Folgen: Mods und eigene KI, Einheiten, Wirtschaft, Burg, Ausloeser, die Ansicht der KI, Zuschauen, Lernschleife.

## Uebersicht

| ID | Meilenstein | Stand | Definition | Erreicht |
|---|---|---|---|---|
| M1.01 | Ziel und Endbild in einem Satz | Grundlage | abgenommen 30.09.2026 | - |
| M1.02 | Was 'abgenommen' heisst | Grundlage | abgenommen 30.09.2026 | - |
| M1.03 | Die Grundregeln der Plattform | Grundlage | abgenommen 30.09.2026 | - |
| M1.04 | Ein Tick ist die Einheit fuer alles | Grundlage | abgenommen 30.09.2026 | - |
| M2.01 | Spiel starten, ohne dass du etwas anfasst | gemessen | abgenommen 30.09.2026 | - |
| M2.02 | Pruefen, dass unser Modul wirklich laeuft | gemessen | abgenommen 30.09.2026 | - |
| M2.03 | Befehl hinein, Antwort heraus | gemessen | abgenommen 30.09.2026 | - |
| M2.04 | Spiel per Befehl beenden | belegt | abgenommen 30.09.2026 | - |
| M2.05 | Absturz und Haengen erkennen | offen | abgenommen 30.09.2026 | - |
| M2.06 | Mehrere Spiele gleichzeitig | offen | abgenommen 30.09.2026 | - |
| M2.07 | UCP3-GUI schliessen, ohne die Config zu beruehren | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 20:59 - live offen |
| M2.08 | Wann die GUI die Config schreibt | gemessen | Daniels Wunsch 30.09.2026 | - |
| M2.09 | UCP3-GUI oeffnen, ohne die Config zu beruehren | Werkzeug gebaut, ungetestet | Daniels Wunsch 30.09.2026 | - |
| M2.10 | Ein Spiel ohne unser Modul beenden | UEBERHOLT durch M2.11/M2.12 | Daniels Wunsch 30.09.2026 | - |
| M2.11 | Stronghold schliessen - in drei Stufen | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 21:06 - live offen |
| M2.12 | Hohe Rechte ohne Klick anfordern | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 21:04 - live offen |
| M2.13 | Config herrichten: Modul + weiterlaufen ohne Fokus | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 21:10 |
| M2.14 | Befehle mit Nummern, die nie doppelt vorkommen | gemessen | M2.03 | Hintergrund belegt 30.09., 21:10 |
| M3.01 | Zurueck ins Hauptmenue per Befehl | gemessen | abgenommen 30.09.2026 | - |
| M3.02 | Eigenes Spiel ohne Maus starten | gemessen (Lauf 1) | abgenommen 30.09.2026 | Hintergrund belegt 21:10; von Daniel live gesehen 21:14 - Aufbau noch falsch |
| M3.03 | Kampagne und eigenes Spiel sicher unterscheiden | halb gemessen (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.04 | Karte waehlen: Liga_Grumpy Neighbors | gemessen (Lauf 1) | abgenommen 30.09.2026 | Hintergrund belegt 21:10; von Daniel live gesehen 21:14 |
| M3.05 | Selfaware auf beide KI-Plaetze | im Speicher ja, im Spiel NEIN (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.06 | Feste Startplaetze: oben und unten | offen, Spur gefunden (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.07 | Kein Mensch im Selbstspiel | offen: unser Startbefehl setzt einen echten Menschen ein (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.08 | Startgold und Startgueter wie in der Team-Liga | offen | abgenommen 30.09.2026 | - |
| M3.09 | Tempo setzen | gemessen | abgenommen 30.09.2026 | - |
| M3.10 | Neues Spiel ohne Neustart des Programms | teils gemessen | abgenommen 30.09.2026 | - |
| M3.11 | Spiel pausieren und fortsetzen per Befehl | gemessen (Lauf 1) | Daniel 30.09.: "du kannst das Spiel pausieren" | Hintergrund belegt 21:10 |
| M3.12 | Tempo erst NACH dem Start setzen | gemessen (Lauf 1) | Lauf 1 | Hintergrund belegt 21:10 |
| M4.01 | Die Lords im Gefecht finden | gemessen | abgenommen 30.09.2026 | - |
| M4.02 | Lord-Tod erkennen | gemessen | abgenommen 30.09.2026 | - |
| M4.03 | Was nach dem Lord-Tod wirklich passiert | offen | abgenommen 30.09.2026 | - |
| M4.04 | Der einfachste echte Tod: zwei Lords laufen aufeinander zu | offen | abgenommen 30.09.2026 | - |
| M4.05 | Den Sieger aus dem Speicher lesen | offen | abgenommen 30.09.2026 | - |
| M4.06 | Den Endbildschirm erkennen | gemessen | abgenommen 30.09.2026 | - |
| M4.07 | Zeitlimit: die ersten X Ticks | offen | abgenommen 30.09.2026 | - |
| M5.01 | Was ein Tick ist und wo er steht | belegt | abgenommen 30.09.2026 | - |
| M5.02 | Die Grenze: hoechstens 11 Ticks je Bild | abgelesen | abgenommen 30.09.2026 | - |
| M5.03 | Greift unser Modul jeden Tick ein oder nur jedes Bild? | offen | abgenommen 30.09.2026 | - |
| M5.04 | Wie lange Ereignisse dauern (Katalog) | teils belegt | abgenommen 30.09.2026 | - |
| M5.05 | Veraendert das Tempo das Spiel? | offen | abgenommen 30.09.2026 | - |

## Die Meilensteine im Einzelnen

### M1.01 Ziel und Endbild in einem Satz

*Stand beim Anlegen: Grundlage*

ZIEL: Eine KI 'Selfaware', die sich im Selbstspiel verbessert. Endbild: du schaust zu und fliegst frei ueber die Karte, waehrend die KI jeden Tick ihre eigene Ansicht des Spielfelds hat.  
STAND: steht im Plan (Selfaware-AI/Plan-selbstlernende-KI.md), mit dir abgestimmt am 30.09.  
DU SIEHST: den Plan im Repo.  
WIDERLEGT, WENN: du das Endbild anders beschreibst.  

**Vorschlag:** Abnehmen, wenn der Satz so stimmt.  

### M1.02 Was 'abgenommen' heisst

*Stand beim Anlegen: Grundlage*

ZIEL: Ein Meilenstein gilt erst als erreicht, wenn (1) ich ihn im Speicher oder Log belegt habe UND (2) du ihn am laufenden Spiel gesehen und abgenommen hast.  
STAND: deine Regel vom 30.09.  
ABLAGE: Jede Abnahme bekommt eine Zeile mit Datum im Meilenstein-Katalog im Selfaware-Repo; die Messung dazu steht im Wissensstand.  
WIDERLEGT, WENN: ein Punkt als erreicht gilt, ohne dass beides vorliegt.  

**Vorschlag:** So festhalten.  
**Daniel, 30.09.:** Ausnahme: Dinge, die sich nicht sichtbar pruefen lassen, werden im Hintergrund abgenommen.  

### M1.03 Die Grundregeln der Plattform

*Stand beim Anlegen: Grundlage*

ZIEL: Die vier Dinge, gegen die man nicht bauen kann, sind jedem Schritt klar: (1) nur das Modul im Spiel darf ans Spiel, von aussen ist alles gesperrt; (2) ein Spiel faehrt immer nur eine Sitzung (Testsperre); (3) die ucp-config.yml hat einen Schreiber; (4) die UCP3-GUI bleibt beim Testen zu - sie wirft unser Modul aus der Config (heute gemessen).  
STAND: belegt, Betriebsregeln und Wissensstand 13.  
WIDERLEGT, WENN: ein Testlauf ohne Sperre oder mit offener GUI als gueltig gezaehlt wird.  

**Vorschlag:** So festhalten.  

### M1.04 Ein Tick ist die Einheit fuer alles

*Stand beim Anlegen: Grundlage*

ZIEL: Jede Dauer, jedes Zeitlimit und jede Messung wird in Ticks angegeben; Sekunden und Spielzeit werden nur daraus umgerechnet.  
STAND: deine Entscheidung vom 30.09.; die Umrechnung ist belegt (Tag = 50 Ticks, Jahr = 9.600; Ticks je Sekunde = Tempo).  
WIDERLEGT, WENN: irgendwo eine Dauer nur in Sekunden steht.  

**Vorschlag:** So festhalten.  

### M2.01 Spiel starten, ohne dass du etwas anfasst

*Stand beim Anlegen: gemessen*

ZIEL: Das Spiel startet per Befehl im Hintergrund, dein Fenster bleibt vorn.  
STAND: gemessen am 30.09. mit werkzeug/starte_spiel.py (Meldung: 'Dein Fenster ist wieder vorn, das Spiel liegt dahinter').  
ICH PRUEFE: genau ein Crusader-Prozess, Fenstertitel 'Crusader'.  
DU SIEHST: Stronghold laeuft, du hast nichts geklickt und dein Fenster ist vorn geblieben.  
WIDERLEGT, WENN: du klicken musst oder zwei Prozesse laufen.  

**Vorschlag:** Beim naechsten Start live abnehmen.  

### M2.02 Pruefen, dass unser Modul wirklich laeuft

*Stand beim Anlegen: gemessen*

ZIEL: Vor jedem Test steht fest, dass das Modul geladen ist - sonst ist jede Beobachtung wertlos.  
STAND: gemessen am 30.09. (Logzeile 'villagestudio aktiv' um 19:53, nachdem ich das Modul wieder eingetragen hatte).  
ICH PRUEFE: 3 Eintraege 'villagestudio' in der Config UND die Logzeile.  
DU SIEHST: die Logzeile, die ich dir zeige.  
WIDERLEGT, WENN: ein Befehl wirkt, obwohl die Zeile fehlt, oder umgekehrt.  

**Vorschlag:** Abnehmen.  

### M2.03 Befehl hinein, Antwort heraus

*Stand beim Anlegen: gemessen*

ZIEL: Jeder Befehl kommt an und hinterlaesst eine Antwort im Log.  
STAND: gemessen am 30.09. - mit einer Falle: Befehle mit einer schon benutzten Nummer (id) werden uebersprungen. Zwei Messlaeufe waren deshalb wirkungslos. Loesung: Nummern aus der Uhrzeit, stetig steigend.  
ICH PRUEFE: zu jeder Befehlsnummer genau eine Antwortzeile.  
DU SIEHST: ich schicke 'Tempo 100', das Spiel wird sichtbar langsamer.  
WIDERLEGT, WENN: ein Befehl ohne Antwortzeile wirkt oder eine Antwort ohne Wirkung kommt.  

**Vorschlag:** Nummern-Regel fest ins Werkzeug einbauen, dann abnehmen.  

### M2.04 Spiel per Befehl beenden

*Stand beim Anlegen: belegt*

ZIEL: Das Spiel laesst sich ohne dich beenden - von aussen ist das gesperrt.  
STAND: belegt laut Betriebsregeln ({ "beenden": true } ruft ExitProcess im Spiel).  
ICH PRUEFE: danach kein Crusader-Prozess mehr.  
DU SIEHST: das Fenster verschwindet.  
WIDERLEGT, WENN: der Prozess bleibt.  

**Vorschlag:** Live abnehmen.  

### M2.05 Absturz und Haengen erkennen

*Stand beim Anlegen: offen*

ZIEL: Die Schleife merkt selbst, wenn das Spiel abstuerzt oder haengt, und startet neu - sonst steht nachts alles still.  
STAND: offen. Drei Merkmale sind denkbar: Prozess weg, Uhr steht, Log waechst nicht mehr.  
ICH PRUEFE: je Merkmal einen absichtlich herbeigefuehrten Fall.  
DU SIEHST: nach einem erzwungenen Ende startet das Spiel von selbst wieder.  
WIDERLEGT, WENN: ein stehendes Spiel laenger als eine Minute unbemerkt bleibt.  

**Vorschlag:** Vor der Lernschleife bauen, nicht jetzt.  

### M2.06 Mehrere Spiele gleichzeitig

*Stand beim Anlegen: offen*

ZIEL: 2, dann 5, dann mehr Spielkopien laufen nebeneinander.  
STAND: offen. Die 'laeuft schon'-Sperre greift je Installation; ob Kopien sich Config, Log und Befehlsdatei teilen, ist ungeprueft.  
WIDERLEGT, WENN: eine zweite Kopie im 'laeuft schon'-Dialog haengt.  

**Vorschlag:** Erst nach dem ersten durchgespielten Spiel (deine Regel).  

### M2.07 UCP3-GUI schliessen, ohne die Config zu beruehren

*Stand: gemessen 30.09.2026. Daniel: "es gibt keinen zu kleinen Schritt".*

ANLEITUNG: `python werkzeug/gui.py schliessen` (im Selfaware-AI-Repo). Das Werkzeug bittet die GUI zu schliessen - dieselbe Nachricht wie ein Klick aufs X - und wartet bis zu 15 s. Erzwungen wird nie.  
ERKLAERUNG: Die GUI muss zu sein, bevor wir testen, weil sie beim Spielstart die Config ueberschreibt (M2.08). Sie laeuft auf derselben Rechtestufe wie Claude und darf deshalb von hier geschlossen werden (Pfad lesbar: `%LOCALAPPDATA%\UCP3-GUI\UCP3-GUI.exe`).  
TEST, EINGEBAUT: geschafft = kein GUI-Prozess mehr UND Pruefsumme der Config vorher = nachher. Nicht geschafft = Prozess lebt nach 15 s noch; das Werkzeug nennt den wahrscheinlichen Grund (offener Dialog, z. B. ungespeicherte Aenderungen) und verwirft nichts.  
GEMESSEN 30.09., 20:59: GUI (PID 30528) geschlossen, Config-Pruefsumme `58591298a2e027cc` vorher wie nachher, Rueckgabe 0.  
DU SIEHST: das GUI-Fenster verschwindet, ohne dass du klickst.  
WIDERLEGT, WENN: die GUI weiterlaeuft oder die Pruefsumme sich aendert.  

### M2.08 Wann die GUI die Config schreibt

*Stand: gemessen 30.09.2026.*

ERGEBNIS: Die GUI schreibt die Config **beim Spielstart aus der GUI** - Aenderungszeit der Config 20:21:34 = Startzeit des Spiels, auf die Sekunde. **Beim Schliessen schreibt sie nicht** (Pruefsumme gleich, M2.07). Beim Oeffnen: noch offen, prueft M2.09.  
FOLGE: Das Spiel nie aus der GUI starten, solange getestet wird. Wer es doch tut, verliert `villagestudio` in der Config und bekommt ein Spiel ohne unser Modul (M2.10).  
WIDERLEGT, WENN: die Config sich aendert, ohne dass aus der GUI gestartet wurde.  

### M2.09 UCP3-GUI oeffnen, ohne die Config zu beruehren

*Stand: Werkzeug gebaut, noch nicht ausgefuehrt.*

ANLEITUNG: `python werkzeug/gui.py oeffnen`. Startet die GUI, wartet auf ihren Prozess und vergleicht die Pruefsumme der Config 10 s spaeter.  
TEST, EINGEBAUT: geschafft = GUI-Prozess da UND Config unveraendert. Meldet ausdruecklich, falls schon das Oeffnen schreibt.  
WIDERLEGT, WENN: die Pruefsumme sich beim blossen Oeffnen aendert.  

### M2.10 Ein Spiel ohne unser Modul beenden

*Stand: UEBERHOLT am 30.09.2026, 21:06 - geloest durch M2.11 und M2.12. Daniel: "das soll kein Blocker sein". Der alte Text bleibt als Sicherung stehen.*

WARUM NICHT: Das aus der GUI gestartete Spiel (PID 15208) laeuft auf hoeherer Rechtestufe - schon sein Programmpfad ist von hier aus nicht lesbar. Von aussen beenden scheitert daran (Betriebsregeln: Fehler 5). Der einzige Weg von innen ist unser Modul (`{ "beenden": true }`, M2.04) - und genau das fehlt in einem Spiel, das aus der GUI kam.  
ANLEITUNG: Daniel schliesst dieses eine Spiel selbst. Vorbeugung: das Spiel nur ueber `werkzeug/starte_spiel.py` (VillageStudio) bzw. die Entwicklermodus-Verknuepfung starten - dann ist das Modul drin und das Beenden geht per Befehl.  
TEST: `python werkzeug/gui.py status` meldet "hoehere Rechtestufe, von hier NICHT beendbar" oder "laeuft nicht".  
WIDERLEGT, WENN: sich ein aus der GUI gestartetes Spiel doch von hier beenden laesst.  

### M2.11 Stronghold schliessen - in drei Stufen

*Stand: gemessen 30.09.2026, 21:06.*

ANLEITUNG: `python werkzeug/spiel.py beenden` (Status vorher/nachher: `python werkzeug/spiel.py status`).  
ERKLAERUNG: Drei Stufen, von sanft nach hart: (1) ist unser Modul geladen, beendet es das Spiel von innen (`{ "beenden": true }`, M2.04); (2) sonst bittet ein still erhoehter Helfer (M2.12) das Fenster zu schliessen, wie ein Klick aufs X; (3) erst wenn das nach 10 s nichts bewirkt, beendet der Helfer den Prozess hart. Das Werkzeug sagt, welche Stufe gewirkt hat.  
TEST, EINGEBAUT: geschafft = kein Crusader-Prozess mehr. Nicht geschafft = nach allen drei Stufen laeuft er noch; das Werkzeug nennt die moeglichen Gruende.  
GEMESSEN 30.09., 21:06: das aus der GUI gestartete Spiel (PID 15208, ohne Modul) - Stufe 1 entfiel, **Stufe 2 hat gewirkt**; Gegenprobe mit `tasklist`: kein Crusader-Prozess mehr.  
DU SIEHST: das Stronghold-Fenster verschwindet, ohne dass du klickst.  
WIDERLEGT, WENN: das Spiel weiterlaeuft oder nur mit Stufe 3 zu beenden ist, obwohl es auf Stufe 2 reagieren muesste.  

### M2.12 Hohe Rechte ohne Klick anfordern

*Stand: gemessen 30.09.2026, 21:04.*

ERKLAERUNG: Das Spiel laeuft auf hoher Rechtestufe, diese Sitzung auf mittlerer - daher kam jede Sperre "von aussen" (Fehler 5). Gemessen: Windows ist hier auf **"Erhoehen ohne Nachfrage"** eingestellt (`ConsentPromptBehaviorAdmin = 0`), und Daniels Konto ist in der Gruppe Administratoren. Ein Helfer, der hohe Rechte anfordert (`Start-Process -Verb RunAs`), bekommt sie also still - ohne Dialog, ohne Klick. Es wird dabei **keine Einstellung geaendert**; genutzt werden nur die Rechte, die das Konto ohnehin hat, und nur fuer den einen Befehl.  
TEST: `scratchpad`-Probe schrieb aus dem erhoehten Helfer "Hohe Verbindlichkeitsstufe (S-1-16-12288)", fertig nach 0,3 s, und konnte den Programmpfad des Spiels lesen - den eine normale Sitzung NICHT lesen kann.  
FOLGE: Was bisher "von aussen gesperrt" hiess (Spiel beenden, vermutlich auch Fenster verschieben, Tasten schicken, Speicher lesen), ist mit einem erhoehten Helfer erreichbar. Einzeln zu messen, bevor es behauptet wird.  
OFFEN: Warum das Spiel ueberhaupt hoch laeuft - es hat weder das Kompatibilitaets-Haekchen "Als Administrator ausfuehren" noch ein Manifest, das Rechte verlangt.  
WIDERLEGT, WENN: der Helfer mit mittlerer Stufe laeuft oder Windows einen Dialog zeigt.  

### M3.01 Zurueck ins Hauptmenue per Befehl

*Stand beim Anlegen: gemessen*

ZIEL: Aus jedem Bildschirm zurueck ins Hauptmenue.  
STAND: gemessen ({ "menue": 41 }, zuletzt am 30.09. aus dem Endbildschirm).  
DU SIEHST: das Hauptmenue erscheint, ohne Klick.  
WIDERLEGT, WENN: das Spiel im alten Bildschirm stehen bleibt.  

**Vorschlag:** Live abnehmen.  

### M3.02 Eigenes Spiel ohne Maus starten

*Stand beim Anlegen: teils gemessen*

ZIEL: Ein 'Eigenes Spiel' (nicht Kampagne) startet per Befehl.  
STAND: Der Befehl 'eigenesGefecht' im Modul ist am 01.09. gelaufen, aber noch NIE mit der Team-Liga und der Liga-Karte.  
ICH PRUEFE: Spielmodus 'Gefecht', keine Kampagnen-Mission, Uhr laeuft.  
DU SIEHST: das Spiel startet auf der Liga-Karte, du hast nichts geklickt.  
WIDERLEGT, WENN: wieder eine Kampagnen-Mission kommt (mein Fehler von heute).  

**Vorschlag:** Als erstes live messen.  

### M3.03 Kampagne und eigenes Spiel sicher unterscheiden

*Stand beim Anlegen: offen*

ZIEL: Die Schleife weiss aus dem Speicher, ob ein eigenes Spiel laeuft - nicht aus einem Bild.  
STAND: offen. Anhaltspunkt im Modul: isSkirmishTrail = 0 beim eigenen Spiel.  
WIDERLEGT, WENN: das Merkmal bei der Kampagnen-Mission denselben Wert hat.  

**Vorschlag:** Bei M3.02 gleich mitmessen.  

### M3.04 Karte waehlen: Liga_Grumpy Neighbors

*Stand beim Anlegen: offen*

ZIEL: Die Karte ist per Befehl waehlbar.  
STAND: offen. Der Befehl nimmt einen Kartennamen ohne '.map'; die Datei liegt im Plugin-Ordner der Team-Liga, der Kartenlader ist darauf eingestellt. Ob der Name von dort gefunden wird, ist nicht gemessen.  
DU SIEHST: die Liga-Karte mit ihrer Form.  
WIDERLEGT, WENN: eine andere Karte oder die Vorgabekarte erscheint.  

**Vorschlag:** Mit M3.02 zusammen messen.  

### M3.05 Selfaware auf beide KI-Plaetze

*Stand beim Anlegen: abgelesen*

ZIEL: Beide Computergegner sind unsere KI.  
STAND: abgelesen - der Befehl setzt alle KI-Plaetze auf denselben Typ; 'ki: 1' ist der Rattenplatz (in diesem Mod Rotkaeppchen). Solange Selfaware noch nicht angelegt ist, spielen dort zwei Rotkaeppchen.  
ICH PRUEFE: KI-Liste im Speicher zeigt zweimal Typ 1.  
DU SIEHST: zwei Rotkaeppchen im Spiel.  
WIDERLEGT, WENN: eine andere Figur auftaucht.  

**Vorschlag:** Zuerst mit Rotkaeppchen abnehmen, Selfaware folgt in Lieferung 2.  

### M3.06 Feste Startplaetze: oben und unten

*Stand beim Anlegen: offen*

ZIEL: Unsere zwei KIs stehen immer oben und unten - wie in deinem Bild.  
STAND: offen. Das Modul verteilt die Plaetze heute ZUFAELLIG (abgelesen im Code). Die Platzliste liegt bei 0x01A275D0; wie man dort feste Plaetze eintraegt, ist ungeklaert.  
DU SIEHST: in drei Starts hintereinander stehen die Burgen jedes Mal an denselben Stellen.  
WIDERLEGT, WENN: sich die Plaetze zwischen zwei Starts aendern.  

**Vorschlag:** Das ist die erste echte Forschungsaufgabe - klein, aber noetig.  

### M3.07 Der Mensch auf Platz 1

*Stand beim Anlegen: offen*

ZIEL: Klaeren, was der Mensch im Selbstspiel tut, ohne das Ergebnis zu verfaelschen.  
STAND: offen. Das Modul setzt immer einen Menschen ('Daniel') auf Platz 1. Ohne Menschen war ein frueherer Versuch nach 87 Ticks entschieden. Greifen die KIs zuerst den Menschen an, misst das Spiel etwas anderes als 'Selfaware gegen Selfaware'.  
WIDERLEGT, WENN: ein Spiel endet, weil der Mensch faellt.  

**Vorschlag:** Siehe Frage 1.  
**Daniel, 30.09.:** ERLEDIGT durch Daniel: Einen Menschen auf Platz 1 gibt es in eigenen Gefechten der Team-Liga 2 nicht - der Mensch ist dort nur ein Geist. Genau dafuer wurde der Mod gewaehlt. Es spielen nur die zwei Selfaware-KIs gegeneinander, wie im StarCraft-Vorbild. Pruefen im ersten Lauf: Platz 1 hat keinen Lord. Wenn es spaeter auch in Vanilla ohne Menschen geht: gerne.  

### M3.08 Startgold und Startgueter wie in der Team-Liga

*Stand beim Anlegen: offen*

ZIEL: Das Spiel startet mit den Liga-Regeln, z. B. 0 Gold.  
STAND: offen. Das Modul setzt Ausgleich 2 und Startstufe 1 (am 01.09. gemessen, fuer die alte Config). Was das unter der Team-Liga ergibt, ist ungeprueft.  
ICH PRUEFE: Gold und Waren beider KIs im ersten Tick.  
DU SIEHST: die Gold-Anzeige.  
WIDERLEGT, WENN: eine KI mit Gold startet.  

**Vorschlag:** Mit M3.02 zusammen messen.  
**Daniel, 30.09.:** Die Balances gehoeren dazu. Quelle: SBAs Balance-Daten (shc-vergleichstabelle/daten, README zuerst); fuer Team-Liga ist liga_ai.json die Wahrheit. GEMESSEN 30.09.: die im Spiel installierte liga_ai.json (Mod-KI-Team-Liga-2.0.2) ist inhaltlich identisch mit SBAs Quelle (Commit 5e9a83f) - 942 von 942 Werten gleich, nur die Schreibweise der Datei weicht ab. Das Startgold steht NICHT in liga_ai.json, sondern in der Erweiterung startResources (ucp-config.yml) - welcher ihrer Werte im eigenen Gefecht greift, wird im ersten Lauf gemessen.  

### M3.09 Tempo setzen

*Stand beim Anlegen: gemessen*

ZIEL: Das Tempo ist per Befehl einstellbar.  
STAND: gemessen am 30.09.: Tempo 40 = 40 Ticks/s, 1000 = rund 1100 Ticks/s.  
DU SIEHST: ich schalte zwischen 40 und 1000 um, das Spiel wird sichtbar schnell und wieder langsam.  
WIDERLEGT, WENN: sich die Ticks je Sekunde nicht aendern.  

**Vorschlag:** Live abnehmen.  

### M3.10 Neues Spiel ohne Neustart des Programms

*Stand beim Anlegen: teils gemessen*

ZIEL: Nach einem Spiel sofort das naechste - ohne Stronghold neu zu starten.  
STAND: gemessen nur fuer die Kampagnen-Mission (Hauptmenue, dann Start mit 'trotzdem' - die Uhr sprang auf 3470). Fuer das eigene Spiel noch nicht.  
DU SIEHST: zwei Spiele hintereinander, ohne dass das Fenster verschwindet.  
WIDERLEGT, WENN: das zweite Spiel den Zustand des ersten erbt (Uhr, Einheiten, Gold).  

**Vorschlag:** Nach M3.02 messen.  

### M4.01 Die Lords im Gefecht finden

*Stand beim Anlegen: gemessen*

ZIEL: Fuer jeden Spieler seinen Lord im Speicher finden.  
STAND: gemessen am 05.09.: Lord = Einheitentyp 55, je aktivem Spieler genau einer, Leben 150.000-165.000.  
ICH PRUEFE: in einem eigenen Spiel genau zwei KI-Lords plus dein Lord.  
DU SIEHST: ich nenne dir die Lords und ihre Leben; du findest sie im Spiel an den Burgen.  
WIDERLEGT, WENN: ein aktiver Spieler null oder zwei Lords hat.  

**Vorschlag:** Im ersten eigenen Spiel live abnehmen.  

### M4.02 Lord-Tod erkennen

*Stand beim Anlegen: gemessen*

ZIEL: Die Schleife merkt, wann ein Lord stirbt.  
STAND: gemessen am 05.09.: der Ausloeser ist das Leben (<= 0), nicht der Zustand der Einheit - bei Leben 0 bleibt die Einheit zunaechst stehen.  
WIDERLEGT, WENN: ein Lord im Spiel faellt, ohne dass sein Leben auf 0 steht.  

**Vorschlag:** Zusammen mit M4.04 live abnehmen.  

### M4.03 Was nach dem Lord-Tod wirklich passiert

*Stand beim Anlegen: offen*

ZIEL: Die echte Kette verstehen: Lord stirbt -> was passiert mit Einheiten, Gebaeuden, Anzeige, Uhr?  
STAND: offen. Bekannt ist nur: die Kampagnen-Mission endet mit Endbildschirm und stehender Uhr.  
ICH PRUEFE: den Zustand in den 500 Ticks nach dem Tod.  
DU SIEHST: den Moment, in dem der Lord faellt, und was danach geschieht.  
WIDERLEGT, WENN: das Spiel nach dem Tod normal weiterlaeuft, als waere nichts.  

**Vorschlag:** Wichtigster offener Punkt dieses Blocks.  

### M4.04 Der einfachste echte Tod: zwei Lords laufen aufeinander zu

*Stand beim Anlegen: offen*

ZIEL: Dein Vorschlag - beide Lords per Befehl aufeinander zuschicken, bis einer stirbt. Der kuerzeste echte Spielausgang.  
STAND: offen. Eine Einheit per Befehl bewegen ist belegt (05.09.); zwei Lords gegeneinander noch nie.  
ICH PRUEFE: Leben beider Lords je Tick, bis einer bei 0 ist.  
DU SIEHST: die zwei Lords laufen los, treffen sich, kaempfen, einer faellt.  
WIDERLEGT, WENN: sie aneinander vorbeilaufen oder nicht kaempfen.  

**Vorschlag:** Nach M4.01 - das ist der erste Punkt, der richtig Spass macht zu zeigen.  

### M4.05 Den Sieger aus dem Speicher lesen

*Stand beim Anlegen: offen*

ZIEL: Die Schleife liest selbst, wer gewonnen hat.  
STAND: offen; die Regel steht (Zettel Grundbedingungen): Sieger = der Spieler, dessen Lord als einziger noch lebt.  
WIDERLEGT, WENN: der gelesene Sieger nicht zu dem passt, was du am Bildschirm siehst.  

**Vorschlag:** Mit M4.04 abnehmen.  

### M4.06 Den Endbildschirm erkennen

*Stand beim Anlegen: gemessen*

ZIEL: Erkennen, dass das Spiel auf dem Endbildschirm steht.  
STAND: gemessen am 31.08.: Ansicht 30 = verloren. Achtung: der Wert 'Spielmodus' zeigt auch dann noch 'laeuft' - er taugt nicht als Anzeige.  
WIDERLEGT, WENN: der Endbildschirm zu sehen ist, die Ansicht aber nicht 30 (oder 58) meldet.  

**Vorschlag:** Im eigenen Spiel neu abnehmen.  

### M4.07 Zeitlimit: die ersten X Ticks

*Stand beim Anlegen: offen*

ZIEL: Kein Spiel laeuft ewig. Nach X Ticks endet es, gewertet wird nach Belohnung.  
STAND: offen - X ist noch nicht festgelegt.  
WIDERLEGT, WENN: ein Spiel ueber X Ticks hinaus laeuft.  

**Vorschlag:** Siehe Frage 2.  

### M5.01 Was ein Tick ist und wo er steht

*Stand beim Anlegen: belegt*

ZIEL: Ein Tick ist ein Rechenschritt der Spiellogik. Die Anzahl seit Spielbeginn steht im Speicher.  
STAND: belegt (Tickzaehler 0x0117CADC; Tag, Woche und Monat daraus vorhergesagt, 6 Messpunkte ohne Abweichung).  
DU SIEHST: ich lese den Tick, du vergleichst mit der Spieluhr (1 Tag = 50 Ticks).  
WIDERLEGT, WENN: Tick und Spielkalender auseinanderlaufen.  

**Vorschlag:** Live abnehmen.  

### M5.02 Die Grenze: hoechstens 11 Ticks je Bild

*Stand beim Anlegen: abgelesen*

ZIEL: Wissen, wann das Tempo nicht mehr steigt.  
STAND: abgelesen im Code - hoechstens 11 Ticks je gezeichnetem Bild. Bei 1.100 Ticks/s heisst das: rund 100 Bilder je Sekunde noetig. Faellt die Bildrate, faellt das Tempo mit.  
ICH PRUEFE: Ticks je Sekunde bei Tempo 1000, 2000 und 5000.  
WIDERLEGT, WENN: 2000 deutlich mehr als 1100 Ticks/s bringt.  

**Vorschlag:** Messen - bestimmt, wie viele Spiele pro Stunde gehen.  

### M5.03 Greift unser Modul jeden Tick ein oder nur jedes Bild?

*Stand beim Anlegen: offen*

ZIEL: Dein Endbild verlangt, dass die KI JEDEN Tick sieht. Dafuer muss das Modul je Tick laufen, nicht je Bild - bei Tempo 1000 liegen bis zu 11 Ticks zwischen zwei Bildern.  
STAND: offen. Laut Betriebsregeln haengt die Befehlsabfrage an der Tick-Funktion; die Zustandsmeldungen zaehlen aber Bilder.  
ICH PRUEFE: ein Zaehler im Modul je Aufruf, verglichen mit dem Tickzaehler.  
WIDERLEGT, WENN: der Modul-Zaehler langsamer steigt als der Tickzaehler.  

**Vorschlag:** Frueh klaeren - davon haengt die ganze 'Ansicht der KI' ab.  

### M5.04 Wie lange Ereignisse dauern (Katalog)

*Stand beim Anlegen: teils belegt*

ZIEL: Ein wachsender Katalog: Ereignis -> Dauer in Ticks -> beeinflussbar ja/nein.  
STAND: belegt ist erst ein Eintrag: ein Bauschritt der KI dauert genau 50 Ticks (445 von 445 Schritten). Offen: Rekrutieren, Laufen je Feld, Pfeilflug, Produktion, Nahrung.  
WIDERLEGT, WENN: ein gemessener Wert bei Wiederholung abweicht.  

**Vorschlag:** Den Katalog anlegen und mit jeder Messung fuellen - nicht alles vorab.  

### M5.05 Veraendert das Tempo das Spiel?

*Stand beim Anlegen: offen*

ZIEL: Sicher sein, dass ein Spiel bei Tempo 1000 genauso ausgeht wie bei Tempo 40 - sonst lernt die KI etwas, das im echten Spiel nicht gilt.  
STAND: offen.  
ICH PRUEFE: dieselbe Partie 5x bei Tempo 100 und 5x bei 1000, Ausgang und Tick des Lord-Todes vergleichen.  
WIDERLEGT, WENN: sich die Ausgaenge zwischen den Tempi klar unterscheiden.  

**Vorschlag:** Vor der Lernschleife messen.  

## Entscheidungen aus Lieferung 1

- **Frage 1 - Was macht der Mensch auf Platz 1?** Entfaellt - siehe M3.07 (kein Mensch in TL2-Gefechten).
- **Frage 2 - Wie gross ist X beim Zeitlimit?** Angenommen: X wird gemessen (drei Spiele ohne Limit, X = das Anderthalbfache des laengsten, auf Spieljahre gerundet). Daniel: alle Liga-KIs sind gut ausbalanciert; toetet unsere KI frueher, umso besser.
- **Frage 3 - Bei welchem Tempo nimmst du ab?** Zuschau-Tempo 90 (Daniel: da sieht man noch, wie die KI einzelne Befehle erteilt). Gelernt wird bei 1000.

## Laufprotokoll

### Lauf 1 - 30.09.2026, 21:10 - erstes eigenes Spiel

Aufbau: `werkzeug/config.py eintragen` -> `starte_spiel.py --links` -> `{"eigenesGefecht": true, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 2}` -> sofort `{"pause": true}` -> messen -> Tempo 90. Alle Befehle ueber `werkzeug/befehl.py`.

**Was geklappt hat (im Hintergrund belegt, Daniel hat das Spiel live gesehen):**
- Eigenes Spiel per Befehl, Karte "Liga_Grumpy Neighbors" (Kartenname im Speicher), Kampagnen-Kennzeichen isSkirmishTrail = 0, Spielmodus 99, Ansicht 14 (im Spiel). Fuer M3.03 fehlt noch der Vergleichswert einer Kampagnen-Mission.
- Beide KI-Plaetze tragen Typ 1 (Rotkaeppchen): KI-Liste `[0, 0, 1, 1, 0, 0, 0, 0, 0]`.
- Pause per Befehl haelt: Tick 4691 vor und nach dem Messen gleich (M3.11). Fortsetzen ebenso.
- Einheiten-Array im Spiel erneut bestaetigt (fuenf Totschlagtests gruen, 241 belegte Plaetze).

**Was dabei gelernt wurde (Pannen als Gewinn):**
- Die GUI hatte `continueOutOfFocus` auf `pause` gesetzt -> im Hintergrund hielt das Spiel an, kein Befehl kam an. Jetzt prueft und repariert `config.py` das mit (M2.13). Hin- und Rueckweg: `pause` = angehalten, `render` = laeuft weiter.
- Ein Tempo-Befehl VOR dem Start verpufft: nach dem Start stand das Tempo auf 3000 (M3.12). Das Spiel lief damit nur rund 780 Ticks/s - ein weiterer Hinweis auf die Grenze von 11 Ticks je Bild (M5.02).
- `peek` liefert negative Speicherwoerter 16-stellig statt 8-stellig; beim Auswerten auf 32 Bit kuerzen.

**Was noch nicht stimmt (Daniel, 21:14: "du bist ein Spieler unten, Rotkaeppchen ist rechts statt oben, beide sollten Rotkaeppchen sein"):**
- **Ein echter Mensch spielt mit:** Spieler 1 hat einen Lord, 12 Einheiten, 4000 Gold und eine Burg unten links. Daniels Weg ueber die Lobby macht den Menschen in der Team-Liga zum Geist - unser nachgebauter Startbefehl `eigenesGefecht` setzt ihn dagegen ausdruecklich ein (M3.07 wieder offen).
- **Nur eine Rotkaeppchen ist im Spiel:** Spieler 3 hat Lord, 84 Einheiten, 1467 Gold; Spieler 2 hat KEINEN Lord, 0 Gold, 0 Holz, 4 Einheiten.
- **Startplaetze zufaellig und vermutlich ungueltig:** Startplatz-Liste `[246, 0, 246, 2, 1, 246, 246, 246]` (246 = frei). Vermutung, ungeprueft: Index = Startplatz auf der Karte, Wert = Spieler. Dann stuende Spieler 2 auf Startplatz 4 - die Karte hat aber nur vier Plaetze. Das wuerde erklaeren, warum er weder Burg noch Lord hat.
- Startgold nicht gemessen: pausiert wurde erst bei Tick 4691. Naechstes Mal sofort nach dem Start.

### Lauf 2 - 30.09.2026, ab 21:18 - Daniels richtiger Aufbau als Referenz

Daniel hat das Gefecht ueber die Lobby so aufgebaut, wie es sein soll: Liga_Grumpy Neighbors, zwei Rotkaeppchen oben und unten, kein Mensch. `werkzeug/aufbau.py` hat diesen Aufbau aus dem Speicher gelesen - **das Rezept fuer unseren Startbefehl, gemessen statt geraten:**

| Feld | Lobby (richtig) | unser `eigenesGefecht` |
|---|---|---|
| Spieler-IDs (fullID) | alle -1 | Platz 1 = Mensch |
| Mannschaft des Menschen | 255 = nicht dabei (Geist) | 0 = spielt mit |
| Mannschaft der KIs | 0 und 0 | 1 und 2 |
| Startplatz-Liste | `[246, 2, 1, 246, ...]` -> Plaetze 1 und 2 | zufaellig, u. a. 4 |
| KI-Variante | 0 und 1 (Grossmutter / Jaegersmann) | nicht gesetzt |
| Lords | Spieler 2 und 3 je einer, Spieler 1 nichts | Mensch mit Lord, Spieler 2 ohne |

Beide KIs hatten bei Tick 114 je 1850 Gold. Beobachter-Daten: `daten/lauf2_daniels_aufbau.jsonl` (rund 90 Ticks/s, beide Lords lebten bis mindestens Tick 28.160).

### Sammeln statt raten - das Verfahren (30.09.2026, Daniel: "erst alles sammeln, dann etwas Klares rausfischen und damit testen")

- **M6.01 Schnappschuss** `{ "abzug": "<name>" }` (logik.lua): 11 Speicherbereiche roh in Dateien - Spieler, Einheiten, Gebaeude, Bauplaene, Spielzustand, Kern, fuenf Kartenschichten. **Gemessen: 3,6 MB in 0,2 s** - schnell genug fuer jede Pause.
- **M6.02 Vergleich** `werkzeug/vergleich.py <A> <B>`: welche Stellen sich bewegt haben, bei Tabellen je Feld zusammengefasst, Uhr-Felder markiert. **Gegenprobe bestanden:** die eigene Tempo-Aenderung 90 -> 50 erscheint genau bei Kern +0xC8 = der bekannten Tempo-Adresse.
- Erstes Paar (Tick 28.058 -> 28.160): rund 12.000 geaenderte Woerter. Zeitstempel-Felder (Einheit +0x3C/+0x40/+0x350/+0x354, Gebaeude +0x27C, Kern +0x98), bewegte Einheiten (+0xC4/+0xD4 bei 173 von 682), ein gemeinsamer Gebaeude-Zaehler (+0xC0 bei allen 207: 57 -> 59), 36 Kartenkacheln verlieren ein Bit, wachsende Spielerfelder (+0x2088, +0x2148/+0x22DC). Bericht: `daten/vergleich_p1.json`.
- Naechster Schritt je Kandidat: **Steuerbarkeitstest** - Wert schreiben, laufen lassen, zuruecklesen: gehalten (steuerbar) oder ueberschrieben (vom Spiel berechnet).
- **M6.03 Steuerbarkeitstest** `werkzeug/steuertest.py <adresse> <wert> [ticks] [tempo]` - pausieren, schreiben, sofort zuruecklesen, N Ticks laufen lassen, einordnen, Original wiederherstellen (Rueckweg). Erste drei Laeufe, je rund 100 Ticks bei Tempo 100 (30.09.2026, Daniels Lobby-Gefecht):
  - **Gold Spieler 2** (Eichung, belegt schreibbar): 77777 geschrieben -> 77772 nach 102 Ticks -> **steuerbar**, das Spiel rechnet vom geschriebenen Wert weiter (5 Gold ausgegeben).
  - **Kern +0x98** (gedacht als Negativlauf, weil es mit der Uhr tickt): 5 geschrieben -> 106 nach 101 Ticks. **Meine Annahme war falsch:** ein Zaehler, der je Tick um 1 waechst, uebernimmt den geschriebenen Wert und zaehlt von dort weiter - er ist also schreibbar. Das Werkzeug hat richtig geurteilt, der Negativlauf war schlecht gewaehlt.
  - **Spieler 2 +0x2148** (Kandidat aus dem Vergleich): 999 geschrieben -> 110 nach 100 Ticks (Original 108). **Das Spiel berechnet den Wert selbst neu** - nicht direkt steuerbar; steuern ginge nur ueber seine Zutaten. Vermutet, ungeprueft: Bevoelkerung (dieselben Werte stehen bei +0x22DC).
  - Damit hat das Werkzeug beide Ergebnisarten gezeigt: "steuerbar" und "wird berechnet". Der echte Negativfall kam aus dem Kandidaten, nicht aus dem geplanten Negativlauf.

### Lauf 3 - 30.09.2026, 21:30 - wiederholbarer Selbstspiel-Start und Pause auf den Tick genau

- **M3.13 Selbstspiel-Start** `{ "eigenesGefecht": true, "selbstspiel": true, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 2 }` schreibt die an Daniels Lobby gemessenen Werte (kein Mensch, Mannschaft 255/0/0, Startliste `[246,2,1,...]`, Varianten 0/1) und laesst die Zufallsplatzierung weg. **Test `werkzeug/selbstspiel.py 3` - GESCHAFFT:** drei Starts hintereinander identisch - Burgen immer bei (162,104) und (224,282), je ein Lord bei Spieler 2 und 3, Spieler 1 ohne Einheit, sogar gleiche Einheitenzahlen (22/23). Loest M3.05, M3.06, M3.07 fuer unseren Startweg.
- **M5.06 Pause auf den Tick genau** `{ "tickpause": { "bei": N, "alle": K, "bis": M } }` - ein Waechter im Taktgeber `everyTick()`, der jeden Tick laeuft. **Test `werkzeug/tickpause_test.py`:** bei Tempo 100 UND 1000 haelt das Spiel exakt beim Ziel-Tick an (+0), danach laeuft kein Tick mehr durch. Damit ist auch **M5.03 beantwortet: unser Modul laeuft wirklich jeden Tick mit.**
- **M5.07 Pause bei Tick 1 eines neuen Spiels** `"startpause": 1` im Startbefehl. Zweimal exakt bei Tick 1. Zwei Funde auf dem Weg: (a) **Im Hauptmenue kommen nur Startbefehle durch** - `tickpause` und `pause` im Menue werden stillschweigend verworfen; (b) **waehrend des Gefechtsaufbaus liefert der Tickzaehler kurz Unsinn** (7.807.163) - der Waechter ignoriert jetzt Werte weit ueber dem Ziel.
- **Erster Blick in den Spielbeginn, tick-genau:** Tick 1-25 nur neutrale Einheiten; Tick 50 je Spieler 1 Einheit ohne Lord; **Tick 100 je ein Lord** (4 bzw. 5 Einheiten); Tick 400 rund 20 Einheiten. Die Lords erscheinen zwischen Tick 50 und 100.

### Lauf 4 - 30.09.2026, 21:40 - Steuerkarte der Spielerfelder

- **M6.04 Steuerkarte** `werkzeug/steuerkarte.py <ausgabe.json> [start] [schritt] [spieler]`: frisches Selbstspiel, Pause genau bei Tick 1000, Schnappschuss, 100 Ticks weiter, zweiter Schnappschuss; Kandidaten = die Felder von Spieler 2, die sich bewegt haben. Je Feld: Original + 1000 schreiben, **genau 100 Ticks** (Tick-Pause), zuruecklesen, einordnen, Original zurueck. Werte mit Betrag >= 100.000 nicht angefasst (vermutlich Zeiger).
- Umfang: 45 bewegte Felder, 4 nicht angefasst, **41 getestet in rund 2,5 Minuten** (41 Schritte zu je 100 Ticks; die Zeit geht in die Befehle, nicht in die Ticks).
- **Ergebnis: 13 steuerbar, 28 vom Spiel berechnet.**
  - gehalten (8): +0x444 (100), +0x448 (1850), +0x44C (0), **+0x4D8 Holz** (Ware 2), +0x20AC (3), +0x2A54 (4), +0x2AFC (6), +0x389C (24)
  - weitergerechnet (5): **+0x50C Gold** (Ware 15; 2826 -> 2726, 100 ausgegeben), +0x20EC (11976, +600 je 100 Ticks), +0x2B38 (79), +0x2B3C (81), +0x39D4 (5100, +100 je 100 Ticks - zaehlt mit den Ticks)
  - zurueckgesetzt (10): +0x8C, **+0x500 (Ware 12, Fleisch)**, +0x2094, +0x2180, +0x2190, +0x223C, +0x2B14, +0x2B78, +0x3684, +0x3928
  - neu berechnet (18): +0x78, +0x84, +0x88, +0x450, +0x2088, +0x209C, +0x20B0, +0x20B4, +0x2188, +0x2AE4, +0x2AF8, +0x2B08, +0x2B0C, +0x2B50, +0x2B6C, +0x2B70, +0x3100, +0x3860
- Auffaellig: Holz bleibt stehen, **Fleisch wird zurueckgesetzt** - Nahrung zaehlt das Spiel offenbar aus dem Kornspeicher nach, Holz nicht. Ungeprueft.
- Was die Felder bedeuten, ist bis auf Holz, Fleisch und Gold **nicht gedeutet** - die Karte sagt nur, WAS steuerbar ist. Rohdaten: `daten/steuerkarte_spieler2.json`.

### Lauf 5 - 30.09.2026, 21:46 - Wirkungstest der 13 steuerbaren Felder

- **M6.05 Wirkungstest** `werkzeug/wirkung.py`: zwei Kontroll-Laeufe ohne Eingriff (Selbstspiel, Tick 1000 -> genau 1100), dann je Feld ein Lauf mit Wert + 5000 bei Tick 1000; Vergleich mit Kontrolle 1 = **Fussabdruck** des Felds.
- **Rauschen:** auch die zwei Kontrollen unterscheiden sich an 4-5 Stellen (Kern +0x8 und +0xBC - wachsen wie Echtzeit-Zaehler; Kern +0x8C, +0xAC; Spieler 1 +0x34 beim Geist). Diese Stellen gehoeren kuenftig in eine Ausnahmeliste des Vergleichs.
- **Daniel, 30.09.:** zwei gleiche Kontrollen im Fenster Tick 1000-1100 sagen NICHTS darueber, ob das Spiel deterministisch ist - "wie wenn man bei Schach aus den ersten zwei Zuegen schliesst, das Spiel sei deterministisch". Verschiedene Kontrollen wuerden es dagegen widerlegen.
- **Fussabdruecke (Rauschen abgezogen):**
  - **+0x2A54** (4 -> 5004, gehalten): **458 Stellen** - 230 Einheitenfelder, 77 Gebaeudefelder, 100 Kacheln der Logikschicht, Grafik, Holz und Gold von Spieler 2. Der groesste Hebel; Bedeutung offen.
  - **+0x20AC** (1 -> 5001, nach 100 Ticks 0): Brot und Fleisch (Ware 10 und 12) verschieben sich, dazu ein Gebaeude (+0x148/+0x150). Vermutet: Kornspeicher/Nahrungsverteilung.
  - **+0x50C Gold** -> **+0x448 zieht mit** (1880 -> 6880): +0x448 ist ein Spiegel des Golds.
  - +0x444, +0x448, +0x44C, +0x4D8, +0x2AFC, +0x389C, +0x20EC, +0x2B38, +0x2B3C, +0x39D4: **in diesem Fenster keine Wirkung ueber das Rauschen hinaus** - nicht "wirkungslos", manche wirken vielleicht spaeter.
- Rohdaten: `daten/wirkung_spieler2.json`.

## Leitsatz (Daniel, 30.09.2026)

Das Ziel ist kein wiederholbares Spiel, sondern eine KI, die **jeden Tick auf spontane Entscheidungen reagiert** - spaeter gegen Menschen. Wiederholbarkeit ist ein **Pruefstand** (gleicher Start, eine Aenderung, vergleichen) und ein **Trainingswerkzeug**: ueber Spielstaende laesst sich eine bestimmte Lage beliebig oft laden und gezielt ueben. Immer opportunistisch denken.

## Naechste Kette: Spielstaende als Trainingslagen (M7, Definition offen fuer Daniel)

- **M7.01** Spielstand speichern per Befehl, ohne Maus. - **Im Hintergrund belegt 30.09., 22:03** (Lauf 7), Live-Abnahme durch Daniel offen.
- **M7.02** Spielstand laden per Befehl. - **Abgenommen von Daniel 30.09., 22:23** ("ja nehme ab"; Lauf 8).
- **M7.03** Gegenprobe: Schnappschuss direkt nach dem Speichern und direkt nach dem Laden - gleich bis auf das bekannte Rauschen = verlustfrei. - **30.09., 23:28-23:33 gemessen (Lauf 9): so wie definiert NICHT erfuellt** - der geladene Stand ist die Welt einen Tick weiter, der Tickzaehler zeigt aber den gespeicherten Wert; wiederholbar ist das Laden dagegen (zweimal laden = gleich). Entscheidung bei Daniel, ob das fuer M7.04 reicht.
- **M7.04** Szenario-Bibliothek: benannte Spielstaende fuer Sonderfaelle (Lord in Gefahr, Belagerung, Wirtschaftskrise); jeder Trainingslauf startet exakt dort.
- Danach **M8** Ansicht der KI je Tick und erste Reaktions-Regel mit gemessener Reaktionszeit in Ticks.

### Stand M7 nach Nachsehen (30.09.2026, 21:52 - Daniels Hinweis "schau, ob das schon beantwortet ist")

- **M7.02 Laden: SCHON GELOEST (gemessen 02.09.2026)** - VillageStudio `doku/Menue-Handbuch.md` ("Einen bestimmten Spielstand laden") und `doku/Uebergabe_2026-09-02.md`: Lade-Dialog per Menueknopf, dann in EINEM Auftrag (`befehle`) Scrollstand `0x01126628` und markierte Zeile `0x01126624` setzen und `{"laden": 2}` - 1,5 s. Fallen: Laden hebt die Pause auf (danach pausieren und Flag `0x01FEA054` pruefen); zwei Befehle kurz nacheinander loeschen einander (Poll alle 20 Bilder). **Wird uebernommen, nicht neu gebaut.**
- **M7.01 Speichern: OFFEN** ("noch nicht angefasst" laut Uebergabe 02.09.). Zwei Wege gefunden, Entschluesselung in `daten/dekomp_speichern_laden.c`:
  - (a) **Menueweg wie beim Laden** - im Lade-/Speicher-Dialog ist Knopf 3 "Speichern" (bisher nur abgelesen); braucht zusaetzlich den Dateinamen im Eingabefeld.
  - (b) `AutoSaveTriggered` (0x00489880) ist **kein einfacher Speicherknopf**, sondern ein netzwerk-synchronisierter Spielbefehl (verpackt Parameter, merkt je Spieler die Ankuendigung). Direkt rufen moeglich, aber riskanter.
  - Vorschlag: (a) zuerst - derselbe, schon belegte Mechanismus wie beim Laden.
- Nebenbei: `{"kamera": [x, y]}` gibt es schon (Uebergabe 02.09.) - Kamera an eine Kartenstelle, nuetzlich fuers Zuschauen (M12).

### Lauf 6 - 30.09.2026, 21:55 - erster Speicherversuch (M7.01), nicht geschafft - was wir dabei gelernt haben

- Speicherordner: `Documents\Stronghold Crusader\Saves` (neuester Stand vorher: "Walltest 4", 30.08.2026).
- Im laufenden Selbstspiel (Tick 1100): `{"optionen": 3}` (Speichern) und `{"laden": 3}` (Knopf Speichern) melden beide `ok=true` - **aber keine neue Datei**, und die **Ansichtsnummer bleibt 14** (im Spiel). **Befund:** im laufenden Spiel oeffnen die Knopf-Befehle keinen Dialog; vermutlich muss das Spieloptionen-Fenster (Esc) erst offen sein, bevor seine Knoepfe wirken. Ungeprueft.
- Die Bilder (`{"bild": "menue"}`) zeigen das bekannte **Mischbild** (oben altes Hauptmenue, unten Statusleiste) - kein Beweis in die eine oder andere Richtung. `"blt": true` in dieser Form loeste das Umkopieren NICHT aus (Logzeile fehlt) - die richtige Form des Schalters ist zu klaeren.
- **Naechster Schritt:** die Funktion finden, die im Spiel das Optionen-Fenster oeffnet (wie Esc), dann Speichern + Dateiname; Beweis ist allein die neue .sav-Datei im Ordner, nicht das Bild.

**Korrektur zu Lauf 6 (21:58):** `{"bild": "karte"}` liefert das echte Spielbild (das `"menue"`-Bild ist im Spiel das Mischbild mit pinkem Streifen - Daniel hat es erkannt). Darauf ist zu sehen: **der Speichern-Dialog IST offen** (Liste der Spielstaende, Knoepfe Speichern/Zurueck, **leeres Namensfeld**). Die Aussage "der Dialog geht im Spiel nicht auf" war falsch - gemessen war die Ansichtsnummer, geurteilt ueber den Dialog; ein Dialog, der sich darueberlegt, aendert die Ansicht nicht. Vermutlich speicherte der Knopf nur wegen des leeren Namens nicht. **M12.01 Bild vom laufenden Spiel: `{"bild": "karte"}` - belegt** (Bild `daten/bilder/bild_karte_1.png`, nicht im Repo).

**Spur zum Namensfeld (22:00, fuer M7.01):**
- `MenuTextInputState` beginnt bei **0x011265A8** (Groesse 0x1828): markierte Zeile `0x01126624` = Feld +0x7C, Scrollstand `0x01126628` = +0x80 (aus der Lade-Messung vom 02.09. zurueckgerechnet).
- Knopf 3 "Speichern" (`MenuItemActionHandler_SaveLoadMap_Buttons` 0x004943B0, case 3) holt den Dateinamen ueber `UserTextHandler::getCurrentText(&DAT_UserTextHandlerState)`; ist `textContentLengthArray[textArrayIndex]` leer, passiert nichts - **deshalb speicherte Lauf 6 nicht** (Dekompilat: `daten/dekomp_speichern_knopf.c`).
- Beim Oeffnen leert das Spiel das Feld (`activateModalDialogAndClearText`, MMT_SAVE_MAP). **Korrektur 22:06 - gemessen falsch:** nach einem Speichern stand beim erneuten Oeffnen der alte Name noch im Feld (Laenge 31). Das leere Feld beim allerersten Oeffnen hiess nur: es war noch nie etwas drin.
- Kandidaten zum Setzen des Namens: `getCurrentText` 0x004697C0, `getTextArrayPointer` 0x004697E0, **`setTextEntryAndUpdateCursor` 0x00469800** (this, p1, p2), `resetToTextIndex` 0x00469790. Naechster Schritt: diese entschluesseln (Adresse von DAT_UserTextHandlerState + Aufbau der Textablage), Namen schreiben, Knopf 3, Beweis = neue .sav im Ordner.
- **Live gesehen von Daniel (30.09., 21:58, eigener Screenshot):** Speichern-Dialog im laufenden Spiel offen, geoeffnet per `{"optionen": 3}` - Liste der Spielstaende, Knoepfe Speichern/Zurueck, leeres Namensfeld. Teilschritt "Dialog oeffnen per Befehl" damit abgenommen; offen bleibt nur der Name.
- **Namensregel fuer Spielstaende (Daniel, 30.09., 22:00: "klarerer Name, am besten was du testen willst"):** `<Meilenstein> <Was getestet wird> <Karte> T<Tick>`, Punkte als Bindestrich, hoechstens 32 Zeichen (das Spiel kuerzt Kartennamen auf 33). Erster Test: **`M7-01 Speichertest Grumpy T1100`**. Spaetere Trainingslagen z. B. `M7-04 Lord in Gefahr Grumpy T8000`.
- **Textablage entschluesselt (22:03, `daten/dekomp_textfeld.c`):** 16 Textfelder zu je 250 Byte ab **0x01652890** (`getTextArrayPointer`: Feld*0xFA + 0x1652890). `setTextEntryAndUpdateCursor` (0x00469800, thiscall, this ungenutzt, Argumente Feld und char*) kopiert einen Text ins Feld und setzt `textContentLengthArray[Feld]` und `textCursorIndexArray[Feld]` - genau die Laenge, die der Speichern-Knopf prueft. `getCurrentText` liefert `textArray[textArrayIndex]` (nur wenn `unknown01` != 0). **Plan:** Name `M7-01 Speichertest Grumpy T1100` ins aktive Feld schreiben (poke), dann `setTextEntryAndUpdateCursor(aktivesFeld, Zeiger auf dieses Feld)` rufen, damit Laenge/Cursor stimmen, dann `{"laden": 3}`. Offen: Adresse von `DAT_UserTextHandlerState` (fuer textArrayIndex).

### Lauf 7 - 30.09.2026, 22:03-22:09 - M7.01 Speichern ohne Klick: GESCHAFFT (im Hintergrund belegt)

Werkzeug: `werkzeug/speichern.py "<Name>"`. Selbstspiel Grumpy, pausiert bei Tick 1100 (Pause-Flag 1, Ansicht 14 - blieb die ganze Zeit so).

- **Weg (gemessen):** `{"optionen": 3}` oeffnet den Speichern-Dialog -> aktives Textfeld lesen (`0x01652740` = 2, also ist **DAT_UserTextHandlerState = 0x01652740 bestaetigt**, nicht mehr nur abgeleitet) -> Name wortweise ins Feld `0x01652890 + Feld*250` schreiben, Laenge nach `0x016527D0 + Feld*4`, Cursor nach `0x01652810 + Feld*4` -> `{"laden": 3}` (Knopf Speichern).
- **Beweis:** neue Datei `Documents\Stronghold Crusader\Saves\M7-01 Speichertest Grumpy T1100.sav`, 1.056.101 Byte, 22:03. Im Dialog oben in der Liste sichtbar ("M7-01 Speichertest Grump", 30/09/26 20:08 - **das Spiel zeigt Weltzeit**, zwei Stunden hinter der Ortszeit; "Walltest 4" genauso: Datei 21:32, Liste 19:32). Bild: `daten/bilder/m7-01_dialog_liste_t1100.png` (nicht im Repo).
- **Speichern geht in der Pause:** Der Knopf reicht einen Spielbefehl (`GCT_SAVE`, mit Tick und Pruefsumme der Einheiten) in die Warteschlange - er wird trotz Pause sofort ausgefuehrt, der Tick bleibt 1100.
- **Gegenlauf (22:07, gueltig):** Name "M7-01 Gegenlauf leer" steht sichtbar im Feld, Laenge aber 0 -> Knopf Speichern -> **keine Datei** (31 Dateien vorher, 31 nachher), Dialog bleibt offen. Damit ist belegt: die Laenge bei `0x016527D0` ist genau die Sperre, die der Knopf prueft - und die neue Datei kam vom Namen, nicht von allein.
- **Erster Gegenlauf-Versuch war ungueltig (22:05):** Ich wollte "ohne Namen" speichern, aber das Feld hatte noch den alten Namen (siehe Korrektur oben) -> das Spiel fragte **"Datei ueberschreiben?"**. Opportunistisch genutzt:
- **Ueberschreiben per Befehl (gemessen):** `{"dialogJa": true}` beantwortet die Ueberschreib-Frage - Dateizeit 22:03 -> 22:07. `speichern.py` macht das jetzt selbst, wenn es den Namen schon gibt; im Werkzeug-Durchlauf 22:08 bestaetigt.
- **Nebenbefund zum Sammeln:** Derselbe pausierte Stand, dreimal gespeichert: 1.056.101 / 1.056.104 / 1.056.104 Byte. Ein gespeicherter Stand ist also nicht Byte fuer Byte immer gleich lang - fuer M7.03 den Vergleich im Speicher machen (Schnappschuss nach Laden), nicht an der Datei.
- **Verlust bemerkt:** Die erste Fassung (22:03) ist durch das Ueberschreiben weg. Seitdem kopiert `speichern.py` jede gespeicherte Fassung mit Uhrzeit nach `daten/spielstaende/` (nicht im Repo, 1 MB je Stand).
- **Offen:** Live-Abnahme durch Daniel (Dialog steht offen, Eintrag oben in der Liste).

### Lauf 8 - 30.09.2026, 22:12-22:22 - M7.02 Laden per Name (Daniels Auftrag: Walltest 4, Waffengebaeude_test, den aeltesten)

Werkzeug: `werkzeug/laden.py "<Name>"` (oder `--liste`). Rezept aus dem Menue-Handbuch (02.09.) uebernommen, dazu zwei neue Teile:

- **Liste im Speicher gelesen statt geraten (gemessen):** Das Spiel sortiert nach einem eigenen Datum, das nicht immer zur Dateizeit passt (Walltest 3: Datei 19:21, Liste 17:28 Weltzeit). Anzahl bei `0x0112661C` (30); Eintrag n (0 = oben) = Namensnummer k bei `0x01126E28 + 4n`; Name bei `0x11BFCF8 + k*0x3E9` (`getLoadedMapNameForIndex` 0x0046C2E0, `daten/dekomp_kartenliste.c`). Geladen wird n = markierte Zeile + Scrollstand. (Die Strukturliste nennt `DAT_ArrayOfMapIndices` bei +0x884 = `0x01126E2C`; das Spiel liest aber Feld[n-1], also beginnt die Liste effektiv 4 Byte davor.) Aeltester Stand in der Liste = letzter Eintrag = **Tiberias 4 LUL** (Datei 12.04.2020) - nach Dateizeit ebenfalls der aelteste.
- **Neue Lade-Pause im Modul (`{"ladepause": true}`):** haelt beim ersten Tick an, an dem die Spielzeit springt - in beide Richtungen. Anlass (Panne, opportunistisch genutzt): die erste Fassung nutzte die Tick-Pause "jetzt + 1"; die greift nur, wenn der geladene Stand SPAETER liegt als der alte. Beim Laden eines frueheren Stands waere das Spiel ungebremst weitergelaufen.

| Stand | Eintrag | erster Tick nach dem Laden | Beleg |
|---|---|---|---|
| Walltest 4 | 1 | **18.988** | Bild `m7-02_Walltest_4_t18988.png` - Bergfried im Mauerring, rote Truppen (wie Bild vom 02.09.) |
| M7-01 Speichertest Grumpy T1100 (Probe mit bekannter Loesung) | 0 | **1.100** = gespeicherte Spielzeit | Sprung -17.888 erkannt, sofort angehalten |
| Waffengebaeude_test | 15 | **24.604** | anderes Gelaende (Oase, Felder, Bergfried mit Truppen); Waffenwerkstaetten im Bildausschnitt nicht eindeutig zu sehen |
| Tiberias 4 LUL (aeltester, 2020) | 29 (Scrollstand 14, Zeile 15) | **83.339** | grosse Burg mit Wassergraben; laedt ohne Absturz |

- **Gegenprobe vorher festgelegt, einmal nicht bestanden:** Fuer Walltest 4 hatte ich aus dem Handbuch 40.524 Ticks vorhergesagt - es waren 18.988. Vermutung (ungeprueft): das Handbuch hat die Zeit gemessen, nachdem das Spiel schon weitergelaufen war (dort steht, die Pause kam zu spaet). Die harte Probe lieferte dann M7-01: geladen = gespeichert = 1.100, auf den Tick.
- **Laden ist tick-genau:** der erste Tick nach dem Laden ist die gespeicherte Spielzeit selbst (M7-01: 1.100).
- **Beobachtung, Ursache offen:** Nach dem Anhalten kamen noch drei Tick-Aufrufe an, alle mit derselben Spielzeit - der Taktgeber laeuft kurz weiter, ohne dass die Zeit vorrueckt.
- **Beobachtung:** Nach dem Laden von Tiberias stand das Tempo auf 20 (vorher 1000er-Bereich) - vermutlich bringt der Spielstand sein Tempo mit. Danach auf Daniels Zuschauertempo 90 gesetzt.
- **Offen:** Live-Abnahme durch Daniel (Tiberias steht pausiert im Spiel); M7.03 = Schnappschuss nach Speichern gegen Schnappschuss nach Laden.

### Lauf 9 - 30.09.2026, 23:21-23:34 - M7.03 Verlusttest: verliert Speichern und Wiederladen etwas?

Vorlauf: Das Spiel war um 22:24 zu (Log endet 8 s nach dem Laden eines Stands mit Tick 25.194; kein Absturz in der Windows-Ereignisanzeige). Neu gestartet per `VillageStudio/werkzeug/bis_menue.py` (10 s bis Hauptmenue, Config unveraendert).

**Zwei Pannen, beide opportunistisch zu Faehigkeiten gemacht:**
- **Laden aus dem Hauptmenue:** dort reicht das Modul nur Listen (`{"befehle": [...]}`) und wenige Einzelbefehle durch - `optionen`, `laden`, `ladepause` einzeln kaemen nie an. `laden.py`/`speichern.py` schicken jetzt jeden Befehl als Liste; im Hauptmenue oeffnet `laden.py` erst die Einstellungen (`hauptmenue: 8`). Gemessen: Spielstart + Laden = Tick 1100 in rund 20 s.
- **Wiederladen mit gleicher Spielzeit (23:26:00, Log):** M7-01 ueber M7-01 geladen -> kein Zeitsprung -> die Lade-Pause merkte nichts, das Spiel lief bis Tick 1564. **Gemessen dazu (23:26:48):** der Taktgeber des Moduls laeuft auch in der Pause (Tick-Pause auf den aktuellen Tick loeste im pausierten Spiel aus, Spielzeit blieb stehen). Die Lade-Pause erkennt ein Laden jetzt an **Zeitsprung ODER aufgehobener Pause** (scharf gemacht wird im pausierten Spiel; Laden hebt die Pause auf). Proben: scharf im pausierten Spiel, 3 s nichts geladen -> loest nicht aus; zweimal M7-01 hintereinander -> "Laden erkannt (Pause aufgehoben) bei Tick 1100".

**Der Verlusttest** (`werkzeug/verlusttest.py`, Bericht `daten/verlusttest_232853.json`): M7-01 laden, genau 100 Ticks -> A (Tick 1200); speichern als `M7-03 Verlusttest Grumpy T1200` -> A2; M7-01 laden (Speicher ueberschrieben) -> Z; M7-03 laden -> B. Je Schnappschuss 11 Bereiche, 3,6 MB.

**Eingrenzung** (`werkzeug/verlust_eingrenzen.py`, Bericht `daten/verlust_eingrenzen_233135.json`):

| Vergleich | abweichende Woerter (ausser Rauschen) | heisst |
|---|---|---|
| A gegen A2 | 0 | Speichern veraendert nichts |
| A gegen Z (Gegenprobe) | 3.917 | der Vergleich misst etwas |
| B gegen B2 (zweimal dieselbe Datei laden) | 1 (Kern +0xB0, 1 -> 2) | **Laden ist wiederholbar** |
| A gegen A' (zweimal "M7-01 + 100 Ticks") | 2 (Kern +0xB4/+0xB8) | der Lauf ist wiederholbar (in diesem Fenster) |
| **A gegen B** (vorher festgelegter Massstab) | **1.655** | **nicht verlustfrei wie definiert** |
| B gegen A'1 (A plus ein Tick) | **60** | B ist die Welt **einen Tick weiter** |
| B1 gegen A'2 (einen Tick spaeter) | 76 | der Versatz bleibt bei einem Tick |

- **Befund:** Nach dem Laden steht der Tickzaehler auf dem gespeicherten Wert (1200), Einheiten, Gebaeude und Spieler sind aber schon einen Tick weiter (z. B. Gebaeude-Zeitstempel 1201 statt 1200). Ob das Speichern oder das Laden den Tick dazugibt, ist **offen** (A2 = A, der laufende Stand aendert sich beim Speichern also nicht).
- **Die 60 Reststellen:** Gebaeudeliste-Kopf +0x8 (nach jedem Laden 2000, im Lauf 69) und +0x10; vier Gebaeude (Nr. 3, 5, 12, 14) mit Zaehlern um einen Schritt anders; bei allen Spielern +0x2AE4 (2 statt 1); Spieler 2/3 +0x6C, +0x2AEC, +0x2B08; ein Einheitenfeld; Kern +0x98/+0xA0/+0xB8; 23 Stellen in der Grafikschicht. **Gold, Vorraete und die uebrigen Einheitendaten: gleich.**
- **Kern +0xA0** = Tick des letzten Ladens + 1 (A: 1101 nach Laden bei 1100; B: 1201 nach Laden bei 1200) - ein Lade-Merker, kein Spielzustand.
- **Was das fuer das Training heisst (Vorschlag, Daniels Entscheidung):** Fuer die Szenario-Bibliothek zaehlt, dass jeder Trainingslauf aus einem Spielstand **gleich** startet - das ist belegt (B = B2). Der Startpunkt einer Lage ist dann "der geladene Stand", nicht "der Moment des Speicherns".
