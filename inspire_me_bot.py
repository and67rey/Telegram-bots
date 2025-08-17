import os
import telebot
import requests
from deep_translator import GoogleTranslator

from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# URL для получения случайной цитаты
ZEN_QUOTES_URL = 'https://zenquotes.io/api/random'

# Словарь для хранения выбранного языка пользователей
user_language = {}

# Функция для получения случайной цитаты
def get_random_quote():
    try:
        response = requests.get(ZEN_QUOTES_URL)
        if response.status_code == 200:
            data = response.json()
            quote = f"{data[0]['q']} — {data[0]['a']}"
            return quote
        else:
            return "Не удалось получить цитату, попробуйте позже."
    except Exception as e:
        print(f"Ошибка при получении цитаты: {e}")
        return "Произошла ошибка при получении цитаты."


# Функция для перевода цитаты на русский язык
def translate_to_russian(text):
    try:
        translated = GoogleTranslator(source='en', target='ru').translate(text)
        return translated
    except Exception as e:
        print(f"Ошибка при переводе: {e}")
        return "Не удалось перевести цитату."


# Команда /start - приветственное сообщение и установка языка по умолчанию
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_language[user_id] = 'rus'  # Устанавливаем язык по умолчанию на русский
    bot.reply_to(
        message,
        "👋 Привет! Я - ваш мотивационный бот! Я могу помочь вам начать день с вдохновения.\n"
        "Используйте команду /motivate, чтобы получить случайную мотивирующую цитату.\n"
        "Для изменения языка используйте команды /english и /russian."
    )


# Команда /help - описание работы с ботом
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        "❓ Вот что я умею:\n"
        "/start - Приветственное сообщение и установка русского языка по умолчанию\n"
        "/help - Краткая информация о боте и его функциях\n"
        "/motivate - Получите случайную мотивирующую цитату\n"
        "/english - Переключение на английский язык\n"
        "/russian - Переключение на русский язык"
    )


# Команда /motivate - отправка мотивирующей цитаты в зависимости от выбранного языка
@bot.message_handler(commands=['motivate'])
def send_motivation(message):
    user_id = message.from_user.id
    quote = get_random_quote()

    # Проверяем выбранный язык пользователя
    if user_language.get(user_id) == 'rus':
        # Переводим цитату на русский
        quote = translate_to_russian(quote)

    bot.reply_to(message, quote)


# Команда /english - переключение на английский язык
@bot.message_handler(commands=['english'])
def set_english(message):
    user_id = message.from_user.id
    user_language[user_id] = 'eng'
    bot.reply_to(message, "🌍 Язык установлен на английский. Теперь цитаты будут на английском языке.")


# Команда /russian - переключение на русский язык
@bot.message_handler(commands=['russian'])
def set_russian(message):
    user_id = message.from_user.id
    user_language[user_id] = 'rus'
    bot.reply_to(message, "🌍 Язык установлен на русский. Теперь цитаты будут на русском языке.")


# Запуск бота
bot.polling()