from core.db import get_conn


def login(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def register(username, password):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()