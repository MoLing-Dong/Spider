import re

import requests
from bs4 import BeautifulSoup
from loguru import logger

headers = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41',
    'sec-ch-ua':
        '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

response = requests.get('https://movie.douban.com/chart',
                        headers=headers,verify=False)

tree = BeautifulSoup(response.text, 'lxml')
movie_list = tree.find_all('div', class_='pl2')
for movie_item in movie_list:
    movie_name = movie_item.find('a').get_text()
    # 清 除 空 格 和 换 行
    movie_name = re.sub(r'\s', '', movie_name)
    movie_url = movie_item.find('a').get('href')
    movie_info = movie_item.find('p', class_='pl').get_text()
    movie_info = re.sub(r'\s', '', movie_info)
    movie_info = re.sub(r'/', ',', movie_info)
    logger.info(f'{movie_name},{movie_url},{movie_info}')