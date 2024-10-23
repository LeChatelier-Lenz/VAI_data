import pandas as pd


def sort_taxi_df(dir_path,start_m,end_m,time_col):
    '''
    读取指定目录下的所有parquet文件，按照时间列排序
    :param dir_path:
    :param start_m: 开始月份
    :param end_m: 结束月份
    :param time_col: 有pickup和dropoff两种
    :return:
    '''
    y_result_df = pd.DataFrame()
    g_result_df = pd.DataFrame()
    for i in range(start_m,end_m+1):
        green_df = pd.read_parquet(dir_path+"green_tripdata_2021-"+str(i).zfill(2)+".parquet")
        green_df = green_df[[f'lpep_{time_col}_datetime','PULocationID', 'DOLocationID']].sort_values(by=f"lpep_{time_col}_datetime")
        yellow_df = pd.read_parquet(dir_path+"yellow_tripdata_2021-"+str(i).zfill(2)+".parquet")
        yellow_df = yellow_df[[f'tpep_{time_col}_datetime','PULocationID', 'DOLocationID']].sort_values(by=f"tpep_{time_col}_datetime")
        y_result_df = pd.concat([y_result_df,yellow_df])
        g_result_df = pd.concat([g_result_df,green_df])
    # g_result_df.to_csv("green_tripdata_2021-"+str(start_m).zfill(2)+"-"+str(end_m).zfill(2)+".csv", index=False)
    return y_result_df,g_result_df


def sort_bike_df(start_m,end_m,sort_col):
    '''
    读取指定目录下的所有csv文件，按照时间列排序
    :param start_m: 开始月份
    :param end_m: 结束月份
    :param sort_col: 有started_at和ended_at两种
    :return:
    '''
    result_df = pd.DataFrame()
    for i in range(start_m,end_m+1):
        root_path = "2021"+str(i).zfill(2)+"-citibike-tripdata"
        # 每个文件夹名称为"2021{str(i).zfill(2)}-citibike-tripdata"
        # 每个文件夹下都有4个csv文件，名称为文件夹名称+“_1”、“_2”、“_3”、“_4”
        this_mouth_df = pd.DataFrame()
        for j in range(1, 5):
            df = pd.read_csv(root_path+"/"+root_path+"_"+f"{j}.csv")
            df = df[['started_at','ended_at','start_station_name','end_station_name']]
            this_mouth_df = pd.concat([this_mouth_df,df])
        this_mouth_df = this_mouth_df.sort_values(by=sort_col)
        result_df = pd.concat([result_df,this_mouth_df])
    return result_df

