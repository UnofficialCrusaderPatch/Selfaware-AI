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
