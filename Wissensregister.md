# Wissensregister Selfaware-AI

Angelegt 06.10.2026 20:23 auf Daniels Wunsch: "alle diese Dinger als ungeprueft von dir oder per Tests oder von mir
confirmed festhalten, nicht einfach fuer bare Muenze nehmen; wenn du es getestet und ich verifiziert habe, gerne so
uebernehmen als festes Wissen."

**Stufen**
- **ungeprueft** – nur im Spielcode gelesen, aus einer fremden Quelle oder von Claude vermutet
- **getestet** – von Claude im Spiel gemessen; Werkzeug und Datei stehen als Beleg dabei
- **Daniel** – von Daniel aus Spielerfahrung gesagt, noch nicht getestet
- **fest** – getestet UND von Daniel bestaetigt; nur das gilt als festes Wissen

Eine Stufe steigt nur durch einen Test (-> getestet) oder durch Daniel (-> Daniel / fest). Was in der Weg-Ebene des
Spiels abgelesen ist, aber noch nicht mit laufenden Einheiten geprueft, bleibt "ungeprueft".

## Abriss

| Nr | Aussage | Stufe | Grundlage | Stand |
|---|---|---|---|---|
| A1 | Der Abriss-Knopf gibt die Haelfte der Baukosten zurueck | **fest** | Daniel 20:06 ("die Haelfte"); Code: Knopf schickt 50 % (0x00438ad9); getestet Messpartie 8 (Schmiede 20/8 -> 10/4) | 06.10. |
| A2 | Es wird je Ware abgerundet, kein Rest wird gemerkt (3 -> 1, 15 -> 7) | getestet | `abriss_messen.py`, 6 von 6 wie vorhergesagt, `daten/abriss_messung_20261006_201248.json` | 06.10. |
| A3 | Der Zustand (Schaden) aendert die Rueckgabe nicht | Daniel | Daniel 20:06; Code-Formel hat keinen Zustand-Anteil (ungeprueft) - mit beschaedigtem Gebaeude nicht getestet | 06.10. |
| A4 | Ohne Lagerplatz fuer die Ware ist die Rueckgabe weg (nur Ton "kein Platz") | ungeprueft | Code `giveBackResourceForDestroyedBuilding` | 06.10. |
| A5 | Gratis gebaute Gebaeude (kein Holz und kein Holzfaeller) geben beim Abriss nichts zurueck | ungeprueft | Code `placeBuilding`: Marke +0x288 = 1, ClickDestroyBuilding gibt nur bei 0 zurueck | 06.10. |
| A6 | Torhaus/Turm: abreissen und neu bauen kann billiger sein als reparieren | Daniel | Daniel 20:06 | 06.10. |
| A7 | Mauern sammeln Bruchteile ueber mehrere Abrisse | ungeprueft | Code (Weg -1/-2 mit stoneGainedFraction/woodGainedFraction) | 06.10. |

## Streitkolben-Kette und Lager

| Nr | Aussage | Stufe | Grundlage | Stand |
|---|---|---|---|---|
| S1 | Ein Streitkolbenkaempfer kostet 20 Gold + 1 Keule + 1 Lederharnisch | getestet | Messpartien 3 und 8 (`streitkolben_messen.py`) | 06.10. |
| S2 | Markt: 5 Keulen kaufen 300 / verkaufen 150; 5 Leder 160 / 50; 5 Eisen kaufen 270 | getestet | Messpartie 8; Eisen Messpartie 4 (20 Eisen = 1.080 Gold) | 06.10. |
| S3 | Gerberei macht aus einer Kuh 3 Lederharnische | getestet | Messpartie 3, nur 2 Kuehe - mit groesserer Zahl bestaetigen | 06.10. |
| S4 | Schmiede: 1 Eisen -> 1 Keule; ohne Umstellung macht sie Schwerter; Umstellung per Spielbefehl 33 | getestet | Messpartien 4-6, 3 Stueck - mit groesserer Zahl bestaetigen | 06.10. |
| S5 | Schmiede holt am Lager (~6 Felder) alle ~2.100 Ticks ein Eisen, bei ~55 Feldern ~4.100 | getestet | Messpartien 4-6, je 2 Proben | 06.10. |
| S6 | Jedes Lagerteil fasst nur EINE Warenart, hoechstens 48 | getestet | Messung 19:58 (Gebaeude +0x184/+0x188/+0x18C), Tipp Daniel | 06.10. |
| S7 | Nur Gold ist eine reine Zahl; gesetzte Waren werden aus den Lagern neu gezaehlt | getestet | Messpartie 2 (Stein 300 gesetzt -> 0) | 06.10. |

