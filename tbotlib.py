#!/usr/bin/env python
#-*- coding: utf-8 -*-
from sys import version as python
from datetime import datetime
from string import Formatter
from json import loads as json_load
#
#
python = python.split()[0]
#
if python.startswith('2'):
    from httplib import urlsplit
    from urllib import urlencode
    from httplib import HTTPSConnection
    #
elif python.startswith('3'):
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
        self.__data = json_load(resp.read())
        self.__data = self.__data['result']
        tbot.close()
    #
    def __iter__(self):
        for item in self.__data: yield item
    #
    def __len__(self): return len(self.__data)
    #
    def __getitem__(self, item): return self.__data[item]
    #
    def __setitem__(self, item, value): self.__data[item] = value
    #
    def __delitem__(self, item): del self.__data[item]
    #
    @property
    def data(self): return self.__data
    #
    def data_sort(self, func=None):
        'Default: data_sort(func=self.get_chat_type)'
        if not func: func = self.get_chat_type
        self.__data = list(sorted(self.__data, key=func))
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
        'Return: datetime()'
        date = message['message']['date']
        return datetime.fromtimestamp(date)
    #
    @classmethod
    def get_username(self, message, dl=' '):
        'Return: \"first_name + dl + last_name\"'
        first = message['message']['chat']['first_name']
        last = message['message']['chat']['last_name']
        return '{}{}{}'.format(first, dl, last)
    #
    @classmethod
    def get_chat_text(self, message):
        return message['message']['text']
    #
    @classmethod
    def get_msg_items(self, message):
        return message['message']['entities']
    #
    @classmethod
    def is_command(self, message):
        for item in self.get_msg_items(message):
            if item['type'] == 'bot_command': return True
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
        'Return: \"Format string.\"'
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
        'Return: json data.'
        self.__send_req('getMe')
        data = Request(self.__web)
        return data.data
    #
    def get_resp(self):
        'Return: request object.'
        self.__send_req('getUpdates')
        return Request(self.__web)
    #
    def __call__(self):
        'Call get_resp()'
        return self.get_resp()
    #
    def send_message(self, chat_id, message):
        'Return: request data.'
        data = urlencode({'chat_id': chat_id, 'text': message})
        self.__send_req('sendMessage?' + data, 'POST')
        data = Request(self.__web)
        return data.data

