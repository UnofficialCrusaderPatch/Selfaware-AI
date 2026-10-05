# Backlog Selfaware-AI

Eine Stelle fuer alles Offene (Daniel 05.10.2026 19:14: "schreib dir das in den Backlog und picke dann daraus immer das
passende"). Vor jedem neuen Schritt hier den passenden Punkt waehlen; Erledigtes wird abgehakt und bleibt stehen.
Herkunft je Punkt in Klammern. Einzelheiten und Messwerte stehen in `Meilensteine.md`.

Lernstufen je Sache (Daniel 05.10. 19:18) - ein Prozess, kein Schritt ist fest, aber jeder muss irgendwann beantwortet
werden (und viele weitere Fragen): **1.** bauen koennen - **2.** es wirksam machen - **3.** wissen, warum man es NICHT
bauen muss - **4.** wissen, warum und WANN man es bauen sollte - **5.** selbstaendig situativ auf kreative Loesungen kommen.

## Jetzt dran
- [x] **Ertrags-Planer** (Daniel 19:11/19:14; Stand 4 seit 05.10. 20:10, M21): erst Messpartie (Ertrag je Gebaeude je 1.000 Ticks, Verkaufspreis Stein/Eisen, Weglaenge), dann jede Runde die Aktion mit der schnellsten Amortisation bauen, ohne feste Stueckzahlen; Umgebung bestimmt alles. Stein und Eisen vermutlich vorne.
- [x] **Planer lernt im Spiel** (Befund 9t; erledigt 05.10. 20:10, M21): Ertrag je Gebaeudeart aus dem laufenden Spiel messen (Bestand + Verkauf + Verbrauch je Ware, geteilt durch Zahl der Betriebe) und die Startwerte ersetzen - dann hoert er von selbst auf, Jaegerhuetten zu bauen, die nichts bringen.
- [x] **Zeithorizont fuer Investitionen** (Befund 9t; erledigt 05.10. 20:10: Gewinn bis Partieende, M21): nur bauen, was sich innerhalb des Horizonts bezahlt macht; sonst geht das Gold in Truppen.
- [x] Apfelplantage und Holzfaeller ueber Platzkarten statt Raster/Baumliste (erledigt 05.10. 20:10, Karten ueber die ganze Karte) (Befund 9t: 0 Apfelplantagen, Baum-Ziel 6-mal bebaut)
- [ ] Wegformel je Art aus den Messdaten statt vermutet (M21: Holz haengt kaum am Weg, Jaeger unklar)
- [x] Mehrere Laeufe je Planer-Stand (erledigt 05.10. 20:22: `serie.py`, Serie x 8 Laeufe, M22)
- [ ] Startwerte aus frueheren Partien (`daten/ertrag_gelernt_*.json`) - erster Schritt zum Selbstlernen
- [ ] Horizont in echten Partien ohne festes Ende (bis zum geplanten Angriff?) - Daniel fragen

## Wirtschaft
- [ ] Holzfaeller: 3 je Baum, Clusterung; Holzfaeller/Lager live umsetzen (04.10.)
- [x] Apfel-Seasoning (05.10., `wirtschaft.py`; untaetig 40 % -> 11-35 %)
- [ ] Ochsenjoche am Steinbruch, wenn das Abtragen zu langsam ist - vorausschauend (05.10. 00:26)
- [ ] Wirtschaft erweitern: Stein, Eisen, Pech bis zum Maximum (05.10. 00:26, 19:05, 19:11)
- [ ] Wirtschaft nachbauen: Holzfaeller, Apfelplantagen, Haeuser (05.10. 19:06)
- [ ] Waffenproduktion, Bier (05.10. 19:06), Brot, Religion, Essensvielfalt (04.10. 23:25, 05.10. 00:26)
- [ ] Angstfaktor positiv/negativ (05.10. 00:26)
- [ ] Jagd an Rehen (05.10. 19:05) - erste Regel steht, geht im Ertrags-Planer auf
- [ ] Steuern nach Beliebtheit (05.10. 00:26) - erste Regel steht, geht im Ertrags-Planer auf
- [x] Nahrung auf Kante verkaufen (05.10. 18:51)
- [x] Lager erst beim ersten Lieferwunsch, altes Lager dann weg (04.10., 05.10. 19:09)
- [ ] Lager rechtzeitig erweitern - vorausschauend nach Ladung unterwegs (04.10.)
- [x] Start mit 0 Gold wie in der Liga (05.10. 00:55, M19)
- [x] Nie blind starten: Bergfried aus dem Spiel, Plan je Start, nur eigene Seite (05.10. 18:55)

## Kampf
- [ ] Wirksames Minimum je Lord-Welle aus den Wellen-Daten lernen (Groesse, Fern/Nah am Lord, Schaden, Verluste) - Daniel 21:05
- [ ] Weitere Parameter messen: Moerderloecher, Feuer, Hunde, Bevoelkerung im Weg (Daniel 21:05)
- [ ] Eigenen Lord schuetzen, wenn Rotkaeppchens Grossangriff kommt (Serie t2: Niederlage bei Tick 20.990)
- [ ] Mehr Eisen: erste Mine wieder frueher (mit Startwerten aus Partien rueckte sie auf Tick ~8.000)
- [ ] **Lord-Trupp bildet sich nie** (M22: 0 Pruefungen in 8 Laeufen): erst messen, wie viele frei sind vs. noetig; dann Assassinen sammeln statt sofort verteilen (Daniel 05.10. 00:26: "Angriffsarmeen sammeln")
- [x] Lord-Trupp nach Daniels Regel (05.10. 00:52, M18)
- [ ] Zugebauten Lord freilegen (05.10. 00:52) - Wegtest steht, Freilegen fehlt
- [ ] Sinnvoller angreifen, Angriffsarmeen sammeln (05.10. 00:26)
- [x] Zielwahl nach Wert: Ausbildungslager, Steinbrueche, Haeuser vor Apfelplantagen (05.10. 19:05)
- [ ] Einheiten besser optimieren (05.10. 00:26)
- [ ] Mauern bauen, Lord schuetzen (05.10. 00:26)
- [ ] Sammelpunkt des Soeldnerlagers (Spielbefehl 71) (04.10.)
- [ ] Echtzeit ab Tempo 40 und hoeher (04.10. 21:54)

## Spaeter
- [ ] **Echtes Selbstlernen** ueber tausende Partien statt Codeaenderungen (05.10. 00:57)
- [ ] **Challenges** (05.10. 19:14): kein Markt; keine arabischen Einheiten; schnellste Kathedrale; schnellster Kill; weitere nach Daniels Wahl
