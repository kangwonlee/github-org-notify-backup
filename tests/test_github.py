import os
import pathlib
import sys
import urllib.parse as up

import pytest


test_file_path = pathlib.Path(__file__)
test_folder_path = test_file_path.parent.absolute()
project_folder_path = test_folder_path.parent.absolute()


sys.path.insert(
    0,
    str(project_folder_path),
)

import github
import my_token


def test_github__has_Github():
    assert hasattr(github, "Github"), dir(github)


def skip_condition() -> bool:
    return all((
        (os.getenv("GITHUB_TOKEN") is None),
        (not my_token.read_key_file_location().exists()),
    ))


def skip_message() -> str:
    return "Envirnment variable not available and key file not found"


@pytest.mark.skipif(skip_condition(), reason=skip_message())
def test_get_clone_url(org_emyl_test, repo_emyl_test, token, url_emyl_test):
    result = github.get_clone_url(org_emyl_test, repo_emyl_test, token)

    result_parsed = up.urlparse(result)
    url_parsed = up.urlparse(url_emyl_test)

    assert result_parsed.scheme == url_parsed.scheme, (result_parsed.scheme, url_parsed.scheme)
    assert result_parsed.path == url_parsed.path, (result_parsed.path, url_parsed.path)
    assert result_parsed.netloc.endswith("github.com"), result_parsed.netloc.split('@')[-1]
    assert token in result_parsed.netloc, "netlog has not token"


@pytest.mark.skipif(skip_condition(), reason=skip_message())
def test_gen_org_repo_url__one_org(auth):
    orgs = ("test-github-class-kpu",)

    result = tuple(github.gen_org_repo_url(orgs, auth))

    org_repo_list = tuple(
        filter(
            lambda s: s[0] in orgs,
            map(
                lambda url: up.urlparse(url).path.split('/')[1:3],
                result
            )
        )
    )

    assert org_repo_list


@pytest.mark.skipif(skip_condition(), reason=skip_message())
def test_get_repo_branches(auth):
    org = "test-github-class-kpu"
    repo = "18pycpp-05"

    branches = github.get_repo_branches(auth, org, repo)

    assert "master" in branches, branches
    assert "develop" in branches, branches


@pytest.mark.skipif(skip_condition(), reason=skip_message())
def test_get_repo_branches__second_org_repo(auth):
    org = "eca21z"
    repo = "eca21c-40-200-kangwon-naver"

    branches = github.get_repo_branches(auth, org, repo)

    assert "master" in branches, branches


@pytest.mark.skipif(skip_condition(), reason=skip_message())
def test_make_delete_a_branch(auth):
    org = "test-github-class-kpu"
    repo = "org-asgn-std-id-01"

    branches = github.get_repo_branches(auth, org, repo)

    new_branch = "__new__"

    if new_branch not in branches:
        if "master" in branches:
            base="master"
        elif "main" in branches:
            base = "main"

        github.make_a_branch(auth, org, repo, new_branch, base=base)

        branches = github.get_repo_branches(auth, org, repo)

        assert new_branch in branches, f"could not create {new_branch} to test"

    r = github.remove_a_branch(auth, org, repo, new_branch)

    branches = github.get_repo_branches(auth, org, repo)

    assert new_branch not in branches, f"could not delete {new_branch} : still in {branches}\n{r}"


if "__main__" == __name__:
    pytest.main([__file__])
