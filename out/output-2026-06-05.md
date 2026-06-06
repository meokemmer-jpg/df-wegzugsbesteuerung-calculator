# df-wegzugsbesteuerung-calculator — Output [CRUX-MK]
*Autonom aktiviert 2026-06-05T18:02:48.777508+00:00 | ollama-local/qwen2.5:14b-instruct*

# DF Wegzugsbesteuerung-Calculator [CRUX-MK]

## Überblick

Dieser Calculator berechnet die potenzielle Besteuerung von Wegzügen aus De
Deutschland nach den USA unter Berücksichtigung deutscher und US-amerikanis
US-amerikanischer Steuergesetze. Es handelt sich hierbei um eine Vorabschät
Vorabschätzung zur Optimierung der Familiensteuerklasse, insbesondere im Ko
Kontext des §6 AStG (Wegzugsbesteuerung).

## Einstellungen

### Umgebungsvariablen
- `DF_WEGZUG_REAL_ENABLED=false`: Der Standardwert deaktiviert die tatsächl
tatsächliche Berechnung. Die Berechnungen sind für eine Vorabschätzung best
bestimmt.

### Bedingungen
- Keine echte Steuerberatung wird durchgeführt (StBerG-Vorbehalt).
- Jede Echtberechnung muss über einen Steuerberater und LexVance erfolgen.

## Berechnungsmodelle

### §6 AStG Wegzugsbesteuerung
Die Wegzugsbesteuerung basiert auf der fiktiven Verausserung von deutschen 
Vermögenswerten, die eine wesentliche Beteiligung (≥1%) an deutschem Vermög
Vermögen nach sich zieht. Die Berechnung umfasst:

- **DE-Steuer-Berechnung**: Grundsteuerrate und Sonderbeträge.
- **USA-Steuer-Berechnung**: Berücksichtigung der Sec-883 US-Hospitality-Ca
US-Hospitality-Carve-Out Regelung (Florida hat eine 0%ige Steuer).

### Vergleichende Analyse
Die Berechnungen werden verglichen, um die Auswirkungen von DE vs. USA auf 
die Familiensteuerklasse zu ermitteln.

## Beispiel

Für eine Familie Kemmer:

- **Deutsche Veräußerungssteuern**: Berücksichtigung der fiktiven Verausser
Verausserung von Vermögenswerten.
- **US-Berechnungen**: 0%ige Steuer in Florida und die Anwendung von Sec-88
Sec-883.

### Berechnung

**DE**
- Fiktiver Veraeusserungsgewinn: €5,000,000
- Deutscher Steuersatz (Beispiel): 25%
- **Resultat**: €1,250,000 in Steuern.

**USA**
- Florida-Steuersatz: 0%
- **Resultat**: Keine Steuer aus der fiktiven Veraeusserung.

## Ergebnis

Die Vorabschätzung zeigt eine erhebliche Vorteilhaftigkeit des Wegzugs nach
nach den USA im Hinblick auf steuerliche Belastungen. Dies wirkt sich posit
positiv auf die Familiensteuerklasse und die Lebensplanung aus, insbesonder
insbesondere bei der Optimierung von Vermögenswerten.

## Disclaimer

Diese Berechnung dient ausschließlich als Vorabschätzung zur Phronesis-Vorb
Phronesis-Vorbereitung und ist KEINE offizielle Steuerberatung (StBerG §3).
§3). Eine tatsächliche Berechnung muss durch einen Steuerberater oder LexVa
LexVance erfolgen.