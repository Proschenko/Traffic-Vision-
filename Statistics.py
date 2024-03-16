import matplotlib.pyplot as plt

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

def hist_pool_load():
    pass