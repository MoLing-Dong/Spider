import requests

cookies = {
    'SINAGLOBAL': '385231718020.9153.1734939586738',
    'SCF': 'An7VUdumkrkMcAe252nEeEPfmHPdLXTmbtSOYqFLfeJCBVLnpbP54OH_2wD698J-0zz6Kp8mb6QwgcCvX1fY-5s.',
    'XSRF-TOKEN': 'Ey3pdbFD_BXTfWcjSZtqy6q4',
    'SUB': '_2A25KdhRZDeRhGeFG6lsT9izEyjmIHXVpCimRrDV8PUNbmtANLWakkW9NfjPenBbcMNR_6lThzi3klyaKZzJh6eow',
    'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WWJjmlRPuFvpb9xNOuaZa7c5JpX5KzhUgL.FoMReK.ESozReK-2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1h24eoqE1h2f',
    'ALF': '02_1738141961',
    '_s_tentry': 'passport.weibo.com',
    'Apache': '3646407794151.885.1735549963741',
    'ULV': '1735549964273:2:2:1:3646407794151.885.1735549963741:1734939586741',
    'WBPSESS': 'Dt2hbAUaXfkVprjyrAZT_I7iK1KUyTrN2dyMGJEJ-gESCc4GzV_RgqEPJh_jaBnYf_CcfRova-E7KgtEDmumnYNXYvqCBKSZXcolw3t4l6Ntn078w7VHpLRkFwNfXjCjJ457UxoeQ0zUubnq30EnssKh-052Yoy8HTeuHpzgMnutXz5Z0w5IPqCiVlnXXAHjIlaeTvIxJwW6OSNmGIeS-Q==',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'client-version': 'v2.47.15',
    # 'cookie': 'SINAGLOBAL=385231718020.9153.1734939586738; SCF=An7VUdumkrkMcAe252nEeEPfmHPdLXTmbtSOYqFLfeJCBVLnpbP54OH_2wD698J-0zz6Kp8mb6QwgcCvX1fY-5s.; XSRF-TOKEN=Ey3pdbFD_BXTfWcjSZtqy6q4; SUB=_2A25KdhRZDeRhGeFG6lsT9izEyjmIHXVpCimRrDV8PUNbmtANLWakkW9NfjPenBbcMNR_6lThzi3klyaKZzJh6eow; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWJjmlRPuFvpb9xNOuaZa7c5JpX5KzhUgL.FoMReK.ESozReK-2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1h24eoqE1h2f; ALF=02_1738141961; _s_tentry=passport.weibo.com; Apache=3646407794151.885.1735549963741; ULV=1735549964273:2:2:1:3646407794151.885.1735549963741:1734939586741; WBPSESS=Dt2hbAUaXfkVprjyrAZT_I7iK1KUyTrN2dyMGJEJ-gESCc4GzV_RgqEPJh_jaBnYf_CcfRova-E7KgtEDmumnYNXYvqCBKSZXcolw3t4l6Ntn078w7VHpLRkFwNfXjCjJ457UxoeQ0zUubnq30EnssKh-052Yoy8HTeuHpzgMnutXz5Z0w5IPqCiVlnXXAHjIlaeTvIxJwW6OSNmGIeS-Q==',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://weibo.com/u/2328516855?tabtype=feed',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'server-version': 'v2024.12.27.1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'x-xsrf-token': 'Ey3pdbFD_BXTfWcjSZtqy6q4',
}

params = {
    'uid': '2328516855',
    'page': '1',
    'q': '警情通报',
}

response = requests.get('https://weibo.com/ajax/statuses/searchProfile', params=params, cookies=cookies,
                        headers=headers)
print(response.text.encode('gbk', errors='ignore').decode('gbk'))