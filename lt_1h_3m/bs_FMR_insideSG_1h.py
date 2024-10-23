import pandas as pd
from tqdm import tqdm

from lt_1h_3m.sort_3m_df import sort_bike_df

# bs_station_df = pd.read_csv("0526BikeCoorNew.csv")
# bs_record_df = sort_bike_df(6,8,"started_at")

bike_stations_df = pd.read_csv("0526BikeCoorNew.csv")
bike_stations_df = bike_stations_df[["sta_name"]]
station_dict = {}
for i in range(len(bike_stations_df)):
    station_dict[bike_stations_df["sta_name"].iloc[i]] = i
# 从sg中提取出自行车站点-出租车区域的映射


def get_station_id(name):
    if name in station_dict:
        return station_dict[name]
    else:
        return -1


bike_taxi_dict = {}
taxi_bike_df = pd.read_csv("sg_taxi_area.csv")
for i in range(len(taxi_bike_df)):
    taxi_zone_id = taxi_bike_df["taxi_zone_id"].iloc[i]
    bike_station_list = eval(taxi_bike_df["bs_staname"].iloc[i])
    if len(bike_station_list) == 0:
        continue
    for j in range(len(bike_station_list)):
        bike_station_id = station_dict[bike_station_list[j]]
        bike_taxi_dict[bike_station_id] = taxi_zone_id

# 读取出租车区域信息
taxi_zones_df = pd.read_csv("taxi_zones.csv")
taxi_zones_df = taxi_zones_df[["LocationID"]].sort_values(by="LocationID")

# 处理提取需要的几列数据
bs_record_df = sort_bike_df(6,8,"ended_at")

# print(sub_record_df.head(100))
outliers = []

# 整理出按照时间顺序作为记录行，每行包括各个站点该时刻进站/出站的人数
end_list = [0 for i in range(len(taxi_zones_df)+1)]
FMR_list = [] # end count

# 先按照开始时间计算LMR数据
bs_record_df_end = bs_record_df[['ended_at','end_station_name']].sort_values(by=['ended_at','end_station_name'], ascending=[True,True])
init_time = pd.to_datetime(bs_record_df_end['ended_at'].iloc[0])
init_time_stamp = int(init_time.timestamp())
fixed_time = pd.to_datetime(init_time_stamp-(init_time_stamp % 3600), unit='s')
print(fixed_time)
for i in tqdm(range(len(bs_record_df_end))):
    this_time = pd.to_datetime(bs_record_df_end['ended_at'].iloc[i])
    if this_time - fixed_time >= pd.Timedelta('1 hours'):
        # 新的时间戳，记录上一个时间戳的数据
        FMR_list.append(end_list)
        end_list = [0 for i in range(len(taxi_zones_df)+1)]
        this_time_stamp = int(this_time.timestamp())
        fixed_time = pd.to_datetime(this_time_stamp-(this_time_stamp % 3600), unit='s')
    this_bike_index = get_station_id(bs_record_df_end['end_station_name'].iloc[i])
    if this_bike_index == -1:
        continue
    # this_index记录的是出租车区域的索引
    try:
        end_list[bike_taxi_dict[this_bike_index]] += 1
    except Exception as e:
        print(e)
        print(bike_taxi_dict[this_bike_index])
        continue

    # 最终更新索引

# 将最后一个时间戳的数据加入
FMR_list.append(end_list)
FMR_df = pd.DataFrame(FMR_list)
FMR_df.to_parquet("bs_FMR_insideSG_1h.parquet")
