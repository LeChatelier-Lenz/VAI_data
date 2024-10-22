import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 读取CSV文件
df = pd.read_csv('./0526BikeCoorNew.csv')

# 假设CSV文件包含以下列： 'id'（唯一标识名称）, 'latitude', 'longitude'
# 创建一个包含Point几何的列
geometry = [Point(xy) for xy in zip(df['long'], df['la'])]

# 创建GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# 设置坐标参考系 (CRS), 这里假设是 WGS84 (EPSG:4326)
gdf.set_crs(epsg=4326, inplace=True)

# 显示GeoDataFrame的前几行
print(gdf.head())
