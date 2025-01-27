import telebot
import re

API_TOKEN = '7636596309:AAFequmAPe6tb_cTDK3-9V7KQONlBLzHuiU'
bot = telebot.TeleBot(API_TOKEN)

user_products = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_products[chat_id] = []
    bot.send_message(chat_id,
                     "Привет! Введи товары и цены")

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
        items = message.text.split('\n')
        for item in items:
            if not item.strip():
                continue

            match = re.search(r"(.+?)\s*[-:]*\s*(\d+[.,]?\d*)[^\d]*$", item)
            if match:
                name = match.group(1).strip()
                numeric_price = match.group(2).replace(',', '.')

                try:
                    price_value = float(numeric_price)
                    user_products[chat_id].append({"name": name, "price": price_value, "raw_price": item})
                except ValueError:
                    bot.send_message(chat_id, f"Строка '{item}' пропущена: не удалось извлечь цену.")
            else:
                bot.send_message(chat_id, f"Строка '{item}' пропущена: не удалось извлечь название и цену.")
        bot.send_message(chat_id, "Товары добавлены. Введите команду /up для изменения цен или добавьте новые товары.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
def apply_markup(message):
    chat_id = message.chat.id
    try:

        markup = float(message.text.replace(',', '.')) / 1000

        updated_products = []
        for product in user_products[chat_id]:
            updated_price = product["price"] + markup
            updated_price_str = f"{updated_price:.3f}"

            updated_price_with_suffix = re.sub(
                r"(\d+[.,]?\d*)([^\d]*)$",
                lambda match: f"{updated_price_str}{match.group(2)}",
                product["raw_price"]
            )
            updated_products.append(updated_price_with_suffix)

        bot.send_message(chat_id, "\n" + "\n".join(updated_products))
        user_products[chat_id] = []
        bot.send_message(chat_id, "Вы можете ввести новые товары.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите числовое значение наценки.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")

bot.polling()
