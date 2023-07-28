from note import get_notes

from pathlib import Path
from htutil import file

dir_data = Path("data")

task_name = "example"

dir_input = dir_data / "input" / task_name
dir_output = dir_data / "output" / task_name
dir_output.mkdir(parents=True, exist_ok=True)

file_pptx = dir_input / "file.pptx"
notes = get_notes(file_pptx)
for i, note in enumerate(notes):
    file.write_text(dir_output / f"note_{i}.txt", note)
