# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json


class APIResponse(object):
    def __init__(self, content, status_code):
        self.content = content
        self.success = content.get('success')
        self.error = content.get('error')
        self.message = content.get('message')
        self.status_code = status_code

    def has_error(self):
        return not self.success


class AuthorizeResponse(APIResponse):
    def __init__(self, content, status_code):
        self.access_token = content.get('access_token')
        self.expire_in = content.get('expire_in')
        super(AuthorizeResponse, self).__init__(content, status_code)


class APIClient(object):
    API_BASE_URL = 'https://dnsdb.io/api/v1'

    def __init__(self):
        self.session = requests.Session()
        self.AUTHORIZE_URL = self.API_BASE_URL + "/authorize"
        self.SEARCH_DNS_URL = self.API_BASE_URL + "/dns/search"
        self.SEARCH_ALL_DNS_URL = self.API_BASE_URL + "/dns/search_all"
        self.RETRIEVE_DNS_URL = self.API_BASE_URL + "/dns/retrieve"
        self.RESOURCES_URL = self.API_BASE_URL + "/resources"

    def authorize(self, username, password):
        response = self.session.post(self.AUTHORIZE_URL, data={'username': username, 'password': password})
        return AuthorizeResponse(response.json(), response.status_code)

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
        return APIResponse(response.json(), response.status_code)

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
        return APIResponse(response.json(), response.status_code)

    def retrieve_dns(self, access_token, search_id):
        headers = {'Access-Token': access_token}
        response = self.session.get(self.RETRIEVE_DNS_URL, params={"id": search_id}, headers=headers)
        return APIResponse(response.json(), response.status_code)

    def resources(self, access_token):
        headers = {'Access-Token': access_token}
        response = self.session.get(self.RESOURCES_URL, headers=headers)
        return APIResponse(response.json(), response.status_code)
