import pandas as pd
import xlrd,os,time
import pymysql


def insert_into_db(param):
    conn = pymysql.connect(host='192.168.1.70', user='leyizhou', password='Deya123', db='deya_data_eurostat')
    cur = conn.cursor()
    try:
        sql = "insert into dy_trade_"+str(param[0][5]//100)+" (product,flow,indicators,reporter,partner,period,value,extracted_on,created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.executemany(sql, param)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
    conn.close()

path = "D:\\work\\code\\article\\xls"     # 文件夹名
files= os.listdir(path)
#遍历文件夹下的文件名,把一个文件下的记录按年份放到不同数组
for file in files:
    param2014 = []
    param2015 = []
    param2016 = []
    param2017 = []
    param2018 = []
    excel_path = path+"//"+file
    sheetnames = xlrd.open_workbook(excel_path).sheet_names()
    # 遍历文件下的所有sheet
    for sheetname in sheetnames:
        sheet = pd.read_excel(excel_path,sheet_name=sheetname)
        product = sheet.iat[6,1]
        flow = int(sheet.iat[7,1])
        indicators = sheet.iat[8,1]
        if indicators == 'QUANTITY_IN_100KG':
            indicators = 1
        elif indicators == 'VALUE_IN_EUROS':
            indicators = 2
        else:
            indicators = -1
        partner = sheet.iat[5, 1]
        extracted_on = time.strftime("%Y-%m-%d",time.strptime(sheet.iat[2,1]._date_repr,"%Y-%m-%d"))
        created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 遍历sheet部分里的表格，即对应数据库中每一个value值
        for i in range(11,14):
            for j in range(1,59):
                reporter = sheet.iat[i,0]
                if reporter.startswith("GERMANY"):
                    reporter='DE'
                elif reporter.startswith("EURO"):
                    reporter = 'EA19'
                elif reporter.startswith("EU28"):
                    reporter = 'EU28'
                period = int(sheet.iat[10,j])
                value = sheet.iat[i,j]
                if value ==':':
                    value = None
                else:
                    value = float(value)
                table = str(period//100)
                if period//100==2014:
                    param2014.append([product,flow,indicators,reporter,partner,period,value,extracted_on,created_at])
                elif period//100==2015:
                    param2015.append([product, flow, indicators, reporter, partner, period, value, extracted_on, created_at])
                elif period//100==2016:
                    param2016.append([product, flow, indicators, reporter, partner, period, value, extracted_on, created_at])
                elif period//100==2017:
                    param2017.append([product, flow, indicators, reporter, partner, period, value, extracted_on, created_at])
                elif period//100==2018:
                    param2018.append([product, flow, indicators, reporter, partner, period, value, extracted_on, created_at])
    print(len(param2014),'\t',len(param2015),'\t',len(param2016),'\t',len(param2017),'\t',len(param2018))
    # 每遍历一次文件，就插入一次数据库
    # insert_into_db(param2014)
    # insert_into_db(param2015)
    # insert_into_db(param2016)
    # insert_into_db(param2017)
    # insert_into_db(param2018)

# import pandas as pd
# import xlrd,os
# import pymysql,time,datetime
#
# def insert_into_db(excel_path):
#     sheetnames = xlrd.open_workbook(excel_path).sheet_names()
#     # Connect to the database
#     for sheetname in sheetnames:
#         sheet = pd.read_excel(excel_path,sheet_name=sheetname)
#         product = sheet.iat[6,1]
#         flow = int(sheet.iat[7,1])
#         indicators = sheet.iat[8,1]
#         if indicators == 'QUANTITY_IN_100KG':
#             indicators = 1
#         elif indicators == 'VALUE_IN_EUROS':
#             indicators = 2
#         else:
#             indicators = -1
#
#         partner = sheet.iat[5, 1]
#         extracted_on = time.strftime("%Y-%m-%d",time.strptime(sheet.iat[2,1]._date_repr,"%Y-%m-%d"))
#         created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         for i in range(11,14):
#             for j in range(1,59):
#                 reporter = sheet.iat[i,0]
#                 if reporter.startswith("GERMANY"):
#                     reporter='DE'
#                 elif reporter.startswith("EURO"):
#                     reporter = 'EA19'
#                 elif reporter.startswith("EU28"):
#                     reporter = 'EU28'
#                 period = int(sheet.iat[10,j])
#                 value = sheet.iat[i,j]
#                 if value ==':':
#                     value =None
#                 else:
#                     value = float(value)
#                 conn = pymysql.connect(host='192.168.1.70',
#                                        user='leyizhou',
#                                        password='Deya123',
#                                        db='deya_data_eurostat')
#                 cur = conn.cursor()
#                 sql = "insert into dy_trade_"+str(period//100)+"(product,flow,indicators,reporter,partner,period,value,extracted_on,created_at) SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s " \
#                       "FROM DUAL WHERE NOT EXISTS(SELECT product,flow,indicators,reporter,partner,period,value,extracted_on,created_at FROM dy_trade_"+str(period//100)+" WHERE " \
#                       "product=%s and flow=%s and indicators=%s and reporter=%s and partner=%s and period=%s and value=%s and extracted_on=%s) limit 1"
#
#                 res = cur.execute(sql, (product,flow,indicators,reporter,partner,period,value,extracted_on,created_at,product,flow,indicators,reporter,partner,period,value,extracted_on))
#                 conn.commit()
#                 conn.close()
#
# excel_path = "C://Users//lyz//Desktop//DS-018995 (2).xls"
# path = "C://Users//lyz//Desktop//欧盟海关进出口_6"
# files= os.listdir(path)
# for file in files:
#     excel_path = path+"//"+file
#     insert_into_db(excel_path)
