# Datenvertrag — ZEW DP 26-021

Formalisierung des in `implementation_plan.md` (Teil H) definierten Datenvertrags.

## Pflichtdateien
- `scenarios_eu.csv` — EU-Szenarienkennzahlen
- `signal.csv` — effektiver Signal-Anteil λ

## Optionale Dateien (steuern erweiterte Features)
- `prices_eu.csv` — Preisänderungen in % ggü. Baseline
- `scenarios_us.csv` — US-Szenarien

## Format-Vorgaben
- Spaltennamen exakt wie unten (sie sind die API zwischen Daten und Vorlage).
- **UTF-8 ohne BOM**, Punkt als Dezimaltrenner, keine Tausendertrennzeichen.
- Fehlende Werte = leer (nicht 0).

## Spalten
- `scenarios_eu.csv`: `scenario`, `global_emissions_pct`, `leakage_pct`, `welfare_bn`,
  `out_flat_pct`, `out_long_pct`, `out_macro_pct`, `carbon_price`
- `prices_eu.csv`: `scenario`, `import_flat_pct`, `import_long_pct`, `user_flat_pct`,
  `user_long_pct`, `cpi_pct`
- `signal.csv`: `label`, `setting`, `design`, `lambda`
- `scenarios_us.csv`: `scenario`, `global_emissions_pct`, `reverse_leakage_pct`,
  `welfare_bn`, `out_flat_pct`, `out_long_pct`, `out_macro_pct`, `carbon_price`
