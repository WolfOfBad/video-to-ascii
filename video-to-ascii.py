import os
import sys
import subprocess
import time
import glob
import cv2
from PIL import Image

ESC = b'\033'
CSI = ESC + b'['

# macOS/Linux/Windows ANSI
use_ansi_escape_sequences = True

video_columns, video_lines = 140, 45


def clear_console():
    print("\033[2J\033[1;1H", end='')


# Очистка
clear_console()

# ---------------------------------------------
#  ВЫБОР ВИДЕО
# ---------------------------------------------
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

# ---------------------------------------------
#  ОТКРЫВАЕМ ВИДЕО И БЕРЁМ FPS
# ---------------------------------------------
vidcap = cv2.VideoCapture(selected_video)
fps = vidcap.get(cv2.CAP_PROP_FPS)

if fps is None or fps <= 0:
    fps = 30

print(f"\nAuto FPS detected: {fps}")

success, image = vidcap.read()
if not success:
    print("Не удалось открыть видео!")
    exit()

# ---------------------------------------------
#  INPUT SETTINGS (FIXED)
# ---------------------------------------------
has_inverted_colors = input("Inverted colors? (true/false): ").strip().lower() != "false"
loop = input("Loop video? (true/false): ").strip().lower() != "false"

# ---------------------------------------------
#  ЗАПУСК АУДИО (ffplay)
# ---------------------------------------------
print("\nЗапуск аудио…")
audio_process = subprocess.Popen(
    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", selected_video]
)

# ---------------------------------------------
#  ASCII ПОДГОТОВКА
# ---------------------------------------------
clear_console()

symbols = list(r'$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1[]?-_+~<>i!lI;:,   ')
if has_inverted_colors:
    symbols.reverse()

stdout = os.fdopen(sys.stdout.fileno(), 'wb', video_columns * video_lines * 2)

# ---------------------------------------------
#  ГЛАВНЫЙ ЦИКЛ — ИДЕАЛЬНАЯ СИНХРОНИЗАЦИЯ
# ---------------------------------------------
start_time = time.time()
frame_index = 0

try:
    while True:
        success, image = vidcap.read()

        # ---------------------------------
        #  ЛУП ВИДЕО + ПЕРЕЗАПУСК ЗВУКА
        # ---------------------------------
        if not success:
            if loop:
                vidcap = cv2.VideoCapture(selected_video)
                success, image = vidcap.read()

                audio_process.kill()
                audio_process = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", selected_video]
                )

                start_time = time.time()
                frame_index = 0
            else:
                break

        # ---------------------------------
        #  ASCII РЕНДЕР КАДРА
        # ---------------------------------
        im = Image.fromarray(image)
        im = im.resize((video_columns, video_lines))
        im = im.convert('L')
        pixels = im.load()

        result = []

        for y in range(video_lines):
            for x in range(video_columns):
                result.append(symbols[pixels[x, y] // 36])
            result.append('\n')

        stdout.write(CSI + b'1;1H')
        stdout.write(''.join(result).encode())
        stdout.flush()

        # ---------------------------------
        #  ИДЕАЛЬНАЯ СИНХРОНИЗАЦИЯ СО ЗВУКОМ
        # ---------------------------------
        target_time = start_time + (frame_index / fps)
        now = time.time()

        delay = target_time - now
        if delay > 0:
            time.sleep(delay)

        frame_index += 1

except KeyboardInterrupt:
    pass

print("\nОстановлено.")
