import json

import requests
from fake_useragent import UserAgent
from loguru import logger
from requests.exceptions import RequestException

# 定义常量
URL = 'http://df.huayu.edu.cn/wxapp/pay/queryElectricity'
COOKIES = {
    'JSESSIONID': '7BADF1EB7FD02E56B8DCEA08C04E40A5',
}
HEADERS = {
    'User-Agent': UserAgent().random,
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://df.huayu.edu.cn',
    'Referer': 'http://df.huayu.edu.cn/wxapp/api/oauth',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}
DATA = {
    'userXq': '山东华宇工学院',
    'userFj': '401018',
    'payType': '1',
}


def fetch_electricity_info():
    try:
        # 发起POST请求并忽略SSL验证
        response = requests.post(URL, cookies=COOKIES, headers=HEADERS, data=DATA, verify=False)
        response.raise_for_status()  # 如果响应状态不是200，将抛出HTTPError异常
    except RequestException as e:
        # 使用loguru记录更详细的错误信息
        logger.error(f"请求失败: {e}")
        return None

    try:
        response_json = response.json()['message']
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"解析响应JSON失败: {e}")
        return None
    logger.info(f"解析响应JSON成功: {response_json}")

    # 构建信息字符串9
    info = (
        f"剩余免费电量：{response_json.get('freeElec', 'N/A')}度\n"
        f"总电量：{response_json.get('plusElec', 'N/A')}度\n"
        f"剩余电费：{response_json.get('feeElec', 'N/A')}度\n"
        f"宿舍号：{response_json.get('room', 'N/A')}\n"
        f"状态：{response_json.get('status', 'N/A')}"
    )
    return info


if __name__ == '__main__':
    electricity_info = fetch_electricity_info()
    if electricity_info:
        logger.info("查询到的电量信息如下：")
        logger.info(electricity_info)
    else:
        logger.error("未能成功获取电量信息。")

