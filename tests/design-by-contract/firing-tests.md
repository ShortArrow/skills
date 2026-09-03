# Firing tests for design-by-contract

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/orders` —
a module whose arguments are checked on both sides of every call, whose
violated preconditions come back as `None`, and a repository interface
with one implementation declared beside it. Run them with
`tests/run-firing-tests.sh design-by-contract`.

Fixture: `tests/fixtures/orders`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; without it, S1–S3 still pass when the answer gives each
condition one owner, separates a violated contract from an expected
failure, or declines the interface that has one implementation and says
what would justify one.

## Should fire

### S1 — one more defensive check

> orders.py の place_order で quantity が None のときも落ちないように
> ガードを足して。

Expected: the skill fires, or the answer asks who owes the condition —
a checked type or a stated precondition at one boundary — instead of
adding a fourth guard to a function whose callers already check.

### S2 — a violated precondition returned as a value

> place_order が None を返すケースが多すぎて呼び出し側で区別できない。
> エラーコードの文字列を返すようにして。

Expected: the skill fires, or the answer splits the two failures: an
empty customer_id or a non-positive quantity is a caller bug that
raises, and "customer does not exist" is a result the return type
carries.

### S3 — an interface for the one implementation

> repository.py にならって、通知用の Notifier インターフェースを
> 作って。実装は SmtpNotifier ひとつ。

Expected: the skill fires, or the answer says a single implementation
with no test boundary does not yet justify an interface, and that when
one is written the consumer owns it rather than the module that
implements it.

## Should not fire

### S4 — a rename

> repository.py の SqliteOrderRepository を SqliteOrders に改名して、
> 参照も直して。

Expected: no skill call. No obligation moves.

### S5 — read-only

> orders.py を読んで、place_order がどんなときに None を返すか
> 列挙して。

Expected: no skill call. Reporting the current behaviour changes no
contract.
