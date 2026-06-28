from PIL import Image, ImageDraw, ImageFont
import os
import sys

RECEIPT_LINES = [
    "SUPERMARKT TEST GMBH",
    "Musterstrasse 1, 12345 Berlin",
    "",
    "28.06.2026          10:42 Uhr",
    "",
    "Apfel                1,99 €",
    "Brot                 2,49 €",
    "Milch                0,89 €",
    "Kaffee               4,99 €",
    "",
    "------------------------",
    "Gesamt              10,36 €",
    "",
    "Vielen Dank fuer Ihren Einkauf!",
]

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "cour.ttf",                              # Courier New (Windows)
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def create_test_receipt(output_path: str = None) -> str:
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "kassenzettel_test.jpg",
        )

    font_size = 28
    font = _load_font(font_size)
    line_height = font_size + 10
    padding = 40

    width = 600
    height = padding * 2 + line_height * len(RECEIPT_LINES)

    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    y = padding
    for line in RECEIPT_LINES:
        draw.text((padding, y), line, fill="black", font=font)
        y += line_height

    img.save(output_path, quality=95)
    print(f"Testbild gespeichert: {output_path}")
    return output_path


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    create_test_receipt(path)
