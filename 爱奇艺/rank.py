import sys

import requests

# 设置标准输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
cookies = {
    '__uuid': '7edd5767-b3f1-4b85-0c24-66c3868171fc',
    '__oaa_session_id__': '0b8710a243704f53d072bb25d461a0f6',
    'QC005': 'd6afbc8038dcfad9ddff32b2d6d0fec9',
    'QC008': '1738512525.1738512525.1738512525.1',
    'QC007': 'DIRECT',
    'QC175': '%7B%22upd%22%3Atrue%2C%22ct%22%3A%22%22%7D',
    'QC189': '8883_A%2C10274_B%2C8739_B%2C9419_B%2C9379_B%2C9922_B%2C10276_B%2C8004_B%2C5257_B%2C9776_A%2C8873_E%2C10123_B%2C7423_C%2C8401_A%2C6249_C%2C7996_B%2C9576_B%2C10358_A%2C9365_B%2C5465_B%2C6843_B%2C10096_B%2C6578_B%2C6312_B%2C6091_B%2C8690_A%2C8737_D%2C8742_A%2C9484_B%2C10193_B%2C6752_C%2C10426_B%2C10188_B%2C8971_B%2C7332_B%2C9683_B%2C8665_E%2C6237_B%2C9569_A%2C8983_C%2C7024_C%2C5592_B%2C9117_A%2C6031_B%2C7581_B%2C9506_A%2C9517_A%2C10216_D%2C9394_B%2C8542_B%2C6050_B%2C9167_D%2C9469_B%2C8812_B%2C6832_C%2C7074_C%2C7682_C%2C8867_B%2C5924_D%2C6151_C%2C5468_B%2C10447_B%2C6704_C%2C8808_B%2C8497_B%2C8342_B%2C8871_C%2C9790_C%2C9355_B%2C10389_A%2C8760_B%2C9292_B%2C6629_B%2C5670_B%2C9158_A%2C9805_B%2C9959_A%2C6082_B%2C5335_B',
    '__oaa_session_referer_app__': 'ranks1-cid-id',
    'QC191': '',
    'QC006': '6j4fdqdlcrtesncznkchhuyd',
    'QC186': 'false',
    'TQC030': '1',
    'nu': '0',
    'QC235': 'b1f954080f5f493abf21656e16d08cf4',
    'QC234': '55e03452deb818c6bde18d70dfe6d853',
    'T00404': 'f1e689eb30f924eb99304ec43150ddf2',
    'IMS': 'IggQABj_z4O9BiomCiA3NmYyYmIwZWNkYjk0MDE0YTJhNzMxODUyNmE2ZDM2MRAAIgByJAogNzZmMmJiMGVjZGI5NDAxNGEyYTczMTg1MjZhNmQzNjEQAIIBBCICEAGKASQKIgogNzZmMmJiMGVjZGI5NDAxNGEyYTczMTg1MjZhNmQzNjE',
    '__dfp': 'a05234b3ac93084561898c12ce616e7cd42c3db6c648a7da8865a89d78ef2710a7@1739808528233@1738512529233',
    'curDeviceState': 'width%3D2048%3BconduitId%3D%3Bscale%3D125%3Bbrightness%3Ddark%3BisLowPerformPC%3D0%3Bos%3Dbrowser%3Bosv%3D10.0.19044',
    'QP0037': '0',
    'QP007': '480',
    'QC173': '0',
    'QC187': 'true',
    'QC010': '195528699',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    # 'cookie': '__uuid=7edd5767-b3f1-4b85-0c24-66c3868171fc; __oaa_session_id__=0b8710a243704f53d072bb25d461a0f6; QC005=d6afbc8038dcfad9ddff32b2d6d0fec9; QC008=1738512525.1738512525.1738512525.1; QC007=DIRECT; QC175=%7B%22upd%22%3Atrue%2C%22ct%22%3A%22%22%7D; QC189=8883_A%2C10274_B%2C8739_B%2C9419_B%2C9379_B%2C9922_B%2C10276_B%2C8004_B%2C5257_B%2C9776_A%2C8873_E%2C10123_B%2C7423_C%2C8401_A%2C6249_C%2C7996_B%2C9576_B%2C10358_A%2C9365_B%2C5465_B%2C6843_B%2C10096_B%2C6578_B%2C6312_B%2C6091_B%2C8690_A%2C8737_D%2C8742_A%2C9484_B%2C10193_B%2C6752_C%2C10426_B%2C10188_B%2C8971_B%2C7332_B%2C9683_B%2C8665_E%2C6237_B%2C9569_A%2C8983_C%2C7024_C%2C5592_B%2C9117_A%2C6031_B%2C7581_B%2C9506_A%2C9517_A%2C10216_D%2C9394_B%2C8542_B%2C6050_B%2C9167_D%2C9469_B%2C8812_B%2C6832_C%2C7074_C%2C7682_C%2C8867_B%2C5924_D%2C6151_C%2C5468_B%2C10447_B%2C6704_C%2C8808_B%2C8497_B%2C8342_B%2C8871_C%2C9790_C%2C9355_B%2C10389_A%2C8760_B%2C9292_B%2C6629_B%2C5670_B%2C9158_A%2C9805_B%2C9959_A%2C6082_B%2C5335_B; __oaa_session_referer_app__=ranks1-cid-id; QC191=; QC006=6j4fdqdlcrtesncznkchhuyd; QC186=false; TQC030=1; nu=0; QC235=b1f954080f5f493abf21656e16d08cf4; QC234=55e03452deb818c6bde18d70dfe6d853; T00404=f1e689eb30f924eb99304ec43150ddf2; IMS=IggQABj_z4O9BiomCiA3NmYyYmIwZWNkYjk0MDE0YTJhNzMxODUyNmE2ZDM2MRAAIgByJAogNzZmMmJiMGVjZGI5NDAxNGEyYTczMTg1MjZhNmQzNjEQAIIBBCICEAGKASQKIgogNzZmMmJiMGVjZGI5NDAxNGEyYTczMTg1MjZhNmQzNjE; __dfp=a05234b3ac93084561898c12ce616e7cd42c3db6c648a7da8865a89d78ef2710a7@1739808528233@1738512529233; curDeviceState=width%3D2048%3BconduitId%3D%3Bscale%3D125%3Bbrightness%3Ddark%3BisLowPerformPC%3D0%3Bos%3Dbrowser%3Bosv%3D10.0.19044; QP0037=0; QP007=480; QC173=0; QC187=true; QC010=195528699',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

response = requests.get('https://www.iqiyi.com/ranks1/1/-4', cookies=cookies, headers=headers)
print(response.text)
# 写入文件
with open('iqiyi.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
