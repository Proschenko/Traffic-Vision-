import matplotlib.pyplot as plt
from datetime import datetime

def water_spilled(people: list) -> int:
    """
    Возвращает количество воды, что вытеснило N человек
    пока 50 литров на человека
    :param people: Список людей
    :type people: list
    :return: Количество воды в литрах на N людей
    :rtype: int
    """
    return len(people) * 50 

def hist_pool_load(time: list, in_people: list, out_people: list) -> None:
    times = [datetime.strptime(time_str, "%H-%M-%S") for time_str in time]
    hourly_in = {}
    hourly_out = {}
    for time, in_val, out_val in zip(times, in_people, out_people):
        hour = time.hour
        if hour not in hourly_in:
            hourly_in[hour] = 0
        if hour not in hourly_out:
            hourly_out[hour] = 0
        hourly_in[hour] += in_val
        hourly_out[hour] += out_val
    
    hours = list(hourly_in.keys())
    values = [hourly_in[hour] for hour in hours]

    plt.bar(hours, values, color='blue', alpha=0.7, label='Вошло людей')
    plt.xlabel('Часы')
    plt.ylabel('Количество людей')
    plt.title('Гистограмма входа и выхода людей по часам')
    plt.show()
    
if __name__ == "__main__":
    hist_pool_load(["00-00-00", "00-10-00", "02-00-00"], [1, 2, 3], [2, 3, 4])
    