import base64
import json
import time

import requests


def btoa(srcstr):
    return base64.b64encode(srcstr.encode()).decode()


cookies = {
    'Hm_lvt_c99546cf032aaa5a679230de9a95c7db': '1718590817',
    'sessionid': 'di4xdxjp00fnag4402frn10cvgfir5pa',
    'qpfccr': 'true',
    'no-alert3': 'true',
}

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://match.yuanrenxue.cn/match/12',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'x-requested-with': 'XMLHttpRequest',

}
sum = 0
api_url = "http://match.yuanrenxue.com/api/match/12"

for i in range(1, 6):
    srcstr = f"yuanrenxue{i}"
    params = {
        "page": i,
        "m": btoa(srcstr),
    }

    try:
        response = requests.get(api_url, cookies=cookies, params=params, headers=headers)
        # response.raise_for_status()  # 检查HTTP请求是否成功

        # 使用 json 库解析响应内容
        data = json.loads(response.text)

        for value in data.get("data", []):
            print(value)
            sum += value.get("value", 0)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except json.JSONDecodeError:
        print(f"解析JSON失败，响应内容: {response.text}")
    except Exception as e:
        print(f"其他错误: {e}")

    time.sleep(1)  # 延迟10秒

print(sum)
