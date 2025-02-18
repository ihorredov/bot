import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния разговора
(FULL_NAME, BIRTH_DATE, ADDRESS, PHONE, EDUCATION_DATA, SNILS,
 PASSPORT_PHOTO, REGISTRATION_PHOTO, SNILS_PHOTO, EDUCATION_PHOTO, EDUCATION_PHOTO_2) = range(11)

# Временное хранилище данных
participants = {}

# Функции-обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} начал регистрацию")
    
    await update.message.reply_text(
        'Добро пожаловать в систему регистрации на курсы вожатых! '
        'Я помогу вам пройти процесс регистрации. Для начала, пожалуйста, '
        'введите ваши ФИО полностью.'
    )
    return FULL_NAME

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_folder = f'documents/{user.id}'
    os.makedirs(user_folder, exist_ok=True)
    
    participants[user.id] = {'full_name': update.message.text}
    
    # Save user data to text file
    with open(f'{user_folder}/user_data.txt', 'w', encoding='utf-8') as f:
        f.write(f"ФИО: {update.message.text}\n")
    
    await update.message.reply_text(
        'Спасибо! Теперь, пожалуйста, введите вашу дату рождения в формате ДД.ММ.ГГГГ'
    )
    return BIRTH_DATE

async def birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    participants[user.id]['birth_date'] = update.message.text
    
    # Append to user data file
    with open(f'documents/{user.id}/user_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"Дата рождения: {update.message.text}\n")
    
    await update.message.reply_text(
        'Отлично! Теперь введите ваш адрес проживания'
    )
    return ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    participants[user.id]['address'] = update.message.text
    
    # Append to user data file
    with open(f'documents/{user.id}/user_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"Адрес: {update.message.text}\n")
    
    await update.message.reply_text(
        'Теперь введите ваш номер телефона'
    )
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    participants[user.id]['phone'] = update.message.text
    
    # Append to user data file
    with open(f'documents/{user.id}/user_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"Телефон: {update.message.text}\n")
    
    await update.message.reply_text(
        'Введите данные об образовании (учебное заведение, факультет, курс)'
    )
    return EDUCATION_DATA

async def education_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    participants[user.id]['education_data'] = update.message.text
    
    # Append to user data file
    with open(f'documents/{user.id}/user_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"Образование: {update.message.text}\n")
    
    await update.message.reply_text(
        'Введите ваш номер СНИЛС'
    )
    return SNILS

async def snils(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    participants[user.id]['snils'] = update.message.text
    
    # Append to user data file
    with open(f'documents/{user.id}/user_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"СНИЛС: {update.message.text}\n")
    
    await update.message.reply_text(
        'Теперь отправьте фото паспорта (разворот с фото)'
    )
    return PASSPORT_PHOTO

async def passport_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f'documents/{user.id}/passport.jpg'
    await photo_file.download_to_drive(photo_path)
    participants[user.id]['passport_photo_path'] = photo_path
    
    await update.message.reply_text(
        'Теперь отправьте фото прописки'
    )
    return REGISTRATION_PHOTO

async def registration_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f'documents/{user.id}/registration.jpg'
    await photo_file.download_to_drive(photo_path)
    participants[user.id]['registration_photo_path'] = photo_path
    
    await update.message.reply_text(
        'Отправьте фото СНИЛС'
    )
    return SNILS_PHOTO

async def snils_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f'documents/{user.id}/snils.jpg'
    await photo_file.download_to_drive(photo_path)
    participants[user.id]['snils_photo_path'] = photo_path
    
    await update.message.reply_text(
        'Отправьте фото документа об образовании (диплом/студенческий билет)'
    )
    return EDUCATION_PHOTO

async def education_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f'documents/{user.id}/education.jpg'
    await photo_file.download_to_drive(photo_path)
    participants[user.id]['education_photo_path'] = photo_path
    
    await update.message.reply_text(
        'Если у вас есть дополнительные документы об образовании, отправьте их фото или нажмите /skip для завершения'
    )
    return EDUCATION_PHOTO_2

async def education_photo_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f'documents/{user.id}/education2.jpg'
    await photo_file.download_to_drive(photo_path)
    participants[user.id]['education_photo_path_2'] = photo_path
    
    return await finish_registration(update, context)

async def skip_education_photo_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await finish_registration(update, context)

async def finish_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} завершил регистрацию")
    
    await update.message.reply_text(
        'Спасибо за регистрацию! Ваши данные успешно сохранены. '
        'Мы свяжемся с вами для дальнейших инструкций.'
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} отменил регистрацию")
    
    await update.message.reply_text(
        'Регистрация отменена. Вы можете начать заново, используя команду /start'
    )
    return ConversationHandler.END

def main():
    # Создание папки для документов, если её нет
    os.makedirs('documents', exist_ok=True)
    
    # Инициализация бота
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Добавление обработчика разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_date)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            EDUCATION_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, education_data)],
            SNILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, snils)],
            PASSPORT_PHOTO: [MessageHandler(filters.PHOTO, passport_photo)],
            REGISTRATION_PHOTO: [MessageHandler(filters.PHOTO, registration_photo)],
            SNILS_PHOTO: [MessageHandler(filters.PHOTO, snils_photo)],
            EDUCATION_PHOTO: [MessageHandler(filters.PHOTO, education_photo)],
            EDUCATION_PHOTO_2: [
                MessageHandler(filters.PHOTO, education_photo_2),
                CommandHandler('skip', skip_education_photo_2)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Запуск бота
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()