import os
import asyncio

from PIL import Image

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile

from dotenv import load_dotenv

load_dotenv()


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
processing_done = False
complete_img = []


def check_and_create_dir():
    directories = ['img_in', 'out']

    for dir in directories:
        os.makedirs(os.path.join(os.getcwd(), dir), exist_ok=True)


async def convert(pth_in='img_in'):
    for pic in os.listdir(path=pth_in):
        if pic.endswith('.jpg') or pic.endswith('.png'):
            img_path = os.path.join(pth_in, pic)
            img = Image.open(img_path)
            img = img.resize((512, 512))
            f = os.path.splitext(pic)[0]
            out_path = os.path.join('out', f'{f}.webp')

            # Устанавливаем качество изображения для сжатия (от 0 до 100, где 0 - минимальное качество, 100 - максимальное)
            quality = 95

            # Сжимаем изображение и сохраняем в формате WebP
            img.save(out_path, 'WEBP', quality=quality)

            # Проверяем размер файла и уменьшаем качество, пока не уложимся в 64 КБ
            while os.path.getsize(out_path) > 64 * 1024:  # переводим килобайты в байты
                quality -= 1
                img.save(out_path, 'WEBP', quality=quality)

            print(f'Конвертация {pic} завершена и сохранена как {f}.webp. Размер файла: {os.path.getsize(out_path) / 1024} КБ')


async def del_img(pth_in='img_in', pth_out='out'):
    for file in os.listdir(path=pth_in):
        os.remove(f'{pth_in}/{file}')
    for file in os.listdir(path=pth_out):
        os.remove(f'{pth_out}/{file}')


@dp.message(Command('start'))
async def start_cmd(message: types.Message):
    await message.answer("Отправьте изображения")

# Функция сохранения отправленных фото
@dp.message(F.photo)
async def get_photo_conver_webp(message: types.Message, bot: Bot):
    global processing_done

    if not processing_done:
        file_info = await bot.get_file(message.photo[-1].file_id)
        processing_done = True
        file_name = file_info.file_path.split('photos/')[1]
        await bot.download_file(file_info.file_path, 'img_in/' + file_name)
        await message.answer("Обрабатываю изображения, подождите...")
        await convert()
        # Отправляем готовый шаблон-стикер
        async def upload_doc():
            for file_name in os.listdir(path='out/'):
                if file_name not in complete_img:
                    complete_img.append(file_name)
                    webp_img = FSInputFile(f'out/{file_name}')
                    await message.answer_document(webp_img, caption='Готовый WebP')
        await upload_doc()
        await del_img()
        complete_img.clear()
        processing_done = False


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    check_and_create_dir()
    asyncio.run(main())
