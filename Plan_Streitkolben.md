# Plan: 10-20-30-40-50 Streitkolbenkaempfer so schnell wie moeglich (Stand 06.10.2026, 19:50)

## Auftrag (Daniel 06.10. 19:45, woertlich)
"mach danach die Streitkolbenkaempfer 10-20-30-40-50 und hier bitte maximal aufpassen auf die Waffenproduktion,
Ausbildungslager naeher zum Vorratslager, minimale Laufwege fuer die Wirtschaft, erst bauen wenn Ressourcen im
Vorratslager ankommen fuer maximale Effektivitaet. Bitte kreative Loesungen finden, wenn Gold zu viel ueber ist (was ich
bezweifle) gerne auch Essen kaufen. Du brauchst Lederharnische und Harnischmacher etc. Berechne wie produktiv alle
Gebaeude sind, also wie viele Kuehe wann generieren, wie viele Lederharnische aus einer Kuh gemacht werden koennen, wie
viele Streitis aus einem Eisen gebraucht werden etc."
Vorher (19:21): Testpartie gegen eine leere KI - am schnellsten 10.000 Gold, dann 10-20-30-40-50 Streitkolbenkaempfer,
dann jede Einheit. Grundsatz (19:33): gegen mehrere Gegner braucht es stabiles Wachstum, Rohstoffverkauf reicht nicht.

## Challenge-Regeln (Daniel 06.10. 19:49)
- Es zaehlt die genaue Anzahl, so schnell wie moeglich - wie ein TAS-Run (Speedrun mit Werkzeug).
- Fuer die letzten Kaempfer duerfen nicht mehr gebrauchte Waffen verkauft werden; Abreissen bringt tendenziell die
  Haelfte der investierten Ressourcen als verkaufbare Produkte -> theoretisch alles abreissen bis auf das, was die
  Rekrutierung braucht, und die letzten rauspressen.
- Reihenfolge: erst Recherche, dann Aufbau, dann Benchmark, dann immer weniger Zeit. "Ich glaube, es ist schneller als
  ich denke."
- Arbeitsweise (19:49): selbst herausfinden, aber Daniel hat viel Spielerfahrung - nicht ALLE Fehler selbst machen;
  stoppt er, ihm vertrauen und die richtigen Infos sammeln.

## Testumgebung (steht)
`erstes_spiel.py assassinen=0 leere_ki=ja gold_ziel=N bis_tick=60000` - Rotkaeppchen mit Waren/Gold jede Runde 0.
Ausgangswert Gold (gold10k_2, 06.10.): 1.000 bei 15.975, 10.000 bei 36.226; verkauft vor allem Holz, Fleisch, Aepfel, Stein.

## Was feststeht (Liga-Balance liga_ai.json, abgelesen)
| | Wert |
|---|---|
| Streitkolbenkaempfer | 20 Gold + Keule + Lederharnisch; 25.000 Leben |
| Kaserne | Kosten [0, 12, 0, 0, 0] |
| Schmiede (Keulen/Schwerter) | [20, 8, 0, 0, 0] |
| Gerberei (Lederharnisch) | [15, 3, 0, 0, 75] |
| Milchviehhof (Kuehe) | [7, 0, 0, 0, 15] |
| Eisenmine | [20, 6, 0, 0, 0]; Eisen doppelt abgeholt (enable_iron_double_pickup) |
| Markt | Keule Kauf 300 / Verkauf 150; Leder 160 / 50; Eisen 270 / 135 (je Los) |
Kosten-Reihenfolge vermutlich [Holz, Stein, Eisen, Pech, Gold] (so liest der Planer die Baukosten aus dem Spiel) - im
Spiel gegenpruefen.

