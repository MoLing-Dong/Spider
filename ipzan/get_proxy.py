import time

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from loguru import logger

from config import settings
from utils.get_ip import get_external_ip


def construct_url(base_url, **params):
    """构造请求的URL"""
    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{base_url}?{query_string}"


def verify_white_list(no, ip):
    """验证IP是否在白名单中"""
    url = construct_url("https://service.ipzan.com/whiteList-verify", no=no, ip=ip)
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.debug(f"白名单验证响应: {response.text}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"白名单验证请求失败: {e}")
        return False


def add_to_white_list(no, ip, sign):
    """将IP添加到白名单"""
    url = "https://service.ipzan.com/whiteList-add"
    data = {
        "no": no,
        "ip": ip,
        "sign": sign
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.debug(f"添加到白名单响应: {response.text}")
        return response.text
    except requests.RequestException as e:
        logger.error(f"添加到白名单请求失败: {e}")
        return None


def get_white_list(no, user_id):
    """获取白名单信息"""
    url = construct_url("https://service.ipzan.com/whiteList-get", no=no, userId=user_id)
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.debug(f"获取白名单响应: {response.text}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"获取白名单请求失败: {e}")
        return None


def extract_ips(no, package_key, num, minute, pool, mode='whitelist', format_type='json', area=None, protocol=1):
    """提取IP地址"""
    url = "https://service.ipzan.com/core-extract"
    params = {
        'no': no,
        'secret': package_key,
        'num': num,
        'mode': mode,
        'minute': minute,
        'format': format_type,
        'area': area,
        'pool': pool,
        'protocol': protocol
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.debug(f"IP提取响应: {response.text}")
        return response.json() if format_type == 'json' else response.text
    except requests.RequestException as e:
        logger.error(f"IP提取请求失败: {e}")
        return None


def encrypt_signature(login_password, package_key, sign_key):
    """生成签名"""
    data = f"{login_password}:{package_key}:{int(time.time())}"
    key = sign_key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return encrypted_data.hex()


def test_proxy(proxy, port, account=None, password=None):
    """测试代理IP的可用性"""
    if account and password:
        proxies = {
            'http': f'http://{account}:{password}@{proxy}:{port}',
            'https': f'http://{account}:{password}@{proxy}:{port}'
        }
    else:
        proxies = {
            'http': f'http://{proxy}:{port}',
            'https': f'http://{proxy}:{port}'
        }
    try:
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=5)
        logger.debug(response.text)
        logger.info(f"代理IP: {proxy}:{port}，可用")
        return True
    except Exception as e:
        logger.error(f"代理IP: {proxy}:{port}，不可用，错误信息: {e}")
        return False


def process_ip(no, login_password, package_key, sign_key, user_id):
    """主流程：验证、添加白名单和提取IP"""
    now_ip = get_external_ip()
    logger.info(f"当前IP: {now_ip}")

    # 验证白名单
    verify_white = verify_white_list(no, now_ip)
    if verify_white.get('data'):
        logger.info("IP在白名单中，无需添加。")
    else:
        logger.info("IP不在白名单中，添加到白名单。")
        sign = encrypt_signature(login_password, package_key, sign_key)
        if not add_to_white_list(no, now_ip, sign):
            logger.error("添加到白名单失败，终止程序。")
            return None

    # 提取IP
    res = extract_ips(no, package_key, 1, 1, 'ordinary')
    if not res or 'data' not in res or 'list' not in res['data']:
        logger.error("IP提取失败或返回数据格式错误。")
        return None

    ip_data = res['data']['list'][0]
    proxy, port = ip_data['ip'], ip_data['port']
    account, password = ip_data.get('account'), ip_data.get('password')

    # 检测代理IP的可用性
    if not test_proxy(proxy, port, account, password):
        logger.error(f"代理IP: {proxy}:{port}不可用，程序结束。")
        return None

    return proxy, port


if __name__ == "__main__":
    config = {
        "no": settings.IPZAN_CONFIG_NO,
        "login_password": settings.IPZAN_CONFIG_LOGIN_PASSWORD,
        "package_key": settings.IPZAN_CONFIG_PACKAGE_KEY,
        "sign_key": settings.IPZAN_CONFIG_SIGN_KEY,
        "user_id": settings.IPZAN_CONFIG_USER_ID
    }
    result = process_ip(**config)
    if result:
        proxy, port = result
        logger.info(f"最终代理IP: {proxy}:{port}")
