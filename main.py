import logging
import os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOOSING, TYPING_REPLY = range(2)

# ID администратора
ADMIN_ID = 705415199  # Вставь свой Telegram ID (например, 123456789)

# Тексты для ответов
WELCOME_MESSAGE = (
    "Привет, житель Великих Лук! 👋 Это бот «Великолукское комьюнити». "
    "Выбери, что хочешь сделать:"
)
NEWS_MESSAGE = (
    "📢 Отлично, расскажи свою новость про Великие Луки! "
    "Напиши подробности, отправь фото, видео или что угодно, и мы рассмотрим для публикации."
)
EVENT_MESSAGE = (
    "🎉 Хочешь предложить мероприятие или сотрудничество? "
    "Расскажи, что планируешь: текст, фото, видео или что-то ещё!"
)
CONTACT_MESSAGE = (
    "📞 Нужна помощь или хочешь связаться с админом? "
    "Напиши сообщение, отправь медиа или перешли что-то, и мы ответим!"
)

# Создание клавиатуры
reply_keyboard = [
    ["📢 Предложить новость"],
    ["🎉 Предложить мероприятие"],
    ["📞 Связь с админом"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога, показываем кнопки"""
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=markup)
    return CHOOSING

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пользователя"""
    user_data = context.user_data
    text = update.message.text
    user_data['choice'] = text

    if text == "📢 Предложить новость":
        await update.message.reply_text(NEWS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    elif text == "🎉 Предложить мероприятие":
        await update.message.reply_text(EVENT_MESSAGE, reply_markup=ReplyKeyboardRemove())
    elif text == "📞 Связь с админом":
        await update.message.reply_text(CONTACT_MESSAGE, reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Пожалуйста, выбери одну из кнопок!", reply_markup=markup)
        return CHOOSING

    return TYPING_REPLY

async def send_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пересылка сообщения администратору"""
    user_data = context.user_data
    user = update.message.from_user
    choice = user_data.get('choice', 'Неизвестный выбор')

    # Формируем текстовое сообщение с информацией о пользователе
    admin_message1 = (
        "-----------------------------------------------------------------------------------------\n\n"
        f"📩 Новое сообщение от @{user.username} (ID: {user.id})\n"
        f"Категория: {choice}\n"
    )
    admin_message2 = (
        f"/reply {user.id} "
    )

    # Отправляем информацию о пользователе админу
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message1)
    # Пересылаем оригинальное сообщение админу
    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message2)

    # Подтверждение пользователю
    await update.message.reply_text(
        "Спасибо за сообщение! 🙌 Мы получили его и скоро рассмотрим. "
        "Хочешь отправить ещё что-то? Выбери действие:", reply_markup=markup
    )
    return CHOOSING

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для ответа пользователю, только для админа"""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Эта команда только для админа! 😊")
        return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Используй: /reply <user_id> <текст ответа>")
            return

        user_id = int(args[0])
        reply_text = " ".join(args[1:])

        # Отправляем ответ пользователю
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📬 Ответ от «ВЛК»: \n{reply_text}"
        )
        # Подтверждение админу
        await update.message.reply_text(f"Сообщение отправлено пользователю {user_id}!")

    except ValueError:
        await update.message.reply_text("Ошибка: user_id должен быть числом. Пример: /reply 123456789 Привет!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке: {str(e)}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    await update.message.reply_text(
        "Пока, житель Великих Лук! Если захочешь вернуться, просто напиши /start.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    # Вставь свой токен от @BotFather
    TOKEN = os.getenv("7307124408:AAGap9FL3Azhgb0qZb_Psr7wQjjxl2-wXLk")
    application = Application.builder().token(TOKEN).build()

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(
                filters.Regex('^(📢 Предложить новость|🎉 Предложить мероприятие|📞 Связь с админом)$'),
                button_handler
            )
        ],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex('^(📢 Предложить новость|🎉 Предложить мероприятие|📞 Связь с админом)$'),
                    button_handler
                ),
                MessageHandler(
                    filters.ALL & ~filters.Regex('^(📢 Предложить новость|🎉 Предложить мероприятие|📞 Связь с админом)$') & ~filters.COMMAND,
                    lambda update, context: update.message.reply_text("Пожалуйста, выбери одну из кнопок!👇", reply_markup=markup) or CHOOSING
                )
            ],
            TYPING_REPLY: [
                MessageHandler(filters.ALL & ~filters.COMMAND, send_to_admin)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("reply", reply))

    # Запуск бота через polling
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )


if __name__ == '__main__':
    main()
