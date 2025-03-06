# -*- coding: utf-8 -*-

import concurrent.futures
import json

import pandas as pd
import requests
from loguru import logger

# 配置日志记录
logger.add("fetch.log", rotation="10 MB", retention="10 days", level="INFO")

session = requests.Session()
cookies = {
    'JSESSIONID': '1d2cc103-d089-4f8f-bdad-8910f853c3e3',
    'route': '4e39643a15b7003e568cadd862137cf3',
}

session.cookies.update(cookies)
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Cookie': 'JSESSIONID=aa14eaa3-8618-4580-8b44-279a6a64efa1; route=4e39643a15b7003e568cadd862137cf3; SECKEY_ABVK=uZeysBI0dS+UQXL4kJV1gyAjTuEpV8k7JZFfUDDxcmY%3D; BMAP_SECKEY=lwH-kEIxbZkWlmmKF54ChF7Ivz8V-bSYYkqqeSkCWfiHQlIOXTZ-mQaAFlU4Gti7JgSKOvymYkJsWV8B7yvmU4CGo9cUkcvgSlQX4Xu3Wu48xrM8UnuXpPpHb4KQGsGxHdxCL6Lt3DLHgCUL4sY721SkfnSl1smqHVVCAYR9-U6xI4LQTaMZyIKVRo4So2aY',
    'Origin': 'https://ys.endata.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://ys.endata.cn/BoxOffice/Org',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

data_template = {
    'r': '0.965886316419589',
    'datetype': 'Day',
    'date': '2024-06-08',
    'sdate': '2024-06-08',
    'edate': '2024-06-08',
    'citylevel': '',
    'lineid': '',
    'columnslist': '100,101,102,121,122,103,104,108,123,109',
    'pageindex': '1',
    'pagesize': '20',
    'order': '102',
    'ordertype': 'desc',
}


def fetch_page(page_index):
    """
    获取指定页码的数据
    """
    data = data_template.copy()
    data['pageindex'] = str(page_index)
    response = session.post(
        'https://ys.endata.cn/enlib-api/api/cinema/getcinemaboxoffice_day_list.do',
        headers=headers,
        data=data,
    )
    try:
        response_data = json.loads(response.text)
        logger.info(f"Page {page_index}: {response_data}")
        return response_data.get('data', {}).get('table1', [])
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return []


def save_to_csv(data_list, file_name):
    """
    保存数据到CSV文件
    """
    header_written = False
    for df_temp in data_list:
        df_temp = pd.DataFrame(df_temp)
        if not header_written:
            df_temp.to_csv(file_name, index=False, mode='w')  # 使用'w'模式写入表头
            header_written = True
        else:
            df_temp.to_csv(file_name, index=False, mode='a', header=False)  # 使用'a'模式追加数据


def get_total_pages():
    """
    获取总页数
    """
    response = session.post(
        'https://ys.endata.cn/enlib-api/api/cinema/getcinemaboxoffice_day_list.do',
        headers=headers,
        data=data_template,
    )
    try:
        logger.info(f"Total pages response: {response.text}")
        response_data = json.loads(response.text)
        total_pages = response_data.get('data', {}).get('table2', [{}])[0].get('TotalPage', 0)
        logger.info(f"Total pages: {total_pages}")
        return total_pages
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return 0
    except (IndexError, AttributeError) as e:
        logger.error(f"解析总页数时出错: {e}")
        return 0


def main():
    total_pages = get_total_pages()
    if total_pages == 0:
        logger.error("未能获取总页数，程序终止")
        return

    data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_page = {executor.submit(fetch_page, i): i for i in range(1, total_pages + 1)}
        for future in concurrent.futures.as_completed(future_to_page):
            page_index = future_to_page[future]
            try:
                data_list.append(future.result())
            except Exception as exc:
                logger.error(f"Page {page_index} generated an exception: {exc}")

    # 保存数据到CSV
    csv_file = 'list.csv'
    save_to_csv(data_list, csv_file)


if __name__ == "__main__":
    main()
