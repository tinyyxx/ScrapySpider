import pandas as pd
import openpyxl
import requests,json,time,datetime


def is_repeat(url,df):
    for j in range(len(df)):
        link_df = df.loc[j, "链接"]
        if link_df==url:
            return True
    return False

name = time.strftime("%Y-%m-%d") + '神华油化品竞拍上午11点.xlsx'
df1 = pd.read_excel("D://share//神华早上文件//" + name, sheet_name=0)
df2 = pd.read_excel("D://share//神华早上文件//"+time.strftime("%Y-%m-%d") +"神华油化品竞拍上午11点50分.xlsx", sheet_name=0)

for i in range(len(df2)):
    link_df2 = df2.loc[i, "链接"]
    if is_repeat(link_df2, df1)==False:
        new_line = df2.loc[[i]]
        df1 = pd.concat([df1, new_line], ignore_index=True)

writer = pd.ExcelWriter("D://share//神华早上文件//"+name)
df1.to_excel(writer, sheet_name="sheet", index=False)
writer.save()
