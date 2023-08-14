from fastapi import FastAPI
import uvicorn
from common.logger import create_file_logger, create_main_logger
from common.config import get_cfg
import concurrent.futures
from fastapi import FastAPI, File, UploadFile
import uuid
from pathlib import Path
from htutil import file
import shutil
from note import get_notes
from tts.azure import AzureTTS
from image.pdf import save_images
from video.ffmpeg import make_video
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    executing = "executing"
    done = "done"
    failed = "failed"


poolExecutor = concurrent.futures.ProcessPoolExecutor(max_workers=1)


dir_data = Path("web-data")
dir_data.mkdir(parents=True, exist_ok=True)

# logger = create_file_logger(dir_data / "be.log")
logger = create_main_logger()
dir_fe = Path(__file__).parent.parent / "dist"


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def make_resp(code: int = 0, data=None, msg: str = ""):
    if msg == "":
        if code == 0:
            msg = "success"
        else:
            msg = "fail"
    return {"code": code, "msg": msg, "data": data}


@app.get("/api/hello")
async def hello():
    return make_resp(msg="Hello, This is pptx_speech")


def process_task(dir_task: Path, file_pptx: Path, file_pdf: Path):
    task_name = dir_task.name

    file_task = dir_task / "task.json"

    file.write_json(
        file_task,
        {
            "status": TaskStatus.executing,
        },
    )

    file_video = file_pptx.parent / f"{file_pptx.stem}.mp4"
    if file_video.exists():
        logger.info(f"[{task_name}] video already exists for {file_pptx}")

        file.write_json(
            file_task,
            {
                "status": TaskStatus.done,
            },
        )

        return

    dir_tmp = file_pptx.parent / f"{file_pptx.stem}_tmp"
    if not dir_tmp.exists():
        dir_tmp.mkdir(parents=True, exist_ok=True)

    logger.info(f"[{task_name}] get notes")
    notes = get_notes(file_pptx)
    dir_notes = dir_tmp / "notes"
    dir_notes.mkdir(parents=True, exist_ok=True)
    for i, note in enumerate(notes):
        if note == "":
            logger.warning(f"[{task_name}] Page {i} has no note")
            note = "此页无备注，请注意"
        file.write_text(dir_notes / f"{i}.txt", note)

    logger.info(f"[{task_name}] tts")
    dir_audio = dir_tmp / "audio"
    dir_audio.mkdir(parents=True, exist_ok=True)
    for file_note in sorted(dir_notes.glob("*.txt")):
        file_audio = dir_audio / f"{file_note.stem}.wav"
        if not file_audio.exists():
            azureTTS.tts(file.read_text(file_note), file_audio)
            logger.debug(f"[{task_name}] tts for {file_note.name} success")

    logger.info(f"[{task_name}] get image")
    dir_image = dir_tmp / "image"
    dir_image.mkdir(parents=True, exist_ok=True)
    save_images(file_pdf, dir_image)

    logger.info(f"[{task_name}] make video")
    dir_video = dir_tmp / "video"
    dir_video.mkdir(parents=True, exist_ok=True)
    make_video(dir_image, dir_audio, dir_video)

    file_output = dir_video / "output.mp4"
    if file_output.exists():
        shutil.copyfile(file_output, file_video)
    else:
        file.write_json(
            file_task,
            {
                "status": TaskStatus.failed,
            },
        )

        raise Exception("failed to make video for {}".format(file_pptx))

    logger.info(f"[{task_name}] success to make video")

    # shutil.rmtree(dir_tmp)
    file.write_json(
        file_task,
        {
            "status": TaskStatus.done,
        },
    )


@app.post("/api/task")
async def parse_pdf(file_pptx: UploadFile, file_pdf: UploadFile):
    task_id = uuid.uuid4().hex
    dir_task = dir_data / task_id

    file_task = dir_task / "task.json"

    file.write_json(
        file_task,
        {
            "status": TaskStatus.pending,
        },
    )

    content = await file_pptx.read()
    with open(dir_task / f"{task_id}.pptx", "wb") as buffer:
        buffer.write(content)

    content = await file_pdf.read()
    with open(dir_task / f"{task_id}.pdf", "wb") as buffer:
        buffer.write(content)

    dir_task.mkdir(parents=True, exist_ok=True)

    poolExecutor.submit(
        process_task,
        dir_task,
        dir_task / f"{task_id}.pptx",
        dir_task / f"{task_id}.pdf",
    )

    return make_resp(data={"taskID": task_id})


@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_index():
    return "index.html"


logger.info("start be")

cfg = get_cfg()
azure_cfg = cfg["tts"]["azure"]
azureTTS = AzureTTS(azure_cfg["key"], azure_cfg["region"])
logger.info("init azure tts success")


# when process is interrupted and restarted, it needs to resume execution of the previous task first.
def process_previous_task():
    previous_tasks = []
    for dir_task in dir_data.glob("*"):
        file_task = dir_task / "task.json"
        if file_task.exists():
            task = file.read_json(file_task)
            if task["status"] in [TaskStatus.pending, TaskStatus.executing]:
                file_pptx = list(dir_task.glob("*.pptx"))[0]
                file_pdf = list(dir_task.glob("*.pdf"))[0]
                previous_tasks.append((dir_task, file_pptx, file_pdf))

    if len(previous_tasks) > 0:
        logger.info(f"processing {len(previous_tasks)} previous tasks")
        for dir_task, file_pptx, file_pdf in previous_tasks:
            logger.info(f"processing {file_pptx}")
            process_task(dir_task, file_pptx, file_pdf)


process_previous_task()

app.mount("/static", StaticFiles(directory=dir_data), name="static")
app.mount("/", StaticFiles(directory=dir_fe), name="fe")
uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False)
