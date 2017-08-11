import requests
from lxml import etree

DEFAULT_HEADERS = {'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   }


def get_html_text(url, headers=DEFAULT_HEADERS):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except:
        return resp.status_code


def get_post_text(url, data=None, headers=DEFAULT_HEADERS):
    try:
        resp = requests.post(url, data, headers)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except:
        return resp.status_code


def get_html_tree(url, headers=DEFAULT_HEADERS):
    try:
        resp = requests.get(url=url, headers=headers, timeout=30)
        resp.raise_for_status()
        return etree.HTML(resp.content)
    except:
        return resp.status_code


def get_ua_list():
    url = 'https://techblog.willshouse.com/2012/01/03/most-common-user-agents/'
    resp = get_html_tree(url)
    ua_list = resp.xpath('//textarea[@class="get-the-list"]/text()')[0].splitlines()
    return ua_list


if __name__ == '__main__':
    # test for get_post_text
    # url = "http://www.dce.com.cn/dalianshangpin/sspz/487477/487481/1500303/index.html"
    # post_data = {'articleKey': '1500303',
    #              'columnId': '487481',
    #              'moduleId': '3',
    #              'struts.portlet.action': '/app/counting-front!saveInfo.action'}
    #
    # print(get_post_text(url=url, data=post_data))

    # test for get_ua_list
    ua_list = get_ua_list()

    # from pymongo import MongoClient
    # client = MongoClient('192.168.2.130', 27017)
    # db = client.http_header
    # db.user_agent.insert_many([{'user_agent': ua} for ua in ua_list])
    # db.user_agent.create_index({"user_agent": 1}, {"unique": True, "dropDups": True})

    import redis

    conn = redis.Redis('192.168.2.88', 6379, decode_responses=True)
    conn.sadd('user_agent', *ua_list)
