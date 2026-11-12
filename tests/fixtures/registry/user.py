users = {}


def register(email, name):
    existing = users.get(email)
    if existing is not None:
        if existing["active"]:
            return None
        if existing["banned"]:
            return None
    users[email] = {"email": email, "name": name, "active": True, "banned": False}
    return users[email]


def deactivate(email):
    user = users.get(email)
    if user is None:
        return False
    user["active"] = False
    return True
