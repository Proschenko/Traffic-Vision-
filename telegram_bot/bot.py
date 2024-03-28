import telebot
from telebot import types
import config
from handler import handle_pool_hist

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton("Посмотреть статистику"))

    bot.send_message(message.chat.id, "Выберите один из вариантов:", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    bot.send_message(message.chat.id,
                     f"Вы выбрали вариант {message.text}. Теперь вы можете продолжить с этим вариантом.")

    if message.text == "Посмотреть статистику":
        markup = types.InlineKeyboardMarkup()
        man = types.InlineKeyboardButton('Мужчины', callback_data='man')
        woman = types.InlineKeyboardButton('Женщины', callback_data='woman')
        kid = types.InlineKeyboardButton('Дети', callback_data='kid')
        everyone = types.InlineKeyboardButton('Все', callback_data='all')
        markup.add(man, woman, kid, everyone)
        bot.send_message(message.from_user.id, "Выберите по кому составить статистику", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in ("man", "woman", "kid", "all"):
        bot.send_message(call.message.chat.id, "Введите дату в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(call.message,
                                       lambda message: handle_pool_hist(call.message, bot, call.data, message))


# RUN
bot.polling(none_stop=True)
