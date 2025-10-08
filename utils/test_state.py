_username = None
_password = None

def remember(username: str, password: str) -> None:
    global _username, _password
    _username = username
    _password = password

def recall():
    return _username, _password

def clear():
    global _username, _password
    _username = _password = None
