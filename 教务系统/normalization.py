import json

with open('xjyj_cxXjyjjdlb.json', encoding='utf-8') as f:
    text = f.read()
    cj_list = json.loads(text)
try:
    for cj in cj_list:
        # 遍历cj.kcList数组
        kc_list = cj.get('kcList')
        if kc_list is not None:
            for kc in kc_list:
                # if kc.get('cj') is not None:
                if kc.get('cj') == '未开放':
                    print(kc.get('kcmc') + ":" + kc.get('bfzcj'))
        # do something
        else:
            # print("字典 cj 中没有 'kcList' 键")
            pass
except Exception as e:
    print(e)
