import getpass
import functools
from typing import Dict, List, Tuple, Set


import requests


REPO_INFO = Dict[str, str]


@functools.lru_cache(maxsize=1)
def get_access_token() -> str:

    return getpass.getpass("Access token: ")


def get_repo_full_info_list(org:str) -> List[REPO_INFO]:

    # 헤더를 설정합니다.
    headers = {
        # "Authorization": "Bearer {}".format(get_access_token())
    }

    # GitHub API에 요청합니다.
    response = requests.get(
        f"https://api.github.com/orgs/{org}/repos",
        headers=headers
    )

    assert response.ok, f"에러: {response.status_code}"


    return response.json()


def get_repo_name_from_repo_info(repo_info:REPO_INFO) -> str:
    '''
    This function will get the name of the GitHub repository from the repository information.
    이 함수는 저장소 정보에서 GitHub 저장소의 이름을 가져옵니다.

    Args:
        repo_info (REPO_INFO): 저장소 정보입니다.


    Returns:
        저장소의 이름입니다.
    '''

    return repo_info['name']


def get_committers_emails(repository_name:str) -> Set[str]:
    '''
    This function will get the email addresses of the people who committed to the GitHub repository.
    이 함수는 GitHub 저장소에 커밋한 사람들의 이메일 주소를 가져옵니다.

    The email address is personal information, so you should be careful when using it.
    이메일 주소는 개인 정보이므로 조심해서 사용해야 합니다.

    If there is a person who wants to abuse this email address, it can cause serious damage to those people.
    이 이메일 주소를 악용하려는 사람이 있다면 해당 사람들에게 심각한 피해를 줄 수 있습니다.

    Args:
        repository_name (str): GitHub 저장소의 이름입니다.


    Returns:
        커밋터의 이메일 주소 목록입니다.
    '''

    # GitHub API에 요청합니다.
    response = requests.get("https://api.github.com/repos/{}/commits".format(repository_name))

    # Check that the response was successful.
    assert response.ok, "에러: {}".format(response.status_code)

    # Extract the committer emails from the response.
    return set(commit['commit']['author']['email'] for commit in response.json())


def create_issue(owner:str, repo:str, title:str, body:str, email:str) -> str:
    '''
    Creates a new issue in the specified repository 
        and sends an email notification to the specified email address.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        title: The title of the issue.
        body: The body of the issue.
        email: The email address to send the notification to.

    Returns:
        The ID of the newly created issue.
    '''

    url = 'https://api.github.com/repos/{owner}/{repo}/issues'.format(owner=owner, repo=repo)
    headers = {
        'Authorization': 'Bearer {token}'.format(token=get_access_token()),
    }
    data = {
        'title': title,
        'body': body,
        'assignees': [email],
    }

    response = requests.post(url, headers=headers, data=data)

    assert response.ok, f'Error creating issue: {response.status_code}'

    return response.json()['id']
