import gc
import os
import sys
import shutil
import sqlite3
import tempfile
import unittest
from datetime import datetime

# Projektwurzel in den Suchpfad aufnehmen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_parser import DataParser
from agents.database_writer import DatabaseWriter


# ---------------------------------------------------------------------------
# DataParser
# ---------------------------------------------------------------------------

class TestDataParser(unittest.TestCase):

    def setUp(self):
        self.parser = DataParser()

    def test_parse_items_und_preise(self):
        raw = "Apfel 1,99 €\nBrot 2,49 €\nMilch 0,89 €\n28.06.2026"
        result = self.parser.process(raw)
        items = result["parsed_data"]
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["artikel"], "Apfel")
        self.assertAlmostEqual(items[0]["preis"], 1.99)
        self.assertEqual(items[1]["artikel"], "Brot")
        self.assertAlmostEqual(items[1]["preis"], 2.49)

    def test_datum_wird_erkannt(self):
        raw = "Kaffee 4,99 €\n15.03.2025"
        result = self.parser.process(raw)
        self.assertEqual(result["datum"], "15.03.2025")

    def test_datum_fallback_auf_heute(self):
        raw = "Kaffee 4,99 €"
        result = self.parser.process(raw)
        self.assertEqual(result["datum"], datetime.now().strftime("%d.%m.%Y"))

    def test_leerer_text(self):
        result = self.parser.process("")
        self.assertEqual(result["parsed_data"], [])

    def test_kein_euro_zeichen_wird_ignoriert(self):
        raw = "Artikel ohne Preis\nApfel 1,99 €"
        result = self.parser.process(raw)
        self.assertEqual(len(result["parsed_data"]), 1)


# ---------------------------------------------------------------------------
# DatabaseWriter
# ---------------------------------------------------------------------------

class TestDatabaseWriter(unittest.TestCase):

    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(db_fd)
        self.writer = DatabaseWriter(db_path=self.db_path)

    def tearDown(self):
        self.writer = None
        gc.collect()  # SQLite-Handles auf Windows sofort freigeben
        os.unlink(self.db_path)

    def _dummy_data(self):
        return {
            "parsed_data": [
                {"artikel": "Apfel", "preis": 1.99},
                {"artikel": "Brot",  "preis": 2.49},
            ],
            "datum": "28.06.2026",
        }

    def test_eintraege_werden_gespeichert(self):
        result = self.writer.process(self._dummy_data())
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["items_inserted"], 2)

    def test_datenbank_enthaelt_korrekte_werte(self):
        self.writer.process(self._dummy_data())
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT artikel, preis, datum FROM einkauefe ORDER BY id"
            ).fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ("Apfel", 1.99, "28.06.2026"))
        self.assertEqual(rows[1], ("Brot",  2.49, "28.06.2026"))

    def test_leere_liste_fuegt_nichts_ein(self):
        result = self.writer.process({"parsed_data": [], "datum": "28.06.2026"})
        self.assertEqual(result["items_inserted"], 0)
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM einkauefe").fetchone()[0]
        self.assertEqual(count, 0)

    def test_mehrfaches_einfuegen_akkumuliert(self):
        self.writer.process(self._dummy_data())
        self.writer.process(self._dummy_data())
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM einkauefe").fetchone()[0]
        self.assertEqual(count, 4)


# ---------------------------------------------------------------------------
# End-to-End  (nur wenn Tesseract installiert ist)
# ---------------------------------------------------------------------------

def _tesseract_available():
    return bool(shutil.which("tesseract")) or os.path.isfile(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

@unittest.skipUnless(_tesseract_available(), "Tesseract nicht installiert – E2E wird übersprungen")
class TestEndToEnd(unittest.TestCase):

    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(db_fd)
        img_fd, self.img_path = tempfile.mkstemp(suffix=".jpg")
        os.close(img_fd)
        from tests.create_test_image import create_test_receipt
        create_test_receipt(self.img_path)

    def tearDown(self):
        gc.collect()
        os.unlink(self.db_path)
        os.unlink(self.img_path)

    def test_voller_pipeline_durchlauf(self):
        from agents.ocr_scanner import OCRScanner

        # Schritt 1: OCR
        ocr_result = OCRScanner().process(self.img_path)
        self.assertIn("raw_text", ocr_result)
        self.assertGreater(len(ocr_result["raw_text"]), 0)

        # Schritt 2: Parsen
        parsed = DataParser().process(ocr_result["raw_text"])
        self.assertIn("parsed_data", parsed)
        self.assertIn("datum", parsed)

        # Schritt 3: Datenbank
        result = DatabaseWriter(db_path=self.db_path).process(parsed)
        self.assertEqual(result["status"], "success")

        # Prüfen: mindestens ein Artikel in der DB
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM einkauefe").fetchall()
        self.assertGreater(len(rows), 0)
        print(f"\nE2E: {len(rows)} Artikel gespeichert → {rows}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
