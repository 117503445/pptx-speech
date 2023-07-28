import subprocess

from htutil import file
from pathlib import Path


def make_video(dir_image: Path, dir_audio: Path, dir_output: Path):
    images = sorted(dir_image.glob("*.png"), key=lambda x: int(x.stem))
    file_video_list: list[Path] = []

    for file_image in images:
        file_audio = dir_audio / f"{file_image.stem}.wav"
        file_output = dir_output / f"{file_image.stem}.mp4"
        file_video_list.append(file_output)

        if not file_output.exists():
            print(file_image)
            with open(dir_output / f"{file_image.stem}.log", "w") as f:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",  # overwrite
                        "-i",
                        str(file_image),
                        "-i",
                        str(file_audio),
                        "-vcodec",
                        "libx264",
                        str(file_output),
                    ],
                    stdout=f,
                    stderr=f,
                )

        # subprocess.run([
        #     'ffmpeg',
        #     '-loop', '1',
        #     '-i', str(file_image),
        #     '-i', str(file_audio),
        #     '-c:v', 'libx264',
        #     '-tune', 'stillimage',
        #     '-c:a', 'aac',
        #     '-b:a', '192k',
        #     '-pix_fmt', 'yuv420p',
        #     '-shortest',
        #     '-strict', '-2',
        #     '-loglevel', 'error',
        #     '-y',
        #     str(file_output),
        # ])

    print("combine video")
    # combine video

    files = "\n".join([f"file '{x.name}'" for x in file_video_list])
    file_list = dir_output / "list.txt"
    file.write_text(file_list, files)

    file_output = dir_output / "output.mp4"
    if not file_output.exists():
        with open(dir_output / "combine.log", "w") as f:
            subprocess.run(
                [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-i",
                    # str(file_list.absolute()),
                    str(file_list),
                    "-c",
                    "copy",
                    "-y",
                    str(file_output),
                ],
                stdout=f,
                stderr=f,
            )
