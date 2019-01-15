import requests,json,time,datetime
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from scrapy.selector import Selector


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
# data_url = "https://www.e-shenhua.com/ec/global/report/prod/SKUAndDeliveryPointTrendReportData.jsp?skuId=1-6ZBG97&dpId=A-W-077"
# data = json.loads(requests.get(data_url, verify=False, headers=headers).text.strip())    # 获取近一个月交易概况，将json反序列化为字典
# average_price = float(data['price'][31][1])                             # 取得今日的交易数据
# today_total_qty = float(data['qty'][31][1])

am_excel_path = "D://share//神华早上文件//2019-01-09神华油化品竞拍上午11点.xlsx"
am_excel = pd.read_excel(am_excel_path)
print("sssss")
res = []

for i in range(0, 62):
    response = session.get(am_excel.iat[i, 8], verify=False, headers=headers)
    print(am_excel.iat[i, 8])
    try:
        skuId = Selector(response).xpath("//*[@id='skuId']/option/@value").extract()[0]
        res.insert(i, skuId)
    except Exception:
        res.insert(i, "缺失")

for i in range(0, 62):
    print(res[i], "\n")