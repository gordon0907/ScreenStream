# ScreenStream

Stream your Windows desktop to an RTMP server with system audio using FFmpeg and the `soundcard` Python library.

## Compilation Instructions

1. Set the `rtmp_url` in `main.py`.
2. Download FFmpeg and place `ffmpeg.exe` in the root directory of the repository.
3. Choose an icon, rename it to `icon.ico`, and place it in the root directory.
4. Set up the environment using the dependencies listed in `requirements.txt`.
5. Run `make.bat` to compile.
