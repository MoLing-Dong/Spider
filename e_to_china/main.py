
import json

import requests
from loguru import logger

# 配置日志
logger.add("fetch.log", rotation="10MB", level="INFO")

# 配置会话和参数
session = requests.Session()
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://hs.e-to-china.com.cn/showtree-0.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
cookies = {
    "PHPSESSID": "pgo3b7vjrumqg457q9teopl746",
    "_ga": "GA1.1.1050576667.1740102307",
    "_ga_C9B0DJP305": "GS1.1.1740102307.1.1.1740102318.49.0.0",
}
session.headers.update(headers)
session.cookies.update(cookies)


def fetch_children(node, depth=0, max_retries=3):
    """
    递归获取子分类
    :param node: 当前节点
    :param depth: 递归深度
    :param max_retries: 最大重试次数
    """
    logger.info(f"正在获取----------- {node['text']} 的子分类")
    if node.get("children"):
        for child in node["children"]:
            logger.info(f"正在获取++++++++++ {child} 的子分类")
            if child.get("hasChildren") == True:
                # 发送请求
                retries = 0
                while retries < max_retries:
                    try:
                        response = session.get(
                            f"https://hs.e-to-china.com.cn/classify/ajax/ajax.php?root={child['id']}",
                            timeout=10,
                        )
                        response.raise_for_status()
                        # logger.debug(f"请求成功 ===========: {response.json()}")
                        child["children"] = response.json()
                        for child in child["children"]:
                            # logger.info(
                            #     f"正在获取++++++++++ {child['md5']},{child['text']} 的子分类"
                            # )
                            # 发送请求
                            retries = 0
                            try:
                                response = session.get(
                                    f"https://hs.e-to-china.com.cn/classify/ajax/ajax.php?root={child['md5']}",
                                    timeout=10,
                                )
                                response.raise_for_status()
                                # logger.debug(f"请求成功 ===========: {response.json()}")
                                child["children"] = response.json()
                            except requests.exceptions.RequestException as e:
                                logger.error(f"请求失败: {e}")
                                # time.sleep(1)
                        # logger.info(f"成功获取 {child['text']} 的子分类")
                        break
                    except requests.exceptions.RequestException as e:
                        retries += 1
                        logger.error(f"请求失败: {e}")
                        # time.sleep(1)


# 获取顶层分类
top_level = []
try:
    response = session.get(
        "https://hs.e-to-china.com.cn/classify/ajax/ajax.php?hscode=0&root=source",
        timeout=10,
    )
    response.raise_for_status()
    top_level = response.json()

    logger.info(f"成功获取顶层分类，共 {len(top_level)} 个节点")

    for node in top_level:
        fetch_children(node)


except requests.exceptions.RequestException as e:
    logger.error(f"初始请求失败: {e}")

# 保存结果
with open("./hierarchy.json", "w", encoding="utf-8") as f:
    json.dump(top_level, f, ensure_ascii=False, indent=2)

logger.info("数据已保存至 hierarchy.json")
