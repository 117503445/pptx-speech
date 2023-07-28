import typer
from typing import Optional
from pathlib import Path
import os
from typing_extensions import Annotated
import logging
import tempfile
import shutil

from note import get_notes
from tts.azure import AzureTTS
from image.pdf import save_images
from video.ffmpeg import make_video
from htutil import file


def create_main_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    return logger

def main(azure_key: Annotated[str, typer.Option(envvar="AZURE_KEY")], azure_region: Annotated[str, typer.Option(envvar="AZURE_REGION")], dir_data: Path = Path('./data')):
    if not dir_data.exists():
        raise Exception("Directory {} does not exist".format(dir_data))
    if not dir_data.is_dir():
        raise Exception("{} is not a directory".format(dir_data))

    files = list(dir_data.glob("**/*.pptx"))
    if len(files) == 0:
        raise Exception("No pptx file found in {}".format(dir_data))
    elif len(files) > 1:
        raise Exception("More than one pptx file found in {}".format(dir_data))
    else:
        file_pptx = files[0]

    files = list(dir_data.glob("**/*.pdf"))
    if len(files) == 0:
        raise Exception("No pdf file found in {}".format(dir_data))
    elif len(files) > 1:
        raise Exception("More than one pdf file found in {}".format(dir_data))
    else:
        file_pdf = files[0]
    
    logger = create_main_logger()
    logger.info(f'file_pptx: {file_pptx}')
    logger.info(f'file_pdf: {file_pdf}')

    logger.info('get notes')

    notes = get_notes(file_pptx)
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        dir_temp = Path(tmp_dir_name)

        dir_notes = dir_temp / "notes"
        dir_notes.mkdir(parents=True, exist_ok=True)

        for i, note in enumerate(notes):
            if note == '':
                logger.warning(f'Page {i} has no note')
                note = '此页无备注，请注意'
            file.write_text(dir_notes / f"{i}.txt", note)
        

        logger.info('tts')
        azureTTS = AzureTTS(azure_key, azure_region)
        dir_audio = dir_temp / "audio"
        dir_audio.mkdir(parents=True, exist_ok=True)
        for file_note in dir_notes.glob("*.txt"):
            file_audio = dir_audio / f"{file_note.stem}.wav"
            if not file_audio.exists():
                azureTTS.tts(file.read_text(file_note), file_audio)

        logger.info('get image')
        dir_image = dir_temp / "image"
        dir_image.mkdir(parents=True, exist_ok=True)
        save_images(file_pdf, dir_image)

        logger.info('make video')
        dir_video = dir_temp / "video"
        dir_video.mkdir(parents=True, exist_ok=True)
        make_video(dir_image, dir_audio, dir_video)

        file_output = dir_video / "output.mp4"
        if file_output.exists():
            shutil.copyfile(file_output, dir_data / f'{file_pptx.stem}.mp4')
        else:
            raise Exception("No output file found in {}".format(dir_video))



if __name__ == "__main__":
    typer.run(main)