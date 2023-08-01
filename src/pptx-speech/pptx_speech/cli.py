import typer
from typing import Optional
from pathlib import Path
import os
from typing_extensions import Annotated
import tempfile
import shutil

from note import get_notes
from tts.azure import AzureTTS
from image.pdf import save_images
from video.ffmpeg import make_video
from common.logger import create_main_logger
from htutil import file


def main(
    azure_key: Annotated[str, typer.Option(envvar="AZURE_KEY")],
    azure_region: Annotated[str, typer.Option(envvar="AZURE_REGION")],
    dir_data: Path = Path("./data"),
):
    logger = create_main_logger()

    if not dir_data.exists():
        raise Exception("Directory {} does not exist".format(dir_data))
    if not dir_data.is_dir():
        raise Exception("{} is not a directory".format(dir_data))

    files = list(dir_data.glob("**/*.pptx"))
    if len(files) == 0:
        raise Exception("No pptx file found in {}".format(dir_data))

    for file_pptx in files:
        file_pdf = file_pptx.parent / f"{file_pptx.stem}.pdf"
        if not file_pdf.exists():
            logger.error(f"No pdf file found for {file_pptx}")
            continue

        logger.info(f"file_pptx: {file_pptx}")
        logger.info(f"file_pdf: {file_pdf}")

        file_video = file_pptx.parent / f"{file_pptx.stem}.mp4"
        if file_video.exists():
            logger.info(f"video already exists for {file_pptx}")
            continue

        dir_tmp = file_pptx.parent / f"{file_pptx.stem}_tmp"
        if not dir_tmp.exists():
            dir_tmp.mkdir(parents=True, exist_ok=True)

        logger.info("get notes")
        notes = get_notes(file_pptx)
        dir_notes = dir_tmp / "notes"
        dir_notes.mkdir(parents=True, exist_ok=True)
        for i, note in enumerate(notes):
            if note == "":
                logger.warning(f"Page {i} has no note")
                note = "此页无备注，请注意"
            file.write_text(dir_notes / f"{i}.txt", note)

        logger.info("tts")
        azureTTS = AzureTTS(azure_key, azure_region)
        dir_audio = dir_tmp / "audio"
        dir_audio.mkdir(parents=True, exist_ok=True)
        for file_note in dir_notes.glob("*.txt"):
            file_audio = dir_audio / f"{file_note.stem}.wav"
            if not file_audio.exists():
                azureTTS.tts(file.read_text(file_note), file_audio)

        logger.info("get image")
        dir_image = dir_tmp / "image"
        dir_image.mkdir(parents=True, exist_ok=True)
        save_images(file_pdf, dir_image)

        logger.info("make video")
        dir_video = dir_tmp / "video"
        dir_video.mkdir(parents=True, exist_ok=True)
        make_video(dir_image, dir_audio, dir_video)

        file_output = dir_video / "output.mp4"
        if file_output.exists():
            shutil.copyfile(file_output, file_video)
        else:
            raise Exception("failed to make video for {}".format(file_pptx))

        logger.info(f"success to make video for {file_pptx}")

        shutil.rmtree(dir_tmp)


if __name__ == "__main__":
    typer.run(main)
