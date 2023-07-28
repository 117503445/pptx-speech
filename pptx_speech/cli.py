from note import get_notes
from tts.azure import AzureTTS
from image.pdf import save_images

from pathlib import Path
from htutil import file

dir_data = Path("data")

task_name = "example"

dir_input = dir_data / "input" / task_name
dir_output = dir_data / "output" / task_name
dir_output.mkdir(parents=True, exist_ok=True)

file_pptx = dir_input / "file.pptx"
notes = get_notes(file_pptx)
dir_notes = dir_output / "notes"
dir_notes.mkdir(parents=True, exist_ok=True)
for i, note in enumerate(notes):
    file.write_text(dir_notes / f"{i}.txt", note)


cfg = file.read_yaml("config.yaml")
azure_cfg = cfg['tts']['azure']
azureTTS = AzureTTS(azure_cfg['key'], azure_cfg['region'])

dir_audio = dir_output / "audio"
dir_audio.mkdir(parents=True, exist_ok=True)
for file_note in dir_notes.glob("*.txt"):
    file_audio = dir_audio / f"{file_note.stem}.wav"
    if not file_audio.exists():
        azureTTS.tts(file.read_text(file_note), file_audio)

file_pdf = dir_input / "file.pdf"
dir_image = dir_output / "image"
dir_image.mkdir(parents=True, exist_ok=True)
save_images(file_pdf, dir_image)