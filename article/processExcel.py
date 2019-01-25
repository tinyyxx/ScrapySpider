import requests, json, time, openpyxl, traceback
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from scrapy.selector import Selector
# from .utils import sendEmail
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

headers = {
        "Host": "www.e-shenhua.com",
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64;rv: 60.0) Gecko / 20100101Firefox / 60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q = 0.8",
        "Accept-Language": "zh-CN,zh;q = 0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br"
    }

class process_excel(object):
    excel_path = "D://share//神华日度数据.xlsx"
    am_excel_path = "D://share//神华早上文件//"+time.strftime("%Y-%m-%d")+"神华油化品竞拍上午11点.xlsx"
    #pm_excel_path = "D://work//code//article//"+time.strftime("%Y-%m-%d")+"神华油化品竞拍下午.xlsx"
    def __init__(self):
        self.am_excel = pd.read_excel(self.am_excel_path)
        #self.pm_excel = pd.read_excel(self.pm_excel_path)

    def parse(self, column):

        notnull = column.notnull()                    # 判断是否存在url
        for i in range(0, notnull.size):
            if notnull[i]:
                first_url_pos = i
                break
        total_morning_qty = 0  # 上午总成交量
        add_today_total_qty = 0  # 今日总成交量 每个url的成交量相加
        today_average_price = 0  # 第一个url的成交均价
        auction_price = 0  # 上午起拍价
        maxBidUnitPrice = 0  # 上午最高报价
        minBidUnitPrice = 0  # 上午最低报价
        today_afternoon_qty = 0  # 计算出的下午总成交量
        afternoon_price = 0  # 计算出的下午价格
        auction_qty = 0   # 竞价总量

        for i in range(0, len(column.values)):          #解析出该列的全部数据
            if notnull.values[i]:
                print(column.values[i], '\n')
                try:
                    response = session.get(column.values[i], verify=False, headers=headers) #timeout=(60, 120, 300)
                    skuId = Selector(response).xpath("//*[@id='skuId']/option/@value").extract()[0]
                    dpId = Selector(response).xpath("//*[@id='dpId']/option/@value").extract()[0]
                    data_url = "https://www.e-shenhua.com/ec/global/report/prod/SKUAndDeliveryPointTrendReportData.jsp?skuId=" + skuId + "&dpId=" + dpId
                    data = json.loads(session.get(data_url, verify=False, headers=headers).text.strip())    # 获取近一个月交易概况，将json反序列化为字典
                    average_price = float(data['price'][31][1])                             # 取得今日的交易数据
                    today_total_qty = float(data['qty'][31][1])
                    #name = Selector(response).xpath("//*[@id='skuId']/option/text()").extract()[0]
                    warehouse = Selector(response).xpath("//*[@id='dpId']/option/text()").extract()[0]
                    today_url = self.am_excel.loc[(self.am_excel.产品名称ID==skuId) & (self.am_excel.仓库==warehouse),'链接']

                    if (not today_url.empty) and i==first_url_pos and today_total_qty!=0:
                        #response = requests.get(today_url.values[0], verify=False)
                        auction_price += float(self.am_excel.loc[(self.am_excel['产品名称ID']==skuId) & (self.am_excel['仓库']==warehouse),'竞拍单价'].values[0])
                        maxBidUnitPrice += float(self.am_excel.loc[(self.am_excel['产品名称ID']==skuId) & (self.am_excel['仓库']==warehouse),'当前最高报价'].values[0])
                        minBidUnitPrice += float(self.am_excel.loc[(self.am_excel['产品名称ID']==skuId) & (self.am_excel['仓库']==warehouse),'当前最低报价'].values[0])
                        total_morning_qty += float(self.am_excel.loc[(self.am_excel['产品名称ID']==skuId) & (self.am_excel['仓库']==warehouse),'总成交数量'].values[0])
                        auction_qty += float(self.am_excel.loc[(self.am_excel['产品名称ID']==skuId) & (self.am_excel['仓库']==warehouse),'数量'].values[0])
                        add_today_total_qty += today_total_qty
                        today_average_price += average_price
                        first_url_pos_afternoon_qty = today_total_qty - total_morning_qty
                        if first_url_pos_afternoon_qty > 0:
                            morning_average_price = (minBidUnitPrice+maxBidUnitPrice)/2 if minBidUnitPrice==0 else maxBidUnitPrice
                            afternoon_price += (average_price*today_total_qty-morning_average_price*total_morning_qty)/first_url_pos_afternoon_qty

                    elif today_url.empty and today_total_qty!=0:
                        add_today_total_qty += today_total_qty
                    elif (not today_url.empty) and i!=first_url_pos and today_total_qty!=0:
                        #response = requests.get(today_url.values[0], verify=False)
                        total_morning_qty += float(self.am_excel.loc[(self.am_excel['产品名称ID'] == skuId) & (self.am_excel['仓库']==warehouse),'总成交数量'].values[0])
                        auction_qty += float(self.am_excel.loc[(self.am_excel['产品名称ID'] == skuId) & (self.am_excel['仓库'] == warehouse), '数量'].values[0])
                        add_today_total_qty += today_total_qty
                    elif (not today_url.empty) and today_total_qty==0 and i==first_url_pos:
                        auction_price += float(self.am_excel.loc[(self.am_excel['产品名称ID'] == skuId) & (self.am_excel['仓库'] == warehouse), '竞拍单价'].values[0])

                except:
                    f = open("D:\\article\\exception_log.txt", 'a')
                    f.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "  当前错误URL:" + column.values[i] + "\n")
                    traceback.print_exc(file=f)
                    f.write("\n")
                    f.flush()
                    f.close()

        today_afternoon_qty += (add_today_total_qty - total_morning_qty)

        if auction_price==0:
            auction_price=None
        if maxBidUnitPrice==0:
            maxBidUnitPrice=None
        if minBidUnitPrice==0:
            minBidUnitPrice=None
        if today_average_price==0:
            today_average_price=None
        if afternoon_price==0:
            afternoon_price=None


        return {
            "warehouse":column.name,                            # 返回仓库名
            "auction_price": auction_price,                     # 上午竞拍单价
            "auction_qty":auction_qty,                          # 上午竞拍总量
            "maxBidUnitPrice": maxBidUnitPrice,                 # 上午最高报价
            "minBidUnitPrice": minBidUnitPrice,                 # 上午最低报价
            "total_morning_qty":total_morning_qty,              # 上午总的成交量
            "today_average_price": today_average_price,         # 当日成交均价
            "today_total_qty": add_today_total_qty,             # 当日总成交量
            "today_afternoon_qty":today_afternoon_qty,          # 下午总的成交量
            "afternoon_price":afternoon_price                   # 下午的均价
            }

