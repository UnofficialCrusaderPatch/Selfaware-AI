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
| A4 | Ohne Lagerplatz fuer die Ware ist die Rueckgabe weg (nur Ton "kein Platz") | Daniel | Daniel 21:24 ("sie geht verloren, wenn du abreisst und kein Platz ist"); Code `giveBackResourceForDestroyedBuilding` passt - Endspiel verkauft darum VOR dem Abriss | 06.10. |
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
| G6 | Eine Schmiede macht aus einem Eisen abwechselnd 1 und 2 Keulen - im Mittel 1,5 je Eisen | Daniel | Daniel 20:43; passt zu den Messungen 13 aus 11 (Abgaben +2) und 43 aus 30 Eisen (Aufbau 20:40, 2 evtl. noch in Arbeit) - Abwechslung je Schmied noch nicht einzeln gesehen | 06.10. |
| G7 | Woher der Gerber nach der ersten Kuh die naechsten bekommt, ist ungeklaert (nur ein Gang zum Hof gesehen); Aufbau 20:40: 0 Kuehe in 12.000 Ticks, weil Beliebtheit 0 / Leute 4 die Hoefe unbesetzt liess (Daniel 20:41) | offen | Kuehe (Typ 51) beim naechsten Mal mitschreiben | 06.10. |
| G8 | Eingang (wo der Arbeiter steht): Schmiede und Gerberei unten Mitte (x+2, y+4); Waffenlager links (x-1, y+2) | getestet | Haltefelder der Arbeiter, Bau-Richtung 0 | 06.10. |
| G9 | Ein Gerber schafft rechnerisch so viel wie ~2 Schmiede (3 Leder je ~1.700-3.300 Ticks gegen 1 Keule je ~1.500-2.600) | ungeprueft | abgeleitet aus G3-G5, nicht im Spiel gegeneinander gemessen | 06.10. |
| G10 | Bau-Richtung dreht den Eingang (4x4: Schmiede, Gerberei, Waffenlager, Huette gleich): 0 unten (x+2,y+4), 2 links (x-1,y+2), 4 oben (x+1,y-1), 6 rechts (x+4,y+1) | getestet | `eingang_messen.py` 20:37, `daten/eingang_20261006_203700.json` | 06.10. |
| G11 | Eingang mit einer Huette zugebaut: der GESPEICHERTE Eingang (+0x112) bleibt gleich - ob Arbeiter einen anderen Zugang nehmen (Daniel W20), ist nicht getestet | getestet (Teil) | dieselbe Messung, Bild `daten/wege_abstand/eingang_blockiert.png` | 06.10. |
| G12 | Ein zweiter Markt wurde in keiner Richtung gebaut | getestet | dieselbe Messung; Grund nicht nachgesehen | 06.10. |
| G13 | Mit Beliebtheit 0 sinkt die Bevoelkerung auf das Minimum 4 und Gebaeude bleiben unbesetzt - Messpartien muessen die Beliebtheit hoch halten (Essen kaufen) | Daniel | Daniel 20:41; gemessen am Ende der Aufbau-Messung: Beliebtheit 0, Leute 4, Wohnplatz 10 | 06.10. |

## Aufbau 5+5 (aufbau_bauen.py, Beliebtheit 100 durch Messumgebung, `daten/aufbau_20261006_204359*.json`)

