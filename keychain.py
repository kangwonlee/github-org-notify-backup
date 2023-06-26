'''
ref : https://gist.github.com/gcollazo/9434580
'''
import re
import subprocess


def add_pwd(service:str, account:str, password:str) -> int:
    '''
    function setpassword() of https://gist.github.com/gcollazo/9434580
    '''
    cmd = (
        '/usr/bin/security', 'add-generic-password', '-U', '-a', account, '-s', service, '-p', password
    )

    p = subprocess.run(cmd, shell=True, check=True)
    return p.returncode


def read_pwd(service:str, account:str):
    '''
    function getpassword() of https://gist.github.com/gcollazo/9434580
    '''

    def decode_hex(s):
        s = eval('"' + re.sub(r"(..)", r"\x\1", s) + '"')
        if "" in s: s = s[:s.index("")]
        return s

    cmd = (
        "/usr/bin/security",
        "find-generic-password",
        "-g",  "-s", f"'{service}'",
        '-a' f"'{account}'",
    )
    p = subprocess.check_output(cmd, shell=True, check=True, encoding='utf-8')
    s = p.stderr
    m = re.match(r"password: (?:0x([0-9A-F]+)\s*)?\"(.*)\"$", s)
    if m:
        hexform, stringform = m.groups()
        if hexform:
            return decode_hex(hexform)
        else:
            return stringform
