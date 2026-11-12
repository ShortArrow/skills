# Session notes

- Went with option B (worker owns the retry), not option A.
- The H1 finding from the review is fixed by this. H2 and H3 are still open.
- The thing we discussed about 4xx: now permanent failure, no retry.
- Interval doubles each attempt, like we said. Defaults 5 / 2s.
- Old client retry (3 times, fixed 1s) is gone.
- TODO later: metrics for give-ups (not in this PR).
