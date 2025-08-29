import execjs
import requests

SONG_ID = 494865824

data = {
    "id": SONG_ID,
    "lv": -1,
    "tv": -1,
    "csrf_token": "",
}


def getData():
    with open("../reverse.js", "r", encoding="utf-8") as f:
        js = f.read()
    js_complied = execjs.compile(js)
    result = js_complied.call("getData", data)
    return {"params": result["encText"], "encSecKey": result["encSecKey"]}


headers = {
    "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}
form_data = ()

r = requests.post("https://music.163.com/weapi/song/lyric?csrf_token=",
                  headers=headers,
                  data=form_data)
print(r.text)
