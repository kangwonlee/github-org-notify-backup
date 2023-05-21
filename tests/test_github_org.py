import pathlib
import sys

import pytest
import requests


file_path = pathlib.Path(__file__)
test_folder = file_path.parent.absolute()
root_folder = test_folder.parent.absolute()

sys.path.insert(0, str(root_folder))


import github_org as go


@pytest.fixture
def public_org() -> str:
    return "python"


@pytest.fixture
def public_repo() -> str:
    return "cpython"


def test_get_repo_list(public_org):
    repo_list = go.get_repo_full_info_list(public_org)
    assert len(repo_list) > 0


def test_get_committers_emails(public_org, public_repo):
    repo_name = '/'.join((public_org, public_repo))

    emails = go.get_committers_emails(repo_name)
    assert len(emails) > 0


@pytest.mark.skipif("pytest.mock" not in sys.modules, reason='This test is skipped because of pytest.mock.')
def test_create_issue_success():
    '''Tests that the `create_issue` function creates a new issue successfully.

    Args:
        None.

    Returns:
        None.
    '''

    # Create a mock response.
    response = {
        'id': 1234,
        'title': 'This is a new issue.',
        'body': 'This is the body of the issue.',
        'assignees': ['johndoe@example.com'],
    }

    # Mock the `requests.post` function.
    with pytest.mock.patch('requests.post', return_value=response):
        # Call the `create_issue` function.
        issue_id = go.create_issue('owner', 'repo', 'This is a new issue.', 'This is the body of the issue.', 'johndoe@example.com')

    # Assert that the `create_issue` function returned the correct issue ID.
    assert issue_id == 1234


@pytest.mark.skipif("pytest.mock" not in sys.modules, reason='This test is skipped because of pytest.mock.')
def test_create_issue_failure():
    '''Tests that the `create_issue` function fails if the request fails.

    Args:
        None.

    Returns:
        None.
    '''

    # Mock the `requests.post` function.
    with pytest.mock.patch('requests.post', side_effect=requests.exceptions.RequestException):
        # Call the `create_issue` function.
        with pytest.raises(Exception):
            go.create_issue('owner', 'repo', 'This is a new issue.', 'This is the body of the issue.', 'johndoe@example.com')
