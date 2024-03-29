import os
from io import BytesIO
import asyncio
import logging

from PIL import Image
from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile
from aiogram import F
from dotenv import load_dotenv

from utils.webp.converter import convert
from utils.webm.converter import generate_webm


load_dotenv()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


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
        input_file = BufferedInputFile(
            converted_photo.getvalue(), filename='image.webp'
        )
        # Отправляем готовый шаблон-стикер
        await message.answer_document(input_file, caption='Готовый WebP')


@dp.message(F.video)
async def get_video_conver_webm(message: types.Message, bot: Bot):
    video = message.video.file_id

    if video:
        get_video = await bot.get_file(video)
        video_path = get_video.file_path
        downloaded_video = await bot.download_file(video_path, BytesIO())

        await message.answer(f'Размер файла - {get_video.file_size}')
        await message.answer("Обрабатываю видео, подождите...")

        if downloaded_video:
            new_video_sticker = await generate_webm(video_data=downloaded_video)
            input_file = BufferedInputFile(
                new_video_sticker.getvalue(), filename='sticker.webm'
            )
            await message.answer_document(input_file, caption='Готовый видеостикер!')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
