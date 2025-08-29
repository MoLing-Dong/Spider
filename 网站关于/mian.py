import requests

cookies = {
    'hb_MA-BFB6-AC673A756684_source': 'qiye.163.com',
    '_ntes_nnid': '0cf41d52f1b1bb739e23d2221bfeab8c,1745222119358',
    '_ntes_nuid': '0cf41d52f1b1bb739e23d2221bfeab8c',
    '_gcl_au': '1.1.709777257.1745223836',
    'hb_MA-8254-1A734A8B4E77_source': 'qiye.163.com',
    '_fbp': 'fb.1.1745223836866.972994038185476787',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'hb_MA-BFB6-AC673A756684_source=qiye.163.com; _ntes_nnid=0cf41d52f1b1bb739e23d2221bfeab8c,1745222119358; _ntes_nuid=0cf41d52f1b1bb739e23d2221bfeab8c; _gcl_au=1.1.709777257.1745223836; hb_MA-8254-1A734A8B4E77_source=qiye.163.com; _fbp=fb.1.1745223836866.972994038185476787',
}

response = requests.get('https://corp.163.com/gb/contactus.html', cookies=cookies, headers=headers)
print(response.text)
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
