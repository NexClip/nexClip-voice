from pydantic import BaseModel


class AudioDownloadRequest(BaseModel):
    clone_audio_url: str
    original_audio_url: str
