Fixture for the firing tests. `is_leap` is wrong for 1900 and 2100 (divisible
by 100, not by 400) and the suite does not cover that class, so a session
asked to fix it has a bug with no failing test in hand. The runner copies
this directory into a fresh git repository before each scenario.