| Nr | Aussage | Stufe | Grundlage | Stand |
|---|---|---|---|---|
| A8 | Messumgebung haelt die Beliebtheit bei 100 (Essen 4 Sorten nachkaufen, doppelte Rationen, Bestechung, Start gesetzt): alle 13 Arbeitsplaetze besetzt | getestet | Beliebtheit 100/100/100 ueber 12.000 Ticks | 06.10. |
| A9 | Ein Waffenlager fasst vermutlich 50 Waffen: Keulen + Leder blieben ab Tick 10.079 bei genau 50, obwohl Eisen und 9 Kuehe da waren | getestet (Indiz) | Verlauf im Bestand; Fuellstand des Waffenlagers selbst noch nicht ausgelesen | 06.10. |
| A10 | Milchviehhof: ~0,46 Kuehe je Hof und 1.000 Ticks (3 Hoefe, 9 Kuehe in ~6.500 Ticks); je Kuh genau 3 Leder (5 Kuehe -> 15) | getestet | Kuehe (Typ 51) alle 50 Ticks | 06.10. |
| A11 | Schmied holt das Eisen am Lagerteil MIT Eisen, nicht am naechsten; Reihenfolge Werkstatt -> Waffenlager -> Eisenteil -> Werkstatt; am Eisenteil Wartezeiten (32+56+34 Ticks) | getestet | Schmied 139 Feld fuer Feld; Plan rechnete 6 Felder, gelaufen 12 | 06.10. |
| A12 | Aufbauplaner Runde 1 unterschaetzt die Gaenge um den Faktor ~2 (Schmiede 12-22 statt 6-13, Gerber 42-127 statt 16-22) - Gruende A11 und weite Hoefe | getestet | VERGLEICH in der Auswertung | 06.10. |
| A13 | Runde 2 (Eisenteil + Hoftore im Plan, laufend anwerben): 44 Kaempfer aus 30 Eisen; 10 nach 5.262, 20 nach 6.539, 30 nach 7.889, 40 nach 10.611 Ticks (ab Messbeginn); Eisen nach 6.425 leer; Schmied-Gaenge 3/7/16/19/14 gegen geplant 4/6/11/12/12 | getestet | `daten/aufbau_20261006_204739.json` | 06.10. |
| A14 | Bester Lagerplatz (Weg-Ebene + Platzkarte des Spiels): heute am Bergfried Kuhweg 27 + Eisenweg 45 = 72 Felder; mit Minen bei (193,309) 1 + 6 = 7; mit Markt-Eisen bei (167,295) Kuhweg 0 | ungeprueft | `standort.py`, `daten/standort_20261006_205012.*`; Naeherung "naechster Hof", 3 Hoefe + Werkstaetten-Platz nicht geprueft | 06.10. |
| A15 | Das Vorratslager umzusetzen ist effektiver, als es am Bergfried zu lassen | Daniel + getestet (A16) - wartet auf Daniels Bestaetigung fuer "fest" | Daniel 20:48 ("100 % sicher"); A14 rechnet in dieselbe Richtung | 06.10. |
| A16 | Lager versetzt nach (167,295) an das Gruenland (Runde 3, Messumgebung, 30 Eisen gekauft): 10 -> 40 Kaempfer in 3.665 Ticks statt 5.349 am Bergfried (-31 %), obwohl nur 9 von 11 Gebaeuden standen (4 Schmieden, 4 Gerbereien); Leder nicht mehr Engpass (43 uebrig), jetzt Eisen/Schmieden | getestet | `daten/aufbau_20261006_205123.json` gegen `..._204739.json`; Vergleich ueber die Spanne 10-40, weil die Arbeiter unterschiedlich frueh besetzt waren | 06.10. |

## Aufbau ab Tick 0 (Daniel 06.10. 20:52)