## Was gemessen werden muss (nichts schaetzen)
1. Milchviehhof: Kuehe je 1.000 Ticks, wann die erste Kuh, wie viele gleichzeitig.
2. Gerberei: Lederharnische je Kuh, Ticks je Harnisch.
3. Schmiede: Keulen je Eisen, Ticks je Keule.
4. Eisenmine: Eisen je 1.000 Ticks (Planer-Messung: 0,61 je Mine bei 61 Feldern Weg - Weg zaehlt).
5. Laufwege: Werkstatt <-> Lager <-> Waffenlager <-> Kaserne in Feldern; Zeit vom fertigen Gegenstand bis im Waffenlager.

## Schritte
1. Messpartie: je eine Kette (2 Milchviehhoefe, 1 Gerberei, 2 Eisenminen, 1 Schmiede, Waffenlager + Kaserne direkt am
   Lager) in der Testumgebung; jede Runde Bestand (Keule, Leder, Eisen) und Arbeiterzustand mitschreiben.
2. Aus den Messwerten die Verhaeltnisse rechnen (Hoefe je Gerberei, Minen je Schmiede) - mit Befehl und Quelle.
3. Lenker "Streitkolben": Werkstaetten nah am Lager, Kaserne/Waffenlager am Lager, bauen erst wenn die Ware im Lager ist,
   anwerben sobald Keule + Harnisch + 20 Gold da sind; Marken 10/20/30/40/50 mit Tick.
4. Gegenprobe: dieselben Marken mit Kauf am Markt (Keule 300 + Leder 160 + 20 je Kaempfer) - was ist schneller?
5. Ueberschuessiges Gold: Essen kaufen (Beliebtheit -> hoehere Steuern) - erst wenn gemessen ist, dass Gold uebrig ist.

## Messergebnisse (Messpartie 3, 06.10. 19:55, `daten/streitkolben_messung_20261006_195508.json`)
- Gesetzte Zahlen wirken nur bei Gold. Stein/Holz/Eisen/Waffen liegen in Lagern; ein gesetzter Zaehler wird neu
  gezaehlt (Stein 0 -> 300 gesetzt, kurz darauf 0). Darum fehlten Kaserne (12 Stein), Schmiede (8), Gerberei (3) -
  Daniel 19:54: "du brauchst gewisse Gueter, siehe Balance". Waren echt am Markt kaufen.
- Markt (je Kauf/Verkauf): 5 Keulen 300 / 150 Gold; 5 Leder 160 / 50; 5 Stein 50.
- Kaserne: ein Streitkolbenkaempfer zieht 20 Gold + 1 Keule + 1 Lederharnisch ab (+1 Einheit Typ 26).
- Gerberei: +3 Lederharnische je Kuh (zwei Spruenge 4->7 bei Tick 5.615, 7->10 bei 7.450; 2 Milchviehhoefe + 1 Gerberei).
- Offen: Keulen je Eisen (Eisenkauf scheiterte, Gold blieb gleich - warum?), Holzkauf scheiterte ebenso;
  Abriss einer frisch gebauten Schmiede gab in 10 Ticks nichts zurueck (zu frueh gemessen? im Bau?).
- Eisen-/Holzkauf geklaert (19:58): alle 4 Lagerteile belegt (Holz 13+48, Stein 17+2) - ein Teil fasst nur eine
  Warenart (48). Vor neuer Warenart freies Teil schaffen.
- Naechster Schritt: Schmiede mit Eisen messen, Abriss nach
  Fertigstellung und laengerer Wartezeit messen; dann Kette dimensionieren und erster Benchmark 10 Kaempfer.

## Messpartie 4 (06.10. 20:00, `daten/streitkolben_messung_20261006_195917.json`)
- Mit angebautem Lagerblock klappt der Eisenkauf: 4 Kaeufe = 20 Eisen fuer 1.080 Gold (270 je 5).
- Schmiede (bei (90,280), Lager am Bergfried (145,264), ~55 Felder): holte je 1 Eisen bei Tick 4.654 und 8.745 -
  ~4.100 Ticks je Stueck, der Weg zum Lager dominiert (Daniel: Werkstaetten nah ans Lager).
