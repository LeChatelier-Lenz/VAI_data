import pandas as pd
from tqdm import tqdm

# 总的FMR定义为**进入**出租车区域的数据处理
# 分别读取自行车、地铁、出租车数据（均有FMR,LMR两份）
# 注意，FMR对于地铁来说是进站；对于出租车来说是下车；对于自行车来说是还车【前一个是离开本区域，后两个是进入本区域】
bs_fmr_df = pd.read_csv("../Seq_Data_sub_bs/0601FMR_bs.csv") # 2021-06-01 00:00:00
sub_lmr_df = pd.read_csv("../Seq_Data_sub_bs/0605LMR_sub.csv") # 2021-06-05 04:00:00
taxi_fmr_df = pd.read_csv("../202106taxi/taxi_seq_4h_FMR.csv") # 2021-06-01 00:00:00

# 需要以地铁站点开始记录时间为基准，使所有数据开始时间一致，因此要调整自行车和出租车数据（所有的数据记录都是按照开始时间每4h一行）
# 已知地铁数据开始时间为2021-06-05 04:00:00
# 自行车数据开始时间为2021-06-01 00:00:00
# 出租车数据开始时间为2021-06-01 00:00:00
# 因此需要调整自行车和出租车数据
# 2021-06-01 00:00:00 -> 2021-06-05 04:00:00
offset = 24//4*(5-1) + 1
bs_fmr_df = bs_fmr_df.iloc[offset:]
taxi_fmr_df = taxi_fmr_df.iloc[offset:]

# 同时，调整最后遍历总长度，使得所有数据长度一致
length = min(len(bs_fmr_df),len(sub_lmr_df),len(taxi_fmr_df))
bs_fmr_df = bs_fmr_df.iloc[:length]
sub_lmr_df = sub_lmr_df.iloc[:length]
taxi_fmr_df = taxi_fmr_df.iloc[:length]
print(length)


# 读取出租车区域信息
sg_df = pd.read_csv("sg_taxi_area.csv")
result = []
each_time_result = []
# 其中，bs_staname列存储了每个出租车区域内的自行车站点(列表形式),sub_staindex列存储了每个出租车区域内的地铁站点(列表形式)
for i in tqdm(range(length)):
    # 开始整理每一行数据
    for j in range(len(sg_df)):
        taxi_location = sg_df["taxi_zone_id"].iloc[j]
        this_taxi_fmr = taxi_fmr_df[str(taxi_location)].iloc[i]
        # 列表在csv文件中是以字符串形式存储的，需要转换为列表
        bs_list = eval(sg_df["bs_staname"].iloc[j])
        this_bs_fmr = 0
        for bs in bs_list:
            this_bs_fmr += bs_fmr_df[bs].iloc[i]
        sub_list = eval(sg_df["sub_staindex"].iloc[j])
        this_sub_lmr = 0
        for sub in sub_list:
            this_sub_lmr += sub_lmr_df[sub].iloc[i]
        # 将三个结果相加，得到总的FMR，即进入出租车区域的人数
        each_time_result.append(this_bs_fmr+this_sub_lmr+this_taxi_fmr)
    result.append(each_time_result)
    each_time_result = []

result_df = pd.DataFrame(result)
result_df.to_csv("seq_sg_4h_FMR.csv",index=False,header=False)



