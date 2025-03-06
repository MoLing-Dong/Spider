from googlesearch import search

results = search("plywood site:x.com", region="countryIN", sleep_interval=5, num_results=200, advanced=True)
url_list = []
for result in results:
    print(f"标题: {result.title}")
    print(f"链接: {result.url}")
    url_list.append(result.url)
    print(f"描述: {result.description}")
print(url_list)
