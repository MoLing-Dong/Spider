import requests
from bs4 import BeautifulSoup
from loguru import logger



headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'ect': '3g',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"133.0.6943.142"',
    'sec-ch-ua-full-version-list': '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.142", "Chromium";v="133.0.6943.142"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
}

params = {
    'q': 'pizza',
}

response = requests.get('https://cn.bing.com/search', params=params,  headers=headers)
html=BeautifulSoup(response.text, 'html.parser')
# 获取clss 为 b_widePag 的a标签
a_tags = html.find_all('a', class_='b_widePag')
logger.info(f"页面的数量：{len(a_tags)}")
# 遍历a标签
for a_tag in a_tags:
    # 获取a标签的href属性
    href = a_tag.get('href')
    # 打印href
    print(href)

# 获取 li 的class 为b_algo
li_tags = html.find_all('li', class_='b_algo')
# 遍历li标签
for li_tag in li_tags:
    # 获取li标签的h2标签
    h2_tag = li_tag.find('h2')
    # 获取h2标签的a标签
    a_tag = h2_tag.find('a')
    # 获取a标签的href属性
    href = a_tag.get('href')
    # 获取a标签的文本
    text = a_tag.text
    # 获取li 标签的所有子孙的 p标签
    p_tag = li_tag.find('p')
    # 获取p标签的文本
    p_text = p_tag.text
    logger.info(f"标题：{text}，链接：{href}，描述：{p_text}")