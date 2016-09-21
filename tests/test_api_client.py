from __future__ import unicode_literals, print_function
from dnsdb.api import APIClient
from nose import with_setup
from nose.tools import assert_equal, assert_true, assert_false
from dnsdb_mock_apiserver import mockserver
from dnsdb_mock_apiserver.models import User

import time


def setup_func():
    APIClient.API_BASE_URL = 'http://localhost:8080/api/v1'
    mockserver.start()
    time.sleep(0.1)


def teardown_func():
    pass
    mockserver.stop()


@with_setup(setup_func, teardown_func)
def test_authorize():
    mockserver.users.append(User('test', '123456'))
    mockserver.default_access_token = "1231313132"
    client = APIClient()
    response = client.authorize('test', '123456')
    assert_true(response.success)
    assert_equal(response.access_token, mockserver.default_access_token)


@with_setup(setup_func, teardown_func)
def test_authorize_failed():
    mockserver.users.append(User('test', '123456'))
    client = APIClient()
    response = client.authorize('test', '123')
    assert_false(response.success)
