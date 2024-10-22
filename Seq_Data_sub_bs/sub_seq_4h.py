import pandas as pd
from tqdm import tqdm

sub_station_df = pd.read_csv("0401SubCoorNew.csv")
sub_record_df = pd.read_csv("0216AvaliableSub.csv")

# 读取地铁站坐标, 并按照站点排序
sub_station_df = sub_station_df[['Station_Latitude','Station_Longitude','staindex']].sort_values(by='staindex')
# 读取地铁站记录
sub_record_df = sub_record_df[['timestamp','station_entry','station_exit','staindex']]

# 按照4小时为一个时间段进行整理
for i in tqdm(range(len(sub_record_df))):
    dt = pd.to_datetime(sub_record_df['timestamp'].iloc[i])
    timestamp_int = int(dt.timestamp())
    timestamp_new = timestamp_int - timestamp_int % 14400 # 按照4小时为一个时间段
    new_dt = pd.to_datetime(timestamp_new, unit='s')
    sub_record_df.loc[i,'timestamp'] = new_dt

# 按照时间戳和站点索引排序
sub_record_df = sub_record_df.sort_values(by=['timestamp','staindex'], ascending=[True,True])

# print(sub_record_df.head(100))
outliers = []

# 整理出按照时间顺序作为记录行，每行包括各个站点该时刻进站/出站的人数
entry_list = [0 for i in range(len(sub_station_df))]
exit_list = [0 for j in range(len(sub_station_df))]
FMR_list = [] # entry count
LMR_list = [] # exit count
last_time = pd.to_datetime(sub_record_df['timestamp'].iloc[0])
this_time = None
this_time_station_index = 0
for i in tqdm(range(len(sub_record_df))):
    this_time = pd.to_datetime(sub_record_df['timestamp'].iloc[i])
    if this_time - last_time > pd.Timedelta('2 hours'):
        print("this time",this_time)
        print("last time",last_time)
        print(i)
        # 新的时间戳，记录上一个时间戳的数据
        FMR_list.append(entry_list)
        LMR_list.append(exit_list)
        entry_list = [0 for i in range(len(sub_station_df))]
        exit_list = [0 for j in range(len(sub_station_df))]
        last_time = this_time
        this_time_station_index = 0
    this_index = sub_record_df['staindex'].iloc[i]
    if sub_station_df['staindex'].iloc[this_time_station_index] == this_index:
        # 此时刻记录的站点与当前站点相同
        entry_list[this_time_station_index] += sub_record_df['station_entry'].iloc[i]
        exit_list[this_time_station_index] += sub_record_df['station_exit'].iloc[i]
    else:
        # 此时刻记录的站点与当前站点不同，找到当前站点的索引
        if sub_station_df[sub_station_df['staindex'] == this_index].empty:
            if this_index not in outliers:
                outliers.append(this_index)
            print("not found")
            continue
        while sub_station_df['staindex'].iloc[this_time_station_index] != this_index:
            if this_time_station_index==len(sub_station_df)-1:
                print("this time station index",this_time_station_index)
                print("this index",this_index)
            # print(sub_station_df['staindex'].iloc[this_time_station_index])
            this_time_station_index += 1
        entry_list[this_time_station_index] += sub_record_df['station_entry'].iloc[i]
        exit_list[this_time_station_index] += sub_record_df['station_exit'].iloc[i]
    # 最终更新索引
    this_time_station_index += 1

# 将最后一个时间戳的数据加入
FMR_list.append(entry_list)
LMR_list.append(exit_list)

# 将两个列表分别转换为DataFrame，并存入对应的csv文件
FMR_df = pd.DataFrame(FMR_list, columns=sub_station_df['staindex'])
LMR_df = pd.DataFrame(LMR_list, columns=sub_station_df['staindex'])
FMR_df.to_csv("0605FMR_sub.csv", index=False)
LMR_df.to_csv("0605LMR_sub.csv", index=False)
#将outliers存入csv文件
outliers_df = pd.DataFrame(outliers, columns=['outliers'])
outliers_df.to_csv("outliers_sub.csv", index=False)











