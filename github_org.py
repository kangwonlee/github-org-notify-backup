import getpass
import functools
from typing import List, Dict


import requests


REPO_INFO = Dict[str, str]


@functools.lru_cache(maxsize=1)
def get_access_token() -> str:

    return getpass.getpass("Access token: ")


def get_repo_full_info_list(org:str) -> List[Dict[str, str]]:

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
