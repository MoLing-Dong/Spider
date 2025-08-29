import csv
import json


# 定义一个递归函数来遍历 JSON 数据到最底层
def traverse_json(data, result):
    if isinstance(data, list):
        for item in data:
            traverse_json(item, result)
    elif isinstance(data, dict):
        if 'children' not in data:
            result.append(data)
        else:
            traverse_json(data['children'], result)
    return result


# 读取同级目录下的 hierarchy.json 文件
try:
    with open('hierarchy.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)
except FileNotFoundError:
    print("未找到 hierarchy.json 文件，请确保该文件存在于当前目录下。")
except json.JSONDecodeError:
    print("无法解析 hierarchy.json 文件中的 JSON 数据，请检查文件格式。")
else:
    # 存储最底层的 JSON 对象
    bottom_level_items = []
    # 调用递归函数遍历 JSON 数据
    traverse_json(json_data, bottom_level_items)

    # 筛选出需要的字段
    selected_fields = ["text", "shortid", "id"]
    csv_filename = 'output.csv'

    # 写入 CSV 文件
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=selected_fields)
        writer.writeheader()  # 写入表头
        for item in bottom_level_items:
            writer.writerow({field: item.get(field, '') for field in selected_fields})

    print(f"CSV 文件已成功保存为 {csv_filename}")
