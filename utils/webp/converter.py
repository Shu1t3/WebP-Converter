from io import BytesIO

from PIL import Image


async def convert(io_data: BytesIO, format='WEBP', quality=95) -> BytesIO:
    # Чтение байтов данных из объекта BytesIO
    pic = io_data.read()
    # Открываем изображение из байтовых данных и меняем размер
    img = Image.open(BytesIO(pic)).resize((512, 512))
    out = BytesIO()
    # Сжимаем изображение и сохраняем в формате WebP
    img.save(out, format, quality=quality)
    # Проверяем размер файла и уменьшаем качество, пока не уложимся в 64 КБ
    while out.tell() > 64 * 1024:  # Проверяем размер данных в BytesIO объекте, если много уменьшаем
        quality -= 1
        # Сбрасываем указатель записи в начало объекта BytesIO и очищаем данные в объекте BytesIO
        out.seek(0)
        out.truncate(0)
        img.save(out, format, quality=quality)
    # Возвращаем указатель чтения в начало объекта BytesIO
    out.seek(0)
    return out
