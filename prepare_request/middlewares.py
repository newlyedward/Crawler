# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from .settings import UA_KEYNAME


class RandUserAgentMiddleware(UserAgentMiddleware):
    """This middleware allows spiders to override the user_agent"""

    def process_request(self, request, spider):
        user_agent = spider.server.srandmember(UA_KEYNAME)
        if 'User-Agent' in request.headers:
            request.headers['User-Agent'] = user_agent
            return None
        elif user_agent:
            request.headers.setdefault(b'User-Agent', user_agent)
            return None
        elif self.user_agent:
            request.headers.setdefault(b'User-Agent', self.user_agent)
