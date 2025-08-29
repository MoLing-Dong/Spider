# -*- coding: utf-8 -*-

import json

# 打开cities.json文件
with open('cities.json', 'r', encoding='utf-8') as f:
    cities = json.load(f)
    print(cities)  # 输出cities的内容
