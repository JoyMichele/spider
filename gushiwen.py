
# coding: utf-8

# In[3]:
import http.client, mimetypes, urllib, json, time, requests

######################################################################

class YDMHttp:

    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username  
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response
    
    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001
    
    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if (cid > 0):
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if (response):
            return response['ret']
        else:
            return -9001

    def post_url(self, url, fields, files=[]):
        for key in files:
            files[key] = open(files[key], 'rb');
        res = requests.post(url, files=files, data=fields)
        return res.text

def get_code_text(codeType,imgPath):
    # 用户名:普通用户
    username    = 'jilei761199418'

    # 密码
    password    = 'lzjl95880'                            

    # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appid       = 6591                                     

    # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appkey      = '099869da9c97a826fa3afc8d8f4de224'    

    # 图片文件
    filename    = imgPath                        

    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype    = codeType

    # 超时时间，秒
    timeout     = 15                                   

    # 检查
    if (username == 'username'):
        print('请设置好相关参数再测试')
    else:
        # 初始化
        yundama = YDMHttp(username, password, appid, appkey)

        # 登陆云打码
        uid = yundama.login();
        print('uid: %s' % uid)

        # 查询余额
        balance = yundama.balance();
        print('balance: %s' % balance)

        # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
        cid, result = yundama.decode(filename, codetype, timeout);
        #print('cid: %s, result: %s' % (cid, result))
    return result

import requests
from lxml import etree

url = "https://so.gushiwen.org/user/login.aspx?from=http://so.gushiwen.org/user/collect.aspx"

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

# 实例化一个session对象
session = requests.Session()

page_text = session.get(url=url, headers=headers).text
tree = etree.HTML(page_text)
# 拿到验证码 图片路径
code_src = "https://so.gushiwen.org" + tree.xpath('//*[@id="imgCode"]/@src')[0]
# 拿到验证码 图片 存到本地
img_data = session.get(url=code_src, headers=headers).content
with open("./gushiwen.jpg", "wb") as fp:
    fp.write(img_data)
# 调用函数让云打码识别验证码图片 返回图片内容
code_text = get_code_text(1004,'./gushiwen.jpg')   
print(code_text)
# 下面这两个很有可能是动态加载的,去前端页面发请求,然后搜索,发现这俩是在 隐藏输入框 中的value
__VIEWSTATE = tree.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
__VIEWSTATEGENERATOR = tree.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0]
# 登录的url
login_url = 'https://so.gushiwen.org/user/login.aspx?from=http%3a%2f%2fso.gushiwen.org%2fuser%2fcollect.aspx'
# post提交需要携带的数据
data = {
    "__VIEWSTATE":__VIEWSTATE,
    "__VIEWSTATEGENERATOR":__VIEWSTATEGENERATOR,
    "from":"http://so.gushiwen.org/user/collect.aspx",
    "email":"www.zhangbowudi@qq.com",
    "pwd":"bobo328410948",
    "code":code_text,
    "denglu":"登录"
}
# 模拟登录 session提交请求 携带cookie (注意这里的session是能够发送请求的对象)
page_text = session.post(url=login_url, headers=headers, data=data).content
# 用写入的方式查看结果 更清晰
with open("./gushiwen.html", "wb") as fp:
    fp.write(page_text)

