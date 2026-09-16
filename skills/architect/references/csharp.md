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

## Further reading

- `csharp-architecture.md` — the layers in detail, project structure,
  dependency injection, cross-cutting concerns
- `csharp-patterns.md` — implementation patterns for DDD, CQRS, MVVM, TDD,
  repositories, unit of work, results
- `csharp-examples.md` — a complete feature, layer by layer, with tests
