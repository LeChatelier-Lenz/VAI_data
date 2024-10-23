import pandas as pd
from tqdm import tqdm

from lt_1h_3m.sort_3m_df import sort_bike_df

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
taxi_bike_dist = {}
taxi_bike_df = pd.read_csv("sg_taxi_area.csv")
for i in range(len(taxi_bike_df)):
    taxi_zone_id = taxi_bike_df["taxi_zone_id"].iloc[i]
    bike_station_list = eval(taxi_bike_df["bs_staname"].iloc[i])
    if len(bike_station_list) == 0:
        continue
    taxi_bike_dist[taxi_zone_id] = []
    for j in range(len(bike_station_list)):
        bike_station_id = station_dict[bike_station_list[j]]
        taxi_bike_dist[taxi_zone_id].append(bike_station_id)
        bike_taxi_dict[bike_station_id] = taxi_zone_id

# 读取出租车区域信息
taxi_zones_df = pd.read_csv("taxi_zones.csv")
taxi_zones_df = taxi_zones_df[["LocationID"]].sort_values(by="LocationID")
# 处理提取需要的几列数据
bs_record_df = sort_bike_df(6,8,"started_at")


# 先按照开始时间计算LMR数据
bs_record_df_start = bs_record_df[['started_at','start_station_name']]
bs_record_df_start.sort_values(by=['started_at','start_station_name'], ascending=[True,True])
bs_record_df_start = bs_record_df_start[bs_record_df_start['started_at'] >= "2021-06-01 00:00:00"]
init_time = pd.to_datetime(bs_record_df_start['started_at'].iloc[0])
init_time_stamp = int(init_time.timestamp())
print(init_time)
for r in tqdm(range(len(taxi_zones_df))):
    # 遍历出租车区域id
    taxi_zone_id = taxi_zones_df['LocationID'].iloc[r]
    # 如果该区域没有自行车站点，则跳过
    if taxi_zone_id not in taxi_bike_dist:
        continue
    # 获取该区域内的自行车站点列表（索引）
    bike_station_list = taxi_bike_dist[taxi_zone_id]
    # 新的一个区域，初始化LMR_list
    LMR_list = []
    # 遍历该区域内的自行车站点（名称）
    for j in range(len(bike_station_list)):
        this_sta_name = bike_stations_df.iloc[bike_station_list[j]].values[0]
        # print(this_sta_name)
        # 获取该站点的tripdata
        this_data_df = bs_record_df_start[bs_record_df_start['start_station_name'] == this_sta_name]
        # 每一个自行车站点，新一次遍历都要重新初始化时间戳
        fixed_time = pd.to_datetime(init_time_stamp-(init_time_stamp % 3600), unit='s')
        # print(fixed_time)
        this_column = []
        this_value = 0
        # 遍历该区域内该自行车站点的tripdata
        for i in range(len(this_data_df)):
            # 该区域内的自行车站点的tripdata是按照时间顺序排列的
            # 新的时间戳，记录上一个时间戳的数据
            this_time = pd.to_datetime(this_data_df['started_at'].iloc[i])
            if this_time - fixed_time >= pd.Timedelta('1 hours'):
                # 超过1小时，更新时间戳，记录数据
                # 更新该区域内的自行车站点的数据
                # 计算
                this_column.append(this_value)
                for k in range((this_time - fixed_time) // pd.Timedelta('1 hours')-1):
                    this_column.append(0)
                this_value = 1
                this_time_stamp = int(this_time.timestamp())
                fixed_time = pd.to_datetime(this_time_stamp-(this_time_stamp % 3600), unit='s')
            # 没有超过1小时，继续累加
            this_value += 1
        # print(this_column)
        # 该区域内的第j个自行车站点的数据处理完毕
        LMR_list.append(this_column)
    # 以最长的为准，其余的补0
    max_len = max([len(i) for i in LMR_list])
    for i in range(len(LMR_list)):
        while len(LMR_list[i]) < max_len:
            LMR_list[i].append(0)
    # 转置
    LMR_list = list(map(list, zip(*LMR_list)))
    LMR_df = pd.DataFrame(LMR_list)
    LMR_df.to_csv("./bs_LMR_insideSG_1h/bs_LMR_insideSG_1h_zone-id-"+str(taxi_zone_id)+".csv",index=False,header=False)


