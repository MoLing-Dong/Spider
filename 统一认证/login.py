# -*- coding: utf-8 -*-
"""统一认证平台的登录
"""
import time

import execjs
import requests
from loguru import logger
from lxml import etree

from config import settings


def create_session():
    """创建一个连接会，并配置日志记录
    """
    session = requests.session()
    logger.add("list.log", rotation="10 MB", retention="10 days", level="INFO")
    return session


def get_login_page(session, auth_server_domain, ehall_domain):
    """发送GET请求获取登录页面
    """
    response = session.get(
        f"{auth_server_domain}/authserver/login?service={ehall_domain}%2Flogin%3Fservice%3D{ehall_domain}%2Fywtb-portal%2Fofficial%2Findex.html"
    )
    return response


def extract_parameters(html_text):
    """提取加密盘、lt和execution参数
    """
    tree = etree.HTML(html_text)
    pwdDefaultEncryptSalt = tree.xpath('//input[@id="pwdDefaultEncryptSalt"]/@value')[0]
    lt = tree.xpath('//input[@name="lt"]/@value')[0]
    execution = tree.xpath('//input[@name="execution"]/@value')[0]
    logger.info(f"pwdDefaultEncryptSalt: {pwdDefaultEncryptSalt}, lt: {lt}, execution: {execution}")
    return pwdDefaultEncryptSalt, lt, execution


def get_encrypted_password(session, auth_server_domain, password, salt):
    """获取加密后的密码
    """
    response = session.get(f"{auth_server_domain}/authserver/custom/js/encrypt.js", allow_redirects=False)
    js_code = response.text
    js_res = execjs.compile(js_code)
    encrypted_password = js_res.call("_ep", password, salt)
    logger.info(f"加密后的密码: {encrypted_password}")
    return encrypted_password


def login(session, auth_server_domain, ehall_domain, username, encrypted_password, lt, execution):
    """发送POST请求进行登录
    """
    headers = {
        "Origin": auth_server_domain,
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }
    params = {
        "service": f"{ehall_domain}/login?service={ehall_domain}/ywtb-portal/official/index.html",
    }
    data = {
        "username": username,
        "password": encrypted_password,
        "lt": lt,
        "dllt": "userNamePasswordLogin",
        "execution": execution,
        "_eventId": "submit",
        "rmShown": "1",
    }
    response = session.post(
        f"{auth_server_domain}/authserver/login",
        params=params,
        headers=headers,
        data=data,
        verify=False,
        allow_redirects=True,
    )
    logger.info(f"登录后的cookie: {session.cookies.get_dict()}")
    return response


def get_user_info(session, ehall_domain):
    """发送GET请求获取用户信息
    """
    timestamp = int(time.time() * 1000)
    response = session.get(f"{ehall_domain}/jsonp/ywtb/info/getUserInfoAndSchoolInfo?_={timestamp}")
    logger.info(f"用户信息响应: {response.text}")
    return response.text


def main():
    auth_server_domain = "http://authserver.huayu.edu.cn"
    ehall_domain = "http://ehall.huayu.edu.cn"
    username = settings.HUAYU_TONGYI_ACCOUNT
    password = settings.HUAYU_TONGYI_PASSWORD
    session = create_session()

    login_page_response = get_login_page(session, auth_server_domain, ehall_domain)
    pwdDefaultEncryptSalt, lt, execution = extract_parameters(login_page_response.text)
    encrypted_password = get_encrypted_password(session, auth_server_domain, password, pwdDefaultEncryptSalt)

    login(session, auth_server_domain, ehall_domain, username, encrypted_password, lt, execution)
    get_user_info(session, ehall_domain)


if __name__ == "__main__":
    main()
