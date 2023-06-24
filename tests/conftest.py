import os
import random

import requests.auth as rauth

import pytest


@pytest.fixture(scope="session")
def token():
    return os.getenv("GITHUB_TOKEN")


@pytest.fixture
def org_emyl_test() -> str:
    '''
    see https://github.com/eca20b/eca20b-40-204-kangwonlee
    '''

    return "eca20b"


@pytest.fixture
def repo_emyl_test(number_str) -> str:
    '''
    see https://github.com/eca20b/eca20b-40-204-kangwonlee
    '''
    return f"eca20b-{number_str}-kangwonlee"


@pytest.fixture
def url_emyl_test(number_str) -> str:
    '''
    see https://github.com/eca20b/eca20b-40-204-kangwonlee
    '''
    return f"https://github.com/eca20b/eca20b-{number_str}-kangwonlee"


@pytest.fixture(params=(2, 3))
def number_str(request) -> str:
    if 2 == request.param:
        result = f"{random.randint(1,9)*10:02d}-{random.randint(0,99)*10:03d}"
    elif 3 == request.param:
        result = f"{random.randint(1,9)*10:02d}-{random.randint(0,99):02d}-{random.randint(0,99):02d}"
    else:
        raise NotImplementedError
    return result


@pytest.fixture(scope="session")
def auth(ta_account, token):
    return rauth.HTTPBasicAuth(ta_account, token)


@pytest.fixture(scope="session")
def ta_account():
    return os.getenv("TA_ACCOUNT")