- Die Schmiede macht ohne Umstellung SCHWERTER: Vorrat danach Schwert 1, Keule unveraendert. Im Spiel wird sie per
  Klick auf Keulen umgestellt -> den Spielbefehl dafuer finden (nicht Speicher setzen).
- Naechste Schritte: (1) Umstell-Befehl der Schmiede finden; (2) Werkstaetten, Waffenlager und Kaserne direkt ans Lager;
  (3) Zeit je Keule und je Harnisch bei kurzem Weg messen; (4) Abriss-Rueckgabe messen (diesmal keine 2. Schmiede gebaut).

## Messpartien 5/6 (06.10. 20:02-20:04)
- Spielbefehl 33 `ClickSetBuildingProductionType` (Gebaeude, Art, UID) -> `SetBuildingProductionType` setzt
  producedItemType, wenn die UID passt (`daten/dekomp_produktionstyp*.c`, Befehlstabelle `daten/befehlstabelle_namen.txt`).
  Art 21 = Keule: danach 3 Keulen aus 3 Eisen (belegt: 1 Eisen = 1 Keule).
- Lager zuerst vergroessern! Messpartie 5 baute alles direkt ans Lager -> kein Anbau moeglich, Eisenkauf scheiterte.
  Messpartie 6: erst zwei Lagerbloecke, dann der Rest -> Eisen (20 fuer 1.080) und Holz (bis 195) kaufbar.
- Schmiede ~6 Felder vom Lager: holt alle ~2.100 Ticks 1 Eisen (3.151 / 5.256 / 7.364), Keulen bei 5.124 und 7.231.
  Bei ~55 Feldern Weg waren es ~4.100 Ticks.
- Gerberei: erste Harnische bei ~6.500 (Milchviehhoefe ~40 Felder weg, bei (174,296)/(178,240)); 1 Kuh = 3 Harnische.
- Abriss einer Schmiede: auch nach 150 Ticks und mit Lagerplatz 0 zurueck - offen (fertig gebaut? andere Art Rueckgabe?).
- Vergleich: Markt 1 Keule 60 Gold, 1 Harnisch 32 Gold -> ein Kaempfer 112 Gold; selbst gemacht: Eisen 54 Gold je Stueck
  (Kauf) + ~2.100 Ticks je Schmiede. Gold ist der Engpass (Ausgangswert: 1.000 Gold erst bei Tick 15.975).
- Naechster Schritt: erster Benchmark 10 Kaempfer ab Tick 0 ohne gesetztes Gold - Weg A nur Markt, Weg B Markt +
  eigene Kette; Marken 1..10 mit Tick.

## Daniel 06.10. 20:05 (Bild: Lager mit Gebaeuden drumherum) - als Naechstes
Woertlich: "ich verstehe nicht genau warum du es so baust, weil der Weg vom Streitimacher gesperrt ist. PS: wenn du
sie genau aufeinanderliegend machst, koennen sie durchlaufen. PS PS: es macht sehr viel Sinn zu schauen, wie du die
Laufwege sehen kannst und natuerlich wie das Spiel sie berechnet, und dann eine moeglichst effektive Aufstellung
erstellst - das wird besonders wichtig, wenn du skalierst, sagen wir 30 Schwertmacher und 30 Lederharnischmacher etc.
bzw. dynamisch anpassend je nachdem wie viele du von was brauchst. Aber bitte gerne testen wie viel Streitis wie viel
Eisen, wie viele Kuehe wie viele Lederharnische."
Daraus:
1. Laufwege sichtbar machen: Arbeiter-Positionen je Runde mitschreiben (Lagebild: x, y, laufx, laufy, zustand) und als
   Karte auswerten; Begehbarkeit/Wegnetz des Spiels lesen (Modulbefehle begehbar, wegtest, rohstoffkarte).
