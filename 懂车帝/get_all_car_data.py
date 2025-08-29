# -*- coding: utf-8 -*-
import json
import time

import requests
from loguru import logger
from requests import Response

session = requests.Session()
# 获取当前日期
today = time.strftime("%Y-%m-%d", time.localtime())
logger.add(f"{today}-list.log", rotation="10 MB", retention="10 days", level="INFO")

cookies = {
    'ttwid': '1%7CDiy0AA_0niDXfYuM-_qPpXJ6NziX7dIRe2-m6xoAw2M%7C1709717482%7Ce59d95b01d30dcffab9c9cc9867da9d6b157a4dd8ea8f00a658e952217cdcfd0',
    'tt_webid': '7343180616353924671',
    'tt_web_version': 'new',
    '_ga': 'GA1.1.134724865.1709717484',
    'city_name': '%E5%BE%B7%E5%B7%9E',
    's_v_web_id': 'verify_lvzfmsen_2kCSBpnd_hwWo_4kN0_9G49_JT0gTMelPWii',
    'is_dev': 'false',
    'is_boe': 'false',
    '_ga_YB3EWSDTGF': 'GS1.1.1716217276.6.1.1716218044.55.0.0',
}

headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    # 'cookie': 'ttwid=1%7CDiy0AA_0niDXfYuM-_qPpXJ6NziX7dIRe2-m6xoAw2M%7C1709717482%7Ce59d95b01d30dcffab9c9cc9867da9d6b157a4dd8ea8f00a658e952217cdcfd0; tt_webid=7343180616353924671; tt_web_version=new; _ga=GA1.1.134724865.1709717484; city_name=%E5%BE%B7%E5%B7%9E; s_v_web_id=verify_lvzfmsen_2kCSBpnd_hwWo_4kN0_9G49_JT0gTMelPWii; is_dev=false; is_boe=false; _ga_YB3EWSDTGF=GS1.1.1716217276.6.1.1716218044.55.0.0',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.dongchedi.com/sales/sale-energy-202403-x-x-x-x',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

params = {
    'aid': '1839',
    'app_name': 'auto_web_pc',
    'city_name': '北京',
    'count': '10',
    'offset': '0',
    'month': '202401',
    'new_energy_type': '1,2,3',
    'rank_data_type': '11',
    'brand_id': '',
    'price': '',
    'manufacturer': '',
    'outter_detail_type': '',
    'nation': '0',
}


def fetch_car_data(month: str, offset: str) -> None | Response:
    """
    从dongchedi.com获取汽车数据。

    参数:
    - month: 字符串，指定要查询的月份。
    - offset: 字符串，分页参数，用于指定数据的偏移量，通常用于翻页。

    返回值:
    - 返回字典，包含从网站获取的汽车数据。如果发生异常，则返回None。
    """
    try:
        # 复制全局参数并更新为指定的月份和偏移量
        local_params = params.copy()
        local_params['month'] = month
        local_params['offset'] = offset

        # 发起HTTP GET请求并记录响应
        this_response = session.get('https://www.dongchedi.com/motor/pc/car/rank_data', params=local_params,
                                    headers=headers)
        # logger.info(this_response.json())
        # logger.info("是否还有更多数据: %s", this_response.json().get('data').get('paging').get('has_more'))
        # logger.info(f"是否还有更多数据: {this_response.json().get('data').get('paging').get('has_more')}")
    except Exception as e:
        # 记录任何在请求过程中发生的异常
        logger.error(e)
        return None
    return this_response.json()


def get_all_car_data(month: str) -> list:
    """
    获取指定月份的所有汽车数据。

    参数:
    - month: 字符串，指定要查询的月份。

    返回值:
    - 返回一个列表，包含从网站获取的所有汽车数据。如果发生异常，则返回空列表。
    """
    this_all_car_data = []
    offset = 0
    while True:
        try:
            # 获取汽车数据
            this_data = fetch_car_data(month, str(offset))
            if this_data is None:
                break
            # 将数据添加到列表
            this_all_car_data.extend(this_data.get('data').get('list'))
            # 如果没有更多数据，则退出循环
            if not this_data.get('data').get('paging').get('has_more'):
                break
            # 更新偏移量
            offset += 10
        except Exception as e:
            # 记录任何在请求过程中发生的异常
            logger.error(e)
            break
    return this_all_car_data


if __name__ == '__main__':
    input_list = {}
    for year in range(2020, 2024):
        for month in range(1, 13):
            logger.info(str(year) + str(month).zfill(2))
            # time.sleep(1)
            all_car_data = get_all_car_data(str(year) + str(month).zfill(2))
            # 转为json格式并保存到文件
            input_list[str(year) + str(month).zfill(2)] = all_car_data
            # 转为json格式并保存到文件
            with open('car_data.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(input_list, ensure_ascii=False, indent=4))

