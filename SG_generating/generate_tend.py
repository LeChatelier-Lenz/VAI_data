import pandas as pd
import numpy as np
from tqdm import tqdm

seen_bikes = set()


def basic_sgs(rate=0.02,dis_df=None):
    """
    生成基本的SG组合，利用dis_df中的数据，取最大距离和最小距离的加权平均值作为半径
    :param rate: 最大半径的加权比例
    :param dis_df: 地铁站sub和自行车站bike的距离数据
    :return: 返回基本的SG组合, 过滤出的sub站点和bike站点
    """
    # 计算dis_df中所有不同bike的数量
    count_total_bikes = dis_df['bike'].nunique()
    count_total_subs = dis_df['sub'].nunique()
    max_radius = dis_df['dis'].max()
    min_radius = dis_df['dis'].min()
    print("\n")
    print(f"Max Radius:{max_radius} Min Radius:{min_radius}")
    radius = rate*max_radius + (1-rate)*min_radius
    print("Radius:", radius)
    r_dis_df = dis_df[dis_df['dis'] <= radius]
    # 按 'bike' 分组，找到每组 'dis' 最小的行的索引
    min_dis_idx = r_dis_df.groupby('bike')['dis'].idxmin()

    # 根据索引提取出对应的行，保留 'bike', 'sub', 'dis' 等列
    u_dis_df = r_dis_df.loc[min_dis_idx, ['sub','bike', 'dis']]
    grouped_df = u_dis_df.groupby('sub')['bike'].apply(list).reset_index()
    # 计算grounded_df中所有的bikes站点数量
    # count_total_bikes = 0
    # for i in range(len(grouped_df)):
    #     count_total_bikes += len(grouped_df['bike'].iloc[i])
    # print("Total Bike Stations:", count_total_bikes)
    # 还要统计一下不在最终的station group当中的sub站点的最近的bike站点距离
    dis_filter_out_df_sub = dis_df[~dis_df['sub'].isin(grouped_df['sub'])]
    dis_filter_out_df_bs = dis_df[~dis_df['bike'].isin(u_dis_df['bike'])]
    min_filter_dis_idx = dis_filter_out_df_sub.groupby('sub')['dis'].idxmin()
    u_filter_dis_df = dis_filter_out_df_sub.loc[min_filter_dis_idx, ['sub','bike', 'dis']]
    # min_dis = u_filter_dis_df['dis'].min()
    # print("Min Dis in Out Subs:", min_dis)
    out_sub_list = dis_filter_out_df_sub['sub'].unique()
    print(f"Total Subway Stations:{count_total_subs}  Filter Out Subway Stations:{len(out_sub_list)}")
    out_bike_list = dis_filter_out_df_bs['bike'].unique()
    print(f"Total Bike Stations:{count_total_bikes}  Filter Out Bike Stations:{len(out_bike_list)}")
    print(f"Number of SGs:{len(grouped_df)}")
    return grouped_df, out_sub_list, out_bike_list


def generate_tend(basic_sg_df):
    # basic_sg_df 就是初始的组合，共有len(basic_sg_df)个站点组合，每个站点组合中有若干个bike站点
    SG_info = []
    interval = pd.to_datetime('2021-06-05 04:00:00')-pd.to_datetime('2021-06-01 00:00:00')
    offset_bs = interval.total_seconds() / 14400

    # 自行车进出量时间序列
    # 从0601FMR_bs中读取数据，从offset_bs开始读取
    bike_fmr_seq = pd.read_csv("../Seq_Data_sub_bs/0601FMR_bs.csv").iloc[int(offset_bs):]
    # 从0601LMR_bs中读取数据，从offset_bs开始读取
    length = len(bike_fmr_seq) # 循环的长度，同时也是后续计算中t的上限
    bike_lmr_seq = pd.read_csv("../Seq_Data_sub_bs/0601LMR_bs.csv").iloc[int(offset_bs):]
    if len(bike_lmr_seq) < length:
        length = len(bike_lmr_seq)


    # 地铁进出量时间序列
    # 从FMR_sub.csv中读取数据
    sub_fmr_seq = pd.read_csv("../Seq_Data_sub_bs/0605FMR_sub.csv")
    if len(sub_fmr_seq) < length:
        length = len(sub_fmr_seq)
    # 从FMR_sub.csv中读取数据
    sub_lmr_seq = pd.read_csv("../Seq_Data_sub_bs/0605LMR_sub.csv")
    if len(sub_lmr_seq) < length:
        length = len(sub_lmr_seq)

    # 所有数据按照时间序列的长度进行截断
    bike_fmr_seq = bike_fmr_seq.iloc[:length]
    bike_lmr_seq = bike_lmr_seq.iloc[:length]
    sub_fmr_seq = sub_fmr_seq.iloc[:length]
    sub_lmr_seq = sub_lmr_seq.iloc[:length]


    print("Computing tend...")
    q_bs_lmr = np.zeros((len(basic_sg_df), length))
    q_bs_fmr = np.zeros((len(basic_sg_df), length))
    q_sub_lmr = np.zeros((len(basic_sg_df), length))
    q_sub_fmr = np.zeros((len(basic_sg_df), length))
    for i in range(len(basic_sg_df)):
        # 对于每一个SG
        sub_fmr_col = sub_fmr_seq[basic_sg_df['sub'].iloc[i]]
        q_sub_fmr[i,:] = sub_fmr_col.values
        # print("Q_SUB_FMR:", q_sub_fmr)
        sub_lmr_col = sub_lmr_seq[basic_sg_df['sub'].iloc[i]]
        q_sub_lmr[i,:] = sub_lmr_col.values
        # print("Q_SUB_LMR:", q_sub_lmr)
        bike_fmr_cols = []
        bike_lmr_cols = []
        for j in range(len(basic_sg_df['bike'].iloc[i])):
            key_bike = basic_sg_df['bike'].iloc[i][j]
            # print("Processing bike:", key_bike)
            bike_fmr_cols.append(bike_fmr_seq[key_bike])
            bike_lmr_cols.append(bike_lmr_seq[key_bike])
            # print(bike_fmr_cols[-1].iloc[:, ])
        bike_lmr_result = sum(df.iloc[:, ] for df in bike_lmr_cols)
        q_bs_lmr[i,:] = bike_lmr_result.values
        bike_fmr_result = sum(df.iloc[:, ] for df in bike_fmr_cols)
        q_bs_fmr[i,:] = bike_fmr_result.values
        # print("Q_BS_LMR:", q_bs_lmr)
        # print("Q_BS_FMR:", q_bs_fmr)
    # print("Q_BS_LMR:", q_bs_lmr)
    # print("Q_BS_FMR:", q_bs_fmr)
    # print("Q_SUB_LMR:", q_sub_lmr)
    # print("Q_SUB_FMR:", q_sub_fmr)
    tend_bs = q_to_tend(q_bs_lmr, q_bs_fmr)
    tend_sub = q_to_tend(q_sub_lmr, q_sub_fmr)
    # print("Tend_BS:", tend_bs)
    # print("Tend_SUB:", tend_sub)
    print("Computing tend done.\n")
    return tend_bs, tend_sub


def q_to_tend(lmr,fmr):
    # 分子
    num = fmr - lmr
    # 分母
    den = (fmr + lmr)/2
    # 将为0的分母替换为1
    den = np.where(den == 0, 0.01, den)
    # numpy数组各元素相除，对于分母为0的情况，结果为nan
    tend = num / den
    # 将nan替换为0
    return tend


if __name__ == '__main__':
    dis_df = pd.read_csv("../0325StaDistance.csv")
    # basic_sgs()
    basic_sg_df, filter_sub,filter_bs = basic_sgs(0.02,dis_df)
    generate_tend(basic_sg_df)