import pandas as pd

# 读取当前文件夹下所有.parquet文件,转化为dataframe
fhv_df = pd.read_parquet("fhv_tripdata_2021-06.parquet")
green_df = pd.read_parquet("green_tripdata_2021-06.parquet")
yellow_df = pd.read_parquet("yellow_tripdata_2021-06.parquet")

# 读取数据的列名
print(fhv_df.columns)

# 打印数据的前5行
print(fhv_df.head(1))
# 打印数据的后5行
print(fhv_df.tail(1))

# 保存为csv文件
fhv_df.to_csv("fhv_tripdata_2021-06.csv", index=False)
green_df.to_csv("green_tripdata_2021-06.csv", index=False)
yellow_df.to_csv("yellow_tripdata_2021-06.csv", index=False)
