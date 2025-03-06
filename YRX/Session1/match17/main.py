# -*- coding: utf-8 -*-
import httpx

# 设置 cookies
cookies = {
    'Hm_lvt_c99546cf032aaa5a679230de9a95c7db': '1718590817',
    'sessionid': 'di4xdxjp00fnag4402frn10cvgfir5pa',
    'qpfccr': 'true',
    'no-alert3': 'true',
    'yuanrenxue_cookie': '1723519964|6GnYYTLIHMABV09DN6f3XiwoJnHFgrp2izIvFEt9EQfNrP8',
}

# 设置请求头
headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://match.yuanrenxue.cn/match/17',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'x-requested-with': 'XMLHttpRequest',
}

# 初始化累加值
total_sum = 0

# 使用 HTTP/2 发起请求
with httpx.Client(http2=True) as client:
    for page in range(1, 6):
        params = {'page': str(page)}
        response = client.get('https://match.yuanrenxue.cn/api/match/17', params=params, cookies=cookies,
                              headers=headers)
        print(f"Page {page} response: {response.text}")

        # 对响应结果进行解析，并累加 sum
        for item in response.json().get('data', []):
            total_sum += item.get('value', 0)

print(f"Total sum: {total_sum}")
