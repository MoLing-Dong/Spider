import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import settings

# 初始化日志记录
logger.add("list.log", rotation="10 MB", retention="10 days", level="INFO")

# 设置会话和重试策略
session = requests.Session()
retry_strategy = Retry(
    total=3,  # 最大重试次数
    status_forcelist=[429, 500, 502, 503, 504],  # 针对这些状态码进行重试
    allowed_methods={"HEAD", "GET", "OPTIONS", "POST"},  # 针对的请求方法，使用集合
    backoff_factor=1  # 每次重试的等待时间递增
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 请求头和数据
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': 'JSESSIONID=7340D057F22502EDB515AC5E35099224',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}
data = {
    'userName': settings.HUAYU_JAVA_ACCOUNT,
    'password': settings.HUAYU_JAVA_PASSWORD,
}

# 尝试发送请求并捕获可能的异常
try:
    #
    response = session.get('http://10.60.80.244:8081/home/index', headers=headers, verify=False)  # 获取更新后的 cookie
    updated_cookies = session.cookies.get_dict()
    # 更新cookie = response
    headers['Cookie'] = 'JSESSIONID=' + updated_cookies['JSESSIONID']
    # headers['Cookie'] = 'JSESSIONID=19C18B5762B58540E8ED3170C2039CAD'
    session.headers.update(headers)
    # 检查headers
    logger.info(f"headers: {headers}")
    # 登录请求
    response = session.post('http://10.60.80.244:8081/login/checkLogin', headers=headers, data=data, verify=False,
                            timeout=10)
    response.raise_for_status()  # 检查响应状态码是否正常
    logger.info(f"登录响应: {response.json()}")

    # 获取签到信息
    response = session.get('http://10.60.80.244:8081/student/sign/info', headers=headers, verify=False, timeout=10)
    response.raise_for_status()
    logger.info(f"签到信息: {response.json()}")

    # 连续签到操作
    for i in range(2000):
        response = session.post('http://10.60.80.244:8081/student/sign/add', headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        logger.info(f"签到第 {i + 1} 次响应: {response.json()}")

except requests.exceptions.RequestException as e:
    # 捕获所有请求相关的异常
    logger.error(f"请求发生错误: {e}")
except Exception as e:
    # 捕获其他异常
    logger.error(f"其他错误: {e}")