| Nr | Aussage | Stufe | Grundlage | Stand |
|---|---|---|---|---|
| B1 | Reihenfolge fuer den Aufbau von 0: Lager zuerst zu schnellem Holz umsetzen, dann Stein, dann Eisen, dann erst die Waffenproduktion; den Zeitpunkt so legen, dass moeglichst alle Lederharnische produziert werden koennen | Daniel | Daniel 20:52 | 06.10. |
| B2 | Messungen ab jetzt immer von Tick 0 unter echten Bedingungen (kein gesetztes Gold, keine Gratis-Gebaeude), damit Daniel zuschauen kann | Daniel | Daniel 20:52 | 06.10. |
| B3 | Kornspeicher nicht an die Hoefe; Huetten, Kaserne und Markt duerfen beliebig weit weg - der Platz am Lager gehoert der Waffenproduktion | Daniel | Daniel 20:54 (Bild Runde 3) | 06.10. |
| B4 | Werkstaetten moeglichst nah am Lager, aber mit 1 Feld Abstand statt 0 - sonst laufen die Arbeiter ueber das Lager, das verlangsamt | Daniel | Daniel 20:54; passt zu W9 (Arbeiter treten auf Lagerteile) - Verlangsamung nicht gemessen | 06.10. |
| B5 | Nur EIN Lagerteil geht nicht dauerhaft: jedes Teil fasst eine Warenart (<= 48), die Kette braucht mindestens Holz, Stein, Eisen -> Eisenteil zur Schmiede-Seite, Holz/Stein abgewandt | getestet (S6) + Folgerung | Antwort auf Daniels Frage 20:54 | 06.10. |
| B6 | Erster Haertetest: Zeit von Tick 0 bis zu den ersten 10 ausgebildeten Streitkolbenkaempfern, Liga-Start (0 Gold, 150 Holz, Startessen) | Daniel | Daniel 20:54 | 06.10. |
| B7 | Der schnellste Weg zu EINER Streitkolben-Werkstatt ist NICHT der schnellste zu 10 Kaempfern - der Aufbau braucht die ganze Wirtschaft: Apfelplantagen, Holzfaeller, Jaeger usw. | Daniel | Daniel 21:01 (Test v1 abgebrochen) | 06.10. |
| B8 | Kaese nicht fuer die Nahrung nutzen - es kommt zu langsam herein | Daniel | Daniel 21:01 | 06.10. |
| B9 | Haertetest v1 (Lager am Bergfried, ohne Nahrungswirtschaft), abgebrochen bei Tick 20.845: Steinbruch ab 646 -> erster Stein 5.246; Eisenmine ab 5.323 -> erstes Eisen 11.823; bis 20.845 keine Keule und kein Leder trotz 6 Kuehen (Ursache nicht gesucht); Beliebtheit 82, Leute 26, Gold 120 | getestet | `daten/haertetest_v1_abgebrochen_20261006.txt` | 06.10. |
| B10 | Kurzes und langes Ziel trennen: Stein/Eisen so schnell wie moeglich ist "jain" - das Ziel braucht nicht nur schnell, sondern viel. Erst maximale Wirtschaft mit maximal viel Gold, im Notfall Waffen kaufen und Werkstaetten aus dem Ueberschuss finanzieren -> nach wenigen Monaten gleichauf, danach exponentiell schneller | Daniel | Daniel 21:05 | 06.10. |
| B11 | Bauordnung v2 = Apfel-Eroeffnung (Phase 1/2 aus erstes_spiel.py) + Waffen am Markt kaufen (5 Keulen 300, 5 Leder 160, Anwerben 20 = 112 je Kaempfer); v3 = + Werkstaetten, sobald sie sich ueber den Horizont rechnen | Plan | `erstes_spiel.py streitkolben=10` | 06.10. |
| B12 | Nicht scheu sein, MEHR zu bauen - mehr ist besser, aber schlau; schlau + mehr ist optimal. Aber nicht immer: beim Rush gibt es einen Zeitpunkt, ab dem man nicht mehr in Wirtschaft, sondern in Militaer investiert, spaeter vielleicht wieder in Wirtschaft - dynamisch, teilweise parallel | Daniel | Daniel 21:07 ("nur ein Gist von hunderten Stunden") | 06.10. |
| B13 | Waffenlager (und Kaserne) nicht frueh bauen - sie haben keinen Wert, bevor Waffen reinkommen; das Holz/der Stein fehlt sonst in der Wirtschaft | Daniel | Daniel 21:07 (Bild v2, Tick ~2.600); umgesetzt: erst wenn Gold fuer das erste Los (300 + 160 + 20 ueber Ruecklage) da ist | 06.10. |
| B14 | Eigene Produktion lohnt sich schon fuer weniger als 10 Kaempfer, wenn sie moeglichst frueh (nicht fruehestmoeglich) laeuft - eine frueh produzierende Werkstatt arbeitet laenger und ist am kosteneffektivsten; offen, ob spaeter 2-4 Produktionen besser sind. Rechnung: Gewinn aus Waffen-, Gebaeude-, Eisenkosten (gekauft vs. produziert) plus Platz, Arbeiter (Steuern, Essen) | Daniel | Daniel 21:11; Rechnung mit Messwerten: 1 Schmiede + 1 Gerberei + 2 Hoefe ab ~6.000 -> bis ~12.000 ~7 Keulen + 7 Leder = ~640 Gold gespart gegen ~380 Einsatz (ungeprueft, v3 prueft) | 06.10. |
| B15 | Hoechstens 2 Lagerplaetze: 3 Teile reichen (Holz, Stein, Eisen) bei optimaler Platzierung und Verkauf, 2 Plaetze (8 Teile) sind sicher | Daniel | Daniel 21:11 (Bild v2b); umgesetzt: MAX_LAGERTEILE = 8 im Ertragsplaner | 06.10. |
| B16 | Anwerben braucht freie Bauern am Feuer - in v2b meist 0-1 (79 Leute / 90 Platz): mehr Huetten fuer freie Leute | getestet | v2b Tick 12.272-12.702 | 06.10. |
| B17 | Beliebtheit wirklich ueber 95 halten, damit die Bevoelkerung schnell genug nachkommt | Daniel | Daniel 21:13 (Bild v2b: Beliebtheit 59, Gold 386, 77/82 Leute) | 06.10. |
| B18 | Seasoning ist wieder nicht optimiert (B-Plantagen nie gesetzt) | Daniel | Daniel 21:13; gemessen v2/v2b "B gesetzt bei None" (Backlog 21:10) | 06.10. |
| B19 | Waffen kaufen ist moeglich, aber nicht optimal | Daniel | Daniel 21:13 | 06.10. |
| B20 | Endspiel zum Optimieren: alles abreissen, alle Ressourcen verkaufen und Waffen kaufen / anwerben (Abriss gibt die Haelfte zurueck, A1; freigesetzte Arbeiter stehen zum Anwerben bereit - ungeprueft) | Daniel | Daniel 21:13 | 06.10. |
| B21 | Fruehes Anwerben nimmt der Wirtschaft das Gold (z. B. fuer die Waffenproduktion) | Daniel | Daniel 21:14 | 06.10. |
| B22 | Ertragsplaner baut endlos Jaegerhuetten: v2b 59 gebaut / 57 stehen bei Tick 26.281, fast alle ohne Arbeiter, meist an derselben Rehherde (77,236-238), je 60 Gold -> ~3.500 Gold verbrannt; Beliebtheit 38, Feuer 0 | getestet | Daniel 21:14 (Bild); `daten/haertetest_v2b_20261006.txt` - Ursachen: keine Arbeiter-Pruefung (Huetten-Regel greift erst bei Leute >= Platz-2), keine Saettigung je Herde, ohne Partieende baut er alles mit Amortisation | 06.10. |
| B23 | Seasoning-Fehler gefunden: der Ertragsplaner setzte VOR der A-Reife eigene Apfelplantagen auf/neben die B-Plaetze (1.079 bei (77,223), 1.155 auf (89,235), 1.233 bei (67,220)); bei A-Reife (1.694) galt 1 B als erledigt, 2 fanden keinen Platz -> B die ganze Partie offen | getestet | v2b-Protokoll | 06.10. |
| B24 | Bilanz-Tabelle: was ist drin / kommt rein, was braucht man WIRKLICH - dann alles abreissen und das Ziel erfuellen (Minimal-/Maximalprinzip) | Daniel | Daniel 21:21; umgesetzt `bilanz.py` + Endspiel im Lenker (v4) | 06.10. |
| B25 | Verkaufspreise: Stein 5 Gold je Stueck (5 -> +25), Eisen 27 (10 -> +270) | getestet | Messung 21:22 im stehenden v3-Spiel (je 1 Verkauf, kurz laufend - Holz/Fleisch dabei verrauscht) | 06.10. |
| B26 | Eine Eisenmine zu bauen ist fast immer besser, als Holz und Stein nur zu verkaufen | Daniel | Daniel 21:34; steht gegen unsere Messung (v4: 11 Minen bis Tick 14.000 kein Eisen, Anlauf 6.664; v5: 359 Holz ungenutzt im Endspiel) -> Verdacht: unsere Minen sind falsch gesetzt/unbesetzt/Eisen sofort verkauft - Diagnose offen | 06.10. |

