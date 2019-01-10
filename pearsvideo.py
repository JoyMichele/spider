import requests
from lxml import etree
from random import random
import re

"""
思路:
1. 向音乐板块的排行榜页面发请求,获取排行榜a标签的href(用于跳转视频播放页面)
2. 向视频播放页面发送请求,拿到video标签中src属性
3. 向video的src地址发送请求,获取视频,保存到本地
"""
url = 'https://www.pearvideo.com/popular_59'
next_url = 'https://www.pearvideo.com/popular_loading.jsp'
headers = {
    # 启用UA代理
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    # 请求结束释放连接,归还到连接池
    'Connection': 'close'
}
xpath_rule = '//a[@class="popularembd actplay"]/@href'
page_text = requests.get(url=url, headers=headers).text

"""
<a href="video_1500281" class="actplay" target="_blank">
    <div class="popularem-img" style="background-image: url(https://image.pearvideo.com/main/20190102/11308777-192800-0.png);">
        <div class="cm-duration">04:45</div>
        </div>
</a>
"""
tree = etree.HTML(page_text)
video_url = tree.xpath(xpath_rule)
"""
在排行榜url使用了懒加载,第一次向排行榜url请求时值返回了前10名的数据
在滚动滚轮到第10名下,或点击加载更多的时候,发送了ajax请求到 https://www.pearvideo.com/popular_loading.jsp
第一次点击加载更多时,请求参数为下列params中的内容,且呈现一定规律,其中        
"start": 10,
"sort": 10,
"mrd": 0.1234568412336998
这次请求服务器返回了一段html,7个li标签包裹着11-17名的内容
返回数据数: 7
已经拥有数据数: 17

start类似于分页的起始页,但不是用于分页,每次请求+10
sort是已经收到的排行榜数据数,已经收到了10个
mrd是用js代码: Math.random()生成的随机小数



第二次:
"start": 20,
"sort": 17,
"mrd": 0.1233699812345684
返回数据数: 5
已经拥有数据数: 22

第二次:
"start": 30,
"sort": 22,
"mrd": 0.1981234523369684
返回数据数 : 10
已经拥有数据数: 32

...

规律已经明了:
start += 10
sort += 从最开始的10开始,一直是已经拥有的数据数量,li标签数(扒出前端js为: $('#popularem li').length)
"""
start_page = 0
sort_page = 0
sort_num = 10
while sort_num:
    start_page += 10
    sort_page += sort_num
    params = {
        "reqType": "1",
        "categoryId": "59",
        "start": start_page,
        "sort": sort_page,
        "mrd": random()
    }
    next_text = requests.get(url=next_url, headers=headers, params=params).text
    new_tree = etree.HTML(next_text)
    new_video_url = new_tree.xpath(xpath_rule)
    video_url.extend(new_video_url)
    sort_num = len(new_video_url)
    # print(len(new_video_url))
    # print(video_url)
video_play_list = []
# 向每个视频详情的url发起请求获取视频文件地址
for video_page in video_url:
    video_full_url = "https://www.pearvideo.com/" + video_page
    video_text = requests.get(url=video_full_url, headers=headers).text
    """
    <script type="text/javascript">
    var contId="1500364",......srcUrl="https://video.pearvideo.com/mp4/third/20190103/cont-1500364-11905134-094747-hd.mp4"......
    """
    # 在script中隐藏着视频地址,利用正则匹配出视频地址
    ex = 'srcUrl="(.*?)"'
    video = re.findall(ex, video_text, re.S)[0]
    video_play_list.append(video)
print(video_play_list)
