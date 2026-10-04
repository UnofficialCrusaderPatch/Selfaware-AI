# Spielwissen - Notizzettel fuer die Selfaware-KI

Daniels Tipps (Quelle in Klammern) und spaeter das, was die KI selbst als wirksam gemessen hat.
Jede Zeile ist eine Regel, die die KI pruefen und gewichten soll - nichts davon ist "bewiesen",
bis eine Messung es bestaetigt (Marke dahinter).

## Ziel
- Gegen das Rotkaeppchen gewinnen, unsere KI auf dem Menschenplatz (Daniel, 04.10.2026).

## Regeln fuer unsere KI als Spieler (Daniel, 04.10.2026, 19:56)
- Keine kostenlosen Mauern - Mauern und alle Gebaeude kosten wie beim Menschen. Gebaut wird nur ueber den Spielbefehl (mit Kostenpruefung des Spiels), nie durch direktes Schreiben von Rohstoffen oder Bauten.
- Handel: die KI darf beliebig viel von einer Ware auf einmal kaufen oder verkaufen (Menschen nur in Schritten von mindestens 5) - zum Marktpreis, ueber den Marktplatz.
- Keine anderen Schummeleien (Gold/Waren setzen, Leben aendern, Einheiten wandeln) im echten Spiel - diese Befehle bleiben Werkzeuge fuer Tests und Trainingslagen.

## Geld
- Immer wissen: wie viel Gold da ist, was hereinkommt, was jede Sache kostet. Passend sparen, genau ausgeben. (Daniel 04.10.)
- Moeglichst viel Geld in Wirtschaft stecken - sie hat den hoechsten Hebel auf Geld und damit Waffen und Truppen. (Daniel 04.10.)
- Beliebtheit erlaubt Steuern = Geld. Rohstoffe verkaufen bringt ebenfalls Geld. (Daniel 04.10.)
- Kosten kommen aus der Balance (Team-Liga): Baukosten int[110][5] (Holz, Stein, Eisen, Pech, Gold) im Spiel bei 0x01124CF4, Index = Gebaeudetyp (VillageStudio lib/kosten.json). (abgelesen)

## Beliebtheit und Essen
- **Beliebtheit ist das Wichtigste.** Unter 95 sinkt die Rate, mit der neue Bauern kommen; bei 50 kommen fast keine mehr; unter 50 gehen Leute AUS dem Dorf. (Daniel 04.10., 19:57)
- Kornspeicher nicht vergessen. (Daniel 04.10., 19:57)
  - Gemessen 04.10.: Ohne Kornspeicher kann man kein Essen kaufen (Kauf braucht Lagerplatz). Kornspeicher (5 Holz) + 50 Aepfel gekauft (~8 Gold je Apfel) -> Beliebtheit 93,25 -> ueber 95 nach ~600 Ticks, 100 nach ~1500 Ticks. **Essen kaufen ist der schnellste Hebel auf die Beliebtheit am Anfang.**
- Kornspeicher haelt das Essen und ist damit sehr wichtig fuer die Beliebtheit. (Daniel 04.10.)
- Beliebtheit vor allem ueber Bier. (Daniel 04.10.)
- Essen anfangs ueber Aepfel. Jagd nur, wenn Wild (Rehe) da ist - erkennen, sonst kein Holz fuer eine Jaegerhuette ausgeben. Jaeger etwa einen Kathedralenabstand vom Wild. (Daniel 04.10.)
  - Erkennbar: Rehe sind Einheitentyp 44 (UT_ANTELOPESHDEER), Besitzer 0. (gemessen 04.10.: 134 bzw. 200 auf Grumpy)

## Bauen
- Moeglichst nah am Vorratslager bauen. (Daniel 04.10.)
- Ausnahmen, deren Arbeiter erst zur Produktion laufen: Holzfaeller mit dem Eingang direkt neben einem Baum (sie holen erst drei Holzscheite); Ochsenjoche direkt neben den Steinbruch (der Ochse bringt dann 12 Stein zum Lager). (Daniel 04.10.)
- **Gebaeude lassen sich nicht drehen** (keine Ausnahme). Den Ausgang/Eingang kann man nur indirekt lenken: den ueblichen Platz zustellen oder dort bauen, wo etwas anderes ihn blockiert - z. B. beim Steinbruch, wohin der Ochse den Stein bringt; jede Produktion (Baecker usw.) laesst sich ueber Nachbargebaeude/Gelaende am Eingang beeinflussen - aber nur fein abgestimmt. (Daniel 04.10., 20:04)
- Abreissen und naeher an Rohstoffen neu bauen (z. B. wenn das Holz in der Naehe weg ist) lohnt erst im Mittel-/Endspiel, dann aber richtig. (Daniel 04.10.)
- Logisch noetige Gebaeude fuer Truppen kennen (Kaserne, Waffenwerkstaetten, Waffenkammer). (Daniel 04.10.)

## Vorteil der KI
- Menschen koennen so schnell nicht handeln - eine perfekte KI ist damit effektiver. (Daniel 04.10.)
- Gemessen: Einheiten lesen ein neues Ziel nur an Feldgrenzen (Bogenschuetze alle 16 Ticks); Befehle schneller als ein Feld verpuffen. (M10.05, 04.10.)
- Gemessen: Die KI wirbt Verluste in ~100 Ticks je Einheit nach; holt zurueckgerufene Arbeiter nicht von selbst an die Arbeit (M10.03/M10.04).
