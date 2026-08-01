# Implementation Patterns

## DDD Patterns

### Entity Base Class

```csharp
public abstract class Entity<TId> : IEquatable<Entity<TId>>
    where TId : notnull
{
    public TId Id { get; protected set; } = default!;

    public override bool Equals(object? obj)
        => obj is Entity<TId> entity && Id.Equals(entity.Id);

    public bool Equals(Entity<TId>? other)
        => other is not null && Id.Equals(other.Id);

    public override int GetHashCode() => Id.GetHashCode();

    public static bool operator ==(Entity<TId>? left, Entity<TId>? right)
        => Equals(left, right);

    public static bool operator !=(Entity<TId>? left, Entity<TId>? right)
        => !Equals(left, right);
}
```

### Value Object Base Class

```csharp
public abstract class ValueObject : IEquatable<ValueObject>
{
    protected abstract IEnumerable<object?> GetEqualityComponents();

    public override bool Equals(object? obj)
        => obj is ValueObject other && Equals(other);

    public bool Equals(ValueObject? other)
    {
        if (other is null) return false;
        return GetEqualityComponents()
            .SequenceEqual(other.GetEqualityComponents());
    }

    public override int GetHashCode()
    {
        return GetEqualityComponents()
            .Aggregate(0, (hash, component) =>
                HashCode.Combine(hash, component?.GetHashCode() ?? 0));
    }

    public static bool operator ==(ValueObject? left, ValueObject? right)
        => Equals(left, right);

    public static bool operator !=(ValueObject? left, ValueObject? right)
        => !Equals(left, right);
}
```

### Aggregate Root

```csharp
public abstract class AggregateRoot<TId> : Entity<TId>
    where TId : notnull
{
    private readonly List<IDomainEvent> _domainEvents = [];

    public IReadOnlyCollection<IDomainEvent> DomainEvents
        => _domainEvents.AsReadOnly();

    protected void AddDomainEvent(IDomainEvent domainEvent)
        => _domainEvents.Add(domainEvent);

    public void ClearDomainEvents() => _domainEvents.Clear();
}
```

### Domain Event

```csharp
public interface IDomainEvent
{
    DateTime OccurredOn { get; }
}

public abstract record DomainEvent : IDomainEvent
{
    public DateTime OccurredOn { get; } = DateTime.UtcNow;
}

// Example
public record OrderCreatedEvent(Guid OrderId, Guid UserId) : DomainEvent;
```

### Specification Pattern

```csharp
public abstract class Specification<T>
{
    public abstract Expression<Func<T, bool>> ToExpression();

    public bool IsSatisfiedBy(T entity)
        => ToExpression().Compile()(entity);

    public Specification<T> And(Specification<T> other)
        => new AndSpecification<T>(this, other);

    public Specification<T> Or(Specification<T> other)
        => new OrSpecification<T>(this, other);

    public Specification<T> Not()
        => new NotSpecification<T>(this);
}

// Example
public class ActiveUserSpecification : Specification<User>
{
    public override Expression<Func<User, bool>> ToExpression()
        => user => user.IsActive && !user.IsDeleted;
}
```

## CQRS Patterns

### Command

```csharp
// Command with no result
public record DeleteUserCommand(Guid UserId) : IRequest;

// Command with result
public record CreateOrderCommand(
    Guid UserId,
    List<OrderItemDto> Items
) : IRequest<Guid>;
```

### Query

```csharp
public record GetUserByIdQuery(Guid UserId) : IRequest<UserDto?>;

public record GetOrdersQuery(
    Guid? UserId = null,
    DateTime? FromDate = null,
    int PageNumber = 1,
    int PageSize = 10
) : IRequest<PagedResult<OrderDto>>;
```

### Handler

```csharp
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, Guid>
{
    private readonly IOrderRepository _orderRepository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateOrderHandler(
        IOrderRepository orderRepository,
        IUnitOfWork unitOfWork)
    {
        _orderRepository = orderRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<Guid> Handle(
        CreateOrderCommand request,
        CancellationToken cancellationToken)
    {
        var order = Order.Create(request.UserId, request.Items);

        await _orderRepository.AddAsync(order, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return order.Id;
    }
}
```

### Pipeline Behavior (Validation)

```csharp
public class ValidationBehavior<TRequest, TResponse>
    : IPipelineBehavior<TRequest, TResponse>
    where TRequest : notnull
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        => _validators = validators;

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        if (!_validators.Any()) return await next();

        var context = new ValidationContext<TRequest>(request);

        var failures = (await Task.WhenAll(
            _validators.Select(v => v.ValidateAsync(context, cancellationToken))))
            .SelectMany(r => r.Errors)
            .Where(f => f is not null)
            .ToList();

        if (failures.Count != 0)
            throw new ValidationException(failures);

        return await next();
    }
}
```

## MVVM Patterns

### ViewModel Base

```csharp
public abstract class ViewModelBase : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    protected virtual void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));

    protected bool SetProperty<T>(
        ref T field,
        T value,
        [CallerMemberName] string? name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value))
            return false;

        field = value;
        OnPropertyChanged(name);
        return true;
    }
}
```

### Relay Command

```csharp
public class RelayCommand : ICommand
{
    private readonly Action<object?> _execute;
    private readonly Func<object?, bool>? _canExecute;

    public RelayCommand(Action<object?> execute, Func<object?, bool>? canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke(parameter) ?? true;

    public void Execute(object? parameter) => _execute(parameter);

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}

public class RelayCommand<T> : ICommand
{
    private readonly Action<T?> _execute;
    private readonly Func<T?, bool>? _canExecute;

    public RelayCommand(Action<T?> execute, Func<T?, bool>? canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke((T?)parameter) ?? true;

    public void Execute(object? parameter) => _execute((T?)parameter);

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

### Async Relay Command

```csharp
public class AsyncRelayCommand : ICommand
{
    private readonly Func<object?, Task> _execute;
    private readonly Func<object?, bool>? _canExecute;
    private bool _isExecuting;

    public AsyncRelayCommand(
        Func<object?, Task> execute,
        Func<object?, bool>? canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter)
        => !_isExecuting && (_canExecute?.Invoke(parameter) ?? true);

    public async void Execute(object? parameter)
    {
        if (_isExecuting) return;

        _isExecuting = true;
        RaiseCanExecuteChanged();

        try
        {
            await _execute(parameter);
        }
        finally
        {
            _isExecuting = false;
            RaiseCanExecuteChanged();
        }
    }

