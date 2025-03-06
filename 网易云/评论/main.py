import os
import time

import execjs
import pandas as pd
import requests
from loguru import logger

#  获取当前文件夹路径
THIS_DIR = os.path.dirname(os.path.abspath(__file__)) + "\\"
TIME_STAMP = int(time.time())
SONG_ID = 31445474
# 时间戳

# 评论参数
word_dict = {
    "rid": "R_SO_4_" + str(SONG_ID),
    "threadId": "R_SO_4_" + str(SONG_ID),
    "pageNo": '1',
    "pageSize": "20",
    "cursor": TIME_STAMP * 1000,
    "offset": '0',
    "orderType": "1",
    "csrf_token": "02da822a32c320f04db0118a3a5606e6"
}


def getData():
    with open("../reverse.js", "r", encoding="utf-8") as f:
        js = f.read()
    js_complied = execjs.compile(js)
    result = js_complied.call("getData", word_dict)
    return {"params": result["encText"], "encSecKey": result["encSecKey"]}


headers = {
    "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}


def main():
    try:
        r = requests.post(
            "https://music.163.com/weapi/comment/resource/comments/get?csrf_token=",
            headers=headers,
            data=getData())
        if r.status_code == 200 & r.json()['code'] == 200:
            data = r.json()['data']
            return data
    except Exception as e:
        print('Error: ', e)


def getComments(count):
    """
    获取指定数量的音乐评论并将其保存到CSV文件中。

    参数:
    count - 要获取的评论数量

    返回值:
    无
    """
    for i in range(1, count):
        # 更新请求参数中的页码和偏移量
        word_dict['pageNo'] = i
        word_dict['offset'] = (i - 1) * 20
        # 设置当前时间戳作为cursor
        word_dict['cursor'] = int(time.time()) * 1000
        # 准备请求数据
        form_data_2 = getData()
        # 发送评论获取请求
        r = requests.post(
            "https://music.163.com/weapi/comment/resource/comments/get?csrf_token=",
            headers=headers,
            data=form_data_2)
        # 请求成功且获取到评论
        if r.status_code == 200 & r.json()['code'] == 200:
            data = r.json()['data']
            # 提取评论内容
            comments = data['comments']
            for comment in comments:
                print(comment['content'])
                # 将评论内容保存到CSV文件中
                df = pd.DataFrame([comment['content']])
                df.to_csv(THIS_DIR + "comments.csv",
                          mode='a',
                          header=False,
                          index=False,
                          encoding="utf_8")

        else:
            # 请求失败处理
            print("获取评论失败", r.status_code, r.text)
            break


""" 热评 """

if __name__ == "__main__":
    data = main()
    time.sleep(1)
    # getComments(data['totalCount'])
    for hotComment in data['hotComments']:
        # # pd写入csv文件
        # df = pd.DataFrame(
        #     [hotComment['content'], [','], hotComment['user']['nickname']])
        # df.to_csv(THIS_DIR + "hotComments.csv", mode='a', encoding="utf_8")

        logger.info(hotComment)
