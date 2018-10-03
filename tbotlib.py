#!/usr/bin/env python2
#-*- coding: utf-8 -*-
from sys import version
from datetime import datetime
from json import loads as json_load
#
#
version = version.split()[0]
#
if version.startswith('2'):
    from httplib import urlsplit
    from urllib import urlencode
    from httplib import HTTPSConnection
else:
    from http.client import urlsplit
    from urllib.parse import urlencode
    from http.client import HTTPSConnection
#
#
class Request(object):
    def __init__(self, tbot):
        resp = tbot.getresponse()
        self.status = (resp.status, resp.reason)
        self.__data = resp.read()
        tbot.close()
    #
    def __iter__(self):
        for item in self.json: yield item
    #
    def __len__(self): return len(self.json)
    #
    @property
    def raw(self): return self.__data
    #
    @property
    def json(self):
        data = json_load(self.__data)
        return data['result']
    #
    def get_first(self): return self.json[0]
    #
    def get_last(self): return self.json[-1]
    #
    @classmethod
    def get_message_id(self, message):
        return message['message']['message_id']
    #
    @classmethod
    def get_chat_id(self, message):
        return message['message']['chat']['id']
    #
    @classmethod
    def get_chat_type(self, message):
        return message['message']['chat']['type']
    #
    @classmethod
    def get_msg_date(self, message):
        date = message['message']['date']
        return datetime.fromtimestamp(date)
    #
    @classmethod
    def get_chat_text(self, message):
        return message['message']['text']
#
#
class Message(object):
    def __init__(self, message):
        pass
#
#
class Telegram(object):
    def __init__(self, token):
        url = 'https://api.telegram.org/bot'
        self.__url = urlsplit('{0}{1}/'.format(url, token))
        self.__web = HTTPSConnection(self.__url.netloc)
    #
    def __send_req(self, target, method = 'GET'):
        self.__web.connect()
        self.__web.request(method, self.__url.path + target)
    #
    def get_botname(self):
        self.__send_req('getMe')
        data = Request(self.__web)
        return data.json
    #
    def get_resp(self):
        self.__send_req('getUpdates')
        return Request(self.__web)
    #
    def __call__(self):
        'Call get_resp()'
        return self.get_resp()
    #
    def send_message(self, chat_id, message):
        data = urlencode({'chat_id': chat_id, 'text': message})
        self.__send_req('sendMessage?' + data, 'POST')
        return Request(self.__web)

