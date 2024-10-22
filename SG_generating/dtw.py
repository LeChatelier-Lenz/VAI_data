import math
import numpy as np
import pandas as pd
from tqdm import tqdm
from generate_tend import basic_sgs, generate_tend


def dtw(tend_sub, tend_bs):
    # tend_sub和tend_bs为lr*T的矩阵
    T = len(tend_sub[0])
    lr = len(tend_sub)

    c = np.zeros(lr, dtype=float)

    for r in tqdm(range(lr), desc="Inner loop", leave=False, position=1):
        # 初始化成本矩阵
        cost = np.full((T, T), np.inf)
        if tend_sub[r,0] == np.inf or tend_bs[r,0] == np.inf:
            cost[0, 0] = np.inf
        else:
            cost[0, 0] = math.sqrt((tend_sub[r,0] - tend_bs[r,0]) ** 2)
        # 动态规划计算最小成本路径
        for i in range(1, T):
            for j in range(1, T):
                if tend_sub[r,i] == np.inf or tend_bs[r,j] == np.inf:
                    dist = np.inf
                else:
                    dist = math.sqrt((tend_sub[r,i] - tend_bs[r,j]) ** 2)
                cost[i, j] = dist + np.min([cost[i-1, j], cost[i, j-1], cost[i-1, j-1]])
        #
        # # 回溯找到最优路径 φ
        # i, j = T - 1, T - 1
        # phi_sub, phi_bs = [i], [j]
        #
        # while i > 0 or j > 0:
        #     if i == 0:
        #         j -= 1
        #     elif j == 0:
        #         i -= 1
        #     else:
        #         steps = [cost[i-1, j], cost[i, j-1], cost[i-1, j-1]]
        #         step = np.argmin(steps)
        #         if step == 0:
        #             i -= 1
        #         elif step == 1:
        #             j -= 1
        #         else:
        #             i -= 1
        #             j -= 1
        #     phi_sub.append(i)
        #     phi_bs.append(j)
        # phi_sub.reverse()
        # phi_bs.reverse()
        # print("φ_SUB:", phi_sub)
        # print("φ_BS:", phi_bs)
        c[r] = cost[T-1, T-1]
    # print("Final Cost:", c)
    Dr = np.mean(c)
    return Dr


if __name__ == "__main__":
    dis_df = pd.read_csv("../0325StaDistance.csv")
    best_sg = None
    best_dr = np.inf
    best_out_sub = None
    best_out_bs = None
    best_radius = 0
    for r in tqdm(range(10,80),desc="Outer loop",position=0,leave=False):
        basic_sg_df, filter_sub,filter_bs = basic_sgs(0.001*r,dis_df)
        Tend_BS,Tend_SUB = generate_tend(basic_sg_df)
        dr = dtw(Tend_SUB, Tend_BS)
        print(f" Dr for this Radius: {dr}\n")
        if dr < best_dr:
            best_sg = basic_sg_df
            best_dr = dr
            best_out_sub = filter_sub
            best_out_bs = filter_bs
            best_radius = 0.001*r
    print("Best SG:\n", best_sg)
    print("Best Dr:\n", best_dr)
    print("Best Radius:\n", best_radius)
    # 将最佳SG,以及对应情况下被过滤掉的sub和bs输出到不同的csv文件(注意先转成DataFrame)
    best_sg.to_csv("best_sg.csv",index=False)
    pd.DataFrame(best_out_sub).to_csv("best_out_sub.csv",index=False)
    pd.DataFrame(best_out_bs).to_csv("best_out_bs.csv",index=False)
