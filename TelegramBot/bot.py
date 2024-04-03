if __name__ == "__main__":
    import sys
    from os.path import dirname
    sys.path.append(dirname(__file__).rpartition('\\')[0])

import time
from threading import Thread

import schedule
import telebot
from telebot import types

from TelegramBot import config
from TelegramBot.handler import handle_pool_hist, handle_water, in_out_handler

bot = telebot.TeleBot(config.TOKEN)

chat = [-1002019934484]  # айди чатов, куда идёт рассылка


def start_schedule():
    global users
    for i in range(24):
        tmp_time = f"{str(i).zfill(2)}:00"
        schedule.every().day.at(tmp_time).do(lambda: in_out_handler(bot, chat))

    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(commands=['spam'])
def add_user(message):
    global users
    user = message.chat.id
    if user not in users:
        users.append(user)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton("Посмотреть загруженность за дату"))
    markup.add(types.KeyboardButton("Посмотреть статистику по воде за дату"))

    bot.send_message(message.chat.id, "Выберите один из вариантов:", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    # bot.send_message(message.chat.id,
    #                  f"Вы выбрали вариант {message.text}. Теперь вы можете продолжить с этим вариантом.")

    if message.text == "Посмотреть загруженность за дату":
        markup = types.InlineKeyboardMarkup()
        man = types.InlineKeyboardButton('Мужчины', callback_data='man')
        woman = types.InlineKeyboardButton('Женщины', callback_data='woman')
        kid = types.InlineKeyboardButton('Дети', callback_data='kid')
        everyone = types.InlineKeyboardButton('Все', callback_data='all')
        markup.add(man, woman, kid, everyone)
        bot.send_message(message.from_user.id, "Выберите по кому составить статистику", reply_markup=markup)
    elif message.text == "Посмотреть статистику по воде за дату":
        bot.send_message(message.chat.id, "Введите дату в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(message, lambda date_message: handle_water(message, bot, date_message))
    else:
        bot.send_message(message.chat.id, users)
        start(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in ("man", "woman", "kid", "all"):
        bot.send_message(call.message.chat.id, "Введите дату в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(call.message,
                                       lambda message: handle_pool_hist(call.message, bot, call.data, message))


def polling():
    bot.polling(none_stop=True)

def main():
    updates_thread = Thread(target=start_schedule)
    polling_thread = Thread(target=polling)

    updates_thread.start()
    polling_thread.start()
    
# RUN
if __name__ == "__main__":
    main()
