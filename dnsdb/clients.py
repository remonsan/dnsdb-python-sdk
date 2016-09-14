# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .api import APIClient
from .errors import DnsDBException, AuthenticationError, APIServerError
import json
import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class AccessToken(object):
    EXPIRE_OFFSET_SECONDS = 15

    def __init__(self, token, expire_in):
        self.create_at = datetime.datetime.now()
        self.token = token
        self.expire_in = expire_in
        self.expire_at = self.create_at + datetime.timedelta(seconds=self.expire_in - self.EXPIRE_OFFSET_SECONDS)

    def has_expired(self):
        return self.expire_at < datetime.datetime.now()

    def is_empty(self):
        return self.token is None

    def __str__(self):
        return json.dumps({'access_token': self.token, 'expire_in': self.expire_in})


class Resource(object):
    def __init__(self, remaining_dns_request):
        self.remaining_dns_request = remaining_dns_request


class DNSRecord(object):
    def __init__(self, host, dns_type, value):
        self.host = host
        self.type = dns_type
        self.value = value

    def __getitem__(self, item):
        if item == 'host':
            return self.host
        elif item == 'type':
            return self.type
        elif item == 'value':
            return self.value

    def __str__(self):
        return json.dumps(self.__dict__)


class SearchResult(object):
    def __init__(self, total, data, remaining_request):
        self.total = total
        self.data = data
        self.remaining_request = remaining_request

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


class RetrieveResult(object):
    def __init__(self, total, search_id, client):
        self.total = total
        self.search_id = search_id
        self.client = client
        self.remaining_request = None
        self.current_set = []

    def __next__(self):
        return self.next()

    def next(self):
        if len(self.current_set) == 0:
            try:
                search_result = self.client.retrieve_dns_once(self.search_id)
                self.current_set = search_result.data
                self.remaining_request = search_result.remaining_request
                if len(self.current_set) > 0:
                    data = self.current_set[0]
                    self.current_set.remove(data)
                    return data
                else:
                    raise StopIteration
            except DnsDBException as e:
                if e.value == 'Not found':
                    raise StopIteration
                else:
                    raise e
        else:
            data = self.current_set[0]
            self.current_set.remove(data)
            return data

    def __iter__(self):
        return self

    def __len__(self):
        return self.total


def require_token(func):
    def _check(*args, **kw):
        client = args[0]
        if client.access_token is None or client.access_token.is_empty():
            raise AuthenticationError.require_login_error()
        if client.access_token.has_expired():
            client.refresh_access_token()
        return func(*args, **kw)

    return _check


class DnsDBClient(object):
    def __init__(self, proxies=None):
        self.api_client = APIClient(proxies=proxies)
        self.username = None
        self.password = None
        self.access_token = AccessToken(None, 0)
        self.__is_login = False
        self.proxies = proxies

    def login(self, username, password):
        self.username = username
        self.password = password
        auth = self.api_client.authorize(self.username, self.password)
        if auth.has_error():
            raise AuthenticationError(auth.message)
        self.access_token = AccessToken(auth.access_token, auth.expire_in)
        self.__is_login = True
        logger.debug("login success, AccessToken: %s", self.access_token)

    def is_login(self):
        return self.__is_login

    def refresh_access_token(self):
        logger.debug("refresh access token")
        if not self.__is_login:
            raise AuthenticationError.require_login_error()
        auth = self.api_client.authorize(self.username, self.password)
        if auth.has_error():
            raise AuthenticationError(auth.message)
        self.access_token = AccessToken(auth.access_token, auth.expire_in)

    @require_token
    def search_dns(self, domain=None, host=None, ip=None, dns_type=None, start=0):
        response = self.api_client.search_dns(access_token=self.access_token.token, domain=domain, host=host, ip=ip,
                                              dns_type=dns_type, start=start)
        self.__check_error(response)
        total = response.content['total']
        remaining_request = response.content['remaining_request']
        data = []
        for record in response.content['data']:
            data.append(DNSRecord(host=record['host'], dns_type=record['type'], value=record['value']))
        return SearchResult(total=total, data=data, remaining_request=remaining_request)

    @require_token
    def retrieve_dns(self, domain=None, host=None, ip=None, dns_type=None):
        response = self.api_client.request_search_id(access_token=self.access_token.token, domain=domain, host=host,
                                                     ip=ip, dns_type=dns_type)
        self.__check_error(response)
        total = response.content['total']
        search_id = response.content['id']
        return RetrieveResult(total=total, search_id=search_id, client=self)

    def retrieve_dns_once(self, search_id):
        response = self.api_client.retrieve_dns(self.access_token.token, search_id)
        self.__check_error(response)
        total = response.content['total']
        remaining_request = response.content['remaining_request']
        data = []
        for record in response.content['data']:
            data.append(DNSRecord(host=record['host'], dns_type=record['type'], value=record['value']))
        return SearchResult(total=total, data=data, remaining_request=remaining_request)

    @require_token
    def get_resources(self):
        response = self.api_client.resources(self.access_token.token)
        self.__check_error(response)
        return Resource(response.content['remaining_dns_request'])

    def __check_error(self, response):
        if response.status_code == 401:
            self.__is_login = False
            raise AuthenticationError(response.message)
        elif 400 <= response.status_code < 500:
            raise DnsDBException(response.message)
        if response.status_code >= 500:
            raise APIServerError()
