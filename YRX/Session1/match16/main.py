import time

import execjs
import requests

headers = {
    "authority": "match.yuanrenxue.cn",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9",
    "referer": "https://match.yuanrenxue.cn/match/16",
    "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

cookies = {
    "Hm_lvt_434c501fe98c1a8ec74b813751d4e3e3": "1701926709,1701955396,1702100746,1702448923",
    "Hm_lvt_c99546cf032aaa5a679230de9a95c7db": "1703552347,1703552869,1703580276,1703646938",
    "qpfccr": "true",
    "no-alert3": "true",
    "Hm_lvt_9bcbda9cbf86757998a2339a0437208e": "1703552349,1703554106,1703580280,1703646951",
    "m": "119a8fe4dbde85c0ca8384785d643dd0|1703646961000",
    "tk": "-4933119763790217557",
    "sessionid": "di4xdxjp00fnag4402frn10cvgfir5pa",
    "Hm_lpvt_9bcbda9cbf86757998a2339a0437208e": "1703646990",
    "Hm_lpvt_c99546cf032aaa5a679230de9a95c7db": "1703647832"
}

url = "https://match.yuanrenxue.cn/api/match/16"
sum = 0
# sxmKNRnTN5P7eWM3fa5b1cc14561e5ab86891f2dc04540cQAJSXENynE
# 1703648742000
# tr223ptSPRnsRFyb0f9fc56451225d010b2a83e95a73618MzFaASJTrc
# 1703649184000
for i in range(1, 6):
    timeNow = (int)(time.time()) * 1000
    ts = execjs.compile(open('./btoa.js', 'r', encoding='utf-8').read()).call('main', timeNow)
    params = {
        "page": f"{i}",
        "m": f"{ts['m']}",
        "t": str(timeNow)
    }
    print(ts['time'])
    print(params)
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    print(response.text)
    listNo = response.json()["data"]
    for li in listNo:
        sum += li['value']
print(sum)