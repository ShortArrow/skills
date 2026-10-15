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

## Two checks, two places

The format check is the adapter's,
and it ends in primitives or a failure:

```csharp
// Infrastructure: does the text parse
public static Result<int> ParseBaudRate(string raw) =>
    int.TryParse(raw, NumberStyles.None, CultureInfo.InvariantCulture, out var n)
        ? Result.Success(n)
        : Result.Failure<int>($"baud rate '{raw}' is not a number");
```

The invariant is the value object's, and its factory is the only way in:

```csharp
// Domain: may this value exist
public sealed record BaudRate
{
    private static readonly int[] Supported = [9600, 19200, 38400, 57600, 115200];
    public int Value { get; }
    private BaudRate(int value) => Value = value;

    public static Result<BaudRate> Create(int value) =>
        Supported.Contains(value)
            ? Result.Success(new BaudRate(value))
            : Result.Failure<BaudRate>($"{value} is not a supported baud rate");
}
```

The adapter chains the two and posts one message,
`ConfigLoaded` or `ConfigFailed`;
the update never sees a string where a `BaudRate` belongs.
A `with` expression sets an `init` member without passing the factory,
so a value object's members are get-only, as above.
A mediator's `ValidationBehavior` (below) holds format checks on the request;
an invariant placed there is a second home for a rule the domain already holds.

## The loop on a channel

The body's loop, for a tool that talks to instruments, ports and files.
A message is a record in one closed hierarchy per slice,
and the state is an immutable record:

```csharp
public abstract record Msg;

public abstract record ScpiMsg : Msg;
public sealed record SendClicked(string Command) : ScpiMsg;
public sealed record ResponseArrived(string Line, DateTimeOffset At) : ScpiMsg;
public sealed record TimeoutOccurred(string Command) : ScpiMsg;

public abstract record ConfigMsg : Msg;
public sealed record ConfigLoaded(Profile Profile) : ConfigMsg;
public sealed record ConfigFailed(string Path, string Reason) : ConfigMsg;

public sealed record Model(Profile? Profile, ScpiState Scpi, LoggerState Logger);
```

The update is a static function with no injected services,
so a test is a table of state, message and expected result:

```csharp
public abstract record Cmd;
public sealed record SendLine(string Line, TimeSpan Timeout) : Cmd;
public sealed record AppendSamples(IReadOnlyList<TelemetrySample> Samples) : Cmd;

public static class Update
{
    public static (Model, IReadOnlyList<Cmd>) Apply(Model model, Msg msg) => msg switch
    {
        ScpiMsg m   => ScpiUpdate.Apply(model, m),
        ConfigMsg m => ConfigUpdate.Apply(model, m),
        LoggerMsg m => LoggerUpdate.Apply(model, m),
        _ => (model, [])
    };
}
```

One `Channel<Msg>` with a single reader is the queue.
The reader applies the update,
publishes the new model and hands each command to the interpreter,
which is the only code that calls an outbound port:

```csharp
var queue = Channel.CreateUnbounded<Msg>(new() { SingleReader = true });

await foreach (var msg in queue.Reader.ReadAllAsync(ct))
{
    (model, var cmds) = Update.Apply(model, msg);
    models.OnNext(model);
    foreach (var cmd in cmds) interpreter.Run(cmd, queue.Writer);
}
```

`Run` starts the effect and returns;
the effect posts its outcome (`ResponseArrived`, `TimeoutOccurred`, `CsvExportCompleted`) to the same writer.
Nothing awaits an effect inside the loop,
so a slow port never stalls the next keypress.

| Piece | Spelled as | Sits in |
|---|---|---|
| Subscription for a port | a `BackgroundService` whose receive loop posts messages to the writer | Infrastructure |
| Subscription for a file | `FileSystemWatcher`, debounced, posting `ConfigChanged`; the loader reads and validates before `ConfigLoaded` is posted | Infrastructure |
| Send side | an `IHardwareSender` whose implementation owns a bounded `Channel<Frame>` and one worker that keeps order and paces the rate | port in Domain or Application, worker in Infrastructure |
| Log writer | an `ITelemetryLogWriter` over a bounded `Channel<LogBatch>`, flushed to disk by its own worker; a full channel is a state the update hears about, not a silent drop | port in Domain or Application, writer in Infrastructure |
| File formats | `TomlConfigLoader`, `CsvScenarioParser` and the CSV writer convert to and from domain values; the domain has no `[TomlProperty]` and no column index | Infrastructure |
| The view | binds to the published model (`IObservable<Model>` observed on the UI thread, `ObserveOn(AvaloniaScheduler.Instance)` or `Dispatcher.UIThread.Post`) and posts a message per user action | Presentation |

The receive side and the send side of one instrument are two classes even when they share a `SerialPort`:
the receive task runs for the life of the connection,
the send worker for the life of the queue,
and a fault in one is a message about the other,
not an exception through it.

In a feature-cut layout each slice holds its messages,
its part of the update and its view; the channel, the reader,
the root dispatch and the interpreter are the one shared piece.

Where the loop replaces the mediator,
a handler is the slice's update and its command interpreter together;
the two are not both used for one request.

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
