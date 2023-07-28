from note import get_notes
from tts.azure import AzureTTS
from image.pdf import save_images
from video.ffmpeg import make_video

from pathlib import Path
from htutil import file

dir_data = Path("data")

task_name = "poh"

dir_input = dir_data / "input" / task_name
dir_output = dir_data / "output" / task_name
dir_output.mkdir(parents=True, exist_ok=True)

file_pptx = dir_input / "file.pptx"
notes = get_notes(file_pptx)
dir_notes = dir_output / "notes"
dir_notes.mkdir(parents=True, exist_ok=True)
for i, note in enumerate(notes):
    if note == '':
        note = '此页无备注，请注意'
    file.write_text(dir_notes / f"{i}.txt", note)


cfg = file.read_yaml("config.yaml")
azure_cfg = cfg['tts']['azure']
azureTTS = AzureTTS(azure_cfg['key'], azure_cfg['region'])

print("tts")
dir_audio = dir_output / "audio"
dir_audio.mkdir(parents=True, exist_ok=True)
for file_note in dir_notes.glob("*.txt"):
    file_audio = dir_audio / f"{file_note.stem}.wav"
    if not file_audio.exists():
        azureTTS.tts(file.read_text(file_note), file_audio)

print("image")
file_pdf = dir_input / "file.pdf"
dir_image = dir_output / "image"
dir_image.mkdir(parents=True, exist_ok=True)
save_images(file_pdf, dir_image)

print("video")
dir_video = dir_output / "video"
dir_video.mkdir(parents=True, exist_ok=True)
make_video(dir_image, dir_audio, dir_video)
