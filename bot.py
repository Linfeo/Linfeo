import telebot
import re
from flask import Flask, request
from threading import Thread
from waitress import serve  # WSGI-сервер для продакшена (Windows + Render)

API_TOKEN = '7636596309:AAFequmAPe6tb_cTDK3-9V7KQONlBLzHuiU'
bot = telebot.TeleBot(API_TOKEN)

user_products = {}

# Создаем Flask-приложение для "Keep-Alive"
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_products[chat_id] = []
    bot.send_message(chat_id, "Привет! Введи товары и цены")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    if message.text.startswith('/up'):
        if not user_products.get(chat_id):
            bot.send_message(chat_id, "Ваш список товаров пуст. Сначала добавьте товары.")
        else:
            bot.send_message(chat_id, "Введите сумму наценки:")
            bot.register_next_step_handler(message, apply_markup)
        return

    try:
        user_products[chat_id] = message.text.splitlines(keepends=True)  # Сохраняем форматирование с пустыми строками
        bot.send_message(chat_id, "Товары добавлены. Введите команду /up для изменения цен или добавьте новые товары.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")

def apply_markup(message):
    chat_id = message.chat.id
    try:
        markup = float(message.text.replace(',', '.')) / 1000

        updated_products = []
        for line in user_products[chat_id]:
            if line.strip() == "":  # Оставляем пустые строки без изменений
                updated_products.append(line)
                continue

            match = re.search(r"(.+?)\s*[-:]*\s*(\d+[.,]?\d*)[^\d]*$", line)
            if match:
                name = match.group(1).strip()
                numeric_price = match.group(2).replace(',', '.')

                try:
                    price_value = float(numeric_price)
                    updated_price = price_value + markup
                    updated_price_str = f"{updated_price:.3f}"

                    updated_line = re.sub(
                        r"(\d+[.,]?\d*)([^\d]*)$",
                        lambda m: f"{updated_price_str}{m.group(2)}",
                        line
                    )
                    updated_products.append(updated_line)
                except ValueError:
                    updated_products.append(line)  # Если цена не разобралась, оставляем строку без изменений
            else:
                updated_products.append(line)  # Если строка не содержит цену, просто оставляем ее

        bot.send_message(chat_id, "".join(updated_products))  # Возвращаем текст с пустыми строками
        user_products[chat_id] = []
        bot.send_message(chat_id, "Вы можете ввести новые товары.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите числовое значение наценки.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")

# Запускаем Flask-сервер через WSGI (waitress)
if __name__ == "__main__":
    Thread(target=bot.polling, kwargs={"none_stop": True}).start()  # Бот работает в фоновом режиме
    serve(app, host="0.0.0.0", port=10000)  # Flask работает через waitress (продакшен-сервер)
