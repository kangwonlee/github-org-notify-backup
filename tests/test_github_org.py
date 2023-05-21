import os
import pathlib
import sys
import tempfile

import pytest
import requests


file_path = pathlib.Path(__file__)
test_folder = file_path.parent.absolute()
root_folder = test_folder.parent.absolute()

sys.path.insert(0, str(root_folder))


import github_org as go
import my_token as mt


@pytest.fixture
def public_org() -> str:
    return "python"


@pytest.fixture
def public_repo() -> str:
    return "cpython"


@pytest.fixture
def private_org() -> str:
    return "eca21x"


@pytest.fixture
def private_repo() -> str:
    return "eca21a-40-242-kangwon-naver"


@pytest.fixture
def clonable_org() -> str:
    return "octocat"


@pytest.fixture
def clonable_repo() -> str:
    return "hello-worId"


@pytest.fixture
def not_so_serious_token() -> str:
    return "my-github-token"


@pytest.fixture
def not_so_serious_github_id() -> str:
    return "kangwonlee"


@pytest.fixture
def serious_token() -> str:
    if "GITHUB_TOKEN" in os.environ:
        return os.environ["GITHUB_TOKEN"]
    else:
        os.environ["GITHUB_TOKEN"] = mt.load_token()
        return os.environ["GITHUB_TOKEN"]


@pytest.fixture
def temp_backup_root() -> pathlib.Path:
    '''
    Create a temporary directory that can be used to test backup_repo.
    '''
    with tempfile.TemporaryDirectory() as backup_root:
        yield pathlib.Path(backup_root)


def test_get_repo_list(public_org):
    repo_list = go.get_repo_full_info_list(public_org)
    assert len(repo_list) > 0


def test_get_committers_emails(public_org, public_repo):
    repo_name = '/'.join((public_org, public_repo))

    emails = go.get_committers_emails(repo_name)
    assert len(emails) > 0


def test_create_issue_success(mocker):
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
    with mocker.patch('requests.post', return_value=response):
        # Call the `create_issue` function.
        issue_id = go.create_issue('owner', 'repo', 'This is a new issue.', 'This is the body of the issue.', 'johndoe@example.com')

    # Assert that the `create_issue` function returned the correct issue ID.
    assert issue_id == 1234


def test_create_issue_failure(mocker):
    '''Tests that the `create_issue` function fails if the request fails.

    Args:
        None.

    Returns:
        None.
    '''

    # Mock the `requests.post` function.
    with mocker.patch('requests.post', side_effect=requests.exceptions.RequestException):
        # Call the `create_issue` function.
        with pytest.raises(Exception):
            go.create_issue('owner', 'repo', 'This is a new issue.', 'This is the body of the issue.', 'johndoe@example.com')


def test_backup_repo_with_existing_repo(
        clonable_org:str, clonable_repo:str,
        temp_backup_root:pathlib.Path,
        not_so_serious_token:str
    ):
    """
    Test that backup_repo can successfully clone an existing repository.
    """

    go.backup_repo(clonable_org, clonable_repo, temp_backup_root, not_so_serious_token)

    assert (temp_backup_root / clonable_org / clonable_repo).exists()


def test_backup_repo_with_non_existing_repo(
        temp_backup_root:pathlib.Path,
        not_so_serious_token:str, not_so_serious_github_id:str
    ):
    """
    Test that backup_repo raises an exception if the repository does not exist.
    """
    org = "zzz"
    repo_name = "non-existing-repo"

    with pytest.raises(AssertionError):
        go.backup_repo(
            org, repo_name, temp_backup_root,
            not_so_serious_token, github_id=not_so_serious_github_id
        )


def test_is_repo_exist_with_existing_repo(
        public_org:str, public_repo:str,
        not_so_serious_token:str, not_so_serious_github_id:str
    ):
    """
    Test if the function returns True for an existing repository.
    """
    assert go.is_repo_exist(
        public_org, public_repo,
        token=not_so_serious_token, github_id=not_so_serious_github_id
    ) is True


def test_is_repo_exist_with_non_existing_repo(
        public_org:str,
        not_so_serious_token:str, not_so_serious_github_id:str
    ):
    """
    Test if the function returns False for a non-existing repository.
    """
    assert go.is_repo_exist(
        public_org, "not-a-real-repo",
        token=not_so_serious_token, github_id=not_so_serious_github_id
    ) is False


def test_is_repo_exist_with_invalid_token(
        private_org:str, private_repo:str,
        not_so_serious_github_id:str
    ):
    """
    Test if the function raises an exception for an invalid token.
    """
    assert go.is_repo_exist(
        private_org, private_repo,
        token="invalid-token", github_id=not_so_serious_github_id
    ) is False


def test_is_repo_exist_with_valid_token(
        private_org:str, private_repo:str,
        serious_token:str
    ):
    """
    Test if the function raises an exception for an invalid token.
    """
    assert go.is_repo_exist(
        private_org, private_repo,
        token=serious_token, github_id=not_so_serious_github_id
    ) is True
