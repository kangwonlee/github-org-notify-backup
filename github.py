import datetime
import os
import pathlib
import sys
import time
import urllib.parse as up

from typing import Dict, List, Tuple

import requests
import requests.auth as rauth


file_path = pathlib.Path(__file__)
proj_folder = file_path.parent.absolute()
sys.path.insert(0, str(proj_folder))

import my_token


class Github():
    """
    Github REST API
    """
    def __init__(self, token=False, auth=False, wait_sec=1.1):
        self.url = "https://api.github.com/"

        self.session = requests.Session()

        if token:
            # https://stackoverflow.com/questions/13825278/python-request-with-authentication-access-token
            self.session.headers["Authentication"] = f"token {token}"
        elif auth:
            self.session.auth = auth
        else:
            raise NotImplementedError

        # https://developer.github.com/v3/#timezones
        # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        self.session.headers["Time-Zone"] = "Etc/UTC"
        self.timezone = datetime.timezone.utc
        self.timezone_str = "+00:00"

        # to avoid abuse limit
        self.wait_to_avoid_abuse_limit_sec = wait_sec

    def __del__(self):
        del self.session
        del self.url

    # pylint: disable=too-many-arguments
    def access(
        self,
        method=None,
        path=None,
        headers=None,
        files=None,
        data=None,
        params=None,
        cookies=None,
        hooks=None,
        json=None,
    ):
        """
        method : one of {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'}
        path : for example '/rate_limit' or '/orgs/octokit/repos'

        ref : https://2.python-requests.org/en/master/user/advanced/#prepared-requests
              https://2.python-requests.org/en/master/user/quickstart/#make-a-request
              https://developer.github.com/v3/
        """

        if method.lower()  != "get":
            time.sleep(self.wait_to_avoid_abuse_limit_sec)

        url = up.urljoin(self.url, path)

        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            cookies=cookies,
            hooks=hooks,
            json=json,
        )

        prep_req = self.session.prepare_request(req)

        result = self.session.send(prep_req)

        return result


def get_github_normal_header() -> Dict[str, str]:
    return {"accept": "application/vnd.github.v3+json"}


def post_a_new_message(auth:rauth.HTTPBasicAuth, owner:str, repo:str, issue_number:int, message:str) -> dict:
    github = Github(auth=auth)

    json_dict = {
        "body": message,
    }

    r = github.access(
        "POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
        headers=get_github_normal_header(),
        json=json_dict,
    )

    assert r.ok, ('\n'
        f'''json message : {r.json()["message"]}\n'''
        f"{owner}/{repo}\n"
        f"issue number : {issue_number}\n"
        f"intended message : {message}\n"
    )

    return r.json()


def get_org_repo_list(org:str, auth:rauth.HTTPBasicAuth) -> List[str]:
    github = Github(auth=auth)

    json_dict = {
        "type": "all",
        "per_page": 100,
        "visibility": "private",
    }

    result = []

    for i_page in range(100):
        json_dict["page"] = i_page

        response = github.access(
            "GET", f"/orgs/{org}/repos",
            headers=get_github_normal_header(),
            params=json_dict,
        )

        assert response.ok, response.text

        for info in response.json():
            result.append(info["clone_url"])
        if len(response.json()) < json_dict["per_page"]:
            break

    return result


def get_org_repo__from_url(url:str) -> Tuple[str]:
    parsed = up.urlparse(url)
    _, org, repo = parsed.path.split('/')

    if repo.endswith(".git"):
        repo = repo[:-4]

    return org, repo


def get_clone_url(owner:str, repo_name:str, token:str) -> str:
    scheme = "https"
    netloc = token + "@github.com"
    path = '/'.join((owner, repo_name))
    return up.urlunparse((scheme, netloc, path, None, None, None))


def get_token() -> str:
    assert "GITHUB_TOKEN" in os.environ, dict(os.environ).keys()
    assert len(os.environ["GITHUB_TOKEN"]), len(os.environ["GITHUB_TOKEN"])
    return os.environ.get("GITHUB_TOKEN")


def get_auth(ta_account:str) -> rauth.HTTPBasicAuth:
    return rauth.HTTPBasicAuth(ta_account, get_token())


def gen_org_repo_url(org_list:List[str], auth:rauth.HTTPBasicAuth) -> Tuple[str]:
    for org in org_list:
        for repo_url in get_org_repo_list(org, auth):
            yield repo_url


def get_repo_branches(auth:rauth.HTTPBasicAuth, owner:str, repo:str, b_protected:str=False, per_page:int=100,) -> List[str]:
    github = Github(auth=auth)

    json = {
        "protected": str(b_protected).lower(),
        "per_page": per_page,
    }

    result = []

    for i_page in range(100):
        json["page"] = i_page

        r = github.access("GET", f"/repos/{owner}/{repo}/branches",
            headers=get_github_normal_header(),
            json=json,
        )

        assert r.ok, (
            f'''json msg : {r.json()["message"]}\n'''
            f"{owner}/{repo}"
        )

        for info in r.json():
            result.append(info["name"])
        if len(r.json()) < json["per_page"]:
            break

    return result


def remove_a_branch(auth, owner, repo, branch):
    # Create and delete branch in github api
    # https://docs.github.com/en/rest/reference/git#delete-a-reference
    # https://titanwolf.org/Network/Articles/Article?AID=f441bab7-8fc8-45ae-b12b-4c41efbbe2d1
    github = Github(auth=auth)
    r = github.access("DELETE", f"/repos/{owner}/{repo}/git/refs/heads/{branch}")
    assert r.ok, (
        f'''json msg : {r.json()["message"]}\n'''
        f"{owner}/{repo}/ref/heads/{branch}"
    )

    return r


def get_a_sha(auth, owner, repo, branch="master") -> str:
    # Create and delete branch in github api
    # https://titanwolf.org/Network/Articles/Article?AID=f441bab7-8fc8-45ae-b12b-4c41efbbe2d1
    github = Github(auth=auth)
    r = github.access("GET", f"/repos/{owner}/{repo}/git/refs/heads/{branch}")
    assert r.ok, r.text

    return r.json()["object"]["sha"]


def make_a_branch(auth, owner, repo, branch, sha:str=None, base:str="master"):
    # Create and delete branch in github api
    # https://titanwolf.org/Network/Articles/Article?AID=f441bab7-8fc8-45ae-b12b-4c41efbbe2d1
    github = Github(auth=auth)

    if sha is None:
        sha = get_a_sha(auth, owner, repo, base)

    json = {
        "ref": f"refs/heads/{branch}",
        "sha": sha,
    }

    r = github.access("POST", f"/repos/{owner}/{repo}/git/refs",
        headers=get_github_normal_header(), json=json,
    )
    assert r.ok, r.text
