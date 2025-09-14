import re
import json
import requests
import sys
import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger
from openai import OpenAI

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入配置
from config import settings

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


def create_openai_client():
    """创建 OpenAI 客户端"""
    try:
        client = OpenAI(
            api_key=settings.zhipu_api_key, base_url=settings.zhipu_base_url
        )
        return client
    except Exception as e:
        logger.error(f"创建 OpenAI 客户端失败: {e}")
        return None


def ai_analyze_shop_data(client, extracted_texts, facebook_url):
    """使用 AI 分析和清理店铺数据"""
    if not client:
        logger.warning("OpenAI 客户端不可用，跳过 AI 分析")
        return None

    # 准备数据给 AI
    data_text = "\n".join(extracted_texts)

    system_prompt = """你是一个专业的数据分析师，专门处理社交媒体店铺信息。
请分析以下Facebook店铺的原始数据，并执行以下任务：

1. 数据清理：
   - 移除重复信息
   - 纠正明显的错误
   - 统一数据格式
   - 提取最有价值的信息

2. 数据标准化：
   - 电话号码标准化
   - 邮箱地址验证
   - URL格式统一
   - 地址信息整理

3. 输出要求：
   - 返回JSON格式
   - 每个字段只保留最准确的一个值
   - 如果某个字段没有有效数据，设为null
   - 粉丝数、关注数等数字要提取纯数字

严格按照以下字段名返回JSON，不要添加或修改字段名：
{
    "name": "店铺名称或null",
    "followers": "粉丝数（纯数字）或null",
    "following": "关注数（纯数字）或null", 
    "likes": "点赞数（纯数字）或null",
    "phone": "标准化电话号码或null",
    "email": "邮箱地址或null",
    "website": "网站URL或null",
    "address": "地址信息或null",
    "description": "店铺描述或null"
}

只返回JSON，不要其他解释文字。"""

    user_content = f"请分析以下Facebook店铺数据：\n\nFacebook URL: {facebook_url}\n\n提取的文本内容：\n{data_text}"

    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
            top_p=0.7,
            stream=False,
        )

        ai_result = response.choices[0].message.content.strip()
        logger.info("AI 分析完成")

        # 清理可能的 markdown 代码块标记
        ai_result = re.sub(r"```json\s*", "", ai_result)
        ai_result = re.sub(r"```\s*$", "", ai_result)

        # 检查name字段是否为空，如果为空则用URL补充
        try:
            result_json = json.loads(ai_result)
            if not result_json.get("name") or result_json.get("name") == "null":
                # 从URL中提取可能的店铺名称
                url_name = (
                    facebook_url.split("/")[-1] if "/" in facebook_url else facebook_url
                )
                result_json["name"] = url_name
                ai_result = json.dumps(
                    result_json, ensure_ascii=False, separators=(",", ":")
                )
        except json.JSONDecodeError:
            logger.warning("无法解析AI返回的JSON，将直接使用原始结果")

        # 直接返回AI生成的JSON字符串
        return ai_result

    except Exception as e:
        logger.error(f"AI 分析失败: {e}")
        return None


def main(facebook_url):
    response_text = fetch_web_page(facebook_url, headers)
    if not response_text:
        logger.error("无法获取网页内容")
        return

    # 保存原始HTML到文件
    try:
        with open(
            "/root/Spider/FaceBook/page_content.html", "w", encoding="utf-8"
        ) as f:
            f.write(response_text)
        logger.info("原始页面HTML已保存到 /root/Spider/FaceBook/page_content.html")
    except Exception as e:
        logger.error(f"保存HTML文件失败: {e}")

    # 简单提取页面文本内容给AI分析
    pattern = r'"text":"([^"]+)"|"content":([^"]+)|"description":([^"]+)'
    matches = extract_text_matches(response_text, pattern)

    # 收集所有文本数据
    extracted_texts = []
    for match in matches:
        match_text = match[0] if match[0] else (match[1] if match[1] else match[2])
        if match_text:
            decoded_match = decode_unicode_escapes(match_text)
            cleaned_match = clean_text(decoded_match)
            if cleaned_match and len(cleaned_match.strip()) > 0:
                extracted_texts.append(cleaned_match)

    # 保存解码后的内容到文件
    try:
        with open(
            "/root/Spider/FaceBook/decoded_content.txt", "w", encoding="utf-8"
        ) as f:
            for text in extracted_texts:
                f.write(f"{text}\n")
        logger.info("解码后的内容已保存到 /root/Spider/FaceBook/decoded_content.txt")
    except Exception as e:
        logger.error(f"保存解码内容文件失败: {e}")

    # 使用 AI 分析和清理数据
    logger.info("开始 AI 数据分析...")
    ai_client = create_openai_client()

    if ai_client:
        final_result = ai_analyze_shop_data(ai_client, extracted_texts, facebook_url)
        if final_result:
            # 直接打印AI生成的JSON
            print(final_result)

            # 保存结果到文件
            output_file = "/root/Spider/FaceBook/shop_analysis_result.json"
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(final_result)
                logger.info(f"分析结果已保存到 {output_file}")
            except Exception as e:
                logger.error(f"保存分析结果失败: {e}")
        else:
            logger.error("AI 分析失败，无法获取结果")
    else:
        logger.error("AI 客户端不可用，无法进行分析")

    return final_result if ai_client and final_result else None


if __name__ == "__main__":
    facebook_url = input("请输入facebook网址：")
    if not facebook_url:
        facebook_url = "https://www.facebook.com/plywoodproject"
    main(facebook_url)
