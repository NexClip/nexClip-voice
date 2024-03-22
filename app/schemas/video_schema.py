from pydantic import BaseModel, HttpUrl


class AudioDownloadRequest(BaseModel):
    clone_audio_url: str
    original_audio_url: str
