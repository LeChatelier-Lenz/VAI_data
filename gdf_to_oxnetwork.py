import networkx as nx
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd


# 假设你已经有一个GeoDataFrame `gdf`，其中包含一个感兴趣区域的多边形 (Polygon)
# 读取CSV文件
df = pd.read_csv('./0526BikeCoorNew.csv')

# 假设CSV文件包含以下列： 'id'（唯一标识名称）, 'latitude', 'longitude'
# 创建一个包含Point几何的列
geometry = [Point(xy) for xy in zip(df['long'], df['la'])]

# 创建GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# 设置坐标参考系 (CRS), 这里假设是 WGS84 (EPSG:4326)
gdf.set_crs(epsg=4326, inplace=True)

# 上述部分来自csv_to_gdf.py

# 检查GeoDataFrame是否包含Polygon，如果没有则需要从点生成
if gdf.geom_type.iloc[0] != 'Polygon':
    gdf = gdf.unary_union.convex_hull
    gdf = gpd.GeoDataFrame(geometry=[gdf])

# 获取多边形范围
polygon = gdf.geometry.iloc[0]

# 使用osmnx从OpenStreetMap下载道路网络
# network_type可以是 'all', 'walk', 'bike', 'drive', 'drive_service' 等
G = ox.graph_from_polygon(polygon, network_type='bike')

# 显示道路网络的统计信息
ox.basic_stats(G)

# 绘制道路网络
ox.plot_graph(G,node_size=1)

# convert graph to line graph so edges become nodes and vice versa
edge_centrality = nx.closeness_centrality(nx.line_graph(G))
nx.set_edge_attributes(G, edge_centrality, "edge_centrality")

# color edges in original graph with closeness centralities from line graph
ec = ox.plot.get_edge_colors_by_attr(G, "edge_centrality", cmap="inferno")
fig_1, ax_1 = ox.plot_graph(G, edge_color=ec, edge_linewidth=2, node_size=0)