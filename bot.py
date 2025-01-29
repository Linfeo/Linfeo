import telebot
import re

API_TOKEN = '7636596309:AAFequmAPe6tb_cTDK3-9V7KQONlBLzHuiU'
bot = telebot.TeleBot(API_TOKEN)

user_products = {}

@bot.message_handler(commands=['start'])
def start(message):
    try:
        chat_id = message.chat.id
        user_products[chat_id] = []
        bot.send_message(chat_id, "Привет! Введи товары и цены")
    except Exception as e:
        handle_error(message, e)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_id = message.chat.id

        if message.text.startswith('/up'):
            if not user_products.get(chat_id):
                bot.send_message(chat_id, "Ваш список товаров пуст. Сначала добавьте товары.")
            else:
                bot.send_message(chat_id, "Введите сумму наценки:")
                bot.register_next_step_handler(message, apply_markup)
            return

        items = message.text.split('\n')
        processed_items = []

        for item in items:
            if not item.strip():  # Пустая строка
                processed_items.append({"raw": item, "processed": None})
                continue

            match = re.search(r"(.+?)\s*[-:]*\s*(\d+[.,]?\d*)[^\d]*$", item)
            if match:
                name = match.group(1).strip()
                numeric_price = match.group(2).replace(',', '.')

                try:
                    price_value = float(numeric_price)
                    processed_items.append({
                        "raw": item,
                        "processed": {"name": name, "price": price_value, "raw_price": item}
                    })
                except ValueError:
                    bot.send_message(chat_id, f"Строка '{item}' пропущена: не удалось извлечь цену.")
            else:
                bot.send_message(chat_id, f"Строка '{item}' пропущена: не удалось извлечь название и цену.")

        user_products[chat_id] = processed_items
        bot.send_message(chat_id, "Товары добавлены. Введите команду /up для изменения цен или добавьте новые товары.")
    except Exception as e:
        handle_error(message, e)

def apply_markup(message):
    try:
        chat_id = message.chat.id
        markup = float(message.text.replace(',', '.')) / 1000

        updated_products = []
        for product in user_products[chat_id]:
            if product["processed"] is None:
                updated_products.append(product["raw"])
                continue

            updated_price = product["processed"]["price"] + markup
            updated_price_str = f"{updated_price:.3f}"

            updated_price_with_suffix = re.sub(
                r"(\d+[.,]?\d*)([^\d]*)$",
                lambda match: f"{updated_price_str}{match.group(2)}",
                product["processed"]["raw_price"]
            )
            updated_products.append(updated_price_with_suffix)

        bot.send_message(chat_id, "\n" + "\n".join(updated_products))
        user_products[chat_id] = []
        bot.send_message(chat_id, "Вы можете ввести новые товары.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите числовое значение наценки.")
    except Exception as e:
        handle_error(message, e)

def handle_error(message, error):
    """
    Обрабатывает ошибки, чтобы бот не завершал работу.
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, (
        "Произошла ошибка! 😔\n"
        f"Описание: {str(error)}\n"
        "Вы можете вернуться к команде /start или проверить входные данные."
    ))
    bot.send_message(chat_id, "Введите /start для начала работы.")
try:
    bot.polling()
except Exception as e:
    print(f"Ошибка в polling: {e}")
