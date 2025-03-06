import requests
from loguru import logger

cookies = {
    'route': '65389440feb63b53ee0576493abca26d',
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://ys.endata.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://ys.endata.cn/BoxOffice/Ranking',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

data = {
    'r': '0.9435953734223699',
    'top': '50',
    'type': '0',
}

response = requests.post(
    'https://ys.endata.cn/enlib-api/api/home/getrank_mainland.do',
    cookies=cookies,
    headers=headers,
    data=data,
)

logger.info(response.json())