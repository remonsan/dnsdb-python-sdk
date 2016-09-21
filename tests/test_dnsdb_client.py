from __future__ import print_function, unicode_literals
from dnsdb.api import APIClient
from dnsdb.clients import DnsDBClient
from dnsdb.errors import AuthenticationError, DnsDBException, APIServerError
from nose import with_setup
from nose.tools import raises, assert_equal, assert_false, assert_true
from dnsdb_mock_apiserver import mockserver
from dnsdb_mock_apiserver.models import User
from dnsdb_mock_apiserver.errors import InternalServerError, GatewayTimeoutError
import datetime
import json

default_username = 'test'
default_password = '123456'
default_remaining_request = 100


def setup_func():
    APIClient.API_BASE_URL = 'http://localhost:8080/api/v1'
    mockserver.return_error_response = None
    mockserver.start()
    mockserver.users.append(User(default_username, default_password, default_remaining_request))


def teardown_func():
    mockserver.stop()


@with_setup(setup_func, teardown_func)
def test_login():
    mockserver.default_access_token = 'dnsdb api access-token'
    client = DnsDBClient()
    assert_false(client.is_login())
    client.login(default_username, default_password)
    assert_true(client.is_login())
    assert_equal(json.loads(str(client.access_token))['access_token'], mockserver.default_access_token)
    assert_equal(client.access_token.token, mockserver.default_access_token)


@raises(AuthenticationError)
@with_setup(setup_func, teardown_func)
def test_login_failed():
    client = DnsDBClient()
    client.login('test', '12345')


@with_setup(setup_func, teardown_func)
def test_search_dns():
    user = User(default_username, default_password, 2)
    mockserver.users = [user]
    mockserver.dns_records = [
                                 {'host': 'a.com', 'type': 'a', 'value': '1.1.1.1'},
                             ] * 100
    client = DnsDBClient()
    client.login(default_username, default_password)
    results = client.search_dns(domain='a.com', ip='1.1.0.0', dns_type='a', host='c.a.com')
    assert_equal(len(results), 30)
    assert_equal(user.remaining_request, 1)
    results = client.search_dns(domain='a.com', start=99)
    assert_equal(len(results), 1)
    assert_equal(user.remaining_request, 0)
    for record in results:
        assert_equal(record['host'], record.host)
        assert_equal(record['type'], record.type)
        assert_equal(record['value'], record.value)
        data = json.loads(str(record))
        assert_equal(data['host'], record.host)
        assert_equal(data['type'], record.type)
        assert_equal(data['value'], record.value)


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


@raises(APIServerError)
@with_setup(setup_func, teardown_func)
def test_search_dns_return_500():
    client = DnsDBClient()
    client.login(default_username, default_password)
    mockserver.return_error_response = InternalServerError
    client.search_dns(domain='a.com')


@raises(APIServerError)
@with_setup(setup_func, teardown_func)
def test_search_dns_return_504():
    client = DnsDBClient()
    client.login(default_username, default_password)
    mockserver.return_error_response = GatewayTimeoutError
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
    client.access_token.expire_at = datetime.datetime.now()
    assert_true(client.access_token.has_expired())
    results = client.retrieve_dns(domain='a.com', dns_type='a', ip='1.1.1.1', host='c.a.com')
    assert_equal(len(results), total)
    count = 0
    for _ in results:
        count += 1
    assert_equal(count, total)


@with_setup(setup_func, teardown_func)
def test_retrieve_dns_without_login():
    client = DnsDBClient()
    try:
        client.retrieve_dns(domain='a.com')
    except DnsDBException as e:
        assert_equal(str(e), 'Require login')


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
