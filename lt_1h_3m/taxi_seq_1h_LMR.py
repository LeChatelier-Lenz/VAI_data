import pandas as pd
from tqdm import tqdm

from lt_1h_3m.sort_3m_df import sort_taxi_df

# 本文件定义为“进入”出租车区域的数据处理
# 所以需要关注 结束时间和目标地点

# 读取地图数据
taxi_zones_df = pd.read_csv("taxi_zones.csv")
taxi_zones_df = taxi_zones_df[["LocationID"]].sort_values(by="LocationID")

yellow_df, green_df = sort_taxi_df("202106-678-taxi/", 6, 8, "pickup")

# 按照每四个小时为一个时间段进行整理，每一行记录包含一个时间段内所有地点的进入人数
# 出租车数据中的每一条记录算作一次进入
# 从开始时间开始，每次遇到新的时间段，记录上一个时间段的数据
# 最终单个出租车数据为一个二维数组，每一行代表一个时间段，每一列代表一个地点的进入人数【时间段数*地点数】
# 分开处理三种出租车数据，最后统一合并，统一用count_taxi()函数处理,输入为三种出租车的dataframe和drop-off时间的列名


def count_taxi(df, time_col, loc_col):
    # 整理出按照时间顺序作为记录行，每行包括各个站点该时刻进站/出站的人数
    end_list = [0 for j in range(len(taxi_zones_df))]
    LMR_list = [] # end count

    # 因为有一些脏数据，需要去除早于2021-06-01 00:00:00的数据
    df = df[df[time_col] >= "2021-06-01 00:00:00"]

    last_time = pd.to_datetime(df[time_col].iloc[0])
    this_time = None
    this_time_station_index = 0

    # 先按照开始时间计算LMR数据
    df = df.sort_values(by=[time_col, loc_col], ascending=[True, True])
    init_time = pd.to_datetime(df[time_col].iloc[0])
    print(init_time)
    init_time_stamp = int(init_time.timestamp())
    fixed_time = pd.to_datetime(init_time_stamp-(init_time_stamp % 3600), unit='s')
    print(fixed_time)

    for i in tqdm(range(len(df))):
        this_time = pd.to_datetime(df[time_col].iloc[i])
        if this_time - fixed_time >= pd.Timedelta('1 hours'):
            # 新的时间戳，记录上一个时间戳的数据
            LMR_list.append(end_list)
            end_list = [0 for i in range(len(taxi_zones_df))]
            this_time_stamp = int(this_time.timestamp())
            fixed_time = pd.to_datetime(this_time_stamp-(this_time_stamp % 3600), unit='s')
            this_time_station_index = 0
        this_index = df[loc_col].iloc[i]
        if this_time_station_index < len(taxi_zones_df) and taxi_zones_df['LocationID'].iloc[this_time_station_index] == this_index:
            # 此时刻记录的站点与当前站点相同
            end_list[this_time_station_index] += 1
        else:
            # 此时刻记录的站点与当前站点不同，找到当前站点的索引
            target = taxi_zones_df[taxi_zones_df['LocationID'] == this_index]
            if target.empty:
                continue
            index = target.index[0]
            end_list[index] += 1
            this_time_station_index = index
        this_time_station_index += 1
        # 最终更新索引

    # 将最后一个时间戳的数据加入
    LMR_list.append(end_list)
    return LMR_list


# fhv_LMR = count_taxi(fhv_df, "pickup_datetime", "PUlocationID")
green_LMR = count_taxi(green_df, "lpep_pickup_datetime", "PULocationID")
yellow_LMR = count_taxi(yellow_df, "tpep_pickup_datetime", "PULocationID")

# 将三种出租车的数据合并,注意要考虑到三种出租车的数据长度不一致，需要补零
LMR_list = []
max_len = max(len(green_LMR), len(yellow_LMR))
for i in range(max_len):
    # if i < len(fhv_LMR):
    #     fhv = fhv_LMR[i]
    # else:
    #     fhv = [0 for j in range(len(taxi_zones_df))]
    if i < len(green_LMR):
        green = green_LMR[i]
    else:
        green = [0 for j in range(len(taxi_zones_df))]
    if i < len(yellow_LMR):
        yellow = yellow_LMR[i]
    else:
        yellow = [0 for j in range(len(taxi_zones_df))]
    LMR_list.append([sum(x) for x in zip(green, yellow)])

LMR_df = pd.DataFrame(LMR_list, columns=taxi_zones_df['LocationID'])
# LMR_df.to_csv("taxi_seq_1h_LMR.csv", index=False)
LMR_df.to_parquet("taxi_seq_1h_LMR.parquet")



