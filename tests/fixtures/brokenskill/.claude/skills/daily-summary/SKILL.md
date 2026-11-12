---
name: daily-summary
description: Summarise the week's work from the issue tracker. Use when asked for a daily or weekly summary of issues.
---

# Daily summary

1. Fetch the issues:

   ```
   python .claude/skills/daily-summary/scripts/fetch.py --limit 100 > issues.json
   ```

2. Group them by label and write one line per issue under each label.
3. Save the result as `summary.md`.
