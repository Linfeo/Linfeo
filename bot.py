import telebot
import re
from flask import Flask
from threading import Thread

API_TOKEN = '7636596309:AAFequmAPe6tb_cTDK3-9V7KQONlBLzHuiU'
bot = telebot.TeleBot(API_TOKEN)

user_products = {}

# Создаем Flask-сервер для "Keep-Alive"
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Запускаем Flask в отдельном потоке
Thread(target=run_flask).start()

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
        user_products[chat_id] = message.text.split('\n')  # Сохраняем текст с пустыми строками
        bot.send_message(chat_id, "Товары добавлены. Введите команду /up для изменения цен или добавьте новые товары.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")

def apply_markup(message):
    chat_id = message.chat.id
    try:
        markup = float(message.text.replace(',', '.')) / 1000

        updated_products = []
        for line in user_products[chat_id]:
            if not line.strip():  # Если строка пустая, просто добавляем ее обратно
                updated_products.append("")
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
                    updated_products.append(line)  # Если цена не разобралась, просто оставляем строку как есть
            else:
                updated_products.append(line)  # Если строка не соответствует формату, просто оставляем ее

        bot.send_message(chat_id, "\n".join(updated_products))  # Отправляем текст, сохраняя пустые строки
        user_products[chat_id] = []
        bot.send_message(chat_id, "Вы можете ввести новые товары.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите числовое значение наценки.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")

bot.polling()
