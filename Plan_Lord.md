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

**Aenderung 21:34 (Daniel): "warum jetzt ploetzlich in Wellen? ... du raidest eh schon mit Assassinen, dann wartest du,
bis du eine kritische Menge auf dem kompletten Feld hast, und alle greifen dann gleichzeitig den Lord an."** Sammelpunkt,
Wellen und Rueckzug-Mikro (meine Konstruktion) fallen weg. Neu: raiden wie bisher; sobald 20 Assassinen leben (Daniel
21:05: "lieber 20 auf einmal"), greifen ALLE mit einem Befehl den Lord an; sind davon weniger als 3 uebrig, wieder raiden
bis 20. Die S1-Messung haengt an diesem Angriff. Abnahme: Attrappe (19 -> kein Angriff, 20 verstreute -> ein Befehl mit
allen 20, Raids nehmen keine Angreifer, Ende bei < 3) gruen und gegen den alten Stand rot; Serie mit 3 Laeufen beantwortet
je Angriff: wie viele kamen am Lord an, wann, was hielt die anderen auf, Lord-Schaden.

S1 ausgefuehrt ab 05.10. 21:33 (Daniel: "ja, fang mit S1 an"). Vorher festgelegt:
- Neu: `assassinen.py` schreibt je Welle und Runde eine Zeile nach `daten/wellen_live_<zeit>_i<inst>.jsonl` (leben,
  Abstand zum Lord mittel/kleinster, greifen Lord an, greifen anderes an + Typ, ohne Ziel, Feinde fern/nah um die Welle,
  Lord-Leben). `werkzeug/wellen_auswerten.py` macht daraus je Welle eine Zeile.
- Gegenprobe kein neues Verhalten: Attrappe gibt mit und ohne Protokoll dieselben Befehle aus.
- Abnahme S1: fuer jede Welle in 3 Laeufen steht da, ob sie den Lord erreicht (jemand <= 3 Felder und greift ihn an),
  und sonst die Ursache: kein Weg (Abstand faellt nicht) / abgefangen (Ziel ist ein anderer Feind) / unterwegs
  gestorben / angekommen ohne Schaden.

**S1 ERGEBNIS (Serie a, 3 Laeufe, Kennung 39acda39, 05.10. 21:45):** 5 Angriffe zu je 20. Wegstrecke beim Befehl
12-91 Felder -> sie kommen einzeln an: am Lord gleichzeitig hoechstens 0-2 von 20; Verluste je Angriff 14-17; Lord-Schaden
nur in a2 (150.000 -> 106.300, -29 %), sonst 0. Ursache = **gleichzeitig befohlen ist nicht gleichzeitig angekommen.**
Daniel 21:46 (Bild): Assassinen nehmen nicht das naechste Ziel, sondern folgen "stupide" den anderen; die Wirtschaft
haette man viel frueher abreissen und dann gezielt auf den Lord gehen koennen.

**Daniel 21:46-21:47 (Bilder), woertlich zusammengefasst:**
- "Assassinen bleiben nach dem Auftrag auf den Lord einfach vor den Mauern stehen - das ist falsch, sie sollten aktiv
  versuchen, weiter den Lord zu killen." "Jeder Tick, wo sie rumstehen, ist eine Sekunde mehr, wo der Gegner Einheiten
  rekrutieren kann - und wo gegnerische Einheiten auf unsere schiessen koennen."
- "Es sieht immer noch so aus, als wuerdest du Holz verkaufen, anstatt Eisenminen oder Steinbrueche zu bauen."
  (gemessen frueher: ~90-100 Holz-Lose je Partie verkauft = rund 2.000 Holz)
- Assassinen nehmen nicht das naechste Ziel, sondern folgen anderen; Wirtschaft frueher abreissen, dann gezielt Lord.

**Neue Reihenfolge (je ein Schritt, Pruefung ohne Spiel, Serie, Abnahme - wie oben):**
- **S2a Nie rumstehen beim Lord-Angriff:** wer im Angriff nicht den Lord angreift (steht, laeuft nicht), bekommt den
  Befehl JEDE Runde neu; bleibt er vor einer Mauer haengen -> messen, wie Assassinen hineinkommen (Haken/Mauer
  erklettern), dann diesen Weg nehmen. Abnahme: kein Angreifer laenger als 2 Runden ohne Ziel/Bewegung.
- **S2b Holz investieren statt verkaufen:** messen, warum der Planer bei Holzueberschuss nicht baut (keine Plaetze?
  Arbeiter? Horizont? Stein?), dann die Ursache beheben. Abnahme: Holz-Verkauf deutlich unter Basis, mehr Steinbrueche/Minen.
- **S2c Gleichzeitig ankommen:** Treffpunkt kurz vor dem Lord ausser Schussweite, dann gemeinsam (S1: Weg 12-91 Felder,
  am Lord hoechstens 2 von 20).
- **S2d Raiden: naechstes Ziel, Wirtschaft zuerst** (nicht anderen folgen).

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
