import pandas as pd

radius = 500

seen_bikes = set()


# 自定义聚合函数，过滤重复的bike值
def unique_bikes(bikes):
    unique_list = [bike for bike in bikes if bike not in seen_bikes]
    seen_bikes.update(unique_list)
    return unique_list


dis_df = pd.read_csv("0325StaDistance.csv")
dis_df = dis_df[dis_df['dis'] <= radius]
dis_filter_out_df = dis_df[dis_df['dis'] > radius]
grouped_df = dis_df.groupby('sub')['bike'].apply(unique_bikes).reset_index()
print(grouped_df)
empty_bike_count = grouped_df[grouped_df['bike'].apply(len) == 0].shape[0]
print(empty_bike_count)
print(len(dis_filter_out_df))

