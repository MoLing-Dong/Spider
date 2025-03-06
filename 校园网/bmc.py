# -*- coding: utf-8 -*-
import requests

cookies = {
    'JSESSIONID': '1xq60ejak80xdd4pcu5edvfgy',
    '__session:sessionID:': 'http:',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Cookie': 'JSESSIONID=1xq60ejak80xdd4pcu5edvfgy; __session:sessionID:=http:',
    'Origin': 'http://172.16.29.13',
    'Pragma': 'no-cache',
    'Referer': 'http://172.16.29.13/bmc/main',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

params = {
    'vtt': 'undefined',
}

data = {
    'isSaveUserName': '',
    'CSRFToken': '',
    'username': 'qwe',
    'password': '76d80224611fc919a5d54f0ff9fba446',
}

response = requests.post('http://172.16.29.13''/bmc/login', params=params, cookies=cookies, headers=headers, data=data,
                         verify=False)

# 将响应文本编码为 UTF-8，并打印
print(response.text.encode("gbk", "ignore").decode("gbk", "ignore"))

