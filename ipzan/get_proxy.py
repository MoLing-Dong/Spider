import time
import sys
import os
from pathlib import Path

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from loguru import logger

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import ipzan_settings
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


def test_proxy(proxy, port, account=None, password=None, timeout=10):
    """测试代理IP的可用性（多种测试方法）"""
    if account and password:
        proxies = {
            'http': f'http://{account}:{password}@{proxy}:{port}',
            'https': f'http://{account}:{password}@{proxy}:{port}'
        }
        proxy_auth = f"{account}:{password}@"
    else:
        proxies = {
            'http': f'http://{proxy}:{port}',
            'https': f'http://{proxy}:{port}'
        }
        proxy_auth = ""
    
    logger.info(f"测试代理: {proxy_auth}{proxy}:{port}")
    
    # 测试URLs列表，按优先级排序
    test_urls = [
        'http://httpbin.org/ip',  # HTTP版本，更容易连接
        'https://httpbin.org/ip', # HTTPS版本
        'http://icanhazip.com',   # 备用服务
        'https://api.ipify.org?format=json'  # 另一个IP服务
    ]
    
    for i, test_url in enumerate(test_urls, 1):
        try:
            logger.debug(f"尝试测试URL {i}/{len(test_urls)}: {test_url}")
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            response.raise_for_status()
            
            # 根据不同服务解析IP
            if 'httpbin.org' in test_url:
                result_ip = response.json().get('origin', '').split(',')[0].strip()
            elif 'icanhazip.com' in test_url:
                result_ip = response.text.strip()
            elif 'ipify.org' in test_url:
                result_ip = response.json().get('ip', '')
            else:
                result_ip = "未知"
            
            logger.info(f"✅ 代理IP: {proxy}:{port} 可用")
            logger.info(f"   通过代理访问的IP: {result_ip}")
            logger.debug(f"   测试URL: {test_url}")
            return True
            
        except requests.exceptions.ProxyError as e:
            logger.debug(f"   代理连接错误 (URL {i}): {e}")
            continue
        except requests.exceptions.Timeout as e:
            logger.debug(f"   连接超时 (URL {i}): {e}")
            continue
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"   连接错误 (URL {i}): {e}")
            continue
        except Exception as e:
            logger.debug(f"   其他错误 (URL {i}): {e}")
            continue
    
    logger.error(f"❌ 代理IP: {proxy}:{port} 不可用（所有测试URL都失败）")
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
    if not res:
        logger.error("IP提取请求失败。")
        return None
    
    if 'data' not in res or res['data'] is None:
        logger.error(f"IP提取失败: {res.get('message', '未知错误')}")
        return None
    
    if 'list' not in res['data']:
        logger.error("返回数据格式错误：缺少list字段。")
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
    # 检查配置是否完整
    config = {
        "no": ipzan_settings.IPZAN_CONFIG_NO,
        "login_password": ipzan_settings.IPZAN_CONFIG_LOGIN_PASSWORD,
        "package_key": ipzan_settings.IPZAN_CONFIG_PACKAGE_KEY,
        "sign_key": ipzan_settings.IPZAN_CONFIG_SIGN_KEY,
        "user_id": ipzan_settings.IPZAN_CONFIG_USER_ID
    }
    
    logger.info("检查IPZAN配置...")
    missing_configs = []
    for key, value in config.items():
        if not value:
            missing_configs.append(key)
            logger.warning(f"配置项 {key} 为空")
        else:
            logger.info(f"配置项 {key}: {'*' * min(len(str(value)), 8)}...")
    
    if missing_configs:
        logger.error(f"以下配置项缺失: {missing_configs}")
        logger.error("请在.env文件中设置以下环境变量:")
        for key in missing_configs:
            env_name = key.upper()
            if not env_name.startswith("IPZAN_CONFIG_"):
                env_name = f"IPZAN_CONFIG_{env_name}"
            logger.error(f"  {env_name}=你的{key}值")
        exit(1)
    
    logger.info("配置检查通过，开始执行...")
    result = process_ip(**config)
    if result:
        proxy, port = result
        logger.info(f"最终代理IP: {proxy}:{port}")
    else:
        logger.error("代理IP获取失败")
