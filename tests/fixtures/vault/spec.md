# Share links

An authenticated user creates a share link for one of their files.
The link carries a random 128-bit token; the token cannot be guessed.
Anyone holding the link can download that file until the link expires or is revoked.
Revocation is immediate: after a user revokes a link,
no further download through it succeeds.
Every download is logged with the token,
the client address and the time.
Downloads are rate-limited to 60 per minute per link,
so a leaked link cannot be used to bulk-download.
An unauthenticated request can never reach a file except through a valid link.

## Delivery

Files are served through the CDN with `Cache-Control: public, max-age=3600` so that popular files do not load the origin.

## Operations

- `create_link(user, path, ttl)` returns a link for the file at `path`,
  owned by `user`.
- `revoke(user, token)` deletes the link.
- `rename(user, old_path, new_path)` moves a file.
- `download(token, client)` serves the file the link points to.