#第一步: 获取每一个url，爬取名称和仓库名,查看今日有无成交额，无成交额则直接略过
#第二步：到上午的excel中查找是否有该项目的竞价交易
#第三步：如果有,爬取六个数据               
import os

def get_file_list():
    file_path = "D:\\share\\result"  # 文件夹名
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        dir_list = sorted(dir_list,  key=lambda x: os.path.getctime(os.path.join(file_path, x)), reverse=True)
        # print(dir_list)
        return dir_list


if __name__ == '__main__':
    process_excel = process_excel()
    wb = openpyxl.load_workbook(process_excel.excel_path)
    sheetnames = wb.sheetnames
    #insert_df = pd.DataFrame(index=['竞拍单价','上午高价','上午低价','上午成交量','总均价','总成交量','下午成交量','下午价格'])
    yesterday_result_path = "D://share//result//"+get_file_list()[0]
    result_path = "D://share//result//"+time.strftime("%Y-%m-%d")+"result.xlsx"
    writer = pd.ExcelWriter(result_path)
    # 遍历每一个sheet
    for sheetname in sheetnames:
        df = pd.read_excel(process_excel.excel_path, sheet_name=sheetname)
        df_auction_price = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_maxBidUnitPrice = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_minBidUnitPrice = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_total_morning_qty = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_today_average_price = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_today_total_qty = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_today_afternoon_qty = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_afternoon_price = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        df_auction_qty = pd.DataFrame(index=[time.strftime("%Y-%m-%d")])
        for col in df.columns.values.tolist():      # 获取这一页sheet中的每一列
            column = df[col]
            parsed_data = process_excel.parse(column)  # 将Excel每一个sheet的每一列作为参数传递，对于每一列，获取所需的六个数据和计算的两个量
            df_auction_price[parsed_data["warehouse"]] = [parsed_data["auction_price"]]
            df_maxBidUnitPrice[parsed_data["warehouse"]] = [parsed_data["maxBidUnitPrice"]]
            df_minBidUnitPrice[parsed_data["warehouse"]] = [parsed_data["minBidUnitPrice"]]
            df_total_morning_qty[parsed_data["warehouse"]] = [parsed_data["total_morning_qty"]]
            df_today_average_price[parsed_data["warehouse"]] = [parsed_data["today_average_price"]]
            df_today_total_qty[parsed_data["warehouse"]] = [parsed_data["today_total_qty"]]
            df_today_afternoon_qty[parsed_data["warehouse"]] = [parsed_data["today_afternoon_qty"]]
            df_afternoon_price[parsed_data["warehouse"]] = [parsed_data["afternoon_price"]]
            df_auction_qty[parsed_data["warehouse"]] = [parsed_data["auction_qty"]]

        # 读取结果中的每一个sheet
        try:
            read_df_auction_price = pd.read_excel(yesterday_result_path, sheet_name=sheetname+'(起拍价)')
            read_df_maxBidUnitPrice = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(上午高价)')
            read_df_minBidUnitPrice = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(上午低价)')
            read_df_total_morning_qty = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(上午总成交量)')
            read_df_today_average_price = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(总均价)')
            read_df_today_total_qty = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(总成交量)')
            read_df_today_afternoon_qty = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(下午成交量)')
            read_df_afternoon_price = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(下午价格)')
            read_df_auction_qty = pd.read_excel(yesterday_result_path,sheet_name=sheetname+'(竞价总量)')
        except:
            read_df_auction_price = pd.DataFrame()
            read_df_maxBidUnitPrice = pd.DataFrame()
            read_df_minBidUnitPrice = pd.DataFrame()
            read_df_total_morning_qty = pd.DataFrame()
            read_df_today_average_price = pd.DataFrame()
            read_df_today_total_qty = pd.DataFrame()
            read_df_today_afternoon_qty = pd.DataFrame()
            read_df_afternoon_price = pd.DataFrame()
            read_df_auction_qty = pd.DataFrame()

        # 整合后将新的df写入excel
        pd.concat([read_df_auction_price, df_auction_price], sort=False).to_excel(writer, sheet_name=sheetname+'(起拍价)')
        pd.concat([read_df_maxBidUnitPrice, df_maxBidUnitPrice], sort=False).to_excel(writer, sheet_name=sheetname+'(上午高价)')
        pd.concat([read_df_minBidUnitPrice, df_minBidUnitPrice], sort=False).to_excel(writer, sheet_name=sheetname+'(上午低价)')
        pd.concat([read_df_auction_qty, df_auction_qty], sort=False).to_excel(writer, sheet_name=sheetname+'(竞价总量)')
        pd.concat([read_df_total_morning_qty, df_total_morning_qty], sort=False).to_excel(writer, sheet_name=sheetname+'(上午总成交量)')
        pd.concat([read_df_today_average_price, df_today_average_price], sort=False).to_excel(writer, sheet_name=sheetname+'(总均价)')
        pd.concat([read_df_today_total_qty, df_today_total_qty], sort=False).to_excel(writer, sheet_name=sheetname+'(总成交量)')
        pd.concat([read_df_today_afternoon_qty, df_today_afternoon_qty], sort=False).to_excel(writer, sheet_name=sheetname+'(下午成交量)')
        pd.concat([read_df_afternoon_price, df_afternoon_price], sort=False).to_excel(writer, sheet_name=sheetname+'(下午价格)')
    writer.save()
    wb = openpyxl.load_workbook(result_path)
    sheetnames = wb.sheetnames
    wb2 = openpyxl.load_workbook(process_excel.excel_path)
    sheetnames = wb.sheetnames
    supposedsheets = len(wb2.sheetnames)*9
    import ctypes
    if len(sheetnames) == supposedsheets:
        #ctypes.windll.user32.MessageBoxA(0, u"结束了，END！结果正确！！！".encode('gb2312'),u' 信息'.encode('gb2312'), 0)
        print("结果正确！！")
    else:
        #ctypes.windll.user32.MessageBoxA(0, u"结束了，END！结果错误！！！".encode('gb2312'), u' 信息'.encode('gb2312'), 0)
        print("结果错误，wrong af!!!!")

    #发送Email给需求方
    # result_name = time.strftime("%Y-%m-%d")+"result.xlsx"
    # sendEmail.mail(result_path, result_name)

    # if len(sheetnames)==126:
    #     print("结果正确！！")
    # else:
    #     print("出错了！！")
    # print("结束了，END！")


