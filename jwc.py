#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
#=============================================================================
#     FileName: jwc.py
#         Desc:
#       Author: Mocker
#        Email: Zuckerwooo@gmail.com
#     HomePage: zuckonit.github.com
#      Version: 0.0.1
#   LastChange: 2012-09-07 15:37:04
#      History:
#=============================================================================
'''


import urllib
import urllib2
import re
import bs4


from setting import *
from items   import *

class JWC(object):
    def __init__(self,usr,pwd):
        self.usr = usr
        self.pwd = pwd

        _cookie_hd   = urllib2.HTTPCookieProcessor()
        _redirect_hd = urllib2.HTTPRedirectHandler()
        self._opener = urllib2.build_opener(_redirect_hd,_cookie_hd)

    @staticmethod
    def _get_viewstate(data):
        parse_viewstate = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        view_state = parse_viewstate.findall(data)[0]
        if view_state:
            return view_state

    @staticmethod
    def _rp_url(url):
        if url.startswith(url_home):
            return url.replace(url_home,_url_home)
        return url

    def login(self):
        jump = self._opener.open(url_home)
        data = jump.read()
        self.url_login = jump.geturl()
        post_data  = {
            '__VIEWSTATE':self._get_viewstate(data),
            'TextBox1':self.usr,
            'TextBox2':self.pwd,
            'RadioButtonList1':u'学生'.encode('gbk'),
            'Button1':'',
            'lbLanguage':''
        }

        req  = urllib2.Request(self.url_login,urllib.urlencode(post_data))
        jump = self._opener.open(req)
        self.url_redirect = jump.geturl()
        self.url_redirect = self._rp_url(self.url_redirect)
        self.url_base     = self._rp_url(self.url_login).replace('default2.aspx','')
        data = jump.read().decode('gbk')
        parse_links = re.compile(r'<a href="(.*?)".*?>(.*?)</a>')
        links  = parse_links.findall(data)
        keys = []
        vals = []
        for link , item in links:
            keys.append(item)
            link = link.encode('gbk')
            for c in link:
                if ord(c) > 127:
                    c = urllib.quote(c)
            vals.append(self.url_base + link)
        self.links = dict(zip(keys,vals))

        req  = urllib2.Request(self.url_redirect)
        req.add_header('Referer',self.url_login)
        jump = self._opener.open(req)



    def get_timetable(self,year='',term=''):
        url = self.links[query_time_table]
        req = urllib2.Request(url)
        req.add_header('Referer',self.url_redirect)
        data = self._opener.open(req).read()
        soup = bs4.BeautifulSoup(data)
        outcome = soup.findAll("td",{"align":"Center","rowspan":re.compile('[234]')})
        if outcome:
            for i in outcome:
                print i.text
            return True
        else:
            self.get_timetable()

if __name__ == '__main__':
    jwc = JWC(username,password)
    jwc.login()
    timetable = jwc.get_timetable()
