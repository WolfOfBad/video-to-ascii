import os
import sys
import subprocess
from time import sleep
import glob
import cv2
from PIL import Image

ESC = b'\033'
CSI = ESC + b'['

# Use ANSI escape sequences (macOS/Linux/modern Windows)
use_ansi_escape_sequences = True

video_columns, video_lines = 140, 45


def set_console_size(columns, lines):
    # macOS does not support `mode con`, so we only clear the screen
    print("\033[2J\033[1;1H", end='')


# Clear console
os.system('clear')

selected_video_number = 0

videos = glob.glob('*.mp4')

if not videos:
    print("Нет .mp4 видео в этой папке!")
    exit()

for video_index, video_name in enumerate(videos):
    print(f'[{video_index + 1}] - {video_name}')

selected_video_number = input('\nВведите номер видео: ')

try:
    selected_video = videos[int(selected_video_number) - 1]
except:
    print(f'{selected_video_number} - неверный номер X_X')
    exit()


# ----------------------------- #
#     ОТКРЫВАЕМ ВИДЕО
# ----------------------------- #
vidcap = cv2.VideoCapture(selected_video)

# ---------- AUTO FPS ----------
fps = vidcap.get(cv2.CAP_PROP_FPS)
if fps is None or fps <= 0:
    fps = 30  # fallback
print(f"\nAuto FPS detected: {fps}")

success, image = vidcap.read()
if not success:
    print("Не удалось открыть видео!")
    exit()


# INPUT SETTINGS (BOOLEAN FIX)
has_inverted_colors = input("Inverted colors? (true/false): ").strip().lower() != "false"
loop = input("Loop video? (true/false): ").strip().lower() != "false"


# ----------------------------- #
#     ЗАПУСК ЗВУКА (ffplay)
# ----------------------------- #
print("\nЗапуск аудио…")

audio_process = subprocess.Popen(
    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", selected_video]
)


# ----------------------------- #
#     ASCII РЕНДЕР
# ----------------------------- #

set_console_size(video_columns, video_lines)

symbols = list(r'$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1[]?-_+~<>i!lI;:,   ')

if has_inverted_colors:
    symbols.reverse()

stdout = os.fdopen(sys.stdout.fileno(), 'wb', video_columns * video_lines * 2)

try:
    while True:
        success, image = vidcap.read()

        # Loop video
        if not success:
            if loop:
                vidcap = cv2.VideoCapture(selected_video)
                continue
            else:
                break

        im = Image.fromarray(image)
        im = im.resize((video_columns, video_lines))
        im = im.convert('L')
        pixels = im.load()

        result = []

        for y in range(video_lines):
            for x in range(video_columns):
                result.append(symbols[int(pixels[x, y] / 36)])
            result.append('\n')

        # Move cursor to the top-left
        stdout.write(CSI + b'1;1H')
        stdout.write(''.join(result).encode())
        stdout.flush()

        sleep(1 / fps)

except KeyboardInterrupt:
    pass

print("\nОстановлено.")
