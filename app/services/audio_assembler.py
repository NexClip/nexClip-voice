from moviepy.editor import AudioFileClip


def merge_audio(audio_path: str, output_path: str):
    audio_clip = AudioFileClip(audio_path)
    audio_clip.write_audiofile(output_path)
