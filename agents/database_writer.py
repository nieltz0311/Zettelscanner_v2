import sqlite3
from typing import Dict, Any

class DatabaseWriter:
    def __init__(self, db_path: str = "kassenzettel.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Datenbank und Tabelle erstellen."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS einkauefe (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artikel TEXT NOT NULL,
                    preis REAL NOT NULL,
                    datum TEXT NOT NULL
                )
            """)

    def process(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Daten in die Datenbank speichern."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for item in parsed_data["parsed_data"]:
                cursor.execute(
                    "INSERT INTO einkauefe (artikel, preis, datum) VALUES (?, ?, ?)",
                    (item["artikel"], item["preis"], parsed_data["datum"])
                )
            conn.commit()
        return {"status": "success", "items_inserted": len(parsed_data["parsed_data"])}
