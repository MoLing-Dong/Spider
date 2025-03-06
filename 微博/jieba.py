import psycopg2
from loguru import logger
from psycopg2 import pool

# 定义连接参数
hostname = '192.168.153.132'
database = 'weibo'
username = 'weibo'
password = 'N8BfwJnpChzBeENH'
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

    # 查询表comments，每次取1000条数据
try:
    connection = connection_pool.getconn()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM comments LIMIT 1000')
    comments = cursor.fetchall()
    connection_pool.putconn(connection)
    logger.info("成功查询表comments")
#     遍历查询结果
    for comment in comments:
        logger.info(comment)
except Exception as e:
    logger.error(f"查询表comments失败: {e}")

