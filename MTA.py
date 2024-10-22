#!/usr/bin/env python


# 尝试直接使用MTA官方API获取数据
# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata
import numpy as np
from tqdm import tqdm

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
# client = Socrata("data.ny.gov", None)

# Example authenticated client (needed for non-public datasets):
client = Socrata("data.ny.gov",
                 "aLxec942edMfPUgdTmENdJQZn",
                 username="lechate0222@gmail.com",
                 password="031716Cqp0222")

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.

station_results = client.get("39hk-dx4f")

# results = client.get("py8k-a8wg", limit=1000)
# Convert to pandas DataFrame
# results_df = pd.DataFrame.from_records(results)

station_results_df = pd.DataFrame.from_records(station_results)

# print(results_df)
#
# print(station_results_df)

# 取出station_results_df中的station_id 和 stop_name列并记录到数组中
# 一共有496个station
station_id = station_results_df['station_id'].values
stop_name = station_results_df['stop_name'].values
# for i in range(len(station_id)):
#     print(station_id[i], stop_name[i])


# MTA Subway Turnstile Usage Data: 2020
# total rows: 13318000
# 每一次取数据上限为1000个，所以一共需要取13318次,累积到一个dataframe中
# 一共有11个列
data = []
for i in tqdm(range(13318)):
    results = client.get("py8k-a8wg", limit=1000, offset=i*1000)
    data.append(pd.DataFrame.from_records(results))
data_df = pd.concat(data, ignore_index=True)

#