import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение ключей из переменных окружения
TELEGRAM_TOKEN = "8006295454:AAFydRG2hWmiWOBWvMsll-cRya_TNvG2XpQ"
OWM_API_KEY = "84b72142623da8f342918e8bf7d53e2d"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для погоды.\n"
        "Напиши название города, и я покажу текущую погоду."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text("Просто отправь мне название города!")


def get_weather(city: str) -> str:
    """Запрос погоды через OpenWeatherMap API"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Проверка на ошибки HTTP

        data = response.json()
        if data["cod"] != 200:
            return "Город не найден. Попробуйте еще раз."

        weather = {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].capitalize(),
            "wind": data["wind"]["speed"]
        }

        return (
            f"Погода в {weather['city']}:\n"
            f"🌡 {weather['temp']}°C (ощущается как {weather['feels_like']}°C)\n"
            f"📖 {weather['description']}\n"
            f"💧 Влажность: {weather['humidity']}%\n"
            f"🌬 Ветер: {weather['wind']} м/с"
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса: {e}")
        return "Ошибка соединения. Попробуйте позже."
    except KeyError as e:
        logger.error(f"Ошибка парсинга данных: {e}")
        return "Ошибка обработки данных."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    city = update.message.text.strip()
    if not city:
        await update.message.reply_text("Пожалуйста, введите название города.")
        return

    weather_report = get_weather(city)
    await update.message.reply_text(weather_report)


def main():
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
