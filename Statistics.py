import matplotlib.pyplot as plt
from datetime import datetime
from DataBase import Redis, Class_, unix_to_datetime


def water_spilled(people: list | int) -> int:
    """
    Возвращает количество воды, что вытеснило N человек
    пока 50 литров на человека
    :param people: Список людей или количество людей
    :type people: list
    :return: Количество воды в литрах на N людей
    :rtype: int
    """
    if type(people) == int:
        return people * 50
    if type(people) == list:
        return len(people) * 50


def hist_pool_load(start_date: datetime, end_date: datetime, gender: Class_ = None) -> None:
    db = Redis()
    entered = db.get_count(start_date, end_date, "enter", 1)
    exitted = db.get_count(start_date, end_date, "exit", 1)

    if gender:
        entered = entered.get(gender, [])
        exitted = exitted.get(gender, [])
    else:
        entered = entered.get("man", []) + entered.get("woman", []) + entered.get("kid", [])
        exitted = exitted.get("man", []) + exitted.get("woman", []) + exitted.get("kid", [])
    if not (entered and exitted):
        print("Нет данных за указанный период")
        return

    combined = [(unix_to_datetime(time), enter_people, exit_people) for (time, enter_people), (_, exit_people) in
                zip(entered, exitted)]

    print(len(entered), len(exitted))
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
    plt.show()


if __name__ == "__main__":
    hist_pool_load(datetime(2000, 6, 15, 0), datetime(2000, 6, 15, 15), "woman")
