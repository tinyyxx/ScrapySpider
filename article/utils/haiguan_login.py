# -*- coding: utf-8 -*-
import requests
import smtplib
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print ("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"
header = {
    "HOST":"www.haiguan.info",
    "Referer": "http://www.haiguan.info/Login.aspx",
    'User-Agent': agent,
    "X-AjaxPro-Method":'Encode'
}

def haiguan_login(account, password):
    print ("手机号码登录")
    post_url = "http://www.haiguan.info/ajaxpro/SCEC.HaiguanInfo.Login,SCEC.HaiguanInfo.ashx"
    post_data = '{"loginStr":"'+account+'/'+'"}'
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

#haiguan_login("deya201", "deya123456")