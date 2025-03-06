# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from loguru import logger

# 设置日志文件
logger.add("song_scraper.log", rotation="10 MB", retention="10 days", level="INFO")

# 请求头信息
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://music.163.com/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}


def fetch_song_list():
    try:
        # 发起 GET 请求获取页面内容
        response = requests.get('https://music.163.com/discover/toplist', headers=headers)
        response.raise_for_status()  # 检查响应状态

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取歌曲列表，提取所有 ul.f-hide 下的 li 标签
        song_list = [li for ul in soup.find_all('ul', class_='f-hide') for li in ul.find_all('li')]

        logger.info(f"成功获取到 {len(song_list)} 首歌曲")
        return song_list

    except requests.exceptions.RequestException as e:
        logger.error(f"请求发生错误: {e}")
        return []
    except Exception as e:
        logger.error(f"解析歌曲列表时发生错误: {e}")
        return []


def main():
    logger.info("开始获取歌曲列表...")
    song_list = fetch_song_list()

    if song_list:
        for song in song_list:
            # 打印每首歌的信息
            #  <li><a href="/song?id=2624184878">细伢子（她·我）</a></li>
            # 取ref和歌名
            song_name = song.find('a').text
            song_url = song.find('a')['href']
            logger.info(f"歌曲名: {song_name}, 链接:https://music.163.com{song_url}")


if __name__ == "__main__":
    main()
