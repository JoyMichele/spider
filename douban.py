# 需求: 爬取豆瓣电影的电影详情数据 (豆瓣电影详情是 ------动态加载------)

from selenium import webdriver  # selenium借助于浏览器的驱动程序
from time import sleep

bro = webdriver.Chrome(executable_path='/Users/joy/Desktop/study/爬虫/chromedriver')
url = 'https://movie.douban.com/typerank?type_name=%E7%88%B1%E6%83%85&type=13&interval_id=100:90&action='

# 发送请求
bro.get(url=url)

# 滚轮滚动的设置 可以去页面Console验证一下
js = 'window.scrollTo(0, document.body.scrollHeight)'  # 可以去页面验证一下js
bro.execute_script(js)
sleep(2)
bro.execute_script(js)
sleep(2)
bro.execute_script(js)
sleep(2)

page_text = bro.page_source

# with open('./douban.html', 'w') as fp:
#     fp.write('page_text')

bro.quit()