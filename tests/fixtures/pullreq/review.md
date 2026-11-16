# Review comments on the pull request

## Comment 1 — on settings.toml, line 5

https://github.com/example/queue-service/pull/42#discussion_r1001

> I pointed staging at an endpoint that was down and sent one item.
> It did not look like it retried.

## Comment 2 — on src/queue/worker.py, `send`

https://github.com/example/queue-service/pull/42#discussion_r1002

> Does this give up after the first failure?
