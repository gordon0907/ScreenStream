import os
import subprocess
from atexit import register
from contextlib import suppress

import numpy as np
import soundcard as sc

# Define RTMP destination URL
rtmp_url = ...  # Replace with your RTMP server URL

# Audio capture configuration
SAMPLE_RATE = 48000  # Sample rate in Hz
CHANNELS = 2  # Stereo
NUM_FRAMES = 128  # Number of frames per audio chunk


@register
def cleanup_on_exit():
    # Ensure ffmpeg process is terminated on exit
    with suppress(Exception):
        ffmpeg_process.kill()


def get_ffmpeg_executable_path() -> str:
    """
    Determine the path to ffmpeg.exe depending on runtime context.
    """
    if '__compiled__' in globals():
        base_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        base_dir = os.getcwd()
    return os.path.join(base_dir, 'ffmpeg.exe')


def get_default_loopback_device(microphones: list) -> int:
    """
    Get the index of the loopback device corresponding to the default speaker.
    """
    default_speaker_name = sc.default_speaker().name
    for index, mic in enumerate(microphones):
        if mic.name == default_speaker_name:
            return index
    return 0  # Fallback index


# FFmpeg command to capture desktop video and system audio
ffmpeg_cmd = [
    get_ffmpeg_executable_path(),
    '-f', 'gdigrab',  # Capture Windows desktop
    '-framerate', '30',  # Set video framerate
    '-i', 'desktop',  # Input video source

    '-f', 'f32le',  # Input audio format: 32-bit float little-endian
    '-ar', str(SAMPLE_RATE),  # Audio sample rate
    '-ac', str(CHANNELS),  # Number of audio channels
    '-channel_layout', 'stereo',  # Audio layout
    '-i', 'pipe:0',  # Read audio from stdin

    '-fps_mode', 'cfr',  # Video sync method
    '-async', '1',  # Audio sync method

    '-c:v', 'libx264',  # Video codec
    '-preset', 'ultrafast',  # Encoding preset
    '-b:v', '6000k',  # Video bitrate
    '-maxrate', '6000k',
    '-bufsize', '6000k',
    '-pix_fmt', 'yuv420p',  # Pixel format

    '-c:a', 'aac',  # Audio codec
    '-b:a', '128k',  # Audio bitrate

    '-f', 'flv',  # Output format
    rtmp_url  # Destination URL
]


def capture_audio_to_ffmpeg(ffmpeg_process):
    """
    Capture system audio using loopback device and stream it into ffmpeg.
    """
    microphones = sc.all_microphones(include_loopback=True)
    loopback_index = get_default_loopback_device(microphones)
    loopback_device = microphones[loopback_index]

    with loopback_device.recorder(samplerate=SAMPLE_RATE, channels=CHANNELS) as recorder:
        while True:
            try:
                audio_data: np.ndarray = recorder.record(numframes=NUM_FRAMES)
                ffmpeg_process.stdin.write(audio_data.tobytes())
            except Exception as err:
                print(f"Audio capture error: {err}")


if __name__ == '__main__':
    ffmpeg_process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
    )
    capture_audio_to_ffmpeg(ffmpeg_process=ffmpeg_process)
