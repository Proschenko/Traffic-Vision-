if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

import os
import sys
from datetime import datetime, timedelta

from DataBase.Statistics import amount_in_out, hist_pool_load, water_spilled, Gender


def in_out_handler(bot, users):
    delta = timedelta(hours=1)
    # delta = timedelta(hours=0)
    start_time = datetime.now() - delta
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    print(f"Отправляю рассылку: {start_time = }")
    try:
        data = amount_in_out(start_time, end_time)
        for user in users:
            bot.send_message(user, f"С {start_time} до {end_time} вошло: {data[0]}, вышло: {data[1]}")
    except Exception:
        print("Пожалуйста, сообщите администратору, что редис не работает или мне не дали доступ к чату.")


def day_stat_handle(bot, users, last=True):
    delta = timedelta(hours=23, minutes=59, seconds=59)
    start_time = datetime.now() - delta if last else datetime.now()
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + delta
    print(f"Отправляю рассылку: {start_time = }")
    try:
        data = amount_in_out(start_time, end_time)
        for user in users:
            # print(f"Статистика за {start_time.day} число")
            # print(f"С {start_time} до {end_time} вошло: {data[0]}, вышло: {data[1]}")
            bot.send_message(user, f"Статистика за {start_time.day} число")
            bot.send_message(user, f"С {start_time} до {end_time} вошло: {data[0]}, вышло: {data[1]}")
    except Exception:
        print("Пожалуйста, сообщите администратору, что редис не работает или мне не дали доступ к чату.")


def datetime_one_day_from_str(date):
    delta = timedelta(days=1)
    date = date.text
    try:
        start_day = datetime.strptime(date, "%d.%m.%Y")
        end_day = start_day + delta
        # print(start_day, end_day)
        return start_day, end_day
    except Exception:
        return None, None


def handle_pool_hist(message, bot, gender, date):
    start_day, end_day = datetime_one_day_from_str(date)
    if not (start_day or end_day):
        bot.send_message(message.chat.id, "Неверный формат даты")
        return
    try:
        if gender == "all":
            plt = hist_pool_load(start_day, end_day)
        else:
            plt = hist_pool_load(start_day, end_day, gender)
    except Exception:
        bot.send_message(message.chat.id, "Пожалуйста, сообщите администратору, что редис не работает.")
        return
    if not plt:
        bot.send_message(message.chat.id, "Нет данных за указанный период")
        return

    folder = 'telegram_bot/temp/'
    path = f'{folder}pool_load_id{message.chat.id}.png'
    if not os.path.exists(folder):
        os.makedirs(folder)

    plt.savefig(path)
    bot.send_photo(message.chat.id, open(path, 'rb'))
    if os.path.exists(path):
        os.remove(path)
    else:
        print("The file does not exist")


def handle_water(message, bot, date):
    start_day, end_day = datetime_one_day_from_str(date)
    if not (start_day or end_day):
        bot.send_message(message.chat.id, "Неверный формат даты")
        return
    try:
        water = water_spilled(start_day, end_day)
        bot.send_message(message.chat.id, f"{water} л")
    except Exception:
        bot.send_message(message.chat.id, "Пожалуйста, сообщите администратору, что редис не работает.")
        return
