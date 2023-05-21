import getpass
import pathlib
import cryptography.fernet as cf


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

    # 토큰 암호화
    encrypted_token = fernet.encrypt(token.encode())

    # 암호화된 토큰 반환
    return encrypted_token


def decrypt_token(encrypted_token, key_file=pathlib.Path(".token_key")):
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


def save_token(token, token_key_file=pathlib.Path(".token_key")):
    """
    토큰을 파일에 저장합니다.

    Args:
        token (str): 저장할 토큰입니다.
    """

    # 암호화된 토큰 생성
    encrypted_token = encrypt_token(token)

    # 암호화된 토큰을 파일에 쓰기
    with token_key_file.open("wb") as f:
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
        getpass.getpass("Enter your GitHub token: ")
    )

    print("토큰이 성공적으로 저장되었습니다.")


if "__main__" == __name__:
    main()
