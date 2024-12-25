import os
import smtplib
from loguru import logger
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from urllib.request import urlretrieve

# Токен Telegram бота
TELEGRAM_TOKEN = ''
# Путь до временного изображения
PHOTO_PATH = 'temporary_image.png'
# Электронная почта Outlook и пароль
OUTLOOK_EMAIL = 'your_email@outlook.com'
OUTLOOK_PASSWORD = 'your_password'
# Получатель
TO_EMAIL = 'recipient_email@domain.com'

class Outlook:
    # Функция для отправки письма с вложением
    def send_email(image_path: str):
        # Создаем MIME объект для письма
        msg = MIMEMultipart()
        msg['From'] = OUTLOOK_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = 'Новое изображение от Telegram бота'
        
        # Открываем изображение и прикрепляем его к письму
        with open(image_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(image_path)}')
            msg.attach(part)

        # Подключаемся к серверу Outlook и отправляем письмо
        try:
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
            server.sendmail(OUTLOOK_EMAIL, TO_EMAIL, msg.as_string())
            server.quit()
            logger.success("Письмо отправлено успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке письма: {e}")
            return False

class Telegram:
    # Функция для обработки сообщений
    async def handle_message(update: Update, context: CallbackContext):
        if update.message.photo:
            # Получаем изображение, await get_file() так как это асинхронная операция
            photo_file = await update.message.photo[-1].get_file()
            
            # Загрузите файл по указанному пути
            urlretrieve(photo_file.file_path, PHOTO_PATH)
            logger.info(f"Изображение загружено в {PHOTO_PATH}")

            await update.message.reply_text('✨Изображение получено и отправлено на почту!')

            # # Отправить изображение по электронной почте
            # response = Outlook().send_email(PHOTO_PATH)
            # # Отправляем пользователю подтверждающее сообщение
            # if response:
            #     await update.message.reply_text('✨Изображение получено и отправлено на почту!')
            # else:
            #     await update.message.reply_text('🚫Не удалось отправить изображение!')
            # Удаляем временный файл
            os.remove(PHOTO_PATH)

# Основная функция
def main():
    # Создаем приложение и регистрируем обработчик сообщений
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    # Регистрируем обработчик сообщений для фото
    application.add_handler(MessageHandler(filters.PHOTO, Telegram().handle_message))
    
    logger.success("Бот успешно запущен!")
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
