# Data Dictionary
> 本文件夹的代码处理基于2021年6-8月份的三种交通工具数据，时间粒度为1小时

## 文件列表
- `lt_1h_3m/README.md`: 本文件
- `lt_1h_3m/taxi_od_overSG_1h.parquet` : 2021年6-8月份的出租车SG间OD数据
- `lt_1h_3m/bs_od_overSG_1h.parquet` : 2021年6-8月份的自行车SG间OD数据
- 上述OD数据的字段说明:
  - 列数为len(taxi_zones) * len(taxi_zones)， 行列索引为`zone_id1`-`zone_id2`，从'1-1'到'264-264'
  - 行数为时间粒度内的数据量
  - taxi_zones.csv中的`zone_id`字段对应OD数据中的行列索引
  - taxi——bike的分组关系在sg_taxi_area.csv中给出
  - 自行车站点数据对应`0526BikeCoorNew.csv`文件

- `\bs_FMR_insideSG_1h\` 保存了各个出租车区域内部的各个自行车站点归还流量数据
- `\bs_LMR_insideSG_1h\` 保存了各个出租车区域内部的各个自行车站点借车流量数据
  - 其中的文件名为`bs_FMR_insideSG_1h_*.csv`，`*`为出租车区域编号
  - 每个区域内部站点顺序与`sg_taxi_area.csv`中的站点顺序一致