import regex
from db import conn

def add(username: str, password: str) -> bool:
    c = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone() != None:
        return False

    if username is None:
        raise ValueError("Username cannot be None")
    if password is None:
        raise ValueError("Password cannot be None")
    if len(username) > 40:
        raise ValueError("Username cannot be longer than 40 characters")
    if len(password) > 40:
        raise ValueError("Password cannot be longer than 40 characters")
    
    if not regex.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValueError("Username must only contain letters, numbers, and underscores")
    
    for c in password:
        if ord(c) < 0x1f or ord(c) > 0x7f:
            raise ValueError("Password must only contain printable characters")

    c = conn.execute("INSERT INTO users VALUES (?, ?)", (username, password))
    conn.commit()
    return True

def check(username: str, password: str) -> bool:
    c = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user != None and user[1] == password:
        return True
    return False

def remove(username: str) -> None:
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()