# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json


class APIResponse(object):
    def __init__(self, content):
        self.content = content
        self.success = content.get('success')
        self.error = content.get('error')
        self.message = content.get('message')

    def has_error(self):
        return not self.success


class AuthorizeResponse(APIResponse):
    def __init__(self, content):
        self.access_token = content.get('access_token')
        super(AuthorizeResponse, self).__init__(content)


class APIClient(object):
    API_BASE_URL = 'https://dnsdb.io/api/v1'
    AUTHORIZE_URL = API_BASE_URL + "/authorize"
    SEARCH_DNS_URL = API_BASE_URL + "/dns/search"
    SEARCH_ALL_DNS_URL = API_BASE_URL + "/dns/search_all"
    RETRIEVE_DNS_URL = API_BASE_URL + "/dns/retrieve"
    RESOURCES_URL = API_BASE_URL + "/resources"

    def __init__(self):
        self.session = requests.Session()

    def authorize(self, username, password):
        response = self.session.post(self.AUTHORIZE_URL, data={'username': username, 'password': password})
        return AuthorizeResponse(json.loads(response.content))

    def search_dns(self, access_token, start=0, domain=None, ip=None, host=None, dns_type=None):
        headers = {'Access-Token': access_token}
        params = {}
        if domain:
            params['domain'] = domain
        if ip:
            params['ip'] = ip
        if host:
            params['host'] = host
        if dns_type:
            params['type'] = dns_type
        params['start'] = start
        response = self.session.get(self.SEARCH_DNS_URL, params=params, headers=headers)
        return APIResponse(json.loads(response.content))

    def request_search_id(self, access_token, start=0, domain=None, ip=None, host=None, dns_type=None):
        headers = {'Access-Token': access_token}
        params = {}
        if domain:
            params['domain'] = domain
        if ip:
            params['ip'] = ip
        if host:
            params['host'] = host
        if dns_type:
            params['type'] = dns_type
        params['start'] = start
        response = self.session.get(self.SEARCH_ALL_DNS_URL, params=params, headers=headers)
        return APIResponse(json.loads(response.content))

    def retrieve_dns(self, access_token, search_id):
        headers = {'Access-Token': access_token}
        response = self.session.get(self.RETRIEVE_DNS_URL, params={"id": search_id}, headers=headers)
        return APIResponse(json.loads(response.content))

    def resources(self, access_token):
        headers = {'Access-Token': access_token}
        response = self.session.get(self.RESOURCES_URL, headers=headers)
        return APIResponse(json.loads(response.content))
