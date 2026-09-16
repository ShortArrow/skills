# Go

The Go spelling of the body's layers.
Read after `SKILL.md`, for a Go module.
Go has no project boundary to lean on,
so the package is the unit that holds a layer or a slice apart,
and the placement rules below are all about which package imports which.

## The package is the slice

```
internal/
  feature/
    cancelorder/
      cancelorder.go     handler, request and response types, the store it needs
      cancelorder_test.go
    placeorder/
      placeorder.go
  domain/
    order.go             types several slices have shown they change together
  storage/
    postgres.go          satisfies the stores the slices declare
```

A feature-named package is the slice: its handler,
its request and response types and the interface it needs,
in one package, with its test beside it.
A second feature is a second package,
and no package under `internal/feature/` imports a sibling.
A slice is as thin as its work:
a read of one row is a handler and a query,
not a repository and a service.

## Interfaces sit on the consuming side

The store a slice needs is declared in the slice,
with only the methods the slice calls:

```go
type store interface {
    Order(ctx context.Context, id OrderID) (Order, error)
    Save(ctx context.Context, o Order) error
}
```

The implementation in `internal/storage` satisfies it without naming it,
which is the language's own rule (accept interfaces, return structs) and `design-by-contract`'s rule about who declares an interface,
said once.
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

## What a slice may import

Its own package, the standard library,
`internal/domain` for a type that several slices have shown they change together,
and nothing under `internal/feature/` but itself.
`go vet` does not enforce that;
a dependency-direction check over the import graph does (`agent-harness`),
and it is a short script.
