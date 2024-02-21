import os
from io import BytesIO
import asyncio
import logging

from PIL import Image

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


async def convert(io_data: BytesIO) -> BytesIO:
    # Чтение байтов данных из объекта BytesIO
    pic = io_data.read()
    # Открываем изображение из байтовых данных и меняем размер и качество
    img = Image.open(BytesIO(pic))
    img = img.resize((512, 512))
    quality = 95
    out = BytesIO()
    # Сжимаем изображение и сохраняем в формате WebP
    img.save(out, 'WEBP', quality=quality)
    # Проверяем размер файла и уменьшаем качество, пока не уложимся в 64 КБ
    while out.tell() > 64 * 1024:  # Проверяем размер данных в BytesIO объекте, если много уменьшаем
        quality -= 1
        # Сбрасываем указатель записи в начало объекта BytesIO и очищаем данные в объекте BytesIO
        out.seek(0)
        out.truncate(0)
        img.save(out, 'WEBP', quality=quality)
    # Возвращаем указатель чтения в начало объекта BytesIO
    out.seek(0)
    return out


@dp.message(Command('start'))
async def start_cmd(message: types.Message):
    await message.answer('Отправьте изображения. Чем "квадратней", тем лучше! :)')


@dp.message(F.photo)
async def get_photo_conver_webp(message: types.Message, bot: Bot):
    # Получаем ID фотки в самом лучше качестве
    photo = message.photo[-1].file_id

    if photo:
        # Этот блок получает фотку, путь для скачивания, скачивает и помещает в память
        get_photo = await bot.get_file(photo)
        photo_path = get_photo.file_path
        downloaded_photo = await bot.download_file(photo_path, BytesIO())

        await message.answer("Обрабатываю изображения, подождите...")
        # Этот блок конвертирует изображение и генерирует объект для отправки
        converted_photo = await convert(downloaded_photo)
        input_file = BufferedInputFile(converted_photo.getvalue(), filename='image.webp')
        # Отправляем готовый шаблон-стикер
        await message.answer_document(input_file, caption='Готовый WebP')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
