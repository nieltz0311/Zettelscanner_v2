# Zettelscanner v2

OCR-Pipeline zum automatischen Erfassen von Kassenzetteln: Foto → strukturierte Daten → SQLite-Datenbank.

## Architektur

```
Kassenzettel-Foto
       │
       ▼
 OCRScanner          ← Tesseract OCR (deu+eng)
       │ raw_text
       ▼
 DataParser          ← Regex: Artikel, Preis, Datum
       │ parsed_data
       ▼
 DatabaseWriter      ← SQLite (kassenzettel.db)
```

Die drei Agenten sind in `workflow.yaml` als OpenClaw-Pipeline definiert und laufen sequenziell.

## Installation

### Voraussetzungen

- Python 3.11+
- [Tesseract OCR 5.x](https://github.com/UB-Mannheim/tesseract/wiki) mit Deutschem Sprachpaket (`deu`)

### Setup

```bash
# 1. venv erstellen und aktivieren
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
source .venv/bin/activate          # Linux/Mac

# 2. Abhängigkeiten installieren
pip install -r requirements.txt
```

## Tests ausführen

```bash
python -m pytest tests/ -v
```

| Testklasse | Beschreibung |
|---|---|
| `TestDataParser` | Unit-Tests für Regex-Parsing (Artikel, Preis, Datum, Fallbacks) |
| `TestDatabaseWriter` | Unit-Tests für SQLite-Schreiboperationen |
| `TestEndToEnd` | Vollständige Pipeline mit synthetischem Testbild (benötigt Tesseract) |

## Projektstruktur

```
Zettelscanner_v2/
├── agents/
│   ├── ocr_scanner.py        # OCR-Agent (plattformunabhängig)
│   ├── data_parser.py        # Parsing-Agent
│   └── database_writer.py    # Datenbank-Agent
├── tests/
│   ├── create_test_image.py  # Synthetisches Testbild mit Pillow
│   └── test_workflow.py      # Test-Suite (10 Tests)
├── workflow.yaml             # OpenClaw-Pipeline-Konfiguration
├── requirements.txt
└── CLAUDE.md                 # Kontext für Claude Code
```

## Abhängigkeiten

| Paket | Version | Zweck |
|---|---|---|
| pytesseract | 0.3.10 | Tesseract-Python-Binding |
| opencv-python | 4.8.0.76 | Bildvorverarbeitung |
| numpy | 1.24.3 | Array-Operationen |
| pillow | 10.0.0 | Testbild-Generierung |
