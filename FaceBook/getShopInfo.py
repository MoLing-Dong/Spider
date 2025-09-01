import re
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger

# 定义 cookies 和 headers
cookies = {
    # 'datr': 'YdC7Z137E1CIru_w6mrw_Fon',
    # 'sb': 'YdC7Z_Z7Rv2MQ8bn_N2MFaDG',
    # 'ps_l': '1',
    # 'ps_n': '1',
    # 'wd': '563x962',
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "no-cache",
    "dpr": "1",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"10.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": UserAgent(
        browsers=["Chrome", "Firefox", "Edge"],
        os=["Windows", "Linux"],
        platforms="desktop",
        min_version=120.0,
    ).random,
    "viewport-width": "563",
}


def fetch_web_page(url, headers, *, cookies=None):
    try:
        response = requests.get(url, cookies=cookies, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"请求出错: {e}")
        return None


def extract_text_matches(text, pattern):
    """
    使用正则表达式从文本中提取匹配的内容
    :param text: 要搜索的文本
    :param pattern: 正则表达式模式
    :return: 匹配结果列表
    """
    return re.findall(pattern, text)


def decode_unicode_escapes(match):
    """
    安全地对包含 Unicode 转义序列的字符串进行解码
    :param match: 包含 Unicode 转义序列的字符串
    :return: 解码后的字符串
    """
    try:
        if "\\u" in match:
            # 处理末尾的反斜杠问题
            if match.endswith("\\") and not match.endswith("\\\\"):
                match = match[:-1]  # 移除末尾的单个反斜杠

            # 使用 json.loads 来安全解码 Unicode 转义序列
            # 这比 bytes().decode('unicode-escape') 更安全
            try:
                # 将字符串包装在引号中，然后用 json 解析
                decoded = json.loads(f'"{match}"')
                return decoded
            except json.JSONDecodeError:
                # 如果 json 解析失败，尝试传统方法
                return match.encode("utf-8").decode("unicode-escape")
        return match
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        logger.error(f"解码 {repr(match[:100])}... 时出错: {e}")
        return match


def clean_text(text):
    """
    安全地清洗文本数据，移除 HTML 标签和多余空格
    :param text: 待清洗的文本
    :return: 清洗后的文本
    """
    try:
        # 首先尝试处理可能的编码问题
        if isinstance(text, str):
            # 移除或替换有问题的字符
            # 处理代理对（surrogate pairs）
            text = text.encode("utf-8", errors="ignore").decode("utf-8")

        # 使用 BeautifulSoup 移除 HTML 标签
        soup = BeautifulSoup(text, "html.parser")
        cleaned = soup.get_text()

        # 移除多余的空格和换行符
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
    except Exception as e:
        logger.error(f"清洗文本时出错: {e}")
        # 如果所有方法都失败，返回原始文本的安全版本
        return re.sub(r"\s+", " ", str(text)).strip()


def remove_commas(number_str):
    """
    从数字字符串中移除逗号
    :param number_str: 包含逗号的数字字符串
    :return: 去掉逗号的数字字符串
    """
    return number_str.replace(",", "")


def safe_regex_search(pattern, text):
    """
    安全地进行正则表达式搜索
    :param pattern: 正则表达式模式
    :param text: 要搜索的文本
    :return: 匹配结果或 None
    """
    try:
        return re.search(pattern, text)
    except Exception as e:
        logger.error(f"正则表达式搜索出错: {e}")
        return None


def main(facebook_url):
    response_text = fetch_web_page(facebook_url, headers)
    if not response_text:
        logger.error("无法获取网页内容")
        return
    
    # 保存原始HTML到文件
    try:
        with open('/root/Spider/FaceBook/page_content.html', 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.info("原始页面HTML已保存到 /root/Spider/FaceBook/page_content.html")
    except Exception as e:
        logger.error(f"保存HTML文件失败: {e}")

    pattern = r'"text":"([^"]+)"|"content":([^"]+)|"description":([^"]+)'
    matches = extract_text_matches(response_text, pattern)

    like_pattern = r"(\d{1,3}(?:,\d{3})*)(?:\s*万?)?次赞"
    follower_pattern = r"(\d{1,3}(?:,\d{3})*)(?:\s*万?)?位粉丝"
    following_pattern = r"关注\s*(\d{1,3}(?:,\d{3})*(?:\s*万?)?)\s*人"
    phone_pattern = (
        r"(\+?\d{1,3}[-.\s]?)?(\(\d{1,4}\)|\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})"
    )
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

    shop_info = {
        "likes": set(),
        "followers": set(),
        "following": set(),
        "phones": set(),
        "emails": set(),
        "urls": set(),
        "addresses": set(),
    }

    for match in matches:
        try:
            # 处理多个捕获组，取第一个非空的值
            match_text = match[0] if match[0] else (match[1] if match[1] else match[2])
            if not match_text:
                continue

            # 安全解码 Unicode 转义序列
            decoded_match = decode_unicode_escapes(match_text)

            # 安全清洗文本
            cleaned_match = clean_text(decoded_match)

            if not cleaned_match or len(cleaned_match.strip()) == 0:
                continue

            # 提取点赞数
            like_match = safe_regex_search(like_pattern, cleaned_match)
            if like_match:
                likes = remove_commas(like_match.group(0))
                shop_info["likes"].add(likes)
                continue

            # 提取粉丝数
            follower_match = safe_regex_search(follower_pattern, cleaned_match)
            if follower_match:
                followers = remove_commas(follower_match.group(0))
                shop_info["followers"].add(followers)
                continue

            # 提取关注数
            following_match = safe_regex_search(following_pattern, cleaned_match)
            if following_match:
                following = remove_commas(following_match.group(1))
                shop_info["following"].add(following)
                continue

            # 检查是否为电话号码
            if safe_regex_search(phone_pattern, cleaned_match):
                shop_info["phones"].add(cleaned_match)
                continue

            # 检查是否为电子邮件
            if safe_regex_search(email_pattern, cleaned_match):
                shop_info["emails"].add(cleaned_match)
                continue

            # 检查是否为 URL
            if safe_regex_search(url_pattern, cleaned_match):
                shop_info["urls"].add(cleaned_match)
                continue

            # 如果以上都不是，且字符串有多个单词，则视为地址
            if len(cleaned_match.split()) > 3:
                shop_info["addresses"].add(cleaned_match)

        except Exception as e:
            logger.error(f"处理匹配项时出错: {e}")
            continue

    # 保存解码后的内容到文件
    try:
        with open('/root/Spider/FaceBook/decoded_content.txt', 'w', encoding='utf-8') as f:
            for match in matches:
                match_text = match[0] if match[0] else (match[1] if match[1] else match[2])
                if match_text:
                    decoded_match = decode_unicode_escapes(match_text)
                    cleaned_match = clean_text(decoded_match)
                    if cleaned_match and len(cleaned_match.strip()) > 0:
                        f.write(f"{cleaned_match}\n")
        logger.info("解码后的内容已保存到 /root/Spider/FaceBook/decoded_content.txt")
    except Exception as e:
        logger.error(f"保存解码内容文件失败: {e}")

    # 输出提取的信息
    for key, values in shop_info.items():
        if values:
            for value in values:
                logger.info(f"{key}: {value}")
        else:
            logger.info(f"{key}: 无数据")


if __name__ == "__main__":
    facebook_url = input("请输入facebook网址：")
    if not facebook_url:
        facebook_url = "https://www.facebook.com/plywoodproject"
    main(facebook_url)