    public void RaiseCanExecuteChanged()
        => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

### ViewModel ↔ View communication

| Mechanism | Kind | Mainly for | VM→View | View→VM | Typical | Watch for |
|------|------|----------|---------|---------|--------|--------|
| **INotifyPropertyChanged** | Interface | Notifying one property changed, so a binding updates | Yes, as state | — | Text, IsEnabled, Visible | Wrong fit for commands such as Close or ShowDialog |
| **INotifyCollectionChanged** (ObservableCollection) | Interface / implementation | Add, remove and reorder in a collection | Yes, Items updates | — | ListBox Items, DataGrid Rows | A change *within* an element usually needs INPC on the element too |
| **ICommand** | Interface | Where an action starts — a button | Partly, through CanExecute | Yes | Button Command, MenuItem Command | Async work and exceptions are tedious to hand-roll |
| **ReactiveCommand** | Class (ReactiveUI) | ICommand with async, exceptions and a state stream | Yes — IsExecuting and friends make state easy to surface | Yes | `SaveCommand = ReactiveCommand.CreateFromTask(...)` | Commits you to ReactiveUI, and it has to be learned |
| **Interaction** (ReactiveUI and others) | Class / pattern | Asking the View to do something — dialog, picker, close | Yes, as a command | — (can return a value) | Confirm dialog, OpenFile, notification | Needs a handler registered on the View; used freely, the flow scatters |
| **MessageBus / Messenger** | Pattern | Loosely coupled events across views or view models | Yes | Yes | Announcing "saved" broadly, navigation requests | Becomes hard to trace. Do not reach for it first |
| **AttachedProperty** | Avalonia mechanism | Making a View-side capability bindable — focus, scroll | Yes; the View reacts to VM state | — | `IsFocused`, `ScrollToEnd` | Costly to implement, and invites UI coupling |
| **Behavior** (Interactivity) | Pattern | View event → command; lifting UI manipulation out | Both directions | Yes | EventTrigger → Command, moving focus | Adds a package dependency and is harder to debug |

**Choosing:**

- Keeping state in sync → `INotifyPropertyChanged` with `ObservableCollection`
- Accepting user action → `ICommand` when simple, `ReactiveCommand` when not
- Commanding the View from the VM → `Interaction`, or `MessageBus`
- Behaviour belonging to the View → `AttachedProperty` or `Behavior`

### Avalonia: the same, plus input validation

The rows above repeat here so validation can be compared against them in
one place.

| Mechanism | Kind | Mainly for | VM→View | View→VM | Typical | Watch for |
|------|------|----------|---------|---------|--------|--------|
| **INotifyPropertyChanged** | Interface | Property change, so a binding updates | Yes | — | Text, IsEnabled, Visible | Wrong fit for Close or ShowDialog |
| **INotifyCollectionChanged** (ObservableCollection) | Interface / implementation | Collection changes | Yes | — | ListBox Items, DataGrid Rows | A change within an element needs INPC on the element |
| **ICommand** | Interface | Running an action — a button | Partly, CanExecute | Yes | Button, MenuItem | Async, exceptions and re-entry are tedious to hand-roll |
| **ReactiveCommand** | Class (ReactiveUI) | ICommand with async, state and exceptions | Yes | Yes | Create, CreateFromTask | Commits you to ReactiveUI's way of doing things |
| **Interaction** (ReactiveUI and others) | Class / pattern | Asking the View for UI work — a dialog | Yes | — (can return a value) | Confirm, OpenFile, Close | Requires a View-side handler; scatters easily |
| **MessageBus / Messenger** | Pattern | Loosely coupled notification across views or VMs | Yes | Yes | "Saved", navigation requests | The receiving end is hard to find. Do not overuse |
| **AttachedProperty** | Avalonia mechanism | Making a UI capability bindable | Yes | — | Focus, scroll, selection | Costly, and invites UI coupling |
| **Behavior** (Interactivity) | Pattern | View event → command; separating UI manipulation | Both directions | Yes | EventTrigger → Command | Package dependency, harder to debug |
| **INotifyDataErrorInfo** | Interface | Validation, reported per property | Yes, through Errors | — | Showing an invalid TextBox | Some work to implement; async validation needs designing |
| **DataAnnotations** (`System.ComponentModel.DataAnnotations`) | Attributes plus a validation API | Declarative required / range / regex | Yes, once wired to INotifyDataErrorInfo | — | `[Required]`, `[Range]` | Attributes alone do not reach the UI — something has to bridge them |
| **ValidationRules** (Avalonia) | Mechanism | Validating a binding, including conversion | Yes, through Validation.Errors | Yes, input → validation | Validation on a `TextBox` binding | Rules drift toward the View, scattering validation outside the VM |
| **Exception-based validation** (thrown on convert or update) | Pattern | Rejecting a parse failure by throwing | Yes, surfaced as an error | Yes | A number that will not parse | Exceptions used as logic get hard to follow |

### Between the layers

| From → To | Purpose | Use | Data | Dependency | Example | Watch for |
|-----------|-----------|----------------------|----------|------------|-----|--------|
| **View → VM** | User action | **Command** (ICommand / ReactiveCommand) | Parameter or input DTO | View → VM | Save, Cancel, search | Keep logic out of the View |
| **View → VM** | Reflecting input | **TwoWay binding** with **INPC** | Primitive, or a VM-side model | View ↔ VM | TextBox.Text ↔ Name | Normalising input usually belongs in the VM |
| **View → VM** | Turning an event into a command | **Behavior / Trigger** | EventArgs → CommandParameter | View → VM | Commit on KeyDown | Overuse complicates the XAML |
| **VM → View** | State, so the display updates | **INotifyPropertyChanged** | State such as IsBusy | VM → View | Busy, progress, error text | Reduce it to *state* and notify that |
| **VM → View** | UI command such as a dialog | **Interaction** (preferred), or a RequestClose event | Request / response | VM → View | Confirm, picker, close | Keeps UI coupling out of the VM |
| **VM ↔ UseCase** | Running an application operation | **An async method call**, or **IObservable** | Input / output DTO | VM → UseCase | `await uc.Save(input)` | The VM absorbs UI-thread concerns |
| **UseCase → VM** | Returning a result or a failure | **A return value, `Result<T>`** — or an exception, by policy | Result or DTO | UseCase → VM | `Result<SaveOutput>` | Exceptions tend to be reserved for the unforeseen |
| **UseCase ↔ Domain** | Applying a domain rule | **A domain method call** | Entity or value object | UseCase → Domain | `order.Pay(...)` | The Domain knows nothing of UI or infrastructure |
| **Domain → UseCase** | A domain event | **Domain event, in memory** | Event object | Domain → (collected) | `OrderPaid` | Usually raised, collected, then handled by a use case |
| **UseCase ↔ Infra** | Persistence and external I/O | **A port** — repository, gateway | Domain object or DTO | UseCase → Port, implemented in Infra | `IOrderRepository` | Inverted: the use case commonly defines the interface |
| **Infra → UseCase/Domain** | Supplying the implementation | **Injected** | Implementation class | Infra → (injected only) | DB, HTTP, filesystem | Infrastructure never references a layer above it |
| **VM ↔ VM** | Between screens | **A navigator interface**, or **MessageBus** sparingly | Route or message | VM → (a dedicated interface, preferably) | Navigation, adding a tab | MessageBus overuse costs traceability |

### Where things go

| Layer | Responsibility |
|----|------|
| **View** | Appearance, and bridging events (Behavior, interaction handlers) |
| **VM** | UI state (INPC) and actions (Command). Calls the use case, turns the result into state |
| **UseCase** | The application's procedure — transactions, permissions, workflow, port calls |
| **Domain** | Business rules — entities, value objects, domain services, domain events |
| **Infra** | DB, HTTP, filesystem, OS, third-party libraries — repositories and the like |

### The shape each layer takes

| Layer | Shape |
|----|-------------|
| **View** | Holds interaction handlers and nothing else — dialog, picker, close |
| **VM** | ReactiveCommand (or ICommand) → `await UseCase.Execute()` → update state through INPC |
| **UseCase** | Drives the Domain through ports such as `IRepository`, returns `Result<T>` |
| **Domain** | Pure logic; exceptions reserved for broken invariants |
| **Infra** | Implements ports; failures become Infra exceptions, converted to a Result in the use case — consistently, one way or the other |

## TDD Patterns

### Abstracting hardware and the OS

| Dependency | Abstraction | Package | Substitute in tests | Typical use | Watch for |
|----------|--------|-------------------|-------------------|--------------|--------|
| **Current time** | `TimeProvider` | .NET 8+, built in | `FakeTimeProvider` | Date comparisons, expiry, timeouts | Before .NET 8, usually a hand-written `IClock` |
| **Current time** | `IClock` (NodaTime) | NodaTime | `FakeClock` | Date arithmetic, time zones | Powerful if you adopt NodaTime's model wholesale |
| **Scheduler** | `IScheduler` | System.Reactive | `TestScheduler` | Timer, Delay, Interval, async streams | `AdvanceTo` / `AdvanceBy` control time |
| **Filesystem** | `IFileSystem` | System.IO.Abstractions | `MockFileSystem` | Reading, writing, directories | An end-to-end test against a real filesystem is usually still needed |
| **Environment variables** | `IEnvironment` | Hand-written, or a library | Mock or fake | `GetEnvironmentVariable`, `MachineName` | No standard exists, so most define their own |
| **Console I/O** | `IConsole` | Hand-written, or Spectre.Console | `TestConsole` | CLI input and output, progress | Spectre.Console ships a TestConsole |
| **HTTP** | `IHttpClientFactory` | Microsoft.Extensions.Http | `MockHttpMessageHandler` | Calling an external API | Avoid constructing `HttpClient` directly |
| **Randomness** | `Random` with a fixed seed, or a hand-written `IRandom` | Built in, or hand-written | Fixed seed, or a mock | Generation, shuffling | .NET 6+ `Random.Shared` is hard to inject |
| **Guid generation** | `IGuidGenerator` | Hand-written | A fake returning a fixed value | Identifiers | No standard exists |
| **Date without time** | `DateOnly` / `TimeOnly` with `TimeProvider` | .NET 6+ | `FakeTimeProvider` | Date comparison, business-day arithmetic | Avoid reaching for `DateTime.Now` |
| **Clipboard** | `IClipboard` | TextCopy | `MockClipboard` | Copy and paste | Cross-platform, and DI-friendly |
| **Clipboard** | `IClipboard` (Avalonia) | Avalonia.Input.Platform | Needs your own wrapper | Copy and paste inside Avalonia | `NotClientImplementable` since 11.1.4 — cannot be mocked directly |
| **Clipboard** | `IClipboard` (MAUI) | Microsoft.Maui.ApplicationModel | Mock or fake | Copy and paste in MAUI | MAUI only |

### Designing an abstraction

| Principle | |
|------|------|
| **Keep the wrapper thin** | Only the methods you need. Resist growing it |
| **Avoid static calls** | `DateTime.Now`, `File.ReadAllText` and the like cannot be injected — wrap them |
| **Implementations go in Infra** | The production implementation, `RealFileSystem` and so on |
| **Fakes go in the test project** | `FakeTimeProvider` and friends, in the tests or a shared test utility |
| **End-to-end uses the real thing** | Fakes for unit tests; a real filesystem and real HTTP for integration and end-to-end |

### Platform-specific notes

**Avalonia `IClipboard` (11.1.4+)**

Marked `[NotClientImplementable]`, so user code may no longer implement it. It cannot be mocked directly in a test, which means defining your own wrapper:

```csharp
// Your own abstraction, declared in Application or Domain
public interface IClipboardService
{
    Task SetTextAsync(string? text);
    Task<string?> GetTextAsync();
}

// Production implementation, in Infra
public class AvaloniaClipboardService : IClipboardService
{
    private readonly IClipboard _clipboard;

    public AvaloniaClipboardService(TopLevel topLevel)
        => _clipboard = topLevel.Clipboard!;

    public Task SetTextAsync(string? text) => _clipboard.SetTextAsync(text);
    public Task<string?> GetTextAsync() => _clipboard.GetTextAsync();
}

// Fake, for tests
public class FakeClipboardService : IClipboardService
{
    public string? Text { get; private set; }
    public Task SetTextAsync(string? text) { Text = text; return Task.CompletedTask; }
    public Task<string?> GetTextAsync() => Task.FromResult(Text);
}
```

## Repository Pattern

### Interface

```csharp
public interface IRepository<T, TId>
    where T : AggregateRoot<TId>
    where TId : notnull
{
    Task<T?> GetByIdAsync(TId id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    void Update(T entity);
    void Remove(T entity);
}
```

### Implementation

```csharp
public class Repository<T, TId> : IRepository<T, TId>
    where T : AggregateRoot<TId>
    where TId : notnull
{
    protected readonly AppDbContext Context;
    protected readonly DbSet<T> DbSet;

    public Repository(AppDbContext context)
    {
        Context = context;
        DbSet = context.Set<T>();
    }

    public virtual async Task<T?> GetByIdAsync(TId id, CancellationToken ct = default)
        => await DbSet.FindAsync([id], ct);

    public virtual async Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default)
        => await DbSet.ToListAsync(ct);

    public virtual async Task AddAsync(T entity, CancellationToken ct = default)
        => await DbSet.AddAsync(entity, ct);

    public virtual void Update(T entity)
        => DbSet.Update(entity);

    public virtual void Remove(T entity)
        => DbSet.Remove(entity);
}
```

## Unit of Work Pattern

```csharp
public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}

public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _context;

    public UnitOfWork(AppDbContext context) => _context = context;

    public async Task<int> SaveChangesAsync(CancellationToken ct = default)
        => await _context.SaveChangesAsync(ct);
}
```

## Result Pattern

```csharp
public class Result
{
    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;
    public string Error { get; }

    protected Result(bool isSuccess, string error)
    {
        IsSuccess = isSuccess;
        Error = error;
    }

    public static Result Success() => new(true, string.Empty);
    public static Result Failure(string error) => new(false, error);
    public static Result<T> Success<T>(T value) => new(value, true, string.Empty);
    public static Result<T> Failure<T>(string error) => new(default!, false, error);
}

public class Result<T> : Result
{
    public T Value { get; }

    protected internal Result(T value, bool isSuccess, string error)
        : base(isSuccess, error)
    {
        Value = value;
    }
}
```
