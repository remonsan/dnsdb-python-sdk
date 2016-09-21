from __future__ import print_function, unicode_literals
from dnsdb.api import APIClient
from dnsdb.clients import DnsDBClient
from dnsdb.errors import AuthenticationError, DnsDBException
from nose import with_setup
from nose.tools import raises, assert_equal
from dnsdb_mock_apiserver import mockserver
from dnsdb_mock_apiserver.models import User
import time

default_username = 'test'
default_password = '123456'
default_remaining_request = 100


def setup_func():
    APIClient.API_BASE_URL = 'http://localhost:8080/api/v1'
    mockserver.start()
    mockserver.users.append(User(default_username, default_password, default_remaining_request))


def teardown_func():
    mockserver.stop()


@with_setup(setup_func, teardown_func)
def test_login_success():
    mockserver.default_access_token = 'dnsdb api access-token'
    client = DnsDBClient()
    client.login(default_username, default_password)
    assert_equal(client.access_token.token, mockserver.default_access_token)


@raises(AuthenticationError)
@with_setup(setup_func, teardown_func)
def test_login_failed():
    client = DnsDBClient()
    client.login('test', '12345')


@with_setup(setup_func, teardown_func)
def test_search_dns_success():
    user = User(default_username, default_password, 2)
    mockserver.users = [user]
    mockserver.dns_records = [
                                 {'host': 'a.com', 'type': 'a', 'value': '1.1.1.1'},
                             ] * 100
    client = DnsDBClient()
    client.login(default_username, default_password)
    results = client.search_dns(domain='a.com')
    assert_equal(len(results), 30)
    assert_equal(user.remaining_request, 1)
    results = client.search_dns(domain='a.com', start=99)
    assert_equal(len(results), 1)
    assert_equal(user.remaining_request, 0)


@raises(AuthenticationError)
@with_setup(setup_func, teardown_func)
def test_search_dns_without_login():
    client = DnsDBClient()
    client.search_dns(domain='a.com')


@raises(DnsDBException)
@with_setup(setup_func, teardown_func)
def test_search_dns_without_params():
    client = DnsDBClient()
    client.login(default_username, default_password)
    client.search_dns()


@raises(DnsDBException)
@with_setup(setup_func, teardown_func)
def test_search_dns_without_remaining_request():
    mockserver.users = [User(default_username, default_password, 0)]
    client = DnsDBClient()
    client.login(default_username, default_password)
    client.search_dns(domain='a.com')


@with_setup(setup_func, teardown_func)
def test_retrieve_dns():
    total = 200
    mockserver.users = [User(default_username, default_password, 2)]
    mockserver.max_page_size = 100
    mockserver.dns_records = [
                                 {'host': 'a.com', 'type': 'a', 'value': '1.1.1.1'},
                             ] * total
    client = DnsDBClient()
    client.login(default_username, default_password)
    results = client.retrieve_dns(domain='a.com')
    assert_equal(len(results), total)
    count = 0
    for _ in results:
        count += 1
    assert_equal(count, total)


@raises(AuthenticationError)
@with_setup(setup_func, teardown_func)
def test_retrieve_dns_without_login():
    client = DnsDBClient()
    client.retrieve_dns(domain='a.com')


@raises(DnsDBException)
@with_setup(setup_func, teardown_func)
def test_retrieve_dns_without_enough_remaining_request():
    total = 200
    mockserver.users = [User(default_username, default_password, 1)]
    mockserver.max_page_size = 100
    mockserver.dns_records = [
                                 {'host': 'a.com', 'type': 'a', 'value': '1.1.1.1'},
                             ] * total
    client = DnsDBClient()
    client.login(default_username, default_password)
    results = client.retrieve_dns(domain='a.com')
    assert_equal(len(results), total)
    for _ in results:
        pass


@with_setup(setup_func, teardown_func)
def test_get_resources():
    mockserver.users = [User(default_username, default_password, 100)]
    client = DnsDBClient()
    client.login(default_username, default_password)
    resources = client.get_resources()
    assert_equal(resources.remaining_dns_request, 100)


@raises(AuthenticationError)
@with_setup(setup_func, teardown_func)
def test_get_resources_without_login():
    client = DnsDBClient()
    client.get_resources()


@with_setup(setup_func, teardown_func)
def test_get_resources():
    mockserver.users = [User(default_username, default_password, 100)]
    client = DnsDBClient()
    client.login(default_username, default_password)
    resources = client.get_resources()
    assert_equal(resources.remaining_dns_request, 100)


@raises(AuthenticationError)
@with_setup(setup_func, teardown_func)
def test_get_resources_without_login():
    client = DnsDBClient()
    client.get_resources()
