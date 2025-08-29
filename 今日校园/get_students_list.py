import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from loguru import logger

URL = 'https://sdhyxy.campusphere.net/wec-campushoy-pc-contacts-apps/v9'

# 必须的cookie，否则会报错
cookies = {
    'MOD_AUTH_CAS': 'userClientId=1725700439248youye0rrvb72cbmgr1a4; HWWAFSESID=8533376cd55d4d9c43; HWWAFSESTIME=1730724968799; MOD_AUTH_CAS=ST-iap:1018615983375022:ST:2d0d8a8d-9ce3-4656-a06e-63364cd27503:20241104205617',
}

# 建议修改为自己的user-agent
headers = {
    'clientType': 'cpdaily_student',
    'tenantId': 'sdhyxy',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 14; LE2120 Build/UP1A.230620.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36 cpdaily/9.4.6 wisedu/9.4.6',
    'deviceType': '1',
    'Cache-Control': 'max-age=0',
    'Host': 'sdhyxy.campusphere.net',
    'Connection': 'Keep-Alive',
}

# 设置If-Modified-Since header
time_now = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
headers['If-Modified-Since'] = time_now

session = requests.Session()


def make_request(url, params=None):
    """发送HTTP请求，捕获所有异常并记录详细日志"""
    try:
        logger.debug(f"Sending request to {url} with params {params}")
        response = session.get(url, params=params, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        logger.debug("Request succeeded")
        return response.json()
    except requests.Timeout:
        logger.error(f"Timeout occurred for URL: {url} with params {params}")
        return {}
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred for URL: {url} with params {params}: {http_err}")
        return {}
    except requests.ConnectionError:
        logger.error(f"Connection error occurred for URL: {url}")
        return {}
    except requests.RequestException as req_err:
        logger.error(f"Request error occurred for URL: {url} with params {params}: {req_err}")
        return {}


def get_org_list(org_kind, parent_id=None):
    """获取组织列表，捕获异常并记录日志"""
    params = {
        'orgId': parent_id,
        'orgKind': org_kind,
        'pageNum': '1',
        'pageSize': '100',
        'needRefreshOrgInfo': 'true',
        'oick': 'a0e35f2a'
    }
    try:
        response = make_request(f'{URL}/user/address-book/student/users-and-org', params)
        if not response:
            logger.error("Failed to retrieve org list.")
            return []
        orgs = response.get('data', {}).get('orgInfo', {}).get('orgs', [])
        logger.info(f"Retrieved {len(orgs)} orgs for orgKind {org_kind}")
        return orgs if orgs else []
    except Exception as e:
        logger.error(f"Error occurred while retrieving org list for orgKind {org_kind}: {e}")
        return []


def get_students_list(org_id, page_num=1, page_size=100, max_depth=10):
    """获取学生列表，捕获异常并记录详细日志"""
    if page_num > max_depth:
        logger.warning("Maximum recursion depth reached. Returning current result.")
        return []

    params = {
        'orgId': org_id,
        'orgKind': '5',
        'pageNum': page_num,
        'pageSize': page_size,
        'needRefreshOrgInfo': 'true',
        'oick': 'a0e35f2a'
    }
    try:
        response = make_request(f'{URL}/user/address-book/student/users-and-org', params)
        if not response:
            logger.error(f"Failed to retrieve students list for orgId {org_id}.")
            return []

        total_size = response.get('data', {}).get('userInfo', {}).get('totalSize', 0)
        result = response.get('data', {}).get('userInfo', {}).get('result', [])
        if result is None:
            logger.warning("No student data found.")
            return []

        if page_size * page_num < total_size:
            result.extend(get_students_list(org_id, page_num + 1, page_size, max_depth))

        return result
    except Exception as e:
        logger.error(f"Error retrieving students list for orgId {org_id}: {e}")
        return []


def process_class(class_info, college_name, major_name):
    """处理班级信息，捕获异常并记录详细日志"""
    try:
        student_list = get_students_list(class_info['id'])
        for student in student_list:
            student['orgName'] = student.get('orgName', college_name)
            student['majorName'] = student.get('majorName', major_name)
            student['className'] = student.get('className', class_info['name'])
        return student_list
    except Exception as e:
        logger.error(f"Error processing class {class_info['name']}: {e}")
        return []


def process_major(major, college_name):
    """处理专业信息，捕获异常并记录详细日志"""
    try:
        classes = get_org_list('4', major['id'])
        if not classes:
            logger.warning(f"No classes found for major: {major['name']}")
            return []

        all_students = []
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_class, class_info, college_name, major['name']): class_info for
                       class_info in classes}
            for future in as_completed(futures):
                try:
                    all_students.extend(future.result())
                except Exception as e:
                    logger.error(f"Error in processing class for major {major['name']}: {e}")
        return all_students
    except Exception as e:
        logger.error(f"Error processing major {major['name']}: {e}")
        return []


def process_college(college):
    """处理学院信息，捕获异常并记录详细日志"""
    try:
        majors = get_org_list('2', college['id'])
        if not majors:
            logger.warning(f"No majors found for college: {college['name']}")
            return []

        all_students = []
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_major, major, college['name']): major for major in majors}
            for future in as_completed(futures):
                try:
                    all_students.extend(future.result())
                except Exception as e:
                    logger.error(f"Error in processing major for college {college['name']}: {e}")
        return all_students
    except Exception as e:
        logger.error(f"Error processing college {college['name']}: {e}")
        return []


if __name__ == "__main__":
    start_time = time.time()
    try:
        colleges = get_org_list('1')
        if not colleges:
            logger.error("No colleges found, terminating process.")

        all_students = []
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_college, college): college for college in colleges}
            for future in as_completed(futures):
                try:
                    all_students.extend(future.result())
                except Exception as e:
                    logger.error(f"Error processing college data: {e}")

        # 将结果写入CSV文件
        if all_students:
            try:
                df = pd.DataFrame(all_students)
                df.to_csv('students.csv', mode='w', index=False, encoding='utf-8', header=True)
                logger.info("Successfully saved student data to students.csv")
            except Exception as e:
                logger.error(f"Error saving CSV file: {e}")
        else:
            logger.warning("No student data to save.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    end_time = time.time()
    logger.info(f"Time elapsed: {end_time - start_time:.2f} seconds")
