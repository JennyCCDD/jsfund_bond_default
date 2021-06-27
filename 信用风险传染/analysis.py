# -*- coding: utf-8 -*-
"""
@author: Mengxuan Chen
@E-mail: chenmx19@mails.tsinghua.edu.cn
@description:
@revise log:
    2021.06.24 19:30-21:00 1h30min
"""
#%%
import pandas as pd
import numpy as np
import datetime
import os,re
import inspect
import warnings
warnings.filterwarnings('ignore')
import time
import datetime
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体） Microsoft YaHei SimHei
plt.rcParams['axes.unicode_minus'] = False   # 步骤二（解决坐标轴负数的负号显示问题）
from tqdm import tqdm

#%%
# 根据当前日期得到前后推一定时间窗口的日期
def time_window(date,tw_before, tw_after):
    begin = date - datetime.timedelta(days=int(tw_before))
    end = date + datetime.timedelta(days=int(tw_after))
    return begin.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S')

#%%
# 输入评级的dataframe判断1. 是否下跌，2. 反弹到原来的水平
def bound(df, date):
    df['if_larger'] = (df.index >= date)
    df_after = df[df['if_larger'] == True]
    df_after['time'] = range(len(df_after))
    bound_list = []
    day_list = []
    for gap_i in df_after.columns[:-2].tolist():
        arr = df_after.loc[:, gap_i]
        count = 0
        bound = 0
        for i in range(0, len(df_after.index) - 1):
            if arr.iloc[i] > arr.iloc[i + 1]:
                count += 1
            if (arr.iloc[i] >= arr.iloc[0]) & (i > count):
                bound = i
            if bound != 0:
                break

        bound_date = arr.index[bound]
        day_list.append(bound)
        bound_list.append(bound_date)

    return bound_list,day_list
#%%
# 1. 统计同行业违约发生的时间差，存入data_industry的columns中
# 2. 画出同行业不同评级违约前后兴证固收行业信用利差指数的变化情况
# wrt = pd.ExcelWriter('./results/同行业不同评级违约前后兴证固收行业信用利差指数的变化情况.xlsx')
data = pd.read_excel('./data/违约债券报表.xlsx',sheet_name='违约债券报表')
data.dropna(how='all',inplace=True)
spread_group_indu = pd.read_excel('./data/违约债券报表.xlsx',sheet_name='兴证固收行业信用利差指数（同行业不同等级）',index_col=0)
industry = data['所属申万行业名称'].drop_duplicates().tolist()

for indursty_i in tqdm(industry):
    data_industry = data[data['所属申万行业名称']==indursty_i]
    data_industry.sort_values(['发生日期'],ascending=True,inplace=True)
    code_list = data_industry['代码'].tolist()
    count = 1
    for i in range(len(data_industry)):
        data_industry[code_list[i]] = data_industry['发生日期'].apply(lambda x: (data_industry['发生日期'].iloc[i]-x).days)
        rating = data_industry.iloc[i,:]['市场隐含评级（中债）']
        date = data_industry.iloc[i,:]['发生日期']
        rating_list = []
        for k in range(len(spread_group_indu.columns)):
            if spread_group_indu.columns[k].split(':')[1]==indursty_i:
                rating_list.append(spread_group_indu.columns[k])
        spread_group_indu_i = spread_group_indu[rating_list]
        begin,end=time_window(date,10,300)
        spread_group_indu_i = spread_group_indu_i.loc[begin:end,:]
        if (len(spread_group_indu_i.columns) > 0)&  (len(spread_group_indu_i.index) > 0):
            spread_group_indu_i.loc['回复时长', :-1] = bound(spread_group_indu_i, date)[1]
            spread_group_indu_i.loc['回复日期', :-1] = bound(spread_group_indu_i.iloc[:-1, :], date)[0]
            spread_group_indu_i.iloc[:-2,:-1].plot()
            plt.axvline(date,  color="red")
            plt.title(data_industry.iloc[i,:]['代码']+'_'+data_industry.iloc[i,:]['名称']
                      +'_'+str(data_industry.iloc[i,:]['发生日期'])[:10])
            plt.savefig('./results/同行业不同等级/'+data_industry.iloc[i,:]['代码']+'_'+data_industry.iloc[i,:]['名称']
                      +'_'+str(data_industry.iloc[i,:]['发生日期'])[:10]+'_line.png')
            # plt.show()
#             spread_group_indu_i.to_excel(excel_writer=wrt, sheet_name=data_industry.iloc[i,:]['名称']
#                       +'_'+str(data_industry.iloc[i,:]['发生日期'])[:10])
#
# wrt.save()
# wrt.close()
#%%



