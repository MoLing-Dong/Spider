# -*- coding: utf-8 -*-
import re

import requests
import urllib3

# 禁用 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 初始 cookies 设置
cookies = {
    'Hm_lvt_c99546cf032aaa5a679230de9a95c7db': '1718590817',
    'sessionid': 'di4xdxjp00fnag4402frn10cvgfir5pa',
    'qpfccr': 'true',
    'no-alert3': 'true',
}

# 请求头设置
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://match.yuanrenxue.cn/match/13',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'priority': 'u=0, i',
}

# 第一次请求，获取页面内容
response = requests.get('https://match.yuanrenxue.cn/match/13', cookies=cookies, headers=headers, verify=False)

# 使用正则表达式提取出拼接后的 cookie 内容
cookie_match = re.search(r"document\.cookie\s*=\s*(.+?);", response.text)
if cookie_match:
    cookie_string = cookie_match.group(1)
    # 使用正则表达式提取 'y' 形式的字符串，并拼接
    result = ''.join(re.findall(r"\('([^']+)'\)", cookie_string))
    # 只保留 '=' 之后的部分
    result = result.split('=')[1] if '=' in result else ''
    # 将提取到的值添加到 cookies 中
    cookies['yuanrenxue_cookie'] = result

    print(f"Extracted yuanrenxue_cookie: {result}")
sum = 0
# 遍历 page 1 到 5，发起请求并输出结果
for page in range(1, 6):
    params = {

        'page': str(page),
    }
    response = requests.get('https://match.yuanrenxue.cn/api/match/13', params=params, cookies=cookies, headers=headers,
                            verify=False)
    print(f"Page {page} response: {response.text}")
    #     对响应结果进行解析，并累加 sun
    for item in response.json()['data']:
        sum += item['value']

print(sum)
