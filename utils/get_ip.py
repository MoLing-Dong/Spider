import requests


def get_external_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()  # 检查是否请求成功
        ip = response.json()['origin']
        return ip
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    external_ip = get_external_ip()
    if external_ip:
        print(f"Your external IP is: {external_ip}")