# -*- coding: utf-8 -*-
import execjs
import requests
from loguru import logger

# 初始化日志文件
logger.add("music_scraper.log", rotation="10 MB", retention="10 days", level="INFO")

# 请求所需的数据模板
data_template = {
    "ids": "",  # SONG_ID 作为可变参数传递
    "level": "standard",
    "encodeType": "aac",
    "csrf_token": "",
}

# 请求头
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


# 获取加密数据的函数
def get_encrypted_data(song_id_encrypted):
    try:
        # 设置当前 song_id
        data_template["ids"] = f"[{song_id_encrypted}]"

        with open("../reverse.js", "r", encoding="utf-8") as f:
            js_code = f.read()
        # 使用 execjs 编译 JavaScript
        js_complied = execjs.compile(js_code)
        # 调用 JavaScript 函数来获取加密的数据
        result = js_complied.call("getData", data_template)
        logger.info(f"加密数据获取成功: {result}")
        return {"params": result["encText"], "encSecKey": result["encSecKey"]}
    except Exception as e:
        logger.error(f"获取加密数据时发生错误: {e}")
        return None


# 发送请求并获取歌曲播放链接的函数
def fetch_song_url(song_id_this: str):
    try:
        encrypted_data = get_encrypted_data(song_id_this)
        if not encrypted_data:
            logger.error("加密数据为空，无法进行请求")
            return

        params = {
            'csrf_token': 'd0aebecb5b99ae82a6d858a5ed477be3',
        }

        # 发送 POST 请求
        response = requests.post(
            'https://music.163.com/weapi/song/enhance/player/url/v1',
            params=params,
            headers=headers,
            data=encrypted_data,
        )

        # 检查响应状态并记录日志
        response.raise_for_status()
        logger.info(f"请求成功，响应数据: {response.text}")
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"请求发生错误: {e}")
    except Exception as e:
        logger.error(f"发生其他错误: {e}")


# 主程序入口
if __name__ == "__main__":
    SONG_ID = "22673491,16334195"  # 可以设置多个歌曲ID，用逗号分隔
    for song_id in SONG_ID.split(","):
        logger.info(f"开始获取歌曲ID为 {song_id} 的播放链接...")
        result = fetch_song_url(song_id.strip())
        if result:
            logger.info(f"歌曲ID {song_id} 的最终播放链接数据: {result}")
