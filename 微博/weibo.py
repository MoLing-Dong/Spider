import asyncio
from typing import Any, Tuple

import aiohttp
import async_timeout
import psycopg2
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from loguru import logger
from psycopg2 import pool

# 定义连接参数
hostname = '47.101.144.135'
database = 'weibo_comments'
username = 'weibo_comments'
password = 'WQNjX677dZQsKJtw'
port = 5432  # 默认的 PostgreSQL 端口号

# 使用链接池
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        host=hostname,
        database=database,
        user=username,
        password=password,
        port=port
    )
    logger.info("成功创建连接池")
except Exception as e:
    logger.error(f"创建连接池失败: {e}")
    exit(1)

# 检测是否存在数据库表comments
try:
    connection = connection_pool.getconn()
    cursor = connection.cursor()
    cursor.execute("SELECT to_regclass('comments')")
    if cursor.fetchone()[0] is None:
        cursor.execute('''
        CREATE TABLE comments (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            "COMMENT" TEXT,
            comment_time TIMESTAMP,
            comment_id VARCHAR(255),
            article_id VARCHAR(255)
        )
        ''')
        connection.commit()
        logger.info("成功创建表comments")
    else:
        logger.info("表comments已存在")
    connection_pool.putconn(connection)
except Exception as e:
    logger.error(f"创建表comments失败: {e}")
    exit(1)

# 添加日志记录器
logger.add("list.log", rotation="3 MB", retention="10 days", level="INFO", encoding="utf-8")

cookies = {
    'SINAGLOBAL': '2598867652217.838.1708872522069',
    'SCF': 'Ai_JzoS98QhWTTXbGkbhUyUXgAmQOl5qcc_unevN0zXS5Ne8iFw-QTqHrdd0p69dWPQKchzNU4OXK8N7l99ZjcU.',
    'ALF': '1728972693',
    'SUB': '_2A25L4grFDeRhGeNI7VYY8i_NzDSIHXVongINrDV8PUJbkNANLVfFkW1NSFA0rxS5xFZb8AjDjYSSskTkgsRkfsjg',
    'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WFv6MxTuB4ugLbqATEJ2Zm.5JpX5KMhUgL.Fo-cSoB4eo2pS0n2dJLoI0YLxK-LBK-L12zLxK-L12qL1K2LxK-L1-zLB.-LxK-LB.eLB.2LxKqL1KqLBo5LxK.L1-BL1KzLxK-LBo.LBoBt',
    '_s_tentry': '-',
    'Apache': '1196671132558.9263.1726568408875',
    'ULV': '1726568408880:17:3:2:1196671132558.9263.1726568408875:1726380694725',
    'UOR': 'www.baidu.com,weibo.com,www.baidu.com',
}

headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://s.weibo.com/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(num, alphabet=ALPHABET):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def base62_decode(string, alphabet=ALPHABET):
    base = len(alphabet)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num


def mid_to_url(midint):
    midint = str(midint)[::-1]
    size = len(midint) // 7 if len(midint) % 7 == 0 else len(midint) // 7 + 1
    result = []
    for i in range(size):
        s = midint[i * 7: (i + 1) * 7][::-1]
        s = base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)


def url_to_mid(url):
    url = str(url)[::-1]
    size = len(url) // 4 if len(url) % 4 == 0 else len(url) // 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))


def extract_article_info(article):
    parts = article.split("/")
    try:
        uid = int(parts[3])
        url_id = parts[4].split("?")[0]
        return uid, url_to_mid(url_id)
    except (IndexError, ValueError) as e:
        logger.error(f"Error processing article: {article}. Error: {e}")
        return None, None


async def fetch(session: ClientSession, url: str, params: dict = None, timeout: int = 10) -> str:
    with async_timeout.timeout(timeout):
        async with session.get(url, params=params) as response:
            return await response.text()


async def get_top_hot(session: ClientSession) -> list[dict[str, str | int | Any]]:
    data_list = []
    params = {'cate': "realtimehot"}
    try:
        response = await fetch(session, 'https://s.weibo.com/top/summary', params=params)
        soup = BeautifulSoup(response, 'html.parser')
        data = soup.find('div', id='pl_top_realtimehot').find_all('tbody')[0].find_all('tr')
    except Exception as e:
        logger.error(f"解析失败: {e}")
        return data_list

    for index, tr in enumerate(data):
        try:
            href = tr.find('a', href=True)
            if not href:
                continue
            title = href.text
            link = f'https://s.weibo.com{href["href"]}'
            if 'javascript:void(0)' in link or index == 0:
                continue
            hot = tr.find('span').text
            data_list.append({'title': title, 'link': link, 'hot': hot})
        except Exception as e:
            logger.error(f"处理第{index + 1}条数据时出错: {e}")
            continue
    return data_list


