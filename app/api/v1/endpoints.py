import os
import re
from datetime import datetime
from typing import Dict

import aiohttp
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger
from starlette.status import HTTP_404_NOT_FOUND

from app.schemas.video_schema import AudioDownloadRequest
from app.services import audio_assembler, audio_processor

router = APIRouter()

# Global dictionary to track the status of tasks
task_status: Dict[str, str] = {}


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
DOWNLOAD_AUDIO = os.path.join(ROOT_DIR, "data", "downloaded_audios")
OUTPUT_AUDIO = os.path.join(ROOT_DIR, "data", "output_audios")

directories = [
    "processed_audios",
    "downloaded_audios",
    "processed_audios",
    "output_audios",
]

base_dir = os.path.join(ROOT_DIR, "data")

# Creazione delle directory se non esistono
for dir_name in directories:
    dir_path = os.path.join(base_dir, dir_name)
    os.makedirs(dir_path, exist_ok=True)


@router.post("/test/")
async def download_and_process_audio(
    request: AudioDownloadRequest, background_tasks: BackgroundTasks
):
    logger.info(request)
    clone_voice_url = request.clone_audio_url
    original_audio_url = request.original_audio_url

    try:
        logger.info(f"Received clone voice URL: {clone_voice_url}")
        logger.info(f"Received original audio URL: {original_audio_url}")

        clone_voice_path = await download_audio(clone_voice_url, DOWNLOAD_AUDIO)
        original_audio_path = await download_audio(original_audio_url, DOWNLOAD_AUDIO)
        current_time_microseconds = datetime.now().strftime("%Y%m%d%H%M%S%f")
        output_path = os.path.join(OUTPUT_AUDIO, f"{current_time_microseconds}.mp3")

        task_status[current_time_microseconds] = "Processing"
        logger.info(f"{output_path}")
        background_tasks.add_task(
            process,
            clone_voice_path,
            original_audio_path,
            output_path,
            current_time_microseconds,
        )

        logger.info(f"{clone_voice_path}, {original_audio_path}, {output_path}")
        return {"audio_id": current_time_microseconds, "status": "Processing started"}
    except Exception as e:
        logger.error(f"Error in download_and_process_audio endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{video_id}")
def get_task_status(video_id: str):
    status = task_status.get(video_id, "Not Found")
    return {"video_id": video_id, "status": status}


@router.get("/download-final-video/{video_id}")
async def download_video(video_id: str):
    video_path = os.path.join(OUTPUT_AUDIO, f"{video_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{video_id}.mp4")


def process(
    clone_voice_path: str,
    original_audio_path: str,
    output_path: str,
    current_time_microseconds: str,
):
    try:
        processed_audio_path = os.path.join(
            ROOT_DIR, "data", "processed_audios", "processed_output.mp3"
        )
        audio_processor.process_audio(
            audio_input_path=original_audio_path,
            audio_target_path=clone_voice_path,
            audio_output_path=processed_audio_path,
        )

        audio_assembler.merge_audio(output_path, processed_audio_path, output_path)

        task_status[current_time_microseconds] = "Completed"

    except Exception as e:
        task_status[current_time_microseconds] = "Failed"
        logger.error(f"Error in process_audio_and_assemble_video: {e}")


async def download_audio(audio_url, destination_folder):
    """
    Asynchronously download an audio from `audio_url` and save it to `destination_folder`.
    Returns the path to the downloaded audio file.
    """
    audio_filename = os.path.basename(audio_url)
    audio_filepath = os.path.join(destination_folder, audio_filename)

    os.makedirs(destination_folder, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(audio_url) as response:
            if response.status == 200:
                with open(audio_filepath, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return audio_filepath
            else:
                raise Exception(
                    f"Failed to download audio: Status code {response.status}"
                )
