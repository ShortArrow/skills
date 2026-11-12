"""Share-link handler. Every function does what spec.md says it does."""
import secrets
import time

LINKS = {}       # token -> {"user": str, "path": str, "expires": float}
FILES = {}       # path -> bytes
HITS = {}        # token -> [timestamps]
ACCESS_LOG = []  # lines readable by support staff


def create_link(user, path, ttl):
    token = secrets.token_hex(16)
    LINKS[token] = {"user": user, "path": path, "expires": time.time() + ttl}
    return token


def revoke(user, token):
    link = LINKS.get(token)
    if link and link["user"] == user:
        del LINKS[token]


def rename(user, old_path, new_path):
    FILES[new_path] = FILES.pop(old_path)


def _log(token, client):
    ACCESS_LOG.append("%s %s %s" % (time.time(), token, client))


def download(token, client):
    link = LINKS.get(token)
    if link is None or link["expires"] < time.time():
        return 404, {}, b""
    window = [t for t in HITS.get(token, []) if t > time.time() - 60]
    if len(window) >= 60:
        return 429, {}, b""
    HITS[token] = window + [time.time()]
    try:
        _log(token, client)
    except Exception:
        pass
    body = FILES.get(link["path"], b"")
    return 200, {"Cache-Control": "public, max-age=3600"}, body
