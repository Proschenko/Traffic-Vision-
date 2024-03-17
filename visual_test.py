from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt

from DataBase import Redis, unix_to_datetime

redis = Redis()

start, end = datetime(2024, 3, 17), datetime(2024, 3, 18)
data = redis.get_count(start, end, "exit", 60)["man"]
time, count = zip(*data)
count = np.array(count)
delta_count = np.diff(count, 1)
time = list(map(unix_to_datetime, time))
print(time)
print(count)

plt.bar(time[1:], delta_count, width=0.001)

plt.gcf().autofmt_xdate()
plt.show()
