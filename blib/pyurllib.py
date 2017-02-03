import urllib2
import re

req_timeout = 25
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " + \
     "AppleWebKit/537.36 (KHTML, like Gecko) " + \
     "Chrome/42.0.2311.135 " + \
     "Safari/537.36 " + \
     "Edge/12.10240"


def urlread2(url, retry_times = 5):
    for i in range(retry_times):
        try:
            req_header = {
                'User-Agent': UA,
                'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Host': re.findall('://.*?/', url, re.DOTALL)[0][3:-1]}
            return urllib2.urlopen(urllib2.Request(url, None, req_header), None, req_timeout).read()
        except:
            pass
    print "Error while reading:", url