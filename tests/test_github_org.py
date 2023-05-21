import pathlib
import sys

import pytest

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
