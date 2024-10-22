import pandas as pd
from tqdm import tqdm

bs_station_df = pd.read_csv("0526BikeCoorNew.csv")
bs_record_df = pd.read_csv("../originals/0621-67-BikeRecord.csv")

# 处理提取需要的几列数据
bs_record_df = bs_record_df[['started_at','ended_at','start_station_name','end_station_name']]
bs_station_df = bs_station_df[['sta_name']].sort_values(by='sta_name')

# print(sub_record_df.head(100))
outliers = []

# 整理出按照时间顺序作为记录行，每行包括各个站点该时刻进站/出站的人数
end_list = [0 for i in range(len(bs_station_df))]
FMR_list = [] # end count

last_time = pd.to_datetime(bs_record_df['ended_at'].iloc[0])
this_time = None
this_time_station_index = 0

# 先按照开始时间计算LMR数据
bs_record_df_end = bs_record_df[['ended_at','end_station_name']].sort_values(by=['ended_at','end_station_name'], ascending=[True,True])
init_time = pd.to_datetime(bs_record_df_end['ended_at'].iloc[0])
init_time_stamp = int(init_time.timestamp())
fixed_time = pd.to_datetime(init_time_stamp-(init_time_stamp % 14400), unit='s')
print(fixed_time)
for i in tqdm(range(len(bs_record_df_end))):
    this_time = pd.to_datetime(bs_record_df_end['ended_at'].iloc[i])
    if this_time - fixed_time >= pd.Timedelta('4 hours'):
        # 新的时间戳，记录上一个时间戳的数据
        FMR_list.append(end_list)
        end_list = [0 for i in range(len(bs_station_df))]
        this_time_stamp = int(this_time.timestamp())
        fixed_time = pd.to_datetime(this_time_stamp-(this_time_stamp % 14400), unit='s')
        this_time_station_index = 0
    this_index = bs_record_df_end['end_station_name'].iloc[i]
    if this_time_station_index < len(bs_station_df) and bs_station_df['sta_name'].iloc[this_time_station_index] == this_index:
        # 此时刻记录的站点与当前站点相同
        end_list[this_time_station_index] += 1
    else:
        # 此时刻记录的站点与当前站点不同，找到当前站点的索引
        target = bs_station_df[bs_station_df['sta_name'] == this_index]
        if target.empty:
            if this_index not in outliers:
                outliers.append(this_index)
            continue
        index = target.index[0]
        end_list[index] += 1
        this_time_station_index = index
    this_time_station_index += 1
    # 最终更新索引

# 将最后一个时间戳的数据加入
FMR_list.append(end_list)
FMR_df = pd.DataFrame(FMR_list,columns=bs_station_df['sta_name'])
FMR_df.to_csv("0601FMR_bs.csv",index=False)
