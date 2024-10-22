import pandas as pd
from shapely import wkt
import geopandas as gpd
from tqdm import tqdm
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



# 分别读取自行车、地铁、出租车站点数据;
bs_station_df = pd.read_csv("../0526BikeCoorNew.csv") # sta_name,la,long
bs_station_gdf = gpd.GeoDataFrame(bs_station_df, geometry=gpd.points_from_xy(bs_station_df.long, bs_station_df.la)).drop(columns=["la","long"]).sort_values(by="geometry").reset_index(drop=True)
sub_station_df = pd.read_csv("../0401SubCoorNew.csv")[["staindex","Station_Latitude","Station_Longitude"]] # staindex,Station_Latitude,Station_Longitude
sub_station_gdf = gpd.GeoDataFrame(sub_station_df, geometry=gpd.points_from_xy(sub_station_df.Station_Longitude, sub_station_df.Station_Latitude)).drop(columns=["Station_Latitude","Station_Longitude"]).sort_values(by="geometry").reset_index(drop=True)
# 注意出租车站点的the_geom列实际上是geopandas的geometry对象，不是经纬度，需要进一步处理
# 将 `the_geom` 列转换为 `MULTIPOLYGON` 几何对象
taxi_zones_df = pd.read_csv("../202106taxi/taxi_zones.csv")
taxi_zones_df['geometry'] = taxi_zones_df['the_geom'].apply(wkt.loads)
# 将 pandas DataFrame 转换为 GeoDataFrame
gdf = gpd.GeoDataFrame(taxi_zones_df, geometry='geometry').drop(columns=["the_geom"]).sort_values(by="LocationID").reset_index(drop=True)

# 根据taxi_zones_df的多边形地理数据，对所有站点进行分组
# 每个组包含三列：taxi_zone_id,bs_staname,sub_staindex，按照taxi_zone_id升序排序
# taxi_zone_id：出租车区域的id
# bs_staname：在该出租车区域多边形内的所有自行车站点名称构成的list
# sub_staindex：在该出租车区域多边形内的所有地铁站点索引构成的list
# 假如有自行车站点或地铁站点不在任何出租车区域内，则划入特殊的区域，taxi_zone_id为-1

# 首先要让geometry信息是处于同一坐标系下,使用标准的WGS84坐标系
bs_station_gdf.set_crs("EPSG:4326", inplace=True)
sub_station_gdf.set_crs("EPSG:4326", inplace=True)
gdf.set_crs("EPSG:4326", inplace=True)


# 用于判断一个点是否在多边形内
def point_in_poly(point, poly):
    '''
    point：geopandas的geometry对象，表示一个点
    poly：geopandas的geometry对象，表示一个多边形
    '''
    return point.within(poly)


# 用于判断一个地铁站点是否在某个出租车区域内
def sub_in_taxi_zone(sub_station, taxi_zone):
    return point_in_poly(sub_station, taxi_zone)


# 用于判断一个自行车站点是否在某个出租车区域内
def bs_in_taxi_zone(bs_station, taxi_zone):
    return point_in_poly(bs_station, taxi_zone)


# 创建结果dataframe
result_df = pd.DataFrame(columns=["taxi_zone_id","bs_staname","sub_staindex"])
result_df["taxi_zone_id"] = gdf["LocationID"].sort_values()

# 先处理自行车站点
bs_staname_list = [[] for i in range(len(gdf))]
# print(bs_station_gdf)
# 循环时跳过index列
for i in tqdm(range(len(bs_station_gdf))):
    bs_station = bs_station_gdf.iloc[i]
    bs_station_in_taxi_zone = False
    for j in range(len(gdf)):
        taxi_zone = gdf.iloc[j]
        if bs_in_taxi_zone(bs_station["geometry"], taxi_zone["geometry"]):
            bs_station_in_taxi_zone = True
            # print(taxi_zone["LocationID"])
            # print(bs_staname_list[taxi_zone["LocationID"]])
            bs_staname_list[taxi_zone["LocationID"]-1].append(bs_station["sta_name"])
            break
    if not bs_station_in_taxi_zone:
        bs_staname_list[-1].append(bs_station["sta_name"])
# 将list的每一个元素（同时也是list），存给result_df的bs_staname列
result_df["bs_staname"] = bs_staname_list
print("bike station not in any taxi region:",bs_staname_list[-1])

# 再处理地铁站点
sub_staindex_list = [[] for i in range(len(gdf))]
for i in tqdm(range(len(sub_station_gdf))):
    sub_station = sub_station_gdf.iloc[i]
    sub_station_in_taxi_zone = False
    for j in range(len(gdf)):
        taxi_zone = gdf.iloc[j]
        if sub_in_taxi_zone(sub_station["geometry"], taxi_zone["geometry"]):
            sub_station_in_taxi_zone = True
            sub_staindex_list[taxi_zone["LocationID"]-1].append(sub_station["staindex"])
            break
    if not sub_station_in_taxi_zone:
        sub_staindex_list[-1].append(sub_station["staindex"])
# 将list的每一个元素（同时也是list），存给result_df的sub_staindex列
result_df["sub_staindex"] = sub_staindex_list
print("subway station not in any taxi region:",sub_staindex_list[-1])


# 将结果dataframe保存为csv文件
result_df.to_csv("sg_taxi_area.csv", index=False)


# 随机抽取一个拥有自行车站点和地铁站店的出租车区域，并在地图上画出出租车区域和其中的站点
# 随机抽取一个taxi_zone_id
taxi_zone_id = random.randint(1, len(gdf)-1)
while len(result_df.iloc[taxi_zone_id-1]["bs_staname"])==0 or len(result_df.iloc[taxi_zone_id-1]["sub_staindex"])==0:
    taxi_zone_id = random.randint(1, len(gdf)-1)
print("taxi_zone_id:",taxi_zone_id)
taxi_zone = gdf[gdf["LocationID"]==taxi_zone_id]
print("taxi_zone:",taxi_zone)
# 画出出租车区域
fig, ax = plt.subplots()
gdf.plot(ax=ax, color='white', edgecolor='black')
taxi_zone.plot(ax=ax, color='red')
# 画出自行车站点
bs_station_gdf[bs_station_gdf["sta_name"].isin(result_df.iloc[taxi_zone_id-1]["bs_staname"])].plot(ax=ax, color='blue', markersize=5)
# 画出地铁站点
sub_station_gdf[sub_station_gdf["staindex"].isin(result_df.iloc[taxi_zone_id-1]["sub_staindex"])].plot(ax=ax, color='green', markersize=5)
# 设置图例
red_patch = mpatches.Patch(color='red', label='Taxi Zone')
blue_patch = mpatches.Patch(color='blue', label='Bike Station')
green_patch = mpatches.Patch(color='green', label='Subway Station')
plt.legend(handles=[red_patch, blue_patch, green_patch])
plt.show()







