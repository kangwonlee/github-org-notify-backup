import configparser
import cryptography.fernet as cf
import getpass
import pathlib

from typing import Union


# TODO : replace encrypted file with OSX `security`


def read_key_file_location(config_file:Union[str, pathlib.Path]=pathlib.Path(".config")) -> pathlib.Path:
    """
    키 파일의 위치를 config 파일로 부터 읽습니다.

    Returns:
        키 파일의 위치입니다.
    """

    # 구성 파서 초기화
    config = configparser.ConfigParser()

    # 구성 파일 읽기
    assert config_file.exists(), f"config 파일이 존재하지 않습니다: {config_file}"
    config.read(pathlib.Path(config_file))

    # 키 파일의 위치 반환
    return pathlib.Path(config["DEFAULT"]["key_file_location"])


def write_key_file_location(
        key_file_location:str,
        config_file:Union[str, pathlib.Path]=pathlib.Path(".config")
    ):
    """
    키 파일의 위치를 config 파일에 씁니다.

    Args:
        key_file_location (str): 키 파일의 위치입니다.
    """

    # 구성 파서 초기화
    config = configparser.ConfigParser()

    # 구성 파일 생성
    config["DEFAULT"] = {}

    # 키 파일의 위치 설정
    config["DEFAULT"]["key_file_location"] = key_file_location

    # 구성 파일 쓰기
    with pathlib.Path(config_file).open("w") as f:
        config.write(f)


def encrypt_token(token):
    """
    토큰을 암호화합니다.

    Args:
        token (str): 암호화할 토큰입니다.

    Returns:
        암호화된 토큰입니다.
    """
    # 암호화 키 생성
    key = cf.Fernet.generate_key()

    # 암호화 객체 초기화
    fernet = cf.Fernet(key)

    with read_key_file_location().open('wb') as f:
        f.write(key)

    # 토큰 암호화
    encrypted_token = fernet.encrypt(token.encode())

    # 암호화된 토큰 반환
    return encrypted_token


def decrypt_token(encrypted_token, key_file=read_key_file_location()):
    """
    암호화된 토큰을 해독합니다.

    Args:
        encrypted_token (str): 해독할 암호화된 토큰입니다.

    Returns:
        해독된 토큰입니다.
    """

    # 암호화 키 가져오기
    with key_file.open("rb") as f:
        key = f.read()

    # 암호화 객체 초기화
    fernet = cf.Fernet(key)

    # 암호화된 토큰 해독
    decrypted_token = fernet.decrypt(encrypted_token).decode()

    # 해독된 토큰 반환
    return decrypted_token


def save_token(token, token_file=pathlib.Path(".token")):
    """
    토큰을 파일에 저장합니다.

    Args:
        token (str): 저장할 토큰입니다.
    """

    # 암호화된 토큰 생성
    encrypted_token = encrypt_token(token)

    # 암호화된 토큰을 파일에 쓰기
    with token_file.open("wb") as f:
        f.write(encrypted_token)


def load_token(token_file=pathlib.Path(".token")):
    """
    파일에서 토큰을 로드합니다.

    Returns:
        로드된 토큰입니다.
    """

    # 파일에서 암호화된 토큰 읽기
    with token_file.open("rb") as f:
        encrypted_token = f.read()

    # 암호화된 토큰을 해독하고 반환
    return decrypt_token(encrypted_token)


def main():
    # 토큰 입력 받기
    # 토큰을 파일에 저장
    save_token(
        token=getpass.getpass("Enter your GitHub token: "),
    )

    print("토큰이 성공적으로 저장되었습니다.")


if "__main__" == __name__:
    main()
