import os
import sys
from datetime import datetime, timedelta
sys.path.append(".") # ЭТА ДИЧЬ СТОЯТЬ ДОЛЖНА ДО ИМПОРТА ЛОКАЛЬНЫХ МОДУЛЕЙ
from Statistics import hist_pool_load, water_spilled

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
        bot.send_message(message.chat.id, "Редис мертв, воскресите")
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
        bot.send_message(message.chat.id, "Редис мертв, воскресите")
        return