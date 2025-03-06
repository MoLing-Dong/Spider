import json
from datetime import datetime, timedelta
from operator import itemgetter
from typing import Dict, List, Any

import execjs
import requests
from loguru import logger

# 配置信息
HEADERS = {
    'accept': 'application/json, text/javascript',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://music.163.com',
    'pragma': 'no-cache',
    'referer': 'https://music.163.com/musician/artist/home',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

PARAMS = {'csrf_token': '005b52c72ebb34e46b28221f28c55064'}


def compile_js(js_path: str) -> Any:
    """编译 JavaScript 文件并返回可调用对象"""
    try:
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        return execjs.compile(js_content)
    except Exception as e:
        logger.error(f"加载 JavaScript 文件失败: {e}")
        raise


def get_data(js_compiled: Any, params: Dict[str, str]) -> Dict[str, str]:
    """通过 JavaScript 加密生成参数"""
    try:
        result = js_compiled.call("getData", params)
        return {"params": result["encText"], "encSecKey": result["encSecKey"]}
    except Exception as e:
        logger.error(f"执行 JavaScript 加密失败: {e}")
        raise


def create_session(cookies: Dict[str, str]) -> requests.Session:
    """为每个用户创建独立的 Session 并设置 Cookies"""
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.cookies.update(cookies)
        return session
    except Exception as e:
        logger.error(f"创建 Session 失败: {e}")
        raise


def post_request(session: requests.Session, url: str, data: Dict[str, str] = None,
                 params: Dict[str, str] = None) -> str:
    """发送 POST 请求并打印响应结果"""
    try:
        response = session.post(url, params=params, data=data)
        response.raise_for_status()
        logger.debug(response.text)
        return response.text
    except requests.RequestException as e:
        logger.error(f"请求 {url} 失败: {e}")
        raise


def fetch_data(session: requests.Session, page_num, page_size, artist_id, dt, order_field, order_direction):
    """获取实时歌曲数据"""
    json_data = {
        'page_num': page_num,
        'artist_id': artist_id,
        'dt': dt,
        'page_size': page_size,
        'order_field': order_field,
        'order_direction': order_direction,
        'use_total_num': 1,
    }
    try:
        session.headers.update({
            "content-type": "application/json"
        })
        response = session.post(
            'https://interface.music.163.com/api/push-song-advisor/open/api/data-service/advisor/real_time_song_list',
            json=json_data,
        )
        response.raise_for_status()
        data = response.json()
        logger.debug(f"获取数据成功: {data}")
        return data
    except requests.RequestException as e:
        logger.error(f"请求失败: {e}")
        raise


def main(user_cookies_list: List[Dict[str, str]], js_path: str):
    try:
        # 加载并编译 JavaScript 文件
        js_compiled = compile_js(js_path)

        for i, user_cookies in enumerate(user_cookies_list, start=1):
            try:
                logger.info(f"处理第 {i} 个用户的请求")
                session = create_session(user_cookies)
                data = get_data(js_compiled, PARAMS)

                # 先请求用户账号信息
                account_response = post_request(
                    session,
                    "https://interface.music.163.com/api/nuser/account/get",
                    params=PARAMS,
                )
                account_id = json.loads(account_response).get("account").get("id")
                logger.info(f"当前用户 ID: {account_id}")

                # 根据用户账号信息进行后续请求
                post_request(
                    session,
                    "https://interface.music.163.com/weapi/push-song-advisor/open/api/id/trans",
                    get_data(js_compiled, {
                        "id": account_id,
                        "sourceIdType": "userId",
                        "targetIdType": "artistId"
                    }),
                    PARAMS,
                )

                # 请求音乐人信息
                user_info = post_request(
                    session,
                    "https://music.163.com/weapi/nmusician/entrance/user/musician/info/get",
                    data,
                    PARAMS,
                )
                user_info = json.loads(user_info)
                logger.info(
                    f'状态: {user_info["message"]} ,当前用户名: {user_info["data"]["artistName"]}')

                # 请求音乐人统计数据
                musician_creator = post_request(
                    session,
                    "https://music.163.com/weapi/creator/musician/statistic/data/overview/get",
                    data,
                    PARAMS,
                )
                musician_creator = json.loads(musician_creator)
                logger.info(
                    f'昨日播放: {musician_creator["data"]["playCount"]} ,总播放: {musician_creator["data"]["totalPlayCount"]}')
                # 请求音乐人收入
                musician_income = post_request(
                    session,
                    "https://music.163.com/weapi/nmusician/workbench/creator/wallet/overview",
                    data,
                    PARAMS,
                )
                logger.debug(musician_income)
                musician_income = json.loads(musician_income)
                logger.info(
                    f'月收入: {musician_income["data"]["monthAmount"]} ,日收入: {musician_income["data"]["dailyAmount"]}')
                # 获取歌曲的今日播放趋势数据
                tend_info = post_request(
                    session,
                    'https://music.163.com/weapi/creator/musician/play/count/statistic/data/trend/get',
                    get_data(js_compiled, {
                        "startTime": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                        "endTime": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                        "csrf_token": "51c7384b8dead9388a033b43afd1b40c"
                    }),
                    PARAMS,
                )
                tend_info = json.loads(tend_info)

                # 检查 tend_info 的结构
                if "data" in tend_info and isinstance(tend_info["data"], list):
                    for entry in tend_info["data"]:
                        date_time = entry.get("dateTime", "N/A")
                        data_value = entry.get("dataValue", "N/A")
                        logger.info(f'日期: {date_time} ,播放量: {data_value}')
                else:
                    logger.error("Unexpected structure of tend_info")

                # 获取歌曲数据
                page_size = 200
                artist_id = account_id
                dt = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                order_field = 'today_play_cnt'
                order_direction = 'desc'
                page_num = 1

                all_songs = []
                first_page_data = fetch_data(session, page_num, page_size, artist_id, dt, order_field, order_direction)
                total_num = first_page_data.get('data', {}).get('total_num', 0)
                total_pages = (total_num + page_size - 1) // page_size
                logger.info(f"总数据量: {total_num}, 总页数: {total_pages}")

                # 收集第一页数据
                all_songs.extend(first_page_data.get('data', {}).get('data', []))

                # 收集其他页数据
                for page_num in range(2, total_pages + 1):
                    data = fetch_data(session, page_num, page_size, artist_id, dt, order_field, order_direction)
                    all_songs.extend(data.get('data', {}).get('data', []))

                # 按 today_play_cnt 降序排序
                sorted_songs = sorted(all_songs, key=itemgetter('today_play_cnt'), reverse=True)

                today_play_cnt_total = sum(song.get('today_play_cnt', 0) for song in sorted_songs)
                logger.info(f"今日播放总量: {today_play_cnt_total}")

                # 输出排序结果
                for song in sorted_songs:
                    song_name = song.get('song_name', '未知歌曲名')
                    today_play_cnt = song.get('today_play_cnt', 0)
                    yesterday_play_cnt = song.get('yesterday_play_cnt', 0)
                    thumbnails = song.get('thumbnails', 0)
                    logger.info(
                        f"歌曲名: {song_name}, 今日播放量: {today_play_cnt}, 昨日播放量: {yesterday_play_cnt}, "
                        f"实时数据: {thumbnails}"
                    )
            except Exception as e:
                logger.error(f"用户 {i} 数据获取失败: {e}")
    except Exception as e:
        logger.error(f"处理失败: {e}")


if __name__ == "__main__":
    logger.add("musician_api.log", rotation="500 MB")
    # 示例用户 Cookies 列表（实际使用时替换为真实数据）
    USER_COOKIES_LIST = [
        {
            'NMTID': '00OI-6BpxN2Lr4uX00lv4b_9oaQoewAAAGTfbjGHw',
            'WEVNSM': '1.0.0',
            'WNMCID': 'tisacr.1732981082494.01.0',
            '__csrf': '005b52c72ebb34e46b28221f28c55064',
            '__remember_me': 'true',
            'MUSIC_U': '00B832584F59F4F1464B14A9693FE64DA3ADEBE56321EFAFFD8C7BB7469A787F3BF85F6A895A21FF603FE0B8C7F4FA9AFA8BD9CD4F84D032B2111BF1439500F5955A01C9E3917190018EA81A5D3970E5CE4AE91413FD443A384FE5036F5AC1698D89791BD50DF929DAE3BDE7F394056BCBA10A8192FABB25415A2CDD5D376E557A71720CCCB3F0B0696233DC77CA29F549144FFF6B3B3CE30EA005720A486516C54C4FB95EAB3ECC99F93BAEA35E06B16A96C41332F5C6E41528BCA3728CC178CE1A475D96695E678ECB41EEDF39C65387DC59BC7FAAF08E06DEAFDD16143E5A75E2523577E45DE3E22F56A69495C6ACD1A0F55A3C1E1CE8DEF2AB38B38A6FF781D680264CFDCF540C8B9615D6B11544233EF15590B0AB8EC932201B3D8DE2BFFDB3AD6B19B80D745C2B41C3DAD984B6F8',
            'WM_TID': 'pL9WcYveiWNBBARRRQfGGtAAw5EFnPzN',
            '_iuqxldmzr_': '33',
            'ntes_kaola_ad': '1',
            'ntes_utid': 'tid._.i9OijDr2WbNEAwABUQPCT9FE1sVsTCxK._.0',
            'sDeviceId': 'YD-JLfXE8qXY05EV1VVVEPQo7%2FtbBLLlq03',
            'JSESSIONID-WYYY': 'd%5CZvI6zlngxSsjCZjTZPcYozj%2BId8uvZNJ5zpm5oZSjZvPcwwY5EooWmmVsIck0vtpcUyKQljpbvxl2qd4JWAvWiqo6b79UAWTr2r8CQJAYlVRT9QTT9G19rj92aSEbB3AwXkGp7Sjo%2F66Pi8AkXtOkc9zl%2BG1wJl2XJpztiK%2B%5CZJTyF%3A1733556312672',
            'csrfToken': 'MvpX76dJNOSyOLSr5tM248Cr',
            'WM_NI': 'HJXqr3zQbM222V2YWulJj%2FbBhTrLINxKBY7sGuS934PsetBvzJej0nf2dc20bAd6aU1cVUnR2x3b9z5Q%2BEugLwAdk9KzeTZlKUF54Uz22gQa2uiW1ny%2B93Ff1ZHlYjJseW8%3D',
            'WM_NIKE': '9ca17ae2e6ffcda170e2e6eeafdc7281b8bf87f464a6928fb7d14f869a9eb0db60f7b28293dc25b891ac85d22af0fea7c3b92a8c969892f139ba8faeaeb13af28afebad67fb096a6d0e14aac8cbeadcc46bc958ebab67985ab9ddab24094adab95c17eba96ab8bb366a6eeac84b13ca29facd7e45ff3bd9ab6ed5af2a8fd83bc72f78fe5a6f86d90a98f85ea3389a6abb5d968898b8ad6b75fbaeefe88d46bf2aba7b8b466bbf5f7d4c56ef386888ddc628aadabb8bb37e2a3',
        },
        {
            'NMTID': '00OATwMX6ziCYZSrUhcny0DmrpwmsQAAAGSW7BH-A',
            '_ntes_nnid': 'b261700967e5998ac4472a325eb0d042,1728115133219',
            '_ntes_nuid': 'b261700967e5998ac4472a325eb0d042',
            'WEVNSM': '1.0.0',
            'WNMCID': 'teafpj.1728115133654.01.0',
            '__snaker__id': 'UQwOwH0H1dDlg65W',
            'WM_TID': 'rjuvv37vP8pFRERAARKXHCbejxBz9YEh',
            'sDeviceId': 'YD-z3Pelp3Q8xtBFhUUUQbSCTLfngR26Lqo',
            'ntes_kaola_ad': '1',
            'ntes_utid': 'tid._.Y8SrLNXTPl9FEhQBEBeXXDKOj1Uy%252BS5i._.0',
            '__remember_me': 'true',
            'MUSICIAN_COMPANY_LAST_ENTRY': '3401613540_musician',
            'mp_MA-B9D6-269DF3E58055_hubble': '%7B%22sessionReferrer%22%3A%20%22https%3A%2F%2Fmusic.163.com%2F%22%2C%22updatedTime%22%3A%201731054132951%2C%22sessionStartTime%22%3A%201731052143724%2C%22sendNumClass%22%3A%20%7B%22allNum%22%3A%2019%2C%22errSendNum%22%3A%200%7D%2C%22deviceUdid%22%3A%20%22949e3c26fc325e5f2de95a38469b1b84e981e844%22%2C%22persistedTime%22%3A%201728401616908%2C%22LASTEVENT%22%3A%20%7B%22eventId%22%3A%20%22enter%22%2C%22time%22%3A%201731054132951%7D%2C%22currentReferrer%22%3A%20%22https%3A%2F%2Fepay.163.com%2FpcMain%2Fwithdraw%3Ffr_sc%3Durs_1fd4864f76d04ff88ca0772503e63bdd%22%2C%22sessionUuid%22%3A%20%2286337de974ed64ca81bd0d58eddd5b59c15e340b%22%7D',
            'gdxidpyhxdE': 'y3VVjkpKn6Igi2jstL6hLXxVMsMnSabrlWnfHRCAcwjWR6y8TvN7Hr49Pa14%2BY3xc6X9qnyGH4R0oSRWdqD2euXpxhwruiBA8m4cpv%2BCI2Ktp5gvdi%5CfBs5TIjOx37Gp%2BoVeIuQtsT%5Ctikta8G3yC%2B%5Cw%2FHBj01seinHXxHz%2BeZZpKTsQ%3A1738995115391',
            '__csrf': '57496fcbec222ceb62098b141b943534',
            'MUSIC_U': '00C95096AB6123A1D8047F55BA50D070038AF1A0E70B6F15B6D9A57D896BB374F728652F4972EA8734A076CE9B3BF514ADFDF24EC70C2046EF5AA8362716302C46C8D6F72F8A8479E9AAA33356AA32F06C35251CD5050846E2C18F84FAA54D3E0671E604EED377D6D4DE5B976780EDF3292EBA2622CE572E7170077A29C676519E9A129920A2A714AF4B3270290B04EBE28FE30196D4852DDF7399BDCC1CD8AD5273CCDCD9E853F7A69D381D48BE364C3CD0EE4429E1162381D6127289B5F1CE81C824EC96429E22503970C49B2DD02BD2AEE144C5F52BC29017A202D896F3BFDFE6DF2B67A17247F20563E2E8451C429F95E0CDBA7E7F32C505E8CD56792A08AADC85E5AFE2719E1C75A5BC220F3F81C78373A64BE235A36F2BBB7D6125FFF49B6EF4321BB383E211C293D969448A9D551F10CC49BC80DBF26484B128AC477BE48EBC1CD8A0D0745DD596619E0D9673995210C432C99565F2E8360150B08254A770D03444E5D5CE3AFDD4E247D16D2D17',
            '_iuqxldmzr_': '32',
            'JSESSIONID-WYYY': 'txvuuN3U%2FA5Q5WQ9ZmN2FkkHW92oscp0gAxCgCb3V3clHxSymq%2B1qDPiY4qN8qXe%2FaljJT6UkX0F%2FOIJStujFHXPxpnAHuKdPlNuWd2djSbMoA7EO95XWx26Xq44z9UbQOlpAISjM68dxXSAKfv0wUe8n8gVcSXBg3B%2FdeePV8%5Ce7W9Y%3A1738997804081',
            'csrfToken': '4dI1r6vAaoP6iROO8QUqRcMz',
            'WM_NI': 'mQzHa8eHk3jqiLOu7cJrPXU7UYwQO91aO568XVSZee72T9sJoGlvlf1C69fnrP3fJpQd8hbMZxXEIG5Zc7tZGaGKplM2dUL%2FvfOt8rBDlac2Zr03kVNlC7IVcFZO6PdVUUY%3D',
            'WM_NIKE': '9ca17ae2e6ffcda170e2e6ee8bf340818cacd9b83aad928ea3d14a979b9bb0d642a3edada8f86b94b59fd5e42af0fea7c3b92aaf8fb6a9e434a798a5d4e97bab948196b6698aaea0b9d83d9787b9b2ce33f3bf81d6b5349c8a9dbbe86ff5ee9cdaf242ad99a497ef6ef39dfadae566b290fd87c97c93bcf889e1479aa898a6cc4df786add8f75285bf89acf3688feeacb6cf25b6ba8195bb7a829ca482e23a9aae00d4ea5e8eb48dd8cc5ea19a96b0b55ca88a9bb6dc37e2a3',
        },
        {
            'csrfToken': 'ZyiiRdRHR5GXbpOIb_hOkTcb',
            'NMTID': '00OTcYzraD_ng9-uEfRqHvGzkvtn2wAAAGS0sasmw',
            '_ntes_nnid': '146bcf81aca9df3b5c7d3928cc4f537c,1730113088908',
            '_ntes_nuid': '146bcf81aca9df3b5c7d3928cc4f537c',
            'WEVNSM': '1.0.0',
            'WNMCID': 'vvaoss.1730113092805.01.0',
            '__snaker__id': 'oJHc5rQLJRRFisjJ',
            'WM_TID': 'wk1qk25hTsRBVUUVQFOTSKYdpGyL6Ci5',
            'ntes_utid': 'tid._.XLqEX8vWzBhBFxQVBROXTOJd5Di0ZHU8._.0',
            'sDeviceId': 'YD-b4LS5MtpZHpEQxBEBVbDTbdN9SmwcSFv',
            'MUSIC_U': '0071C0175DEF8C9EC9FF5D349C7A2EBAAA4262B5FA33C5372AB31FCB5E8407EF878E514462315B1522290B82A2F3E95BBB56AD8207999A8F06CEAA5EF244A6F2E0500084C47DA3DE56FE4CEC0D98875FCDA9182DD3BCCDCBB2BD062E439B5CF13AA6A0AB84241D6475887CDF7912FDF6C2450DF16F5A71BC0255D5B1C5DF69158BCF810DD5EC536D56ACD5D29B53B98D30E0041DF8C612ABC5F0B9F0B05CBFE75BCFC3F81E439E7205B2C821B2C6896C895C5E4A8BE3C370AC56C4CCE0864C6CCA3487F4F565841D46D43083182535F8C7711CAA2468A5DC39838043416CB0F560B7E75BB1CA88A597B6254AD20DEC3B676BA0A9E4CAA9CDAC7A2DCF03691AD4F36FA5905BD18389A1DBAF46B4DD9D5D80323EC3E1A396BC04EC681B6D718FD7E611D7D73C1194984C2E12948C02C442568AD581E44F02EC0D08F77B3345F8C4502394C7F30F9743DBC67DC0A55F4F5E058961ACAED635EEB5E42904C41DF8A9C4',
            '__remember_me': 'true',
            'mp_MA-B9D6-269DF3E58055_hubble': '%7B%22sessionReferrer%22%3A%20%22https%3A%2F%2Fmusic.163.com%2F%22%2C%22updatedTime%22%3A%201730113268257%2C%22sessionStartTime%22%3A%201730113268001%2C%22sendNumClass%22%3A%20%7B%22allNum%22%3A%205%2C%22errSendNum%22%3A%200%7D%2C%22deviceUdid%22%3A%20%22ac748ce34d200e6766c0ce4ad1fa0db9ada817c2%22%2C%22persistedTime%22%3A%201730113267995%2C%22LASTEVENT%22%3A%20%7B%22eventId%22%3A%20%22enter%22%2C%22time%22%3A%201730113268258%7D%2C%22currentReferrer%22%3A%20%22https%3A%2F%2Fepay.163.com%2FpcMain%2Fbind-card%3Ffr_sc%3Durs_f271a458c967492da156875b14df9330%26type%3DaccountBind%26cardType%3DDEBIT%22%2C%22sessionUuid%22%3A%20%2229681e483c52de5c801041b81728c4c0535d9638%22%7D',
            'MUSICIAN_COMPANY_LAST_ENTRY': '1368645428_musician',
            'ntes_kaola_ad': '1',
            '__csrf': 'f0497d7472bbce298f2f39b254730863',
            '_iuqxldmzr_': '33',
            'JSESSIONID-WYYY': 's24v%2F4M1nJiOd61KChVPR1aPj9HVhwR6UfkeOrMhtX366PcHwVugEnNnzrY7Zt3gU1D4JX91jwgw%2FNJo2SrWE%2Bn1NornKr8y0Mrn1TB7JJKAwRwNUcVEkq5A%2FBFi%2B7WbR3jX50gNilMJXWHYKC1d4SrznH71p1rpAOVJV5abK9r%2BPaFk%3A1733382876206',
            'WM_NI': 'QzNACshj0R1yIKfbRTtY3kOD5H1sLN71bgQHrJSl%2B64uE6BYeZQoufXHwJiJgAqSSsyKKueHcOG32XtMZzgCxP28TZ9VymHcPjAN8rAls9qDWy9rKsMo917950eSDMXjNW8%3D',
            'WM_NIKE': '9ca17ae2e6ffcda170e2e6eeaad0459690fb92fc6097868ba6c54b869b8a83c25dadb7e1d0c47082b0a0a3f12af0fea7c3b92a93a682a2c279acb600b3b4738b95aa83d160b887fd8cce50f798ff94cf46f5efae88d444b2969d8daa3ef8ab8bd7c153a7869f90f86e9c98b9abec42a59fbfb4d279bb958596e844a19189d4b154b893969be649bc90fed9d752fb8ab78ecb6994b68fafbb7a83b4bddaf45095a7f793ca798fb1f7d2b633f7f0abb4c7479cb682b8bb37e2a3',
        }
    ]
    JS_PATH = "../reverse.js"  # JavaScript 文件路径
    main(USER_COOKIES_LIST, JS_PATH)
