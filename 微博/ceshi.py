
import requests

cookies = {
    'SINAGLOBAL': '2598867652217.838.1708872522069',
    'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WFv6MxTuB4ugLbqATEJ2Zm.5JpX5KMhUgL.Fo-cSoB4eo2pS0n2dJLoI0YLxK-LBK-L12zLxK-L12qL1K2LxK-L1-zLB.-LxK-LB.eLB.2LxKqL1KqLBo5LxK.L1-BL1KzLxK-LBo.LBoBt',
    'SCF': 'Ai_JzoS98QhWTTXbGkbhUyUXgAmQOl5qcc_unevN0zXS5Ne8iFw-QTqHrdd0p69dWPQKchzNU4OXK8N7l99ZjcU.',
    'ALF': '1722693613',
    'SUB': '_2A25Lgtq9DeRhGeNI7VYY8i_NzDSIHXVo_lJ1rDV8PUJbkNANLXf2kW1NSFA0r6JikX1efsKJ2Xv0-hFmxF3so8Ed',
    '_s_tentry': 'wenku.csdn.net',
    'UOR': 'www.baidu.com,weibo.com,wenku.csdn.net',
    'Apache': '3520588237929.3384.1720150386865',
    'ULV': '1720150386928:5:1:1:3520588237929.3384.1720150386865:1715093515584',
}

headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    # 'cookie': 'SINAGLOBAL=2598867652217.838.1708872522069; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFv6MxTuB4ugLbqATEJ2Zm.5JpX5KMhUgL.Fo-cSoB4eo2pS0n2dJLoI0YLxK-LBK-L12zLxK-L12qL1K2LxK-L1-zLB.-LxK-LB.eLB.2LxKqL1KqLBo5LxK.L1-BL1KzLxK-LBo.LBoBt; SCF=Ai_JzoS98QhWTTXbGkbhUyUXgAmQOl5qcc_unevN0zXS5Ne8iFw-QTqHrdd0p69dWPQKchzNU4OXK8N7l99ZjcU.; ALF=1722693613; SUB=_2A25Lgtq9DeRhGeNI7VYY8i_NzDSIHXVo_lJ1rDV8PUJbkNANLXf2kW1NSFA0r6JikX1efsKJ2Xv0-hFmxF3so8Ed; _s_tentry=wenku.csdn.net; UOR=www.baidu.com,weibo.com,wenku.csdn.net; Apache=3520588237929.3384.1720150386865; ULV=1720150386928:5:1:1:3520588237929.3384.1720150386865:1715093515584',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://s.weibo.com/weibo?q=%E8%8E%8E%E5%A4%B4&t=31&band_rank=50&Refer=top',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

params = {
    'act': 'list',
    'mid': '5052700780401163',
    'uid': '5664921178',
    'smartFlag': 'false',
    'smartCardComment': '',
    'isMain': 'true',
    'suda-data': 'key%3Dtblog_search_weibo%26value%3Dweibo_h_1_p_p',
    'pageid': 'weibo',
    '_t': '0',
    '__rnd': '1720162372107',
}

response = requests.get('https://s.weibo.com/Ajax_Comment/small', params=params, cookies=cookies, headers=headers)
print(response.text)