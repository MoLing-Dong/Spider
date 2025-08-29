import logging

import requests
from bs4 import BeautifulSoup

# 定义全局变量
cookies = {'UserId': '17351945672016447'}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}


def fetch_and_parse_first_page(city_name):
    try:
        response = requests.get(f'https://lishi.tianqi.com/{city_name}/202412.html', cookies=cookies, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        ul_element = soup.find("ul", class_="thrui")
        if ul_element:
            # 使用列表推导式提取数据
            first_page_data = [
                " ".join([data_element.text for data_element in li_element.find_all("div", class_="th200")] +
                        [data_element.text for data_element in li_element.findAll("div", class_="th140")])
                for li_element in ul_element.find_all("li")
            ]
            return first_page_data
        else:
            logging.warning("No ul element with class 'thrui' found.")
            return []
    except requests.RequestException as e:
        logging.error(f"Error occurred while fetching first page: {e}")
        return []


def fetch_and_parse_second_page(city_id):
    try:
        response = requests.get(f'https://tianqi.2345.com/wea_history/{city_id}.htm', cookies=cookies, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, "html.parser")
        table_element = soup.find("table", class_="history-table")
        if table_element:
            # 使用列表推导式提取数据
            second_page_data = [
                td_elements[0].text + " " + td_elements[5].text
                for index, tr_element in enumerate(table_element.find_all("tr")) if index > 0
                for td_elements in [tr_element.find_all("td")] if len(td_elements) >= 6
            ]
            return second_page_data
        else:
            logging.warning("No table element with class 'history-table' found.")
            return []
    except requests.RequestException as e:
        logging.error(f"Error occurred while fetching second page: {e}")
        return []


def merge_data(first_page_data, second_page_data):
    # 将 second_page_data 存储在字典中，键为日期，值为数据
    second_page_dict = {item.split()[0]: item.split()[3] for item in second_page_data}
    merged_data = []
    for first_item in first_page_data:
        date_first = first_item.split()[0]
        merged_item = first_item + " " + second_page_dict.get(date_first, "")
        merged_data.append(merged_item)
    return merged_data


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("foshan")
    first_page_data = fetch_and_parse_first_page("foshan")
    second_page_data = fetch_and_parse_second_page("59288")
    merged_data = merge_data(first_page_data, second_page_data)
    for item in merged_data:
        logging.info(item)
    logging.info("guangzhou")
    guangzhou_first_page_data = fetch_and_parse_first_page("guangzhou")
    guangzhou_second_page_data = fetch_and_parse_second_page("59287")
    merged_data = merge_data(guangzhou_first_page_data, guangzhou_second_page_data)
    for item in merged_data:
        logging.info(item)