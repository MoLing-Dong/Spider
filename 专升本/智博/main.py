import csv
import os

import requests
from bs4 import BeautifulSoup
from loguru import logger


# 日志配置


def get_html(url, params, headers):
    """
    发送 GET 请求并返回页面的 HTML 内容
    """
    try:
        logger.info(f"Requesting URL: {url} with params: {params}")
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        logger.info("Successfully retrieved HTML content.")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error occurred while requesting {url}: {e}")
        return None


def write_csv(file_path, fieldnames, data):
    """
    将数据写入 CSV 文件
    """
    try:
        logger.info(f"Writing data to CSV file at {file_path}")
        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info("Data successfully written to CSV.")
    except Exception as e:
        logger.error(f"Error occurred while writing to CSV: {e}")


def parse_html(html):
    """
    解析 HTML 并提取数据
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        major_list = soup.find_all('div', class_='detail-item')

        fieldnames = ['数学类型', '专业名称', '学校名称', '24年招生计划', '较23年变化', '23年投档线']
        data = []

        for major_item in major_list:
            major_math = major_item.find('label').get_text(strip=True)
            major_name = major_item.find('h3', class_='dialog-title').get_text(strip=True)
            major_plan_school = major_item.find_all('tr')

            for school_item in major_plan_school:
                try:
                    school_name = school_item.find('td', class_='name').get_text(strip=True)
                    school_major_plan_info = [info.get_text(strip=True) for info in
                                              school_item.find_all('td', class_='count')]

                    # 防止缺失数据导致索引错误
                    if len(school_major_plan_info) >= 3:
                        data.append({
                            '数学类型': major_math,
                            '专业名称': major_name,
                            '学校名称': school_name,
                            '24年招生计划': school_major_plan_info[0],
                            '较23年变化': school_major_plan_info[1],
                            '23年投档线': school_major_plan_info[2]
                        })
                    else:
                        logger.warning(f"Incomplete data for school {school_name} under major {major_name}")

                except AttributeError as e:
                    logger.warning(f"Skipping an item due to missing information: {e}")

        return fieldnames, data
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return None, []


def scrape_data():
    """
    主函数：获取网页内容，解析并保存数据
    """
    headers = {
        'User-Agent':
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/111.0.0.0',
    }

    params = {
        'title': '计算机网络技术',
    }

    url = 'http://sdzsbks.zhibojiaoyu.cn/detail'
    html = get_html(url, params, headers)
    if html:
        fieldnames, data = parse_html(html)
        if data:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(this_dir, 'data.csv')
            write_csv(file_path, fieldnames, data)
        else:
            logger.error("No data found to write to CSV.")
    else:
        logger.error("Failed to retrieve HTML content.")


if __name__ == "__main__":
    scrape_data()
