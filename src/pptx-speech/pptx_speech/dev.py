from note import get_notes
from tts.azure import AzureTTS
from image.pdf import save_images
from video.ffmpeg import make_video
from common.config import get_cfg

from pathlib import Path
from htutil import file
import typer
from typing_extensions import Annotated


def main(test_mode:  Annotated[str, typer.Option()] = 'batch'):
    cfg = get_cfg()
    azure_cfg = cfg['tts']['azure']
    azureTTS = AzureTTS(azure_cfg['key'], azure_cfg['region'])

    if test_mode == 'batch':
        dir_data = Path("data")

        task_name = "cons-1"

        dir_input = dir_data / "input" / task_name
        dir_output = dir_data / "output" / task_name
        dir_output.mkdir(parents=True, exist_ok=True)

        print("notes")
        file_pptx = dir_input / "file.pptx"
        notes = get_notes(file_pptx)
        dir_notes = dir_output / "notes"
        dir_notes.mkdir(parents=True, exist_ok=True)
        for i, note in enumerate(notes):
            if note == '':
                note = '此页无备注，请注意'
            file.write_text(dir_notes / f"{i}.txt", note)

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
    elif test_mode == 'audio':
        file_audio = Path("audio.txt")
        if not file_audio.exists():
            s = input('Please input text\n')
        else:
            s = file.read_text(file_audio)
        azureTTS.tts(s, Path("test.wav"))
    else:
        raise Exception(f'Invalid test_mode: {test_mode}')


if __name__ == '__main__':
    typer.run(main)
