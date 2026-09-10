import random
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "ВАШ_ТОКЕН_БОТА"

# Множество зарегистрированных участников
registered_members = set()

logging.basicConfig(level=logging.INFO)

# Главная клавиатура с навигацией
def main_keyboard():
    keyboard = [
        [KeyboardButton("🎮 Участвовать / Старт"), KeyboardButton("👥 Сколько игроков?")],
        [KeyboardButton("ℹ️ Инструкция")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start и обработка кнопки запуска
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    registered_members.add(user_id)
    
    await update.message.reply_text(
        "👋 Вы успешно зарегистрированы в анонимной игре!\n\n"
        "**Как отправлять:** Просто напишите любой текст мне в ЛС, и я случайным образом перешлю его одному из участников.\n"
        "**Одиночный тест:** Если вы пока один, бот отправит сообщение вам же.",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

# Обработка нажатий на кнопки меню
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 Участвовать / Старт":
        registered_members.add(user_id)
        await update.message.reply_text("✅ Вы в списке игроков!", reply_markup=main_keyboard())

    elif text == "👥 Сколько игроков?":
        count = len(registered_members)
        await update.message.reply_text(f"📊 В игре зарегистрировано участников: {count}")

    elif text == "ℹ️ Инструкция":
        await update.message.reply_text(
            "📖 **Инструкция:**\n"
            "1. Нажмите «Участвовать», чтобы попасть в список.\n"
            "2. Напишите любое текстовое сообщение прямо в этот чат.\n"
            "3. Бот случайно выберет одного игрока из списка и переправит ему ваш текст.\n"
            "4. Никто не узнает, кто кому написал!",
            parse_mode="Markdown"
        )
    else:
        # Если текст не с кнопки, отправляем его как анонимку
        await send_anonymous_message(update, context)

# Логика отправки анонимного сообщения
async def send_anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    registered_members.add(sender_id)

    receivers = [u_id for u_id in registered_members if u_id != sender_id]
    
    # Режим одиночного теста: если других игроков нет, шлем себе
    recipient_id = random.choice(receivers) if receivers else sender_id

    try:
        await context.bot.send_message(
            chat_id=recipient_id,
            text=f"✉️ **Анонимка от случайного игрока:**\n\n{update.message.text}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("🚀 Сообщение анонимно отправлено!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка доставки: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    print("Бот с навигацией запущен...")
    app.run_polling()
