import collections.abc  # for high Python3 version
from pptx import Presentation

from htutil import file
from pathlib import Path


def get_notes(file_pptx: Path) -> list[str]:
    ppt = Presentation(str(file_pptx.absolute()))

    notes = []

    for slide in ppt.slides:
        textNote = slide.notes_slide.notes_text_frame.text
        notes.append(textNote)

    return notes