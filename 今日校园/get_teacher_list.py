import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from loguru import logger

URL = 'https://sdhyxy.campusphere.net/wec-campushoy-pc-contacts-apps/v9'

cookies = {
    "MOD_AUTH_CAS": "ST-iap:1018615983375022:ST:909cf380-0945-49dc-8d3f-f6faa06f1e9e:20241211222346",
    "HWWAFSESID": "94ca973e814d61b11f",
    "HWWAFSESTIME": "1733927026602"


}

headers = {
    'clientType': 'cpdaily_teacher',
    'tenantId': 'sdhyxy',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 14; LE2120 Build/UP1A.230620.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36 cpdaily/9.4.6 wisedu/9.4.6',
    'deviceType': '1',
    'Cache-Control': 'max-age=0',
    'Host': 'sdhyxy.campusphere.net',
    'Connection': 'Keep-Alive',
}

time_now = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
headers['If-Modified-Since'] = time_now

session = requests.Session()


def make_request(url, params=None):
    response = session.get(url, params=params, headers=headers, cookies=cookies)
    response.raise_for_status()
    return response.json()


def get_org_list(org_kind, parent_id=None):
    params = {
        'orgId': parent_id,
        'orgKind': org_kind,
        'pageNum': '1',
        'pageSize': '20',
        'needRefreshOrgInfo': 'true',
        'oick': 'a0e35f2a'
    }
    response = make_request(f'{URL}/user/address-book/teacher/users-and-org', params)
    orgs = response.get('data', {}).get('orgInfo', {}).get('orgs', [])
    logger.info(f"Response State: {response['errMsg']}, Data: {orgs}")
    return orgs


def get_teachers_list(org_id, pageNum=1, pageSize=20, max_depth=10):
    all_results = []
    while pageNum <= max_depth:
        params = {
            'orgId': org_id,
            'orgKind': '6',
            'pageNum': pageNum,
            'pageSize': pageSize,
            'needRefreshOrgInfo': 'true',
            'oick': 'a0e35f2a'
        }
        response = make_request(f'{URL}/user/address-book/teacher/users-and-org', params)

        total_size = response.get('data', {}).get('userInfo', {}).get('totalSize', 0)
        logger.info(f"Page: {pageNum}, Total Size: {total_size}")

        results = response.get('data', {}).get('userInfo', {}).get('result', [])
        all_results.extend(results)

        if pageSize * pageNum >= total_size:
            break

        pageNum += 1

    return all_results


def process_college(college):
    teacher_list = get_teachers_list(college['id'])
    for teacher in teacher_list:
        teacher['orgName'] = teacher.get('orgName', '') or college['name']
        teacher['majorName'] = teacher.get('majorName', '')
        teacher['className'] = teacher.get('className', '')
        logger.info(f"Teacher: {teacher}")

    teacher_list_df = pd.DataFrame(teacher_list)
    teacher_list_df.to_csv('teachers.csv', mode='a', index=False, encoding='utf-8', header=False)


if __name__ == "__main__":
    start_time = time.time()
    colleges = get_org_list('1')

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_college, college): college for college in colleges}

        for future in as_completed(futures):
            college = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing college {college['name']}: {e}")

    end_time = time.time()
    logger.info(f"Time elapsed: {end_time - start_time:.2f} seconds")
