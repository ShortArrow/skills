Fixture for the design-by-contract firing tests. `orders.py` has the
shape a codebase takes when no condition has an owner: the same
argument checked in the caller and again in the callee, a violated
precondition returned as `None`, and a docstring that states in prose
what the parameter type could have refused. `repository.py` adds an
interface with exactly one implementation, declared in the module that
implements it. A session asked to extend either has the obligations to
sort out before the change fits anywhere.
