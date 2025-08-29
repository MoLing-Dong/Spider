# -*- coding: utf-8 -*-

import execjs
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Cookie": "sessionid=1vdyp4zc7qjalltx5m5iqykwfesfeof4; qpfccr=true; no-alert3=true; Hm_lvt_c99546cf032aaa5a679230de9a95c7db=1718591069; Hm_lpvt_c99546cf032aaa5a679230de9a95c7db=1718591241",
}

params = {
    "page": "",
    "m": ""
}

url = "https://match.yuanrenxue.cn/api/match/1"
js_compile = execjs.compile(open("md5.js", encoding="UTF-8").read())

s = 0  # 每一页的机票价格之和
times = 0  # 一共有多少次班机

with requests.Session() as session:
    session.headers.update(headers)
    for i in range(1, 6):
        try:
            m = js_compile.call("run")
            params['page'] = i
            params['m'] = m
            response = session.get(url, params=params)
            response.raise_for_status()  # 检查请求是否成功
            json_data = response.json()
            s += sum(item.get("value", 0) for item in json_data.get("data", []))
            times += len(json_data.get("data", []))
        except requests.RequestException as e:
            print(f"请求失败：{e}")
        except ValueError as e:
            print(f"解析JSON失败：{e}")

if times > 0:
    result = s // times  # 最终的结果，平均价格
    print(result)  # 最终结果为4700
else:
    print("未获取到有效数据")
