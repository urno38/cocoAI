from pathlib import Path
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

# convert to image using resolution 600 dpi
pages = convert_from_path(Path.cwd() / "data/CSV_2022_p1.pdf", 600)

# extract text
text_data = ""
for page in pages:
    text = pytesseract.image_to_string(page)
    text_data += text + "\n"

with open("output.txt", "w", encoding="utf8") as f:
    f.write(text_data)


# convert to image using resolution 600 dpi
pages = convert_from_path(Path.cwd() / "data/CSV_2022.pdf", 600)

# extract text
text_data = ""
for i, page in enumerate(pages):
    text = pytesseract.image_to_string(page)
    print(i)
    text_data += text + "\n"
    with open(f"output_page{i}.txt", "w", encoding="utf8") as f:
        f.write(text_data)
