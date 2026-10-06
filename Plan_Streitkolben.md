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
