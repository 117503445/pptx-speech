import fitz
from pathlib import Path

def save_images(file_pdf: Path, dir_output: Path):
    doc = fitz.open(str(file_pdf.absolute())) # type: ignore
    for page in doc:
        pix = page.get_pixmap(dpi=72*5)
        pix.save(dir_output / f"{page.number}.png")