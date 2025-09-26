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

# 添加状态码检查
logger.info(f"请求状态码: {response.status_code}")
logger.debug(f"响应内容长度: {len(response.text)}")

tree = BeautifulSoup(response.text, 'html.parser')

# 调试：查看页面结构
logger.debug("查找所有可能的电影容器...")
possible_containers = tree.find_all('div', class_=['pl2', 'item', 'movie-item'])
logger.debug(f"找到的容器类型: {[div.get('class') for div in possible_containers[:3]]}")

# 查看前几个元素的结构
for i, container in enumerate(possible_containers[:2]):
    logger.debug(f"容器 {i+1} 的HTML结构: {str(container)[:200]}...")

movie_list = tree.find_all('div', class_='pl2')

logger.info(f"找到 {len(movie_list)} 部电影")

for i, movie_item in enumerate(movie_list, 1):
    try:
        # 获取电影名称和链接
        movie_link = movie_item.find('a')
        if not movie_link:
            logger.warning(f"第 {i} 部电影：找不到链接元素")
            continue
            
        movie_name = movie_link.get_text()
        movie_url = movie_link.get('href')
        
        if not movie_name or not movie_url:
            logger.warning(f"第 {i} 部电影：名称或链接为空")
            continue
        
        # 清除空格和换行
        movie_name = re.sub(r'\s', '', movie_name)
        
        # 获取电影信息（更新页面结构）
        movie_info_element = movie_item.find('p')  # 移除class='pl'限制
        if movie_info_element:
            movie_info = movie_info_element.get_text()
            movie_info = re.sub(r'\s', '', movie_info)
            movie_info = re.sub(r'/', ',', movie_info)
            logger.debug(f"第 {i} 部电影 '{movie_name}' 的详细信息: {movie_info[:50]}...")
        else:
            movie_info = "暂无信息"
            logger.debug(f"第 {i} 部电影 '{movie_name}' 没有详细信息")
        
        logger.info(f'{movie_name},{movie_url},{movie_info}')
        
    except Exception as e:
        logger.error(f"处理第 {i} 部电影时发生错误: {e}")
        continue