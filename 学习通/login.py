# -*- coding: utf-8 -*-

import base64

import requests
from Crypto.Cipher import AES  # pip install pycryptodome
from bs4 import BeautifulSoup
from loguru import logger

logger.add("list.log", rotation="10 MB", retention="10 days", level="INFO")

user_account = "18669321513"
user_password = "weibd371327"

session = requests.Session()


def encrypt(content: str) -> str:
    k = "u2oh6Vu^HWe4_AES"
    iv = "u2oh6Vu^HWe4_AES"
    # k:密钥，iv:偏移量，content:需加密的内容
    k = k.encode("utf-8")
    iv = iv.encode("utf-8")
    # pad = lambda s: s + (16 - len(s)%16) * chr(0) # AES加密时，明文长度需为16的倍数。这里的pad用来填充，chr(0)表示为ZeroPadding，在最后填充0直到长度为16的倍数
    pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)  # 这里为Pkcs7填充
    content = pad(content).encode("utf-8")
    cipher = AES.new(k, AES.MODE_CBC, iv)  # CBC模式加密，还有ECB模式
    cipher_text = cipher.encrypt(content)
    enc = base64.b64encode(cipher_text).decode("utf-8")
    # enc = binascii.b2a_hex(cipher_text).decode("utf-8")
    return enc


headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://passport2.chaoxing.com',
    'Pragma': 'no-cache',
    'Referer': 'https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https://i.chaoxing.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

cookies = {
    # 'fid': '108854',
    # 'route': 'fb0878d2b253f576b9614a77ccc901db',
    # 'JSESSIONID': 'C82114BB028F9C953C8B3E15FF90B300',
    # 'source': '""',
    # 'retainlogin': '1',
}


def login():
    """
    登录到 https://passport2.chaoxing.com/fanyalogin 网站。

    该函数没有参数。

    :return: 无返回值，但会在控制台打印登录结果信息。
    """

    # 加密用户账号和密码
    USER_ACCOUNT = encrypt(user_account)
    USER_PASSWORD = encrypt(user_password)

    # 准备登录请求的数据
    data = {
        'fid': '-1',
        'uname': USER_ACCOUNT,
        'password': USER_PASSWORD,
        'refer': 'https%3A%2F%2Fi.chaoxing.com',
        't': 'true',
        'forbidotherlogin': '0',
        'validate': '',
        'doubleFactorLogin': '0',
        'independentId': '0',
        'independentNameId': '0',
    }

    # 发起登录请求
    response = session.post('https://passport2.chaoxing.com/fanyalogin', cookies=cookies, headers=headers, data=data)

    # 记录登录请求的响应内容
    logger.info(response.text)

    # 检查登录是否成功，并记录信息
    if response.json()['status']:
        logger.info("登录成功")


def get_course_list() -> list:
    """
    获取课程列表
    :return:
    """
    data = {
        'courseType': '1',
        'courseFolderId': '0',
        'baseEducation': '0',
        'superstarClass': '',
        'courseFolderSize': '0',
    }

    response = session.post('https://mooc1-1.chaoxing.com/mooc-ans/visit/courselistdata', cookies=cookies,
                            headers=headers,
                            data=data)

    soup = BeautifulSoup(response.text, 'html.parser')
    course_info_list = soup.find_all(class_='course-info')
    # logger.info(course_info_list)
    coure = []
    for course_info in course_info_list:
        logger.info("链接:" + course_info.find('a')['href'])
        logger.info("课程名:" + course_info.find(class_='course-name').text.strip())
        coure.append({"course_name": course_info.find(class_='course-name').text.strip(),
                      "course_url": course_info.find('a')['href']})
    return coure


def get_course_info(course_url: str):
    response = session.get(course_url, cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    course_info = soup.find(class_='course-info')
    logger.info(course_info)
    pass


if __name__ == '__main__':
    login()
    coure_list = get_course_list()
    logger.info(len(coure_list))
    pass
