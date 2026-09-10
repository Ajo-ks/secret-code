import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

Token = "8930561167:AAG4H9WS3Q-TKm6a73OHrcG7BLCdFbC99Fc"
GROUP_ID = -5427365483

# Множество зарегистрированных участников
registered_members = set()

logging.basicConfig(level=logging.INFO)


# Команда для регистрации в игре
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    registered_members.add(user_id)

    await update.message.reply_text(
        f"✅ {update.effective_user.first_name}, ты зарегистрирован в анонимной игре! "
        "Теперь перейди ко мне в ЛС и отправляй сообщения — я перешлю их случайному игроку."
    )


# Приём анонимных сообщений в ЛИЧКЕ бота
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id

    # Автоматически регистрируем, если пишет в личку
    registered_members.add(sender_id)

    # Ищем доступных получателей (все кроме отправителя)
    receivers = [u_id for u_id in registered_members if u_id != sender_id]

    if not receivers:
        await update.message.reply_text(
            "Пока нет других участников! Попроси друзей написать команду /join в группе."
        )
        return

    recipient_id = random.choice(receivers)

    try:
        await context.bot.send_message(
            chat_id=recipient_id,
            text=f"✉️ **Анонимка от случайного игрока:**\n\n{update.message.text}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("🚀 Сообщение анонимно отправлено!")
    except Exception:
        await update.message.reply_text(
            "Не удалось доставить! Возможно, случайный игрок заблокировал бота или ещё не нажал /start в ЛС."
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Команда /join работает и в группе, и в личке
    app.add_handler(CommandHandler("join", join))

    # Обработка анонимок только в ЛС у бота
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, handle_private_message))

    print("Бот запущен...")
    app.run_polling()
