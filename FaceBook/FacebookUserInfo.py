import bs4
import requests

cookies = {
    'datr': 'sB64Z27q0UK8r0_jFAovr6v7',
    'sb': 'sB64Z0vKnQOV2OR9aFo26ah2',
    'ps_l': '1',
    'ps_n': '1',
    'c_user': '100067427447465',
    'fr': '1gE0J0BFSc5k0Z2uh.AWWj22zZmMgqr4isMUN5UrCNqoWVON1hYXCgLg.Bnu8pv..AAA.0.0.Bnu8pv.AWWmaOu2FfQ',
    'xs': '39%3AVQu-s2Gp5BO_lQ%3A2%3A1740119960%3A-1%3A-1%3A%3AAcXwWA8Pglu30q37Q1F-6H97SZV4jiGggPU-63NPqg',
    'presence': 'C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1740360798544%2C%22v%22%3A1%7D',
    'wd': '560x919',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'dpr': '1',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-prefers-color-scheme': 'dark',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-full-version-list': '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.127", "Chromium";v="133.0.6943.127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'viewport-width': '560',
    # 'cookie': 'datr=sB64Z27q0UK8r0_jFAovr6v7; sb=sB64Z0vKnQOV2OR9aFo26ah2; ps_l=1; ps_n=1; c_user=100067427447465; fr=1gE0J0BFSc5k0Z2uh.AWWj22zZmMgqr4isMUN5UrCNqoWVON1hYXCgLg.Bnu8pv..AAA.0.0.Bnu8pv.AWWmaOu2FfQ; xs=39%3AVQu-s2Gp5BO_lQ%3A2%3A1740119960%3A-1%3A-1%3A%3AAcXwWA8Pglu30q37Q1F-6H97SZV4jiGggPU-63NPqg; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1740360798544%2C%22v%22%3A1%7D; wd=560x919',
}

response = requests.get('https://www.facebook.com/stockhonduras/', headers=headers)

# print(response.text)
with open('facebook.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
# ... existing code ...

html = bs4.BeautifulSoup(response.text, 'html.parser')

# 使用正则表达式匹配粉丝数文本
import re
full_pattern = r'"text":"([^"]+?)"}'
full_matches = re.findall(full_pattern, response.text)
if full_matches:
    for match in full_matches:
        match = match.encode().decode('unicode-escape')
        print(match)

# 检测手机号
phone_pattern = r'^\+[1-9]\d{0,2}(?:[ -]?\d)+$'
for match in full_matches:
    if re.match(phone_pattern, match):
        print(f"手机号: {match}")
