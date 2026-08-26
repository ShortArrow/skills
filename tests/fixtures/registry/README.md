Fixture for the state-first firing tests. `user.py` registers users by
email with a branch per case that has come up so far, and `doc.py`
tracks a document with three booleans and a `can_convert` that takes a
property and a state in one signature. A session asked to extend
either has an operation to add and no state model to add it to.
