import requests

cookies = {
    'JSESSIONID': 'CFBBE38B7A17C59111C03C98072D56B7',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254010b) XWEB/11607',
    'Content-Type': 'application/x-www-form-urlencoded',
    'n': 'content,deviceName,keyWord,blogBody,blogTitle,getType,responsibilities,street,text,reason,searchvalue,key,answers,leaveReason,personRemark,selfAppraisal,imgUrl,wxname,deviceId,avatarTempPath,file,file,model,brand,system,deviceId,platform,code,openId,unionid,clockDeviceToken,clockDevice,address',
    'encryptValue': '9523c3187a9d3f891e2dac1953cafb30386c1f370f3c7bfd75152edcd34023a29d97622092c2ff8a8732a8939172b8799f2426c0c132145e76dfbee991683a0a4439898055a83966a73ddf091429366a9827ecbd1ae5ca4ec6b449fee09a62a19dfc65889188decb82d169aafd71064a1b395d38ffc645cca0beb0563c6876493c2caeaf664a4170faf809c0dfb3c50dccb60cd891840f8e7de3956e2e039d63f930baf824ede0a8b040aaf0c06386ddeee7957a52b71905c55bebb1e9cdc68bea9b1cb4c76cb8110d07dabb613d4ea48cebf73794e61554a36855c16a475854',
    'm': '4a26c0c1011161217864846ac993effc',
    'v': '1.6.36',
    'xweb_xhr': '1',
    't': '1737557098',
    's': '1_27_58_8_21_33_14_60_41_46_25_12_36_0_57_22_18_6_11_28',
    'wechat': '1',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://servicewechat.com/wx9f1c2e0bbc10673c/472/page-frame.html',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'Cookie': 'JSESSIONID=CFBBE38B7A17C59111C03C98072D56B7',
}

data = {
    'professionId': '342',
}

response = requests.post('https://xcx.xybsyw.com/find/LoadRecommendAnswerList.action', cookies=cookies, headers=headers, data=data)
print(response.text)
