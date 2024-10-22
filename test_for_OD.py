import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, LineString

# 创建城市数据 (起点和终点)
cities = {
    "CityA": {"coordinates": (116.4074, 39.9042), "population": 2000},  # 北京
    "CityB": {"coordinates": (121.4737, 31.2304), "population": 3000},  # 上海
    "CityC": {"coordinates": (114.3055, 30.5928), "population": 1500},  # 武汉
}

# 创建城市的GeoDataFrame
city_names = list(cities.keys())
city_coords = [Point(cities[city]["coordinates"]) for city in city_names]
gdf_cities = gpd.GeoDataFrame(city_names, geometry=city_coords, columns=["City"])

# 定义OD流动数据 (起点, 终点, 流动数量)
od_data = [
    {"origin": "CityA", "destination": "CityB", "flow": 500},
    {"origin": "CityA", "destination": "CityC", "flow": 300},
    {"origin": "CityB", "destination": "CityC", "flow": 200},
]

# 创建OD线路的GeoDataFrame
lines = []
for od in od_data:
    origin = Point(cities[od["origin"]]["coordinates"])
    destination = Point(cities[od["destination"]]["coordinates"])
    line = LineString([origin, destination])
    lines.append({"geometry": line, "flow": od["flow"]})

gdf_lines = gpd.GeoDataFrame(lines)

# 画图
fig, ax = plt.subplots(figsize=(10, 10))

# 绘制城市节点
gdf_cities.plot(ax=ax, color="blue", markersize=100)

# 在节点旁标注城市名
for x, y, label in zip(gdf_cities.geometry.x, gdf_cities.geometry.y, gdf_cities["City"]):
    ax.text(x, y, label, fontsize=12, ha="right")

# 绘制OD线，线的宽度根据流动数量调整
for _, row in gdf_lines.iterrows():
    ax.plot(*row['geometry'].xy, color='red', linewidth=row['flow']/100)

# 设置图像标题
ax.set_title('OD Flow Map Example')

# 显示图像
plt.show()