## Bewaehrt / nicht bewaehrt (nach jedem Lauf eine Zeile, Daniel 21:05: "schauen, was hat sich bewaehrt und was nicht")

| Lauf | Was | Bewaehrt? | Messwert |
|---|---|---|---|
| Messpartie 8 / Abriss | Abriss-Knopf mit 50 % statt 0 % | bewaehrt | Schmiede 20/8 -> 10/4 zurueck |
| Aufbau 5+5 Runde 1 | ohne Beliebtheit gemessen | NICHT bewaehrt | Beliebtheit 0, Leute 4, 0 Kuehe - Messung wertlos |
| Aufbau 5+5 Runde 2 | Messumgebung (Beliebtheit 100) + Eisenteil im Plan + laufend anwerben | bewaehrt | 44 Kaempfer aus 30 Eisen; Schmied-Gaenge nah am Plan |
| Aufbau 5+5 Runde 3 | Lager ans Gruenland versetzt | bewaehrt | 10->40 Kaempfer 31 % schneller |
| Aufbauplaner Runde 1 | naechstes Lagerteil statt Eisenteil angenommen | NICHT bewaehrt | Gaenge doppelt so lang wie geplant |
| Haertetest v1 | nur Waffenkette ab Tick 0, ohne Nahrungswirtschaft, Kaese verkauft | NICHT bewaehrt | erster Stein 5.246, erstes Eisen 11.823, keine Keule bis 20.845; Daniel brach ab |
| Haertetest v2 (laeuft) | Waffenlager bei Tick 887 gebaut, lange bevor Waffen kamen | NICHT bewaehrt (Daniel B13) | 5 Holz frueh gebunden; fuer v2b geaendert |
| Haertetest v2 | Apfel-Eroeffnung + Waffen kaufen, bis Tick 18.829 (Ende: Ansicht 16) | NICHT bewaehrt | 0 Kaempfer: Kauf wartete auf ausbau.braucht_gold, das wegen nie gesetzter B-Plantagen immer True war (Gold bis 2.220); Stein fuer die Kaserne wurde verkauft; Planer setzte 15 Eisenminen. Wirtschaft selbst: 86 Leute, 19 Holzfaeller, 11 Apfelplantagen bei Tick 18.300 - `daten/haertetest_v2_20261006.txt` |
| Haertetest v2b | Kipppunkt (Kauf wartet nicht auf den Planer) | teils bewaehrt | Kaempfer 1 bei 12.446, 5 bei 14.079 - dann Planer-Fehler (57 Jaegerhuetten, Beliebtheit 38, Feuer 0); abgebrochen bei 26.281 |
| Haertetest v3 | Seasoning-Fix (B-Plaetze frei) + Steuern bis Bestechung + Produktion nach Seasoning | teils bewaehrt | Seasoning: alle 3 B 25 Ticks nach A-Reife (bewaehrt); Beliebtheit 91-98 (bewaehrt); Gold 1.789 bei ~21.000; Produktion startete NIE (Lager-Nummern 6-9 neu vergeben) und 25 Jaegerhuetten mit 10.000-18.800 Ticks Amortisation (nicht bewaehrt); `daten/haertetest_v3_20261006.txt` |
| Haertetest v4 | Apfel-Eroeffnung + Produktion + Bilanz-Endspiel | **bewaehrt (Bestzeit 1)** | 10 Kaempfer bei Tick 14.648 (Endspiel bei 14.000: Gold 489 + Lager 307 + Abriss 56 Betriebe 521 = 1.317 gegen Bedarf 1.240); Seasoning B bei 1.719. NICHT bewaehrt darin: eigene Produktion lieferte 0 (11 Eisenminen, Anlauf 6.664, 55-65 Felder weg; Gerberei fand keinen Platz) |
| Haertetest v5 | nur Wirtschaft + Bilanz-Endspiel, Planer-Horizont 16.000 | **bewaehrt (Bestzeit 2)** | 10 Kaempfer bei Tick 11.930 (-18,6 % gegen v4); Endspiel 11.416, erster Kaempfer 11.867 (Kaserne erst im Endspiel, weit weg); 359 Holz ungenutzt; keine Eisenminen (Horizont) |
