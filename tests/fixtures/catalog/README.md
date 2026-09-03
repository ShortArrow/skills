Fixture for the slice-first firing tests. The catalog is cut by
technical role: `controllers/`, `services/` and `repositories/` each
hold one file per feature, so a single feature lives in three folders
and neither folder says which pieces belong together. Both services
open with the same hand-written validation, and both repositories hold
a near-identical lookup. A session asked to add a field, to share the
lookalike code, or to make a check hold everywhere has to decide the
axis before the change fits anywhere.
