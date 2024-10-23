import pandas as pd
from tqdm import tqdm

from lt_1h_3m.sort_3m_df import sort_taxi_df


taxi_zones_df = pd.read_csv("taxi_zones.csv")
taxi_zones_df = taxi_zones_df[["the_geom","LocationID"]].sort_values(by="LocationID")

total_od_num = len(taxi_zones_df) * len(taxi_zones_df)

yellow_df,green_df = sort_taxi_df("202106-678-taxi/",6,8,"pickup")


def count_taxi_sg(df,time_col,o_id_col,d_id_col):
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
    for i in tqdm(range(len(df))):
        this_time = pd.to_datetime(df[time_col].iloc[i])
        if this_time - fixed_time >= pd.Timedelta('1 hours'):
            # 新的时间戳，记录上一个时间戳的数据
            od_list.append(end_list)
            end_list = [0 for j in range(total_od_num+1)]
            this_time_stamp = int(this_time.timestamp())
            fixed_time = pd.to_datetime(this_time_stamp-(this_time_stamp % 3600), unit='s')
            this_time_station_index = 0
        this_o_index = int(df[o_id_col].iloc[i])
        if this_o_index > len(taxi_zones_df):
            continue
        # print(this_o_index)
        this_d_index = int(df[d_id_col].iloc[i])
        if this_d_index > len(taxi_zones_df):
            continue
        # print(this_d_index)
        try:
            end_list[(this_o_index-1)*len(taxi_zones_df)+(this_d_index-1)] += 1 # 比如 o:0-d:0 存在第一个位置
        except Exception as e:
            print(this_o_index,this_d_index)
            print(e)
            break
    print(len(od_list))
    return od_list


if __name__ == '__main__':
    # count_taxi_sg(fhv_df,"pickup_datetime","PUlocationID","DOlocationID")
    g_od = count_taxi_sg(green_df,"lpep_pickup_datetime","PULocationID","DOLocationID")
    y_od = count_taxi_sg(yellow_df,"tpep_pickup_datetime","PULocationID","DOLocationID")
    od_list = []
    max_len = max(len(g_od),len(y_od))
    for i in range(max_len):
        if i < len(g_od):
            g = g_od[i]
        else:
            g = [0 for j in range(total_od_num)]
        if i < len(y_od):
            y = y_od[i]
        else:
            y = [0 for j in range(total_od_num)]
        od_list.append([sum(x) for x in zip(g,y)])

    # headers = [str(i) + "-" + str(j) for i in range(1,len(taxi_zones_df)+1) for j in range(1,len(taxi_zones_df)+1)]
    od_df = pd.DataFrame(od_list)
    # 用parquet格式存储
    # od_df.to_parquet("taxi_od_overSG_1h.parquet")

    with open('taxi_od_overSG_1h.csv', 'w', encoding='utf-8', newline='') as f:
        # 写入自定义表头
        # f.write(','.join(headers) + '\n')
        # 将 DataFrame 写入 CSV，不写入原有的列名
        od_df.to_csv(f, header=False, index=False)
    print("CSV文件已生成，包含自定义表头。")
    od_df.to_csv("taxi_od_overSG_1h.csv",index=False)

