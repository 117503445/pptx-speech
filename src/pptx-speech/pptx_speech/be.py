from fastapi import FastAPI
import uvicorn
from common.logger import create_main_logger
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
from common.logger import create_main_logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

cfg = get_cfg()
azure_cfg = cfg['tts']['azure']
azureTTS = AzureTTS(azure_cfg['key'], azure_cfg['region'])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = create_main_logger()

poolExecutor = concurrent.futures.ProcessPoolExecutor(max_workers=1)


dir_data = Path("web-data")

dir_fe = Path(__file__).parent.parent / "dist"

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


def create_task(dir_task: Path, file_pptx: Path, file_pdf: Path):
    file_task = dir_task / "task.json"

    file.write_json(
        file_task,
        {
            "status": "executing",
        },
    )

    file_video = file_pptx.parent / f"{file_pptx.stem}.mp4"
    if file_video.exists():
        logger.info(f"video already exists for {file_pptx}")

        file.write_json(
            file_task,
            {
                "status": "done",
            },
        )

        return
    
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
        file.write_json(
            file_task,
            {
                "status": "failed",
            },
        )

        raise Exception("failed to make video for {}".format(file_pptx))

    logger.info(f"success to make video for {file_pptx}")

    shutil.rmtree(dir_tmp)
    file.write_json(
        file_task,
        {
            "status": "done",
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
            "status": "pending",
        },
    )

    # TODO
    # if file_task.exists():
    #     js = file.read_json(file_task)
    #     if js["status"] != "done":
    #         return make_common_data(0, "Success", {"taskID": task_id})
    #     else:
    #         if file.read_json(dir_task / 'output' / 'doc.json')['meta']['flow-pdf-version'] == version:
    #             return make_common_data(0, "Success", {"taskID": task_id})
    #         else:
    #             logger.info(f"clean old task {task_id}")
    #             shutil.rmtree(dir_task)

    content = await file_pptx.read()
    with open(dir_task / f"{task_id}.pptx", "wb") as buffer:
        buffer.write(content)

    content = await file_pdf.read()
    with open(dir_task / f"{task_id}.pdf", "wb") as buffer:
        buffer.write(content)

    dir_task.mkdir(parents=True, exist_ok=True)


    poolExecutor.submit(create_task, dir_task, dir_task / f"{task_id}.pptx", dir_task / f"{task_id}.pdf")

    return make_resp(data={"taskID": task_id})

@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_index():
    return "index.html"


app.mount("/static", StaticFiles(directory=dir_data), name="static")
app.mount("/", StaticFiles(directory=dir_fe), name="fe")
uvicorn.run(app, host="0.0.0.0", port=8080)
