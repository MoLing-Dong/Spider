import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# This is the 2.11 Requests cipher string, containing 3DES.
CIPHERS = (
    'ECDH+AESGCM:'
    '!aNULL:'
    '!eNULL:!MD5'
)


class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests.
    """

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)


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


def getPage(page):
    sss = 0
    page = str(page)
    s = requests.Session()
    s.mount(f'https://match.yuanrenxue.cn/api/match/19?page={page}', DESAdapter())
    r = s.get(headers=headers, cookies=cookies, url=f'https://match.yuanrenxue.cn/api/match/19?page={page}')
    values = r.json()['data']
    for i in values:
        sss += int(i['value'])
        # print(i['value'])
    return sss


sum = 0
for i in range(1, 6):
    sum += getPage(i)

print(sum)
