import pandas as pd
from tqdm import tqdm

from lt_1h_3m.sort_3m_df import sort_bike_df



# 生成sg中的自行车站点-出租车区域的映射
# 先根据自信车站点信息构建"站名"-序号的映射
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
total_od_num = len(taxi_zones_df) * len(taxi_zones_df)


# bike的实际trip数据
bs_df = sort_bike_df(6,8,"started_at")


# print(bike_taxi_dist)
def count_bike_sg(df,time_col,o_id_col,d_id_col):
    # 整理出按照时间顺序作为记录行，每行包括各个站点该时刻进站/出站的人数
    end_list = [0 for j in range(total_od_num)]
    od_list = []
    # 因为有一些脏数据，需要去除早于2021-06-01 00:00:00的数据
    df = df[df[time_col] >= "2021-06-01 00:00:00"]
    # this_time_station_index = 0
    df = df.sort_values(by=[time_col,o_id_col], ascending=[True, True])
    init_time = pd.to_datetime(df[time_col].iloc[0])
    # print(init_time)
    init_time_stamp = int(init_time.timestamp())
    fixed_time = pd.to_datetime(init_time_stamp-(init_time_stamp % 3600), unit='s')
    print(fixed_time)
    for k in tqdm(range(len(df))):
        this_time = pd.to_datetime(df[time_col].iloc[k])
        if this_time - fixed_time >= pd.Timedelta('1 hours'):
            # 新的时间戳，记录上一个时间戳的数据
            od_list.append(end_list)
            end_list = [0 for j in range(total_od_num)]
            this_time_stamp = int(this_time.timestamp())
            fixed_time = pd.to_datetime(this_time_stamp-(this_time_stamp % 3600), unit='s')
        this_o_index = get_station_id(df[o_id_col].iloc[k])
        if this_o_index == -1:
            continue
        if this_o_index > len(taxi_zones_df):
            continue
        # print(this_o_index)
        this_d_index = get_station_id(df[d_id_col].iloc[k])
        if this_d_index == -1:
            continue
        if this_d_index > len(taxi_zones_df):
            continue
        # print(this_d_index)
        try:
            end_list[(bike_taxi_dict[this_o_index]-1)*len(taxi_zones_df)+(bike_taxi_dict[this_d_index]-1)] += 1 # 比如 o:0-d:0 存在第一个位置
        except Exception as e:
            print(this_o_index,this_d_index)
            print(e)
            break
    print(len(od_list))
    return od_list


if __name__ == '__main__':
    od_list = count_bike_sg(bs_df,"started_at","start_station_name","end_station_name")
    headers = [str(i) + "-" + str(j) for i in range(1,len(taxi_zones_df)+1) for j in range(1,len(taxi_zones_df)+1)]
    od_df = pd.DataFrame(od_list)
    with open('bs_od_overSG_1h.csv', 'w', encoding='utf-8', newline='') as f:
        # 写入自定义表头
        # f.write(','.join(headers) + '\n')
        # 将 DataFrame 写入 CSV，不写入原有的列名
        od_df.to_csv(f, header=False, index=False)
    print("CSV文件已生成，包含自定义表头。")


