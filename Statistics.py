import matplotlib.pyplot as plt
from datetime import datetime
from DataBase import Redis, Class_, unix_to_datetime


def water_spilled(start_date: datetime, end_date: datetime) -> int:
    """
    Возвращает количество воды, что вытеснило N человек
    пока 50 литров на человека
    :param start_date:
    :param end_date:
    :return: Количество воды в литрах на N людей
    """
    db = Redis()
    everyone = db.get_count(start_date, end_date, "enter", 1)
    man = everyone.get("man", [])
    woman = everyone.get("woman", [])
    kid = everyone.get("kid", [])
    return sum(map(len, (man, woman, kid))) * 50


def hist_pool_load(start_date: datetime, end_date: datetime, gender: Class_ = None):
    db = Redis()
    entered = db.get_count(start_date, end_date, "enter", 1)
    exited = db.get_count(start_date, end_date, "exit", 1)

    if gender:
        entered = entered.get(gender, [])
        exited = exited.get(gender, [])
    else:
        entered = entered.get("man", []) + entered.get("woman", []) + entered.get("kid", [])
        exited = exited.get("man", []) + exited.get("woman", []) + exited.get("kid", [])
    if not (entered and exited):
        print("Нет данных за указанный период")
        return

    combined = [(unix_to_datetime(time), enter_people, exit_people) for (time, enter_people), (_, exit_people) in
                zip(entered, exited)]

    print(len(entered), len(exited))
    hourly_in = {}
    hourly_out = {}
    for time, in_val, out_val in combined:
        hour = time.hour
        if hour not in hourly_in:
            hourly_in[hour] = 0
        if hour not in hourly_out:
            hourly_out[hour] = 0
        hourly_in[hour] = max(in_val, hourly_in[hour])
        hourly_out[hour] = min(out_val, hourly_out[hour])

    hours = list(hourly_in.keys())
    values = [hourly_in[hour] - hourly_out[hour] for hour in hours]

    plt.bar(hours, values, color='blue', alpha=0.7, label='Люди')
    plt.xlabel('Часы')
    plt.ylabel('Количество людей')
    plt.title('Гистограмма загруженности бассейна по часам')
    # plt.show()
    return plt


def chemistry(smth=True):
    return True


if __name__ == "__main__":
    hist_pool_load(datetime(2000, 6, 15, 0), datetime(2000, 6, 15, 15), "woman")
