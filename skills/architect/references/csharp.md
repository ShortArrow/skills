# C#

The C# spelling of the body's layers.
Read after `SKILL.md`, for a .NET solution.

## MVVM

- **View** — XAML or Razor only.
  Code-behind kept to a minimum.
- **ViewModel** — implements `INotifyPropertyChanged` and `ICommand`.
- **Model** — the Domain layer's entities.

Base classes for both, `RelayCommand` and its async form,
and the Avalonia input-validation variant are in `csharp-patterns.md`.

The screen's arbiter is the root ViewModel, or a shell service it owns:
it holds the current mode as one enumeration and decides visibility for every child.
A child ViewModel exposes its own state for binding and raises what it cannot settle upward,
as an event or through a messenger (`IMessenger` in CommunityToolkit.Mvvm),
and holds no reference to a sibling.
Code-behind never sets `IsVisible`;
a view that does is a view deciding.

## Mediator dispatch

A mediator library (MediatR, Mediator.SourceGenerator, Wolverine and the like) dispatches a request to the one handler that declares it:

```csharp
public record CreateProduct(string Name, decimal Price) : IRequest<int>;

public sealed class CreateProductHandler : IRequestHandler<CreateProduct, int>
{
    public Task<int> Handle(CreateProduct request, CancellationToken ct) => ...;
}
```

The request type is the contract.
Registration scans the assembly,
so a handler is reached by its request type rather than by a reference,
and nothing but the type connects the two.

Cross-cutting concerns go in the pipeline, registered once, in order:

```csharp
public sealed class ValidationBehavior<TRequest, TResponse>
    : IPipelineBehavior<TRequest, TResponse>
{
    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        // validate, then hand on
        return await next();
    }
}
```

`services.AddMediatR(...)` plus one `AddOpenBehavior` call per behaviour is the whole wiring;
the order of registration is the order of execution,
and it is the only place a reader can see what runs before a handler.

Two cautions specific to this stack.
Assembly scanning means a handler with no reference is still reached,
so a stale handler stays alive until someone deletes it.
And a request with one sender and one handler gains nothing from the dispatch but the lost jump to definition.
When the dispatch, the pipeline or the folder layout is the question,
the rule is in `slice-first` and `design-by-contract`;
the code above only shows how this stack spells it.

MediatR left the Apache licence at v13.0.0 (2025-07-02) for a dual commercial and open-source licence and asks for a licence key at registration;
a missing key logs a warning,
and production use requires one under the licence (release notes and the licensing source read 2026-09-17).
A solution adopting it after that date chooses its licence first;
Mediator.SourceGenerator and a direct call to the handler are the routes that do not ask.

## Refactoring moves

Extract method or class, move a type to the layer it belongs in,
introduce a value object, replace a conditional with polymorphism;
each with every test green before and after (`tidy-first`).

## Analyzer codes

- `CA1062` — add the null check, or adopt nullable reference types
- `CA1822` — make it static if it touches no instance state
- `CS8618` — enable nullable reference types, or guarantee initialisation

## Package references

A dependency problem shows in the NuGet and project references;
a code problem in types, namespaces and access modifiers.

## File naming

```
Domain/
  Entities/          {Name}.cs
  ValueObjects/      {Name}.cs
  Services/          {Name}Service.cs
  Events/            {Name}Event.cs

Application/
  Commands/          {Action}{Entity}Command.cs
  Queries/           Get{Entity}Query.cs
  Handlers/          {Command/Query}Handler.cs
  DTOs/              {Name}Dto.cs

Infrastructure/
  Repositories/      {Entity}Repository.cs
  Services/          {External}Service.cs

Presentation/
  ViewModels/        {View}ViewModel.cs
  Views/             {Name}View.xaml
```

## Feature-cut layout

```
src/
  Features/
    Invoices/
      IssueInvoice.cs      endpoint mapping, request record, handler
      VoidInvoice.cs
      GetInvoice.cs
    Payments/
      RecordPayment.cs
  Shared/
    Persistence/BillingDbContext.cs
    Pipeline/RequestLogging.cs
```

The shape follows the one 株式会社一創 draws for C# (Sources in `SKILL.md`):
one file per feature, the endpoint mapping,
the request record and the handler together,
so a change to the feature touches one file,
and whether a change's files stay under `Features/` is the measure of whether the cut is right.
`Shared/` holds the persistence context and the pipeline,
the two things every slice passes through;
anything else placed there takes `slice-first`'s scrutiny.
Cross-cutting has one home per solution:
the mediator pipeline when requests go through a mediator,
ASP.NET Core middleware or an endpoint filter when handlers are called directly.
Never both, and never a line at the top of each handler.
Which of the two layouts a solution uses is `slice-first`'s call;
both are spelled here so that either answer has a shape.

## Further reading

- `csharp-architecture.md` — the layers in detail, project structure,
  dependency injection, cross-cutting concerns
- `csharp-patterns.md` — implementation patterns for DDD, CQRS, MVVM, TDD,
  repositories, unit of work, results
- `csharp-examples.md` — a complete feature, layer by layer, with tests
