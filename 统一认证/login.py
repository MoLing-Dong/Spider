# -*- coding: utf-8 -*-
"""统一认证平台登录（单文件版本）
"""
import time
import warnings
import execjs
import requests
from loguru import logger
from lxml import etree
from dotenv import load_dotenv
import os

# 关闭不安全请求警告
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 加载 .env 环境变量
load_dotenv()
USERNAME = os.getenv("HUAYU_TONGYI_ACCOUNT")
PASSWORD = os.getenv("HUAYU_TONGYI_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("请在 .env 文件中配置 HUAYU_TONGYI_ACCOUNT 和 HUAYU_TONGYI_PASSWORD")

# 域名配置
AUTH_SERVER_DOMAIN = "http://authserver.huayu.edu.cn"
EHALL_DOMAIN = "http://ehall.huayu.edu.cn"

def create_session():
    session = requests.session()
    logger.add("login.log", rotation="5 MB", retention="10 days", level="INFO")
    return session

def get_login_page(session):
    url = f"{AUTH_SERVER_DOMAIN}/authserver/login?service={EHALL_DOMAIN}%2Flogin%3Fservice%3D{EHALL_DOMAIN}%2Fywtb-portal%2Fofficial%2Findex.html"
    return session.get(url)

def extract_parameters(html_text):
    tree = etree.HTML(html_text)
    pwd_salt = tree.xpath('//input[@id="pwdDefaultEncryptSalt"]/@value')[0]
    lt = tree.xpath('//input[@name="lt"]/@value')[0]
    execution = tree.xpath('//input[@name="execution"]/@value')[0]
    logger.info(f"提取参数 - salt: {pwd_salt}, lt: {lt}, execution: {execution}")
    return pwd_salt, lt, execution

def get_encrypted_password(session, password, salt):
    js_url = f"{AUTH_SERVER_DOMAIN}/authserver/custom/js/encrypt.js"
    js_code = session.get(js_url, allow_redirects=False).text
    ctx = execjs.compile(js_code)
    encrypted = ctx.call("_ep", password, salt)
    logger.info(f"加密后的密码: {encrypted}")
    return encrypted

def login(session, encrypted_pwd, lt, execution):
    headers = {
        "Origin": AUTH_SERVER_DOMAIN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Upgrade-Insecure-Requests": "1"
    }
    params = {
        "service": f"{EHALL_DOMAIN}/login?service={EHALL_DOMAIN}/ywtb-portal/official/index.html",
    }
    data = {
        "username": USERNAME,
        "password": encrypted_pwd,
        "lt": lt,
        "dllt": "userNamePasswordLogin",
        "execution": execution,
        "_eventId": "submit",
        "rmShown": "1",
    }
    url = f"{AUTH_SERVER_DOMAIN}/authserver/login"
    resp = session.post(url, params=params, headers=headers, data=data, verify=False, allow_redirects=True)
    logger.info(f"登录响应URL: {resp.url}")
    logger.info(f"Cookies: {session.cookies.get_dict()}")
    return resp

def get_user_info(session):
    timestamp = int(time.time() * 1000)
    info_url = f"{EHALL_DOMAIN}/jsonp/ywtb/info/getUserInfoAndSchoolInfo?_={timestamp}"
    response = session.get(info_url)
    logger.info(f"用户信息: {response.text}")
    return response.text

def main():
    session = create_session()
    login_page = get_login_page(session)
    salt, lt, execution = extract_parameters(login_page.text)
    encrypted_pwd = get_encrypted_password(session, PASSWORD, salt)
    login(session, encrypted_pwd, lt, execution)
    get_user_info(session)

if __name__ == "__main__":
    main()
