import os
import sys
from datetime import datetime, timedelta
from Statistics import hist_pool_load

sys.path.append(".")


def handle_pool_hist(message, bot, gender, date):
    delta = timedelta(days=1)
    date = date.text
    try:
        start_day = datetime.strptime(date, "%d.%m.%Y")
        end_day = start_day + delta
        print(start_day, end_day)
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат даты")
        return

    if gender == "all":
        plt = hist_pool_load(start_day, end_day)
    else:
        plt = hist_pool_load(start_day, end_day, gender)

    if not plt:
        bot.send_message(message.chat.id, "Нет данных за указанный период")
        return

    folder = 'telegram_bot/temp/'
    path = f'{folder}pool_load_id{message.chat.id}.png'

    plt.savefig(path)
    bot.send_photo(message.chat.id, open(path, 'rb'))
    if os.path.exists(path):
        os.remove(path)
    else:
        print("The file does not exist")
