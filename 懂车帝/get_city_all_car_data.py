# -*- coding: utf-8 -*-
"""
用于获取不同城市的车辆信息
"""
import json
import queue
import threading

import requests
from loguru import logger

# loguru配置
logger.add("list.log", rotation="10 MB", retention="10 days", level="INFO")

headers = {
    'authority': 'www.dongchedi.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.dongchedi.com/sales/city-energy-x-x-x',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

params = {
    'aid': '1839',
    'app_name': 'auto_web_pc',
    'city_name': '北京',
    'count': '10',
    'offset': '0',
    'month': '',
    'new_energy_type': '1,2,3',
    'rank_data_type': '64',
    'brand_id': '',
    'price': '',
    'manufacturer': '',
    'outter_detail_type': '',
    'nation': '0',
}

car_list_queue = queue.Queue()
threads = []
NUM_THREADS = 10  # 可以根据需求调整线程数量


def fetch_car_data(city_name, offset):
    try:
        local_params = params.copy()
        local_params['city_name'] = city_name  # 更新城市名称
        local_params['offset'] = str(offset)
        response = requests.get('https://www.dongchedi.com/motor/pc/car/rank_data', params=local_params,
                                headers=headers)
        # logging.info(response.json())
        logger.info(response.json())
        car_list_queue.put(response.json().get('data').get('list'))
    except Exception as e:
        logger.error("请求失败: %s", e)


def worker(city_name):
    while True:
        offset = offsets_queue.get()
        if offset is None:
            break
        fetch_car_data(city_name, offset)
        offsets_queue.task_done()


if __name__ == '__main__':
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities_data = json.load(f)

    for city in cities_data:
        car_list_queue = queue.Queue()
        threads = []
        NUM_THREADS = 10

        # 获取总数以计算需要多少次请求
        params['city_name'] = city  # 更新城市名称
        response = requests.get('https://www.dongchedi.com/motor/pc/car/rank_data', params=params, headers=headers)
        total = response.json().get('data').get('paging').get('total')
        total_requests = (total + 9) // 10

        offsets_queue = queue.Queue()
        for i in range(total_requests):
            offsets_queue.put(i * 10)

        # 创建并启动线程
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=worker, args=(city,))
            t.start()
            threads.append(t)

        # 阻塞队列直到所有任务被处理完
        offsets_queue.join()

        # 停止工作线程
        for _ in range(NUM_THREADS):
            offsets_queue.put(None)
        for t in threads:
            t.join()

        # 从队列中获取所有车辆信息并写入文件
        car_list = []
        while not car_list_queue.empty():
            car_list.extend(car_list_queue.get())

        with open(f'{city}_car_list.txt', 'w', encoding='utf-8') as f:
            for car in car_list:
                logger.info(car)
                f.write(json.dumps(car, ensure_ascii=False) + '\n')
