# Go

The Go spelling of the body's layers.
Read after `SKILL.md`, for a Go module.
Go has no project boundary to lean on,
so the package is the unit that holds a layer or a slice apart,
and every placement rule below is a rule about which package imports which.

## The package is the unit

```
internal/
  feature/
    cancelorder/
      cancelorder.go     handler, request and response types, the store it needs
      cancelorder_test.go
    placeorder/
      placeorder.go
  domain/
    order.go             types several packages have shown they change together
  storage/
    postgres.go          satisfies the stores the feature packages declare
```

Under a feature cut, a feature-named package is the slice: its handler,
its request and response types and the interface it needs,
in one package, with its test beside it,
and no package under `internal/feature/` imports a sibling.
Under a layer cut the same packages are named for the layers (`domain`, `app`, `storage`, `http`),
and the import rule below is the same.
Which cut applies is `slice-first`'s call.

## Interfaces sit on the consuming side

The store a package needs is declared in that package,
with only the methods it calls:

```go
type store interface {
    Load(ctx context.Context, id OrderID) (Order, error)
    Cancel(ctx context.Context, id OrderID, at time.Time) error
}
```

The implementation in `internal/storage` satisfies it without naming it.
Go's own review guidance puts an interface in the package that uses it and returns concrete types from the package that implements it (go.dev/wiki/CodeReviewComments, "Interfaces", read 2026-09-17),
which is `design-by-contract`'s rule about who declares an interface,
said once;
株式会社一創's article shows the same placement for a slice (Sources in `SKILL.md`).
An interface declared next to its one implementation is the one-implementation interface that skill refuses.

## Cross-cutting is a middleware function

Authentication, logging,
the transaction and request validation are `func(http.Handler) http.Handler`,
chained once where the router is built:

```go
h := logging(auth(validate(mux)))
```

That one line, in order, in one place,
is the traceable pipeline `slice-first` asks for;
a check written at the top of each handler is the one the next handler forgets.

## What a package may import

Its own package, the standard library,
`internal/domain` for a type that several packages have shown they change together,
and nothing under `internal/feature/` but itself.
`go vet` does not enforce that; this does,
and it belongs in the one fast command `agent-harness` describes:

```sh
for p in ./internal/feature/*/; do
  go list -f '{{join .Imports "\n"}}' "$p" | grep 'internal/feature/' && echo "$p imports a sibling" && exit 1
done
```
