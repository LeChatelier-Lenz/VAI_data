import csv
import pandas as pd
from tqdm import tqdm
from sort_blocks import sort_blocks

# 读取0621-67-BikeRecord文件的前100行
df = pd.read_csv("../originals/0621-67-BikeRecord.csv")
df_sorted = df.sort_values(by='start_station_name')
station_sf = pd.read_csv("./0526BikeCoorNew.csv")
stations = station_sf['sta_name']
station_gdf, block_gdf = sort_blocks()
outliers = []


def find_fit_od(origin, dest, od_list):
    # 利用二分查找找到对应的OD(下标)，如果不存在则输出最小的大于它的数的下标
    left = 0
    right = len(od_list) - 1
    while left <= right:
        mid = (left + right) // 2
        if od_list[mid]['origin'] == origin and od_list[mid]['dest'] == dest:
            return mid
        elif od_list[mid]['origin'] < origin or (od_list[mid]['origin'] == origin and od_list[mid]['dest'] < dest):
            # 如果mid的OD小于要找的OD，那么要找的OD在mid的右边
            # 如果mid的OD等于要找的OD，但是mid的dest小于要找的dest，那么要找的OD在mid的右边
            # 类似于字典序的比较
            left = mid + 1
        else:
            right = mid - 1
    return left


od = []
for i in tqdm(range(len(df_sorted))):
    this_record = df_sorted.iloc[i]
    # print(this_record)
    re1 = station_gdf[station_gdf['sta_name'] == this_record['start_station_name']]['cluster']
    if re1.empty:
        print(this_record['start_station_name'], "not found")
        outliers.append(this_record)
        continue
    else:
        this_origin = re1.values[0]
    re2 = station_gdf[station_gdf['sta_name'] == this_record['end_station_name']]['cluster']
    if re2.empty:
        print(this_record['end_station_name'], "not found")
        outliers.append(this_record)
        continue
    else:
        this_dest = re2.values[0]
    # 遍历所有record文件中的数据
    if len(od) == 0:
        od.append({
            'origin': this_origin,
            'dest': this_dest,
            'demand': 1
        })
        print(od[0]['origin'])
        continue
    fit_index = find_fit_od(this_origin, this_dest, od)
    if fit_index < len(od) and od[fit_index]['origin'] == this_origin and od[fit_index]['dest'] == this_dest:
        # 如果找到了对应的OD，那么对应的需求+1
        od[fit_index]['demand'] += 1
    else:
        # 如果没有找到对应的OD，那么插入新的OD
        od.insert(fit_index, {
            'origin': this_origin,
            'dest': this_dest,
            'demand': 1
        })

print(od)
csv_file = 'lt_od_bs.csv'

# 确定CSV文件的标题
fieldnames = ['origin', 'dest', 'demand']

# 使用csv模块逐行写入数据
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    # 写入标题行
    writer.writeheader()

    # 写入OD数据
    writer.writerows(od)

print(f"CSV 文件已生成：{csv_file}")

# 将新生成的聚类区块数据写入到CSV文件
block_gdf.to_csv("block_gdf.csv")

# 将outliers写入到CSV文件
outliers_df = pd.DataFrame(outliers)
outliers_df.to_csv("outliers_bs.csv")


# part = df.head(100)
# print(df['started_at'].head(50))
# date_time = pd.to_datetime(df['started_at'].head(50))
# print(date_time)
#
# part_sorted = part.sort_values(by='started_at')
# print(part_sorted)
