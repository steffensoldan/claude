# Projekt-Governance: [Projektname]

Dieses Dokument regelt Lifecycle, IP-Konformität, Risiken und Kostenkontrolle.

---

## 1. Exit-Plan & Stilllegung
* **Archivierungs-Bedingung:** [Wann gilt das Projekt als abgeschlossen/eingestellt?]
* **Datenlöschung / DSGVO:** [Welche Löschpflichten greifen? Wo liegen personenbezogene Daten und wie werden sie gelöscht?]
* **Infrastruktur-Abbau:** [Welche Cloud-Ressourcen oder VM-Volumes müssen gelöscht werden?]

## 2. IP & Lizenz-Audit
* **Dependency-Lizenzprüfung:** [Wurden Abhängigkeiten auf inkompatible Lizenzen (z. B. GPL in geschlossenen Tools) geprüft?]
* **Rechteklärung Output:** [Wem gehört der Code/Output? Ist ein Open-Sourcing rechtlich freigegeben?]

## 3. Risiko-Bewertung
* **Top-Risiken:** [Welche zentralen Risiken existieren (Sicherheitslecks, Ausfall, Datenverlust)?]
* **Mitigation:** [Welche Gegenmaßnahmen sind implementiert?]
* **Restrisiko-Akzeptanz:** [Welche verbleibenden Risiken werden vom Owner explizit akzeptiert?]

## 4. TCO (Laufende Betriebskosten) & Redundanz
* **Budget-Schätzung (fortlaufend):** [Monatliche API-Token-Kosten, Hosting- oder Speichergebühren.]
* **Redundanzregelung (Bus-Faktor):** [Wer übernimmt die Wartung bei Ausfall des Maintainers? Wo liegen Dokumentationen?]

## 5. Wirkung & Barrierefreiheit
* **Erfolgs- & Wirkungskriterien:** [Woran wird der Nutzen/Wert des Projekts gemessen (nicht nur technische Fertigstellung)?]
* **Barrierefreiheit (BITV/WCAG):** [Zutreffend? Wenn ja, wie wird die Konformität sichergestellt und getestet?]