## Laufwege (Weg-Ebene des Spiels)

| Nr | Aussage | Stufe | Grundlage | Stand |
|---|---|---|---|---|
| W1 | Das Spiel fuehrt je Feld ein Byte mit 8 erlaubten Schritten (PathLinkageLayer, 0x01E1E4F8); Bits 1 N, 2 NO, 4 O, 8 SO, 0x10 S, 0x20 SW, 0x40 W, 0x80 NW | ungeprueft | Code `updateSeparateAreaTileMap`; Richtung der Bits noch nicht mit laufender Einheit geprueft | 06.10. |
| W2 | Gerade kommt man nicht auf ein Gebaeudefeld (ausser Sonderfaelle: Lagerteile, Bergfried-Ebene, Lagerfeuer) | ungeprueft | Code `updatePathLinkageLayerBasedOnBuildingsUnk`; Weg-Ebene abgelesen (wegkarte_test0) | 06.10. |
| W3 | Schraeg an einer Ecke vorbei ist nur verboten, wenn BEIDE geraden Nachbarn "Ecksperren" sind | ungeprueft | Code (dieselbe Funktion, Ende) | 06.10. |
| W4 | Ecksperren sind: Soeldnerposten, Kaserne, Waffenlager, Muehle, Kapelle, Bergfriede, Torhaeuser, Tuerme, Aussenposten; Werkstaetten, Lager, Markt, Huetten, Hoefe nicht | ungeprueft | Tabelle BuildingDefinedData +0x1774, gelesen aus der Referenz-exe (nicht aus unserem laufenden Spiel) | 06.10. |
| W5 | An Mauern und Tuermen kommt man nicht schraeg vorbei | Daniel | Daniel 20:21; Code zaehlt Mauerfelder (0x10000000) und Tuerme als Ecksperre (ungeprueft) | 06.10. |
| W6 | Am Wassergraben kommt man schraeg durch | Daniel | Daniel 20:22; Code: Graben sperrt gerade, ist aber keine Ecksperre (ungeprueft); laut Code ebenso Wasser, Baeume, Felsen | 06.10. |
| W7 | Kaserne hat einen begehbaren Vorhof; Milchviehhof ein Gitter; Apfelplantage begehbar, nur die Huette nicht | Daniel | Daniel 20:21 | 06.10. |
| W8 | Gebaeude genau aneinander gebaut lassen Laeufer durch | Daniel | Daniel 20:05 | 06.10. |
| W9 | ~~Lagerteile: von aussen hinauf nicht (Einbahn)~~ WIDERLEGT 20:36: Arbeiter treten zum Abholen/Abliefern sehr wohl vom Boden auf Lagerteile (19 von 19 'verbotenen' Schritten), obwohl die Weg-Ebene es nicht erlaubt | getestet (widerlegt) | Weg-Ebene abgelesen (wegkarte_test0, Tick 1830); Code-Lesart passt; nicht mit Laeufern geprueft | 06.10. |
| W10 | Markt ganz gesperrt; Lagerfeuer begehbar bis auf die Raute in der Mitte; Bergfried oben eigene Ebene ohne Verbindung zum Boden | ungeprueft | Weg-Ebene abgelesen (wegkarte_test0) | 06.10. |
| W11 | Das Wegnetz (welche Gebiete zusammenhaengen) baut das Spiel hoechstens alle 200 Takte neu | ungeprueft | Code `updateSeparateAreaTileMap` (counterForUpdatingSeparateAreaTileMaps = 200) | 06.10. |
| W12 | Arbeiter gehen nicht durch Gebaeude; zugebaute Lager-Eingaenge stoeren | ungeprueft | Fremdquelle (Steam-Forum, Websuche 20:15) | 06.10. |
| W13 | Gebaeude-Koordinate beim Bauen = linke obere Ecke des Grundrisses (Versatz 0/0 bei allen 15 Arten) | getestet | `wege_abstand.py nur=grundriss` 20:28, `daten/wege_abstand_20261006_202838.json` | 06.10. |
| W14 | Kaserne und Soeldnerposten belegen 10x10: Haus 5x5 links oben gesperrt, dazu 3 Exerzierplatz-Stuecke je 5x5 (eigene Gebaeude, Art 57), begehbar bis auf 4 Pfosten | ungeprueft | Weg-Ebene abgelesen (Grundriss 20:28, Bild `daten/wege_abstand/grundriss_Kaserne.png`); deckt sich mit Daniel W7 (Vorhof) | 06.10. |
| W15 | Schmiede, Gerberei, Waffenlager, Huette (4x4), Markt (5x5), Muehle (3x3), Kapelle (6x6) sind ganz gesperrt | ungeprueft | Weg-Ebene abgelesen (Grundriss 20:28) | 06.10. |
| W16 | Lagerplatz 5x5 = vier Teile zu 2x2 (nur herunter) und ein Kreuz aus freiem Boden dazwischen | ungeprueft | Weg-Ebene abgelesen (Grundriss 20:28) | 06.10. |
| W17 | Milchviehhof 10x10: Huette in der Ecke, Zaun mit 2 Felder breiten Toren in der Mitte jeder Seite, innen freier Boden | ungeprueft | Weg-Ebene abgelesen (Grundriss 20:28); deckt sich mit Daniel W7 (Gitter) | 06.10. |
| W18 | Apfelplantage: nur die Huette (3x3) ist Gebaeude, die Plantage zaehlt nicht dazu | ungeprueft | Weg-Ebene abgelesen (Grundriss 20:28); deckt sich mit Daniel W7 | 06.10. |
| W19 | Wachturm, Verteidigungsturm, Torhaus: Felder oben begehbar, vom Boden nicht (ausser Torhaus-Durchfahrt) | ungeprueft | Weg-Ebene abgelesen; Pruefung "vom Boden erreichbar" laeuft (Abstandsreihe 20:31) | 06.10. |
| W20 | Eingaenge lassen sich blockieren (Gebaeude, Mauern, Steingebaeude) - dann nehmen die Arbeiter einen anderen Eingang; so steuert man, wo was passiert | Daniel | Daniel 20:32 ("kleiner Tipp fuer maximale Effektivitaet") | 06.10. |
| W21 | Nur EINE Kaserne je Spieler: eine zweite wurde in 25 von 25 Versuchen nicht gebaut | getestet | Abstandsreihe 20:30 (`daten/wege_abstand_20261006_203014.json`, Kosten 0, Platz frei) - Grund nicht im Code nachgesehen | 06.10. |
| W22 | Ein weiteres Waffenlager wird nur Kante an Kante an ein bestehendes gebaut (Abstand 1-3 und nur Ecke an Ecke: 0 von 14) | getestet | Abstandsreihe 20:30 | 06.10. |
| W23 | Zwei Schmieden gerade ohne Abstand: kein Durchgang; ab 1 Feld Abstand Durchgang (O-W und N-S) | ungeprueft | Weg-Ebene, Abstandsreihe 20:30 (Bauen getestet, Laufen nicht) | 06.10. |
| W24 | Zwei Schmieden Ecke an Ecke: schraeger Durchgang zwischen den Ecken; zwei Verteidigungstuerme Ecke an Ecke: kein Durchgang | ungeprueft | Weg-Ebene, Abstandsreihe 20:30; deckt sich mit W3/W4 und Daniel W8 | 06.10. |
| W25 | Vier Schmieden im Quadrat ohne Abstand: Mitte nicht passierbar; je 1 Feld Abstand: passierbar in beide Richtungen | ungeprueft | Weg-Ebene, Abstandsreihe 20:30 | 06.10. |
| W26 | Huette neben Schmiede: in 3 Lagen (N-S 0, Eck NO 0-0 und 1-0) wurde die Schmiede nicht gebaut - Grund unbekannt | getestet | Abstandsreihe 20:30; offen | 06.10. |
| W27 | Schmiede neben Kaserne: bei jedem Abstand (auch 0) ein Weg - ueber den Exerzierplatz | ungeprueft | Weg-Ebene, Abstandsreihe 20:32 (`daten/wege_abstand_20261006_203223.json`) | 06.10. |
| W28 | Schmiede neben Waffenlager: gerade ohne Abstand kein Durchgang; Ecke an Ecke schraeg durch (nur eine Seite ist Ecksperre) | ungeprueft | Weg-Ebene, Abstandsreihe 20:32; deckt sich mit W3 | 06.10. |

