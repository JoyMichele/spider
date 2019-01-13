import http.client, mimetypes, urllib, json, time, requests
from multiprocessing.dummy import Pool
import re

pool = Pool(5)


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
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
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
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
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
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
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


def code2text(code_type, img_path):
    # 用户名
    username = '#########'  # 此处是云打码平台的用户名

    # 密码
    password = '#########'  # 此处是云打码平台的密码

    # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appid =  ####

    # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appkey = '################################'

    # 图片文件
    filename = img_path

    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = code_type

    # 超时时间，秒
    timeout = 60

    # 检查
    if (username == 'username'):
        print('请设置好相关参数再测试')
        return
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
        print('cid: %s, result: %s' % (cid, result))
        return result


# 自如网站的数据爬取
url = 'http://www.ziroom.com/z/nl/z2.html'  # 自如主页面
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}
search = input('输入地铁,区域,小区名: ')
search_params = {
    "qwd": search
}
house_list_text = requests.get(url=url, headers=headers, params=search_params).text

"""
在请求房源列表服务器返回的html中已经可以直接通过xpath获取除了价格之外的所有简介信息,而价格是通过js处理后渲染上去的
在房源详细页面也是一样,价格通过js处理的,可以根据需求选择在房源列表页面获取信息,同时处理价格的问题,若需要房源详细信息
则在房源详细页面,同时处理价格问题.由于只有价格是需要特殊处理的,其他信息都是直接获取,在此只爬取价格信息
"""

# 第一种需求 : 获取房源列表每个房源价格(第一页)
"""
分析过程:
首先检查html代码中有没有最终渲染数据的全部信息,发现价格信息的span标签没有生成,只有外层的<p class='price'>和内部的其他span
于是考虑是js动态生成的价格span标签,添加到p标签中,在chrome的开发者工具中network中进行'price'的全局搜索,经过筛选发现如下代码:

var ROOM_PRICE = {
    "image": "//static8.ziroom.com/phoenix/pc/images/price/e05092a2f84c9cca5e4d881535072ae1s.png",
    "offset": [[0, 5, 5, 7], [8, 0, 3, 7], [8, 7, 5, 7], [8, 6, 5, 7], [8, 7, 9, 7], [8, 0, 5, 7], [0, 6, 3, 7], [8, 2, 3, 7], 
    [8, 0, 9, 7], [8, 4, 5, 7], [8, 0, 3, 7], [8, 9, 3, 7], [8, 2, 9, 7], [8, 5, 5, 7], [0, 5, 9, 7], [8, 0, 5, 7], [8, 1, 9, 7], [8, 4, 3, 7]]
};
$('#houseList p.price').each(function(i) {
    var dom = $(this);
    if (!ROOM_PRICE['offset'] || !ROOM_PRICE['offset'][i])
        return;
    var pos = ROOM_PRICE['offset'][i];
    for (i in pos) {
        var inx = pos.length - i - 1;
        var seg = $('<span>', {
            'style': 'background-position:-' + (pos[inx] * offset_unit) + 'px',
            'class': 'num'
        });
        dom.prepend(seg);
    }
    var seg = $('<span>', {
        'style': 'background-position:1000px',
        'class': 'num rmb'
    }).html('￥');
    dom.prepend(seg);
});

访问 ROOM_PRICE 字典(对象)中image对应的url,https//static8.ziroom.com/phoenix/pc/images/price/e05092a2f84c9cca5e4d881535072ae1s.png
获得了一张数字图片 : 1743598026 , 且每次获取的ROOM_PRICE变量都是不同的
结合渲染页面中的价格信息,图片数字和ROOM_PRICE中的offset二维数组,一维数组中的每个元素作为索引与数字图片形成映射关系构成了价格
    数字图片               offset            价格
1 7 4 3 5 9 8 0 2 6     [0, 5, 5, 7]  -->   1 9 9 0
                        [8, 0, 3, 7]  -->   2 1 3 0
"""
img_info = re.findall('var ROOM_PRICE = {"image":"(.*?)","offset":(.*?)};', house_list_text, re.S)[0]
# 数字图片的url
price_img_url = 'https:' + img_info[0]

# 数字图片的offset_list
offset_list = json.loads(img_info[1])
print(offset_list)

# 向数字图片的url发送请求并保存图片至本地,调用第三方平台云打码的验证码识别功能用来识别数字图片的内容
img_bytes = requests.get(url=price_img_url, headers=headers).content

# 图片保存路径
price_img_path = './price_model.jpg'
with open(price_img_path, 'wb')as f:
    f.write(img_bytes)
    print('下载图片成功!')

# 识别图片中的数字
price_model = code2text(4010, price_img_path)
for offset in offset_list:
    # 进行索引和数字的映射,解析出价格信息
    price = map(lambda index: price_model[index], offset)
    print(list(price))

# 第二种需求 根据房源列表页面获取的房源详情url进行访问,获取价格信息
# from lxml import etree
#
# tree = etree.HTML(house_list_text)
# detail_list = ('//a[@class="t1"]/@href')
# print(detail)