async def get_articles(session: ClientSession, t: str, band_rank: int, query: str = '微博') -> Tuple[list[str], str]:
    page = 1
    max_page = 100
    articles = []
    params = {
        'q': query,
        'typeall': '1',
        'suball': '1',
        'timescope': t,
        'Refer': 'g',
        'page': str(page),
    }
    try:
        while page <= max_page:
            response = await fetch(session, 'https://s.weibo.com/weibo', params=params)
            soup = BeautifulSoup(response, 'html.parser')
            card_wraps = soup.find_all(attrs={'action-type': 'feed_list_item'})  # 获取当前页面的文章的信息
            ul_element = soup.find('ul', class_='s-scroll')
            if ul_element:
                li_count = len(ul_element.find_all('li'))
                max_page = li_count
            else:
                li_count = 0
            if not card_wraps:
                break

            for card in card_wraps:
                # logger.info(card)
                # 开始对每个文章处理
                feed_from = card.find(attrs={'class': 'from'})
                if feed_from:
                    hrefs = feed_from.find_all('a')
                    for href in hrefs:
                        # logger.info(href['href'])
                        articles.append('https://' + href['href'])
                        break
                        # exit(1)
                #         # if 'uid' in href['href']:
                #         #     articles.append(href['href'])
                #         #     break
                #         articles.append(href['href'])

            page += 1
            params['page'] = str(page)
            await asyncio.sleep(2)

        logger.info(f"排名{band_rank}的'{query}'，获取文章数量：{len(articles)}")
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        return [], query
    return articles, query


async def get_comments(session: ClientSession, article_id: str, query: str) -> list[dict[str, str]]:
    comments_list = []
    page = 1
    max_page = 100
    params = {
        'mid': article_id,
        'max_id_type': '0',
        'page': str(page),
    }
    try:
        while page <= max_page:
            response = await fetch(session, 'https://weibo.com/aj/v6/comment/big', params=params)
            data = response.json()
            if data.get('code') != '100000':
                break

            for comment in data['data']['comment_list']:
                comments_list.append({
                    'user_id': comment['user']['id'],
                    'comment': comment['text'],
                    'comment_time': comment['created_at'],
                    'comment_id': comment['id'],
                    'article_id': article_id,
                })

            page += 1
            params['page'] = str(page)

            await asyncio.sleep(2)  # 加入间隔，避免过于频繁的请求

        logger.info(f"'{query}'，获取评论数量：{len(comments_list)}")
    except Exception as e:
        logger.error(f"获取评论列表失败: {e}")
        return []
    return comments_list


async def save_to_db(connection_pool, comments: list[dict[str, str]]) -> None:
    try:
        connection = connection_pool.getconn()
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO comments (user_id, "COMMENT", comment_time, comment_id, article_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (comment_id) DO NOTHING
        """
        for comment in comments:
            cursor.execute(insert_query, (
                comment['user_id'], comment['comment'],
                comment['comment_time'], comment['comment_id'],
                comment['article_id']
            ))
        connection.commit()
        logger.info(f"保存评论成功，数量：{len(comments)}")
    except Exception as e:
        logger.error(f"保存评论失败: {e}")
    finally:
        connection_pool.putconn(connection)


async def main():
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        top_hot = await get_top_hot(session)
        tasks = []

        for index, band in enumerate(top_hot):
            t = "custom:2024-09-17-0:2024-09-17-24"
            # band_rank = band['title']  数组第几个
            band_rank = index + 1
            query = band['title']
            tasks.append(get_articles(session, t, band_rank, query))

        all_articles = await asyncio.gather(*tasks)

        comment_tasks = []
        for articles, query in all_articles:
            for article in articles:
                uid, mid = extract_article_info(article)
                if uid and mid:
                    comment_tasks.append(get_comments(session, str(mid), query))

        all_comments = await asyncio.gather(*comment_tasks)

        db_tasks = []
        for comments in all_comments:
            db_tasks.append(save_to_db(connection_pool, comments))

        await asyncio.gather(*db_tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
    finally:
        if connection_pool:
            connection_pool.closeall()
