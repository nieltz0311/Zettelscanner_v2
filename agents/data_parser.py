import re
from typing import Dict, Any, List
from datetime import datetime

class DataParser:
    def __init__(self):
        self.item_pattern = re.compile(r"([A-Za-zäöüß\s\-]+)\s+([\d,]+\d{2})\s*€")
        self.date_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{4})")

    def process(self, raw_text: str) -> Dict[str, Any]:
        """Rohtext parsen und strukturierte Daten extrahieren."""
        items = []
        for match in self.item_pattern.finditer(raw_text):
            artikel = match.group(1).strip()
            preis = float(match.group(2).replace(",", "."))
            items.append({"artikel": artikel, "preis": preis})

        date_match = self.date_pattern.search(raw_text)
        datum = date_match.group(1) if date_match else datetime.now().strftime("%d.%m.%Y")

        return {
            "parsed_data": items,
            "datum": datum
        }
