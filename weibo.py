#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1'
__author__ = 'Linjie Ding (i@dingstyle.me)'

'''
Sina Weibo WAP API for Python.
'''

import urllib2, urllib, time

class APIClient(object):
    '''
    API client using synchronized invocation.
    '''
    _BASE_URL = "http://weibo.cn/mblog/sendmblog"
    _BASE_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3',
        # 'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # Content-Length
        #'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'weibo.cn',
        'Origin': 'http://weibo.cn',
        #'Referer': 'http://weibo.cn/?tf=5_009&gsid=3_5bcf07fde86d26d4e475a82049787de56a1102e09a63',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'
    }
    _CONTENT_TYPES = { '.png': 'image/png', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.jpe': 'image/jpeg' }

    def __init__(self, weibo_gsid):
        self._gsid = weibo_gsid

    def post(self, **kw):
        params = {
            "st": "b6cb",
            "gsid": self._gsid
        }
        url = '%s?%s' % (self._BASE_URL, self._encode_params(**params))
        print url
        payload = None
        boundary = None
        payload, boundary = self._encode_multipart(**kw)
        req = urllib2.Request(url, payload, self._BASE_HEADERS)
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
        urllib2.urlopen(req).close()

    def _encode_params(self, **kw):
        '''
        Encode parameters.
        '''
        args = []
        for k, v in kw.iteritems():
            qv = v.encode('utf-8') if isinstance(v, unicode) else str(v)
            args.append('%s=%s' % (k, urllib.quote(qv)))
        return '&'.join(args)

    def _encode_data(self, **kw):
        '''
        Encode form data.
        '''
        return urllib.urlencode(kw)

    def _encode_multipart(self, **kw):
        '''
        Build a multipart/form-data body with generated random boundary.
        '''
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        for k, v in kw.iteritems():
            data.append('--%s' % boundary)
            if hasattr(v, 'read'):
                # file-like object:
                ext = ''
                filename = getattr(v, 'name', '')
                n = filename.rfind('.')
                if n != (-1):
                    ext = filename[n:].lower()
                content = v.read()
                data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
                data.append('Content-Length: %d' % len(content))
                data.append('Content-Type: %s\r\n' % self._guess_content_type(ext))
                data.append(content)
            else:
                data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
                data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
        data.append('--%s--\r\n' % boundary)
        return '\r\n'.join(data), boundary

    def _guess_content_type(self, ext):
        return self._CONTENT_TYPES.get(ext, 'application/octet-stream')