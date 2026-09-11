Fixture for the assumption-breaking firing tests.
`spec.md` and `handler.py` describe and implement a file-sharing service whose every component does what its specification says,
and whose goal still fails:
revocation is "immediate" but the CDN header lets a copy serve for an hour;
a link stores a path, so two valid operations (rename, then download) hand out a different file;
the rate limit counts per token, so cycling tokens bypasses it;
tokens "cannot be guessed",
and are written in full to an access log that support staff read;
and the log service failing lets a download proceed unlogged.
`cli.py` is a small, unrelated command-line listing tool for the scenarios that must not fire.
