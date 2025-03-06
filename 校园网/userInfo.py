import requests

'''
获取当前登录用户的信息包括学号，用户组

'''
headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://172.16.29.12',
    'Referer': 'http://172.16.29.12/homepage/index.html?_FLAG=1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

data = {
    'opr': 'list',
}

response = requests.post('http://172.16.29.12/homepage/info.php', headers=headers, data=data, verify=False)
print(response.text)
