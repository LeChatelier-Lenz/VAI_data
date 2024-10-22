import pandas as pd

c = []
phi_bs = []
phi_sub = []
SGs = []
interval = pd.to_datetime('2021-06-05 04:00:00')-pd.to_datetime('2021-06-01 00:00:00')
offset_bs = interval.total_seconds() / 14400

# 自行车进出量时间序列
# 从0601FMR_bs中读取数据，从offset_bs开始读取
bike_fmr_seq = pd.read_csv("Seq_Data_sub_bs/0601FMR_bs.csv").iloc[int(offset_bs):]
# 从0601LMR_bs中读取数据，从offset_bs开始读取
bike_lmr_seq = pd.read_csv("Seq_Data_sub_bs/0601LMR_bs.csv").iloc[int(offset_bs):]

# 地铁进出量时间序列
# 从FMR_sub.csv中读取数据
sub_fmr_seq = pd.read_csv("Seq_Data_sub_bs/0605FMR_sub.csv")
# 从FMR_sub.csv中读取数据
sub_lmr_seq = pd.read_csv("Seq_Data_sub_bs/0605LMR_sub.csv")


tend_m = []
tend_bs = []

