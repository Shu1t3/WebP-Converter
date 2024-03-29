import asyncio
from io import BytesIO
import numpy as np
from tempfile import NamedTemporaryFile

from PIL import Image
from moviepy.editor import VideoFileClip


def resize_frame(frame):
    # Преобразуем кадр в объект изображения Pillow
    img = Image.fromarray(frame)
    # Изменяем размер изображения с использованием сглаживания LANCZOS
    resized_img = img.resize((512, 512), Image.LANCZOS)
    # Преобразуем изображение обратно в массив numpy
    resized_frame = np.array(resized_img)
    # Возвращаем измененный кадр
    return resized_frame


async def generate_webm(video_data: BytesIO) -> BytesIO:
    # Создаем временный файл для сохранения видео
    with NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        # Получаем байтовые данные из BytesIO
        temp_file.write(video_data.getvalue())
        temp_file.seek(0)

        # Загружаем видео из временного файла
        clip = VideoFileClip(temp_file.name)

        # Обрезаем видео до 3 секунд
        clipped_clip = clip.subclip(0, 3)

        # Изменяем размер до 512x512 пикселей с использованием сглаживания
        resized_clip = clipped_clip.fl_image(lambda frame: resize_frame(frame))

        # Создаем объект BytesIO для записи выходных данных
        output_bytesio = BytesIO()

        # Создаем временный файл для сохранения результата
        with NamedTemporaryFile(suffix='.webm', delete=False) as output_file:
            # Сохраняем видео в формате WebM во временный файл
            await asyncio.to_thread(resized_clip.write_videofile, output_file.name, codec="libvpx", audio_codec="libvorbis", audio=False)
            # Читаем данные из временного файла
            output_file.seek(0)
            result_bytes = output_file.read()

    # Возвращаем объект BytesIO с результатом
    output_bytesio.write(result_bytes)
    output_bytesio.seek(0)
    return output_bytesio
