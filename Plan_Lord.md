# Plan: Rotkaeppchens Lord toeten (Stand 05.10.2026, 21:35)

Anlass: Daniel 21:30 - "du hast komplett die Kontrolle verloren ... maximal unorganisiert". Zwischen 20:30 und 21:30
neun Aenderungen hintereinander, jeder Fehler erst in einer ganzen Partie gefunden, fast jede Serie mit anderem Code.
Ab jetzt gilt dieser Plan; gebaut wird erst nach Daniels Ja, und dann nur Schritt fuer Schritt.

## Ziel
Die Liga-Partie gegen Rotkaeppchen gewinnen: ihren Lord toeten, ohne unseren zu verlieren.

## Arbeitsweise (gilt fuer jeden Schritt)
1. **Eine Aenderung je Schritt.** Vorher aufgeschrieben: was sie bewirken soll und woran man es misst.
2. **Erst die Attrappe:** Pruefung ohne Spiel (`werkzeug/*_pruefen.py`), gruen - und gegen den alten Stand rot.
3. **Dann eine Serie:** 3 Laeufe, Tempo 200, Instanz 1, eine Code-Kennung fuer alle drei (serie.py bricht sonst ab).
4. **Abnahme gegen das vorher festgelegte Kriterium**, verglichen mit der Basis. Kein Flicken waehrend einer Serie.
5. **Bericht an Daniel nach jedem Schritt**, dann der naechste.

## Ist-Stand (gemessen)
| Bereich | Stand | Beleg |
|---|---|---|
| Wirtschaft | Verkaufsgold 7.935-8.360, erste Mine ~Tick 6.000, Steinhaufen am Ende <= 7 | Serie p (3 Laeufe, Kennung d370a5dd) |
| Takt | Tempo 200: ~87 Lenker-Runden je 1.000 Ticks (Tempo 1000: ~25) | Serien t, o |
| Lord, 5er-Wellen | einmal Lord auf 54.900 (-63 %), danach eigene Niederlage bei Tick 20.990 | Serie t2 |
| Lord, 20er-Wellen | in o und p nie gestartet (Ankunftskreis zu klein, Wegtest auf das Lord-Feld) - beides behoben; q1: 1 Welle, Lord unberuehrt, 4 Verluste - WARUM ist unbekannt | Serien o, p, q1 |
| Sammelpunkt | faellt bis an unseren Bergfried zurueck (6-10 Sperren je Partie) | Serie p |
| Verteidigung | eigener Lord ungeschuetzt (t2 verloren); Rotkaeppchens Leute greifen an unserem Bergfried an | Serien t, p |

## Schritte in dieser Reihenfolge
**S0 - Basis festschreiben.** Code-Stand a393bc8a (q1) wird Basis. Keine Aenderung.

**S1 - Sehen, was eine Welle tut (nur Messung, kein Verhalten aendern).** Je Welle und Runde mitschreiben: wie viele
leben, mittlerer Abstand zum Lord, wer greift wen an, wo stirbt wer. Abnahme: fuer jede Welle in 3 Laeufen ist
beantwortet, ob sie den Lord erreicht, und wenn nein, woran sie scheitert (Weg, Bogenschuetzen, Nahkaempfer, Mauer).

**S2 - Die eine Ursache aus S1 beheben, die die meisten Wellen stoppt.** Was genau, entscheidet die Messung aus S1 -
nicht vorher raten. Abnahme: Lord-Schaden je Welle im Mittel ueber 3 Laeufe deutlich ueber der Basis (Zahl lege ich
nach S1 fest, bevor gebaut wird).

**S3 - Eigenen Lord schuetzen**, wenn Rotkaeppchens Grossangriff kommt. Abnahme: 0 Niederlagen in 3 Laeufen.

**S4 - Sammelpunkt stabil vor unserer Burg** (nicht am Bergfried). Erst wenn S2 zeigt, dass der Ort zaehlt.

**Spaeter (Backlog, nicht jetzt):** wirksames Minimum je Welle lernen; Holzfaeller naeher (bis 70 Felder verstreut);
mehr Eisen; Moerderloecher, Feuer, Hunde, Bevoelkerung als Messgroessen.

## Was ausdruecklich NICHT passiert
- keine zweite Aenderung, bevor die erste abgenommen ist
- keine Serie mit gemischtem Code
- keine neuen Baustellen (Wirtschaft, Instanzen, Werkzeuge), bis S1-S3 stehen
