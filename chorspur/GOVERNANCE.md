# Projekt-Governance: Chorspur

Dieses Dokument regelt Lifecycle, IP-Konformität, Risiken und Kostenkontrolle.

---

## 1. Exit-Plan & Stilllegung
* **Archivierungs-Bedingung:** Steffen erklärt das Projekt für beendet, oder es bleibt 12 Monate ungenutzt (Vorschlag, nicht beschlossen).
* **Datenlöschung / DSGVO:**
  * Die App verarbeitet Audio und Noten ausschließlich im Browser. Es gibt keinen Server, keinen Upload und kein Konto.
  * Aufnahmen existieren nur im Arbeitsspeicher und in Dateien, die die Nutzerin oder der Nutzer selbst herunterlädt (Mix-WAV, Projekt-ZIP). Löschen erfolgt dort auf dem Gerät.
  * `localStorage` enthält nur zwei Einstellungen (`chorspur.count`, `chorspur.ref`), keine personenbezogenen Daten.
  * Externe Abrufe beim Seitenaufruf: Google Fonts (IP-Adresse wird an Google übertragen), raw.githack.com bzw. GitHub (Seite selbst); beim Laden von Noten zusätzlich cdn.jsdelivr.net. Rechtliche Bewertung für eine Nutzung im ZEW-Kontext: **offen**.
* **Infrastruktur-Abbau:** keine eigene Infrastruktur. Stilllegung = Branch `claude/chorspur-aufnahme` und Ordner `chorspur/` löschen bzw. archivieren. GitHub Pages ist nicht aktiv.

## 2. IP & Lizenz-Audit
* **Dependency-Lizenzprüfung:**
  * OpenSheetMusicDisplay 1.9.9: BSD-3-Clause (laut `package.json` des npm-Pakets) – mit jeder Projektlizenz vereinbar.
  * Schriften Bricolage Grotesque, IBM Plex: SIL Open Font License (Stand der Kenntnis, nicht erneut geprüft).
  * Keine weiteren Abhängigkeiten. Testwerkzeuge (Playwright, Apache-2.0) werden nicht ausgeliefert.
* **Rechteklärung Output:**
  * Code: erstellt mit Claude Code im Auftrag von Steffen; Projektlizenz **nicht festgelegt**. Das Repository ist **öffentlich** – der Code ist damit einsehbar, aber ohne Lizenz nicht zur Weiterverwendung freigegeben.
  * Noten: „Alle meine Entchen“ ist ein gemeinfreies Volkslied; der Unterstimmensatz und „Na-na-Vamp“ sind eigene, einfache Sätze.
  * Eine Abschrift von *Hey Jude* (Lennon/McCartney, urheberrechtlich geschützt) wurde bewusst **nicht** erstellt.
  * Nutzer sollten nur Notendateien laden, an denen sie die Rechte haben. Geladene Noten werden nur lokal und in selbst gespeicherten Projektdateien abgelegt.
  * Hinweis ZEW: Vor einer Nutzung im dienstlichen Kontext oder einer Veröffentlichung unter ZEW-Bezug Freigabe klären (laut Auftrag gewünscht; noch **offen**).

## 3. Risiko-Bewertung
* **Top-Risiken:**
  1. **Timing am echten Gerät:** Die Gerätelatenz (Kopfhörer, Bluetooth) wird nicht automatisch korrigiert, seit die Latenzeinstellung auf Wunsch entfernt wurde. Ohne Ausrichten liegen Aufnahmen zu spät; das summiert sich, wenn nach vorherigen Spuren gesungen wird.
  2. **iOS-Verhalten ungeprüft:** Stummschalter, Samplerate-Wechsel nach der Mikrofonfreigabe, Dateiauswahl für `.musicxml`/`.zip`, Wake Lock.
  3. **Datenverlust:** Aufnahmen gehen beim Schließen oder Neuladen der Seite verloren, wenn kein Projekt gespeichert wurde. iOS kann Hintergrund-Tabs beenden.
  4. **Abhängigkeit von Drittanbietern:** raw.githack.com (Auslieferung), cdn.jsdelivr.net (Notenanzeige). Fallen sie aus, ist die Seite bzw. die Notenanzeige nicht verfügbar.
  5. **Übersteuerung:** Clipping lässt sich im Nachhinein nicht beheben.
* **Mitigation:**
  * Funktion „Einsätze auf den Schlag ausrichten“ und „Start“ per Hand
  * Projekt speichern/öffnen
  * Übersteuerungswarnung live und nach der Aufnahme
  * Wake Lock
  * Datei-Import als Rückfall, falls das Mikrofon gesperrt ist
  * feste Bibliotheksversion
  * lokaler Betrieb über `http://localhost` möglich
* **Restrisiko-Akzeptanz:** Nicht ausdrücklich erklärt. Vorschlag: Risiken 1, 2 und 4 bis zum iPhone-Realtest akzeptieren und danach neu bewerten.

## 4. TCO (Laufende Betriebskosten) & Redundanz
* **Budget-Schätzung (fortlaufend):** 0 € (keine API, kein Hosting, keine Lizenzkosten). Entwicklungsaufwand fällt nur in Claude-Sessions an.
* **Redundanzregelung (Bus-Faktor):**
  * Maintainer ist nur Steffen.
  * Die App ist eine einzige Datei ohne Build. Jede Person mit Browser und Texteditor kann sie warten.
  * Kontext liegt in `PROJECT.md`, `walkthrough.md`, `task.md` und `TESTBERICHT.md`.
  * Die Tests in `test/` sind ohne weitere Infrastruktur reproduzierbar.

## 5. Wirkung & Barrierefreiheit
* **Erfolgs- & Wirkungskriterien:**
  * Eine Person kann am Handy mindestens zwei Chorstimmen nacheinander aufnehmen, sodass sie hörbar zusammenliegen (blinde Hörprobe, laut Auftrag).
  * Ein Projekt lässt sich speichern und an einem späteren Tag fortsetzen.
  * Beides ist bisher **nicht am Handy nachgewiesen**.
* **Barrierefreiheit (BITV/WCAG):** Eine formale Konformität ist nicht geprüft und nicht zugesichert. Umgesetzt:
  * Bedienelemente als echte Buttons und Selects mit Tastaturfokus und sichtbarem Fokusrahmen
  * `aria-label` an Canvas und Symbolknöpfen
  * Statusmeldungen mit `role="status"` bzw. `role="alert"`
  * Berührflächen mindestens 40–44 px
  * Hell- und Dunkelmodus

  Grenzen:
  * Notenanzeige und Wellenformen sind grafisch (für Screenreader nur eingeschränkt nutzbar).
  * Der Einzählrahmen blinkt bei 160 BPM mit höchstens 2,7 Hz und liegt damit unter der WCAG-Schwelle von 3 Blitzen pro Sekunde (rechnerisch, nicht gemessen).