## Arbeitsgaenge (gemessen mit einheitwacht alle 2 Ticks, `arbeitsgang_messen.py` 20:33, Auswertung `arbeitsgang_auswerten.py`)

| Nr | Aussage | Stufe | Grundlage | Stand |
|---|---|---|---|---|
| G1 | Arbeiter laufen 24 Ticks je Feld - gerade und schraeg gleich schnell | getestet | 2 Schmiede + 1 Gerber, 263+188+98 gerade / 75+117+30 schraeg Felder mit genau 24 Ticks (`daten/arbeitsgang_20261006_203334*.json`) | 06.10. |
| G2 | Der Milchbauer laeuft 16 Ticks je Feld | getestet | 31 Felder, nur einer | 06.10. |
| G3 | Schmied arbeitet 927 Ticks je Keule (926-928 in 9 Zyklen) | getestet | dieselbe Messung | 06.10. |
| G4 | Schmied laeuft je Zyklus EINEN Rundgang: Schmiede -> Lager (Eisen) -> Waffenlager (Keule) -> Schmiede; nah 24 Felder = 588 Ticks, fern 72 Felder = 1.692 Ticks | getestet | dieselbe Messung | 06.10. |
| G5 | Gerber arbeitet ~1.550 Ticks je Kuh und bringt die 3 Lederharnische in EINEM Gang zum Waffenlager | getestet | Leder +3 bei Tick 5.931 und 9.243 (Abstand 3.312 = 1.550 Arbeit + 77 Felder x 24) | 06.10. |
| G6 | Keulen je Eisen: 13 Keulen aus 11 Eisen - mehr als 1:1, ungeklaert (Abgabe manchmal +2) | getestet (offen) | Bestand alle 100 Ticks; feiner messen | 06.10. |
| G7 | Woher der Gerber nach der ersten Kuh die naechsten bekommt, ist ungeklaert (nur ein Gang zum Hof gesehen) | offen | Kuehe (Typ 51) beim naechsten Mal mitschreiben | 06.10. |
| G8 | Eingang (wo der Arbeiter steht): Schmiede und Gerberei unten Mitte (x+2, y+4); Waffenlager links (x-1, y+2) | getestet | Haltefelder der Arbeiter, Bau-Richtung 0 | 06.10. |
| G9 | Ein Gerber schafft rechnerisch so viel wie ~2 Schmiede (3 Leder je ~1.700-3.300 Ticks gegen 1 Keule je ~1.500-2.600) | ungeprueft | abgeleitet aus G3-G5, nicht im Spiel gegeneinander gemessen | 06.10. |
| G10 | Bau-Richtung dreht den Eingang (4x4: Schmiede, Gerberei, Waffenlager, Huette gleich): 0 unten (x+2,y+4), 2 links (x-1,y+2), 4 oben (x+1,y-1), 6 rechts (x+4,y+1) | getestet | `eingang_messen.py` 20:37, `daten/eingang_20261006_203700.json` | 06.10. |
| G11 | Eingang mit einer Huette zugebaut: der GESPEICHERTE Eingang (+0x112) bleibt gleich - ob Arbeiter einen anderen Zugang nehmen (Daniel W20), ist nicht getestet | getestet (Teil) | dieselbe Messung, Bild `daten/wege_abstand/eingang_blockiert.png` | 06.10. |
| G12 | Ein zweiter Markt wurde in keiner Richtung gebaut | getestet | dieselbe Messung; Grund nicht nachgesehen | 06.10. |
