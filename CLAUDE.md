# Zettelscanner v2

Kassenzettel-OCR-Pipeline: Bild → Text → strukturierte Daten → SQLite.

## Projektstruktur

```
Zettelscanner_v2/
├── agents/
│   ├── ocr_scanner.py      # Tesseract OCR (deu+eng), plattformunabhängig
│   ├── data_parser.py      # Regex-Extraktion: Artikel/Preis/Datum
│   └── database_writer.py  # SQLite-Persistenz (kassenzettel.db)
├── tests/
│   ├── create_test_image.py  # Generiert synthetisches Kassenzettel-JPG mit Pillow
│   └── test_workflow.py      # Unit-Tests + E2E-Test (10 Tests)
├── workflow.yaml             # OpenClaw-Pipeline-Definition
└── requirements.txt
```

## Umgebung

- Python 3.11, venv unter `.venv/`
- Tesseract 5.4.0 unter `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows)
- Sprachen: `deu`, `eng`

## Befehle

```bash
# venv aktivieren
.venv\Scripts\Activate.ps1

# Tests ausführen
.venv\Scripts\python.exe -m pytest tests/ -v

# Testbild generieren
.venv\Scripts\python.exe tests/create_test_image.py
```

## Agenten-API

Jeder Agent hat eine `process()`-Methode:

| Agent | Input | Output |
|---|---|---|
| `OCRScanner` | `image_path: str` | `{"raw_text": str}` |
| `DataParser` | `raw_text: str` | `{"parsed_data": list, "datum": str}` |
| `DatabaseWriter` | `parsed_data: dict` | `{"status": str, "items_inserted": int}` |

## Datenbankschema

```sql
CREATE TABLE einkauefe (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    artikel TEXT    NOT NULL,
    preis   REAL    NOT NULL,
    datum   TEXT    NOT NULL
);
```

## Bekannte Eigenheiten

- `DataParser` erwartet Euro-Zeichen (`€`) direkt nach dem Preis — Kassenzettels ohne `€` werden ignoriert
- Auf Windows hält SQLite Datei-Handles offen; Tests rufen `gc.collect()` im Teardown auf
- E2E-Test prüft Tesseract via absolutem Pfad (`C:\Program Files\Tesseract-OCR\tesseract.exe`) zusätzlich zu `shutil.which`
