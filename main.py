import os
import threading
from flask import Flask
from google import genai
import telebot

app = Flask(__name__)


@app.route("/")
def home():
    return "Riveria is alive!"


# Берем ключи из настроек хостинга (Environment Variables)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

RIVERIA_PERSONA = (
    "Ты — Риверия Лиос Альв из аниме 'DanMachi'. "
    "Ты — могущественная эльфийка, королевская особа, рассудительная, спокойная, мудрая "
    "и заботливая, как старшая наставница или матушка. Общаешься сдержанно, но с глубоким уважением "
    "к собеседнику, иногда можешь строго подколоть за глупости. Отвечай на русском языке."
)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        message.chat.id, "Привет! Я Риверия, твой личный бот. Все работает!"
    )


# Принимаем только текстовые сообщения, чтобы не падать на стикерах и фото
@bot.message_handler(content_types=["text"])
def chat_with_riveria(message):
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message.text,
            config={"system_instruction": RIVERIA_PERSONA},
        )
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        print(f"ОШИБКА: {e}")
        bot.send_message(
            message.chat.id, "Хм... Магия дала сбой, смертный. Попробуй еще раз."
        )


def run_bot():
    bot.infinity_polling(none_stop=True)


if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Читаем порт, который выдаст Render, или берем 10000 по умолчанию
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)