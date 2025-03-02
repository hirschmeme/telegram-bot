import os
import random
import string
import asyncio
import ffmpeg
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor

# Bot Token hier einfügen
TOKEN = "7796488007:AAHkQ1bTWTqebqp2KxBAQpE_wIxCcxi8drY"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def process_video(input_file, output_file):
    temp_output = f"temp_{random_string()}.mp4"
    
    # Zufällige Werte für Veränderungen
    scale_factor = round(random.uniform(0.98, 1.02), 2)
    fps = random.choice([24, 25, 26, 28, 29.97, 30])
    bitrate = f'{random.randint(600, 1800)}k'
    trim_start = random.uniform(0, 2)
    metadata_date = f"202{random.randint(0, 5)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00Z"
    
    try:
        input_stream = ffmpeg.input(input_file)
        video_stream = (
            input_stream.trim(start=trim_start)
            .filter('scale', f'trunc(iw*{scale_factor}/2)*2', f'trunc(ih*{scale_factor}/2)*2')
            .filter('eq', contrast=random.uniform(1.01, 1.03), brightness=random.uniform(0.005, 0.015))
            .filter('hue', h=random.uniform(0.01, 0.03), s=1.0)
            .filter('format', 'yuv420p')
            .filter('colorchannelmixer', rr=random.uniform(0.98, 1.02), bb=random.uniform(0.98, 1.02))
        )
        audio_stream = (
            input_stream.audio
            .filter('asetrate', f'{random.choice([44050, 44100, 44200])}')
            .filter('volume', random.uniform(0.98, 1.02))
        )
        (
            ffmpeg.output(video_stream, audio_stream, temp_output, 
                          vcodec='libx264', acodec='aac', 
                          video_bitrate=bitrate, audio_bitrate='128k', 
                          r=fps, 
                          metadata=f'creation_time={metadata_date}',
                          movflags='faststart', 
                          map_metadata=-1)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        os.replace(temp_output, output_file)
    except ffmpeg.Error as e:
        print("FFmpeg-Fehler:", e.stderr.decode())

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Sende mir ein Video, und ich werde es leicht verändern.")

@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_video(message: types.Message):
    video = message.video
    file_id = video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    input_filename = f"input_{random_string()}.mp4"
    output_filename = f"output_{random_string()}.mp4"

    await bot.download_file(file_path, input_filename)
    
    process_video(input_filename, output_filename)

    with open(output_filename, "rb") as video_file:
        await message.reply_video(video_file)

    os.remove(input_filename)
    os.remove(output_filename)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
