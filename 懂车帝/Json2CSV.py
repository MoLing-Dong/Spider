# -*- coding: utf-8 -*-

# 设置字段名
import csv
import json

field_names = ["month", 'series_name', 'min_price', 'max_price', 'count', 'car_review_count', 'brand_name', 'price', 'sub_brand_name']

# 读取json文件
with open('car_data.json', 'r', encoding='utf-8') as f:
    car_data = json.load(f)
# 创建csv文件
with open('car_data.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()

    for month, data in car_data.items():
        for car in data:
            writer.writerow({
                "month": month,
                'series_name': car['series_name'],
                'min_price': car['min_price'],
                'max_price': car['max_price'],
                'count': car['count'],
                'car_review_count': car['car_review_count'],
                'brand_name': car['brand_name'],
                'price': car['price'],
                'sub_brand_name': car['sub_brand_name']
            })
