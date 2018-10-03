#!/usr/bin/env python
#-*- coding: utf-8 -*-
from sys import version
from datetime import datetime
from string import Formatter
from json import loads as json_load
#
#
version = version.split()[0]
#
if version.startswith('2'):
    from httplib import urlsplit
    from urllib import urlencode
    from httplib import HTTPSConnection
    #
elif version.startswith('3'):
    from http.client import urlsplit
    from urllib.parse import urlencode
    from http.client import HTTPSConnection
    #
else: raise EnvironmentError('WTF? Version: {}'.format(version))
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
    def get_first(self):
        try: return self.json[0]
        except IndexError: return
    #
    def get_last(self):
        try: return self.json[-1]
        except IndexError: return
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
        'Return datetime()'
        date = message['message']['date']
        return datetime.fromtimestamp(date)
    #
    @classmethod
    def get_username(self, message, dl=' '):
        'Return \"first_name + dl + last_name\"'
        first = message['message']['chat']['first_name']
        last = message['message']['chat']['last_name']
        return '{}{}{}'.format(first, dl, last)
    #
    @classmethod
    def get_chat_text(self, message):
        return message['message']['text']
#
#
class Message(object):
    '''Telegram message printing...\n
dt_format (Default: %H:%M:%S %m-%d-%Y)
msg_format (Values:\n\tchat_id\n\tmessage_id
\tchat_type\n\tmsg_date\n\tusername\n\tchat_text)'''
    #
    dt_format = '%H:%M:%S %m-%d-%Y'
    msg_format = '{msg_date} {username} {chat_text}'
    #
    def __init__(self, message, dt_format=None, msg_format=None):
        '''\
Message(request_obj, dt_format=None, msg_format=None)
dt_format=None (Use default), msg_format=None (Use default)'''
        self._msg = message
        #
        if dt_format: self.dt_format = dt_format
        if msg_format: self.msg_format = msg_format
    #
    def __str__(self):
        'Return \"Format string.\"'
        try:
            fmt = Formatter()
            buff = []
            #
            for (dl, item, _, _) in fmt.parse(self.msg_format):
                if dl: buff.append(dl)
                #
                if item == 'chat_id':
                    buff.append(str(Request.get_chat_id(self._msg)))
                    #
                elif item == 'message_id':
                    buff.append(str(Request.get_message_id(self._msg)))
                    #
                elif item == 'username':
                    buff.append(Request.get_username(self._msg))
                    #
                elif item == 'chat_type':
                    buff.append(Request.get_chat_type(self._msg))
                    #
                elif item == 'msg_date':
                    date = Request.get_msg_date(self._msg)
                    buff.append(date.strftime(self.dt_format))
                    #
                elif item == 'chat_text':
                    buff.append(Request.get_chat_text(self._msg))
            #
            return ''.join(buff)
            #
        except KeyError: return
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
        'Return json_data'
        self.__send_req('getMe')
        data = Request(self.__web)
        return data.json
    #
    def get_resp(self):
        'Return request_obj'
        self.__send_req('getUpdates')
        return Request(self.__web)
    #
    def __call__(self):
        'Call get_resp()'
        return self.get_resp()
    #
    def send_message(self, chat_id, message):
        'Return request_obj'
        data = urlencode({'chat_id': chat_id, 'text': message})
        self.__send_req('sendMessage?' + data, 'POST')
        return Request(self.__web)

