# -*- coding: utf-8 -*-
import scrapy
import requests
from urllib import parse
import http.cookiejar as cookielib

class HaiguanSpider(scrapy.Spider):
    name = 'Haiguan'
    allowed_domains = ['www.haiguan.info']
    start_urls = ['http://www.haiguan.info/Login.aspx/']
    headers = {
        "HOST": "www.haiguan.info",
        "Referer": "http://www.haiguan.info/Login.aspx",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
        "X-AjaxPro-Method": ''
    }


    def start_requests(self):
        return [scrapy.Request('http://www.haiguan.info/Login.aspx', headers=self.headers, callback=self.login)]

    def parse(self, response):
        pass

    def login(self,response):
        session = requests.session()
        session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
        try:
            session.cookies.load(ignore_discard=True)
        except:
            print("cookie未能加载")
        account = 'deya201'
        password = 'deya123456'
        captcha = response.css("#imgcode::attr(src)").extract_first()
        captcha_url = parse.urljoin(response.url,captcha)
        post_url = 'http://www.haiguan.info/ajaxpro/SCEC.HaiguanInfo.Login,SCEC.HaiguanInfo.ashx'
        post_data = '{"loginStr":"'+account+'/'+password+'"}'
        self.headers['X-AjaxPro-Method']='Encode'
        response = session.post(post_url,data=post_data,headers=self.headers)
        session.cookies.save()
        token = str(response.content,encoding='utf-8').split('"')[1]
        #获取验证码
        t = session.get(captcha_url)
        with open('captcha.jpg','wb') as f:
            f.write(t.content)
            f.close()
        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        code = input("输入验证码\n>")

        post_data = '{"loginStr":"' + token + '","code":"'+code+'"}'
        self.headers['X-AjaxPro-Method'] = 'CheckLogin'
        #请求checklogin
        response = session.post(post_url,data=post_data,headers=self.headers)
        session.cookies.save()

        #scrapy自动发送邮件
        from scrapy.mail import MailSender
        # mailer = MailSender.from_settings(settings)# 出错了，没找到原因
        mailer = MailSender(
            smtphost="smtp.163.com",  # 发送邮件的服务器
            mailfrom="m18868740439@163.com",  # 邮件发送者
            smtpuser="Leo",  # 用户名
            smtppass="85873mn4",  # 发送邮箱的密码不是你注册时的密码，而是授权码！！！切记！
            smtpport=25  # 端口号
        )
        body = """ 
               发送的邮件内容 :
               海关信息网登陆成功啦，赶紧打开你的pycharm查看查看查看！！！！
               """
        subject = '爬虫邮件测试测试'
        # 如果说发送的内容太过简单的话，很可能会被当做垃圾邮件给禁止发送。
        mailer.send(to=["726951055@qq.com"], subject=subject, body=body)

    pass




