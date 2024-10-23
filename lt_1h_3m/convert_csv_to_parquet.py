import pandas as pd


df = pd.read_csv("bs_od_overSG_1h.csv")
df.to_parquet("bs_od_overSG_1h.parquet")