2. Wie das Spiel Wege berechnet (Wegfinder, Wegnetz-Gebiete) im Spielcode nachlesen (Ghidra, findPath...).
3. Aufstellung: Werkstaetten so, dass kein Weg zum Lager/Waffenlager versperrt ist; Gebaeude genau aneinander, damit
   man durchlaufen kann (Daniel) - im Spiel pruefen.
4. Skalierbar und dynamisch: Zahl der Schmieden/Gerbereien/Milchhoefe nach Bedarf (z. B. 30/30) - Verhaeltnisse
   messen: Keulen je Eisen (bisher 1:1, 3 Stueck), Harnische je Kuh (bisher 3, 2 Kuehe) - mit mehr Stueckzahl bestaetigen.

## Daniel 06.10. 20:06 zum Abriss
"sie bekommen nicht mehr Wert, nur weil sie laenger stehen. Sie geben normalerweise die Haelfte ab, egal in welchem
Zustand. Gleiches gilt fuer Torhaeuser oder Tuerme, weshalb es manchmal effektiver sein kann, sie abzureissen und mit der
Haelfte ein neues zu bauen, anstatt sie zu reparieren." - Meine 0-Messungen widersprechen dem: der Modulbefehl abreissen
hat einen Parameter rueckgabe (Standard 0, Spielbefehl 29 {nr, rueckgabe, uid}) - nie gesetzt. Naechster Test: rueckgabe=1.
- Messpartie 7 (20:07): Abriss mit rueckgabe=1 -> wieder 0 Holz/Stein/Gold nach 150 Ticks. Offen; zu pruefen: wurde die
  zweite Schmiede ueberhaupt fertig/abgerissen (Gebaeudeliste vorher/nachher), war das Holz-Lager voll (195 = 4 Teile),
  was param_3 in giveBackResourceForDestroyedBuilding bedeutet (daten/dekomp_abriss_rueckgabe.c ganz lesen).
- GELOEST 20:10: param_3 ist ein Prozentwert (Kosten * Prozent / 100); der Abriss-Knopf schickt 50 (Ghidra
  QueueAufrufe.java: MenuItemActionHandler_BuildMenu_DeleteAction 0x00438ad9 MOV [Param1], 0x32). Modul logik.lua:
  abreissen jetzt Standard 50, gedeckelt bei 50 (Sicherung logik.lua.bak-abriss50-20261006). Messpartie 8: Schmiede
  20/8 -> 10 Holz / 4 Stein zurueck - Daniel bestaetigt.
- Daniel 20:11 "schau mal bei geraden/ungeraden Ressourcen/Abriss": abriss_messen.py (Erwartung vorher im Kopf der
  Datei) - Gerberei 15/3/75 -> 7/1/37 (zweimal gleich, kein gemerkter Rest), Milchviehhof 7/0/15 -> 3/0/7, Kaserne
  0/12 -> 6, Huette 5 -> 2. Es wird ABGERUNDET. daten/abriss_messung_20261006_201248.json.
  Aus dem Code (nicht gemessen): kein Lagerplatz -> Rueckgabe verloren; Mauern sammeln Bruchteile ueber Abrisse.

## Haertetest ab Tick 0 (Daniel 06.10. 20:52/20:54)
Daniel: "immer direkt von 0 anfangen ... dann kann ich zuschauen"; erster Haertetest = Zeit von Tick 0 bis zu den ersten
10 ausgebildeten Streitkolbenkaempfern, realistische Startbedingungen (0 Gold, normale Ressourcen). Reihenfolge (B1):
Lager zu schnellem Holz umsetzen -> Stein -> Eisen -> Waffenproduktion, Zeitpunkt so, dass moeglichst alle
Lederharnische produziert werden. Bauregeln (B3/B4): Kornspeicher/Huetten/Kaserne/Markt weit weg, Werkstaetten 1 Feld
vom Lager.

Gemessen vor dem Start (20:56-20:58, `erkunden.py`, Start ohne Eingriff):
- Startholz kommt nach und nach: 30 bei Tick 120, +~28 je 110 Ticks, 150 ab Tick ~650; Bauern 2 -> 10 bis Tick 566;
  Beliebtheit startet bei 100 und sinkt ohne Essen (97,75 bei 231, 93,25 bei 678).
- Karte (Bergfried 141,265): Wald knapp (76 Baeume im Umkreis 75), Waelder O (191,265) und SO (163,311); Hof ab 27
  Feldern (172,297); Mine ab 48 (141,317); Steinbruch nur im Westen ab 56 (81,267).
- Kosten (Spieltabelle): Huette 5 H, Holzfaeller 5 H, Eisenmine 20 H 6 S, Kaserne 12 S, Waffenlager 5 H, Schmiede
  20 H 8 S, Gerberei 15 H 3 S 75 G, Kornspeicher 5 H, Steinbruch 25 H, Ochsenjoch 5 H, Markt 0, Milchviehhof 7 H 15 G.
- Verkauf (verkaufspreise_liga.txt): Kaese 6, Brot 4, Aepfel 3, Fleisch 1, Holz 1 Gold je Stueck.

Bauordnung v1 (`haertetest.py`, Grundlinie - Lager bleibt am Bergfried, Test 2 versetzt es und misst den Gewinn):
Kornspeicher + Markt -> Kaese/Brot verkaufen (+150) -> 2 Milchviehhoefe -> Steinbruch + Ochsenjoch -> 2 Huetten ->
Gerberei / Eisenmine / Waffenlager / Schmiede (Aufbauplaner) -> Kaserne. Bedarf: 109 Holz, 29 Stein, 305 Gold.
- v1 abgebrochen 21:01 (Daniel): nicht optimiert - es fehlen Apfelplantagen, Holzfaeller, Jaeger; der schnellste Weg
  zu einer einzelnen Streitkolben-Werkstatt ist nicht der schnellste zu 10; Kaese kommt als Nahrung zu langsam (B7/B8).
  Gemessen bis dahin: erster Stein 5.246, erstes Eisen 11.823, keine Keule/kein Leder bis 20.845 (B9).

## Bewertungskette fuer "unter 1 Jahr" (Daniel 21:58/21:59: 5 Versuche; "keine Bewertungskette oder kritische Befragung")
Stand 21:59, Bestzeit v5 11.930 (Endspiel 11.416). Ziel < 9.600 -> Endspiel bei ~9.400 mit Bedarf ~1.185 Gold-Wert;
v5 hatte bei 9.400 erst ~900 -> es fehlen ~30 %.
1. Schnellere Eroeffnung (v11/v12: Seasoning B 1.215 statt 1.720) + schnelleres Endspiel -> grob 11.000. Reicht NICHT.
2. Groesster Hebel = Bedarf senken: von 1.120 gehen 600 an Keulen, 320 an Leder.
   - eigenes Leder: 2 Hoefe + 1 Gerberei direkt nach dem Seasoning (~105 Gold) spart 320 (0,46 Kuehe/Hof/1000, 3 Leder/Kuh).
   - eigene Keulen aus GEKAUFTEM Eisen: 7 Eisen x 54 = 378 -> 10 Keulen (1,5/Eisen) spart ~220 gegen 600.
   -> Bedarf ~30 % kleiner = genau die Luecke. Gegenprobe Zeit: Hoefe ab ~1.300 -> ~7 Kuehe bis 9.000 (21 Leder);
      Schmiede 1,5 Keulen je ~1.100 Ticks -> ~10 bis 8.000. Nur gerechnet (ungeprueft).
3. Gleiche Fassung mehrfach laufen lassen ist KEIN Weg (Daniel) - erst Aenderung mit Rechnung, dann Versuch.
Naechster Schritt v14: weg=bilanz + fruehe Leder-Kette + Schmiede mit Markt-Eisen; Bilanz rechnet eigene Waffen gegen.
