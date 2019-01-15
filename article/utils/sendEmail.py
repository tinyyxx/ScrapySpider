import smtplib
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.application import MIMEApplication


def mail(result_path, result_name):
    my_sender = 'm18868740439@163.com'  # 发件人邮箱账号
    #my_pass = '85873mn4'  # 发件人邮箱密码
    #my_user = '726951055@qq.com'  # 收件人邮箱账号，我这边发送给自己

    name = result_name
    # 第二步发送文件
    sender = my_sender  # 发件人邮箱账号
    my_pass = '85873mn4'  # 发件人授权码
    receiver = 'chj@deyainvest.com'  # 收件人邮箱账号，我这边发送给自己
    try:
        msg = MIMEMultipart()
        msg['From'] = formataddr(["lyz", sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["接收人", receiver])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "每日爬虫文件excel"  # 邮件的主题，也可以说是标题
        filepath = result_path                        #'D://share//' + name  # 绝对路径
        xlsxpart = MIMEApplication(open(filepath, 'rb').read())
        basename = name
        # 注意：此处basename要转换为gbk编码，否则中文会有乱码。
        xlsxpart.add_header('Content-Disposition', 'attachment', filename=('gbk', '', basename))
        msg.attach(xlsxpart)
        server = smtplib.SMTP("smtp.163.com")  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱授权码
        server.sendmail(sender, receiver, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print("success")
    except smtplib.SMTPException as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print('error', e) # 打印错误

