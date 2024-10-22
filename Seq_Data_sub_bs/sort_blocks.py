import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Point
from sklearn.cluster import KMeans


def sort_blocks():
    df = pd.read_csv("0526BikeCoorNew.csv")
    geometry = [Point(xy) for xy in zip(df['long'], df['la'])]

    # 创建GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry)

    # 设置你希望的区域数量 (例如 2 个区域)
    num_clusters = 500

    # 提取经纬度数据用于聚类
    coords = df[['long', 'la']]

    # 使用KMeans进行聚类
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(coords)

    # 将聚类结果添加回GeoDataFrame
    gdf['cluster'] = kmeans.labels_

    # 计算每个聚类的中心点 (即新区域的中心)
    cluster_centers = gdf.groupby('cluster').agg({
        'long': 'mean',
        'la': 'mean'
    }).reset_index()

    # 将中心点转换为GeoDataFrame
    geometry = [Point(xy) for xy in zip(cluster_centers['long'], cluster_centers['la'])]
    gdf_centroids = gpd.GeoDataFrame(cluster_centers, geometry=geometry)

    # # 输出结果
    # print("Original GeoDataFrame:")
    # print(gdf)
    # print("\nCluster Centers GeoDataFrame:")
    # print(gdf_centroids)
    # # 可视化原始点和聚类中心点
    # ax = gdf.plot(color='blue', markersize=50, label='Original Points')
    # gdf_centroids.plot(ax=ax, color='red', markersize=100, label='Cluster Centers', marker='x')
    return gdf, gdf_centroids


if __name__ == '__main__':
    sort_blocks()