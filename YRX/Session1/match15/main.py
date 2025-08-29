#
import random
import time

import pywasm
import requests

# 加载WASM模块
vm = pywasm.load('main.wasm')


# 定义encode函数
def encode(t1, t2):
    return vm.exec('encode', [t1, t2])


# 定义m函数
def m():
    t1 = int(time.time() // 2)
    t2 = int(time.time() // 2 - random.randint(1, 50))
    encoded_result = encode(t1, t2)
    return f'{encoded_result}|{t1}|{t2}'


headers = {
    "authority": "match.yuanrenxue.cn",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9",
    "referer": "https://match.yuanrenxue.cn/match/15",
    "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    'Hm_lvt_c99546cf032aaa5a679230de9a95c7db': '1718590817',
    'sessionid': 'di4xdxjp00fnag4402frn10cvgfir5pa',
    'no-alert3': 'true',
    'yuanrenxue_cookie': '1723519964|6GnYYTLIHMABV09DN6f3XiwoJnHFgrp2izIvFEt9EQfNrP8',
}
url = "https://match.yuanrenxue.cn/api/match/15"

ret = 0
for pageIndex in range(1, 6):
    params = {
        "m": m(),
        "page": pageIndex
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    print(response.text)
    data = response.json()["data"]
    for item in data:
        ret += item['value']
print(ret)
