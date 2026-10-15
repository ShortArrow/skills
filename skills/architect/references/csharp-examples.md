# Implementation Examples

## Complete Feature: Order Management

An order-management feature worked through a pure core and the shell around it,
with CQRS, DDD, MVVM and TDD each in its place.
The core is records and the decider of `csharp.md` (The pure core);
`Result`, `Map` and `Bind` are the ones in `csharp-patterns.md`.

### Domain Layer

#### Value Objects

Each value object has one route in, and the route returns a `Result`.
Its members are get-only,
so a `with` expression cannot step past the check.

```csharp
// Domain/Orders/Quantity.cs
public sealed record Quantity
{
    public int Value { get; }
    private Quantity(int value) => Value = value;

    public static Result<Quantity> Create(int value) =>
        value > 0
            ? Result.Success(new Quantity(value))
            : Result.Failure<Quantity>("Quantity must be positive");

    public Quantity Plus(Quantity other) => new(checked(Value + other.Value));
}
```

```csharp
// Domain/Orders/Money.cs
public sealed record Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    private Money(decimal amount, string currency)
    {
        Amount = amount;
        Currency = currency;
    }

    public static Result<Money> Create(decimal amount, string currency = "JPY") =>
        amount < 0 ? Result.Failure<Money>("Amount cannot be negative")
        : string.IsNullOrWhiteSpace(currency) ? Result.Failure<Money>("Currency is required")
        : Result.Success(new Money(amount, currency.ToUpperInvariant()));

    public static Money Zero(string currency = "JPY") => new(0, currency.ToUpperInvariant());

    public Money Times(Quantity quantity) => new(Amount * quantity.Value, Currency);

    public Money Plus(Money other) =>
        Currency == other.Currency
            ? new(Amount + other.Amount, Currency)
            : throw new ArgumentException($"Cannot add {other.Currency} to {Currency}", nameof(other));
}
```

`Plus` throws rather than returning a failure because mixing currencies inside an order is not an outcome a caller handles:
the decider below refuses a line in a second currency,
so reaching `Plus` with two is a broken precondition (`design-by-contract`).

```csharp
// Domain/Orders/Address.cs
public sealed record Address
{
    public string Street { get; }
    public string City { get; }
    public string PostalCode { get; }
    public string Country { get; }

    private Address(string street, string city, string postalCode, string country)
    {
        Street = street;
        City = city;
        PostalCode = postalCode;
        Country = country;
    }

    public static Result<Address> Create(string street, string city, string postalCode, string country) =>
        string.IsNullOrWhiteSpace(street) ? Result.Failure<Address>("Street is required")
        : string.IsNullOrWhiteSpace(city) ? Result.Failure<Address>("City is required")
        : Result.Success(new Address(street, city, postalCode, country));
}
```

#### The order as data

```csharp
// Domain/Orders/Order.cs
public enum OrderStatus { Pending, Confirmed, Shipped, Delivered, Cancelled }

public sealed record OrderLine(Guid ProductId, string ProductName, Quantity Quantity, Money UnitPrice)
{
    public Money Total => UnitPrice.Times(Quantity);
}

public abstract record OrderState;

public sealed record NoOrder : OrderState;

public sealed record Order(
    Guid Id,
    Guid UserId,
    Address ShippingAddress,
    OrderStatus Status,
    DateTimeOffset CreatedAt,
    ImmutableList<OrderLine> Lines) : OrderState
{
    public Money Total =>
        Lines.IsEmpty
            ? Money.Zero()
            : Lines.Skip(1).Aggregate(Lines[0].Total, (sum, line) => sum.Plus(line.Total));
}
```

`NoOrder` is the state before the first command,
so creating an order is a transition like any other and not a constructor with rules of its own.
A record compares an `ImmutableList<T>` member by reference,
so two orders with equal lines are not `Equals`;
a test compares the lines with `Assert.Equal` on the lists, as below.

#### Commands, events and the decider

```csharp
// Domain/Orders/OrderCommands.cs
public abstract record OrderCommand;
public sealed record PlaceOrder(Guid OrderId, Guid UserId, Address ShippingAddress, DateTimeOffset At) : OrderCommand;
public sealed record AddLine(Guid ProductId, string ProductName, Quantity Quantity, Money UnitPrice) : OrderCommand;
public sealed record ConfirmOrder : OrderCommand;
public sealed record ShipOrder : OrderCommand;
public sealed record CancelOrder : OrderCommand;

// Domain/Orders/OrderEvents.cs
public abstract record OrderEvent;
public sealed record OrderPlaced(Guid OrderId, Guid UserId, Address ShippingAddress, DateTimeOffset At) : OrderEvent;
public sealed record LineAdded(Guid ProductId, string ProductName, Quantity Quantity, Money UnitPrice) : OrderEvent;
public sealed record OrderConfirmed : OrderEvent;
public sealed record OrderShipped : OrderEvent;
public sealed record OrderCancelled : OrderEvent;
```

The new id and the current time are in `PlaceOrder`:
the shell made them, and the decider only copies them.

```csharp
// Domain/Orders/OrderDecider.cs
public static class OrderDecider
{
    public static readonly OrderState Initial = new NoOrder();

    public static Result<IReadOnlyList<OrderEvent>> Decide(OrderCommand command, OrderState state) =>
        (command, state) switch
        {
            (PlaceOrder c, NoOrder) => Happened(new OrderPlaced(c.OrderId, c.UserId, c.ShippingAddress, c.At)),
            (PlaceOrder, Order) => Refused("Order already exists"),
            (_, NoOrder) => Refused("No such order"),

            (AddLine, Order { Status: not OrderStatus.Pending }) => Refused("Cannot modify non-pending order"),
            (AddLine c, Order o) when o.Lines.Any(l => l.UnitPrice.Currency != c.UnitPrice.Currency)
                => Refused("Cannot mix currencies in one order"),
            (AddLine c, Order) => Happened(new LineAdded(c.ProductId, c.ProductName, c.Quantity, c.UnitPrice)),

            (ConfirmOrder, Order { Status: not OrderStatus.Pending }) => Refused("Only pending orders can be confirmed"),
            (ConfirmOrder, Order { Lines.IsEmpty: true }) => Refused("Cannot confirm empty order"),
            (ConfirmOrder, Order) => Happened(new OrderConfirmed()),

            (ShipOrder, Order { Status: OrderStatus.Confirmed }) => Happened(new OrderShipped()),
            (ShipOrder, Order) => Refused("Only confirmed orders can be shipped"),

            (CancelOrder, Order { Status: OrderStatus.Shipped or OrderStatus.Delivered })
                => Refused("Cannot cancel shipped or delivered order"),
            (CancelOrder, Order { Status: OrderStatus.Cancelled }) => Refused("Order is already cancelled"),
            (CancelOrder, Order) => Happened(new OrderCancelled()),

            _ => throw new UnreachableException()
        };

    public static OrderState Evolve(OrderState state, OrderEvent @event) => (state, @event) switch
    {
        (NoOrder, OrderPlaced e) => new Order(e.OrderId, e.UserId, e.ShippingAddress, OrderStatus.Pending, e.At, []),
        (Order o, LineAdded e) => o with { Lines = Merge(o.Lines, e) },
        (Order o, OrderConfirmed) => o with { Status = OrderStatus.Confirmed },
        (Order o, OrderShipped) => o with { Status = OrderStatus.Shipped },
        (Order o, OrderCancelled) => o with { Status = OrderStatus.Cancelled },
        _ => throw new UnreachableException()
    };

    public static Result<(OrderState State, ImmutableList<OrderEvent> Events)> Run(
        OrderState state, IEnumerable<OrderCommand> commands) =>
        commands.Aggregate(
            Result.Success((State: state, Events: ImmutableList<OrderEvent>.Empty)),
            (sofar, command) => sofar.Bind(s => Decide(command, s.State).Map(events =>
                (events.Aggregate(s.State, Evolve), s.Events.AddRange(events)))));

    private static ImmutableList<OrderLine> Merge(ImmutableList<OrderLine> lines, LineAdded e) =>
        lines.FindIndex(l => l.ProductId == e.ProductId) is var i and >= 0
            ? lines.SetItem(i, lines[i] with { Quantity = lines[i].Quantity.Plus(e.Quantity) })
            : lines.Add(new OrderLine(e.ProductId, e.ProductName, e.Quantity, e.UnitPrice));

    private static Result<IReadOnlyList<OrderEvent>> Happened(OrderEvent e) =>
        Result.Success<IReadOnlyList<OrderEvent>>([e]);

    private static Result<IReadOnlyList<OrderEvent>> Refused(string reason) =>
        Result.Failure<IReadOnlyList<OrderEvent>>(reason);
}
```

The rows of `Decide` are `state-first`'s table:
each command against each state it can meet,
the first matching row wins,
and a refusal is a value the caller has to take apart.
`Run` folds several commands through `Decide` and `Evolve` and stops at the first refusal,
so a request that places an order and adds its lines either produces every event or none.

#### Ports

```csharp
// Domain/Orders/IOrderStore.cs
public interface IOrderStore
{
    Task<OrderState> Load(Guid orderId, CancellationToken ct);
    Task Save(Order order, CancellationToken ct);
}

// Domain/Products/IProductCatalog.cs
public sealed record ProductInfo(Guid Id, string Name, decimal Price);

public interface IProductCatalog
{
    Task<ProductInfo?> Find(Guid productId, CancellationToken ct);
}
```

The shell holds these; nothing in `OrderDecider` takes one.

### Application Layer

#### Requests and DTOs

```csharp
// Application/Orders/Requests.cs
public sealed record CreateOrderItem(Guid ProductId, int Quantity);

public sealed record CreateOrderRequest(
    Guid UserId,
    string Street,
    string City,
    string PostalCode,
    string Country,
    IReadOnlyList<CreateOrderItem> Items);

public sealed record ConfirmOrderRequest(Guid OrderId);

public sealed record GetOrderByIdRequest(Guid OrderId);

// Application/Orders/OrderDto.cs
public sealed record OrderItemDto(Guid ProductId, string ProductName, int Quantity, decimal UnitPrice);

public sealed record OrderDto(
    Guid Id,
    Guid UserId,
    string Status,
    decimal TotalAmount,
    DateTimeOffset CreatedAt,
    IReadOnlyList<OrderItemDto> Items)
{
    public static OrderDto From(Order order) => new(
        order.Id,
        order.UserId,
        order.Status.ToString(),
        order.Total.Amount,
        order.CreatedAt,
        order.Lines.Select(l => new OrderItemDto(l.ProductId, l.ProductName, l.Quantity.Value, l.UnitPrice.Amount)).ToList());
}
```

#### Format check

```csharp
// Application/Orders/CreateOrderRequestValidator.cs
public sealed class CreateOrderRequestValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderRequestValidator()
    {
        RuleFor(x => x.UserId).NotEmpty();
        RuleFor(x => x.Street).MaximumLength(200);
        RuleFor(x => x.City).MaximumLength(100);
        RuleFor(x => x.Items).NotEmpty();
        RuleForEach(x => x.Items).ChildRules(item => item.RuleFor(x => x.ProductId).NotEmpty());
    }
}
```

The validator checks the shape of the request: identifiers present,
strings within their column widths, a list that is not empty.
A positive quantity and a non-blank street are the value objects' rules,
and they are not repeated here (`SKILL.md`, Two checks, two places).

#### Handlers: the shell

```csharp
// Application/Orders/CreateOrderHandler.cs
public sealed class CreateOrderHandler(
    IOrderStore store,
    IProductCatalog catalog,
    TimeProvider time,
    ILogger<CreateOrderHandler> logger)
{
    public async Task<Result<Guid>> Handle(CreateOrderRequest request, CancellationToken ct)
    {
        var address = Address.Create(request.Street, request.City, request.PostalCode, request.Country);
        if (address.IsFailure) return Result.Failure<Guid>(address.Error);

        var orderId = Guid.NewGuid();
        var commands = new List<OrderCommand> { new PlaceOrder(orderId, request.UserId, address.Value, time.GetUtcNow()) };

        foreach (var item in request.Items)
        {
            var product = await catalog.Find(item.ProductId, ct);
            if (product is null) return Result.Failure<Guid>($"Product {item.ProductId} was not found");

            var line = Quantity.Create(item.Quantity).Bind(quantity =>
                Money.Create(product.Price).Map(price =>
                    (OrderCommand)new AddLine(product.Id, product.Name, quantity, price)));
            if (line.IsFailure) return Result.Failure<Guid>(line.Error);
            commands.Add(line.Value);
        }

        var run = OrderDecider.Run(OrderDecider.Initial, commands);
        if (run.IsFailure) return Result.Failure<Guid>(run.Error);

        await store.Save((Order)run.Value.State, ct);
        logger.LogInformation("Order {OrderId} created with {Count} events", orderId, run.Value.Events.Count);
        return Result.Success(orderId);
    }
}
```

```csharp
// Application/Orders/ConfirmOrderHandler.cs
public sealed class ConfirmOrderHandler(IOrderStore store)
{
    public async Task<Result> Handle(ConfirmOrderRequest request, CancellationToken ct)
    {
        var state = await store.Load(request.OrderId, ct);
        var run = OrderDecider.Run(state, [new ConfirmOrder()]);
        if (run.IsFailure) return Result.Failure(run.Error);

        await store.Save((Order)run.Value.State, ct);
        return Result.Success();
    }
}
```

```csharp
// Application/Orders/GetOrderByIdHandler.cs
public sealed class GetOrderByIdHandler(IOrderStore store)
{
    public async Task<OrderDto?> Handle(GetOrderByIdRequest request, CancellationToken ct) =>
        await store.Load(request.OrderId, ct) is Order order ? OrderDto.From(order) : null;
}
```

Every handler has the same three steps: read what the decision needs,
decide in the core, write what was decided.
The clock is read once, in `CreateOrderHandler`,
and passed in as a value; the id is made there too.
The handlers are called directly;
put them behind a mediator only when its pipeline earns it (`csharp.md`, Mediator dispatch).

### Infrastructure Layer

The adapter converts between the domain's records and the rows the database holds,
so the domain carries no EF Core attribute and no parameterless constructor.

```csharp
// Infrastructure/Persistence/OrderRows.cs
public sealed class OrderRow
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string Street { get; set; } = "";
    public string City { get; set; } = "";
    public string PostalCode { get; set; } = "";
    public string Country { get; set; } = "";
    public string Status { get; set; } = "";
    public DateTimeOffset CreatedAt { get; set; }
    public List<OrderLineRow> Lines { get; set; } = [];
}

public sealed class OrderLineRow
{
    public Guid OrderId { get; set; }
    public Guid ProductId { get; set; }
    public string ProductName { get; set; } = "";
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public string Currency { get; set; } = "";
}

// Infrastructure/Persistence/AppDbContext.cs
public sealed class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<OrderRow> Orders => Set<OrderRow>();

    protected override void OnModelCreating(ModelBuilder model)
    {
        model.Entity<OrderRow>().HasKey(o => o.Id);
        model.Entity<OrderRow>().HasMany(o => o.Lines).WithOne().HasForeignKey(l => l.OrderId);
        model.Entity<OrderLineRow>().HasKey(l => new { l.OrderId, l.ProductId });
    }
}
```

```csharp
// Infrastructure/Persistence/EfOrderStore.cs
public sealed class EfOrderStore(AppDbContext db) : IOrderStore
{
    public async Task<OrderState> Load(Guid orderId, CancellationToken ct) =>
        await db.Orders.AsNoTracking().Include(o => o.Lines).FirstOrDefaultAsync(o => o.Id == orderId, ct)
            is { } row ? ToDomain(row) : OrderDecider.Initial;

    public async Task Save(Order order, CancellationToken ct)
    {
        var next = ToRow(order);
        var row = await db.Orders.Include(o => o.Lines).FirstOrDefaultAsync(o => o.Id == order.Id, ct);
        if (row is null) db.Orders.Add(next);
        else Sync(row, next);
        await db.SaveChangesAsync(ct);
    }

    private static void Sync(OrderRow row, OrderRow next)
    {
        row.Status = next.Status;
        row.Lines.RemoveAll(l => next.Lines.TrueForAll(n => n.ProductId != l.ProductId));
        foreach (var n in next.Lines)
        {
            var line = row.Lines.Find(l => l.ProductId == n.ProductId);
            if (line is null) row.Lines.Add(n);
            else line.Quantity = n.Quantity;
        }
    }

    private static OrderRow ToRow(Order order) => new()
    {
        Id = order.Id,
        UserId = order.UserId,
        Street = order.ShippingAddress.Street,
        City = order.ShippingAddress.City,
        PostalCode = order.ShippingAddress.PostalCode,
        Country = order.ShippingAddress.Country,
        Status = order.Status.ToString(),
        CreatedAt = order.CreatedAt,
        Lines = order.Lines.Select(l => new OrderLineRow
        {
            OrderId = order.Id,
            ProductId = l.ProductId,
            ProductName = l.ProductName,
            Quantity = l.Quantity.Value,
            UnitPrice = l.UnitPrice.Amount,
            Currency = l.UnitPrice.Currency,
        }).ToList(),
    };

    private static Order ToDomain(OrderRow row) => new(
        row.Id,
        row.UserId,
        Stored(Address.Create(row.Street, row.City, row.PostalCode, row.Country)),
        Enum.Parse<OrderStatus>(row.Status),
        row.CreatedAt,
        row.Lines.Select(l => new OrderLine(
            l.ProductId,
            l.ProductName,
            Stored(Quantity.Create(l.Quantity)),
            Stored(Money.Create(l.UnitPrice, l.Currency)))).ToImmutableList());

    private static T Stored<T>(Result<T> result) =>
        result.IsSuccess ? result.Value : throw new InvalidDataException($"Stored order is invalid: {result.Error}");
}
```

A row read back goes through the same `Create` as a request,
and a failure there is a corrupted store, not a user's mistake,
so it throws instead of returning.

### Presentation Layer (MVVM)

```csharp
// Presentation/ViewModels/OrderViewModel.cs
public sealed class OrderViewModel : ViewModelBase
{
    private readonly GetOrderByIdHandler _getOrder;
    private readonly ConfirmOrderHandler _confirmOrder;
    private OrderDto? _order;
    private string? _error;
    private bool _isLoading;

    public OrderViewModel(GetOrderByIdHandler getOrder, ConfirmOrderHandler confirmOrder)
    {
        _getOrder = getOrder;
        _confirmOrder = confirmOrder;
        LoadOrderCommand = new AsyncRelayCommand(_ => LoadOrderAsync());
        ConfirmOrderCommand = new AsyncRelayCommand(_ => ConfirmOrderAsync(), _ => CanConfirm);
    }

    public Guid OrderId { get; set; }

    public OrderDto? Order
    {
        get => _order;
        private set => SetProperty(ref _order, value);
    }

    public string? Error
    {
        get => _error;
        private set => SetProperty(ref _error, value);
    }

    public bool IsLoading
    {
        get => _isLoading;
        private set => SetProperty(ref _isLoading, value);
    }

    public bool CanConfirm => Order?.Status == nameof(OrderStatus.Pending);

    public ICommand LoadOrderCommand { get; }
    public ICommand ConfirmOrderCommand { get; }

    private async Task LoadOrderAsync()
    {
        IsLoading = true;
        try
        {
            Order = await _getOrder.Handle(new GetOrderByIdRequest(OrderId), CancellationToken.None);
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task ConfirmOrderAsync()
    {
        var result = await _confirmOrder.Handle(new ConfirmOrderRequest(OrderId), CancellationToken.None);
        Error = result.IsFailure ? result.Error : null;
        await LoadOrderAsync();
    }
}
```

A refusal reaches the view as text in `Error`,
not as an exception through `async void`.

### Test Examples (TDD)

The decider's tests are given events, when a command,
then events or a refusal.
No fake and no mock appears in them.

```csharp
// Domain.Tests/Orders/OrderDeciderTests.cs
public class OrderDeciderTests
{
    private static readonly Guid OrderId = Guid.NewGuid();
    private static readonly Guid ProductId = Guid.NewGuid();
    private static readonly DateTimeOffset At = new(2026, 10, 15, 9, 0, 0, TimeSpan.Zero);
    private static readonly Address Tokyo = Address.Create("1-1 Chiyoda", "Tokyo", "100-0001", "Japan").Value;

    private static readonly OrderEvent Placed = new OrderPlaced(OrderId, Guid.NewGuid(), Tokyo, At);
    private static readonly OrderEvent OneLine = Line(ProductId, 1, 1000m, "JPY");

    private static OrderEvent Line(Guid productId, int quantity, decimal price, string currency) =>
        new LineAdded(productId, "Product", Quantity.Create(quantity).Value, Money.Create(price, currency).Value);

    private static OrderState Given(params OrderEvent[] history) =>
        history.Aggregate(OrderDecider.Initial, OrderDecider.Evolve);

    public static TheoryData<OrderEvent[], OrderCommand, string> Refusals => new()
    {
        { [], new ConfirmOrder(), "No such order" },
        { [Placed], new ConfirmOrder(), "Cannot confirm empty order" },
        { [Placed, OneLine, new OrderConfirmed()], new ConfirmOrder(), "Only pending orders can be confirmed" },
        { [Placed], new ShipOrder(), "Only confirmed orders can be shipped" },
        { [Placed, OneLine, new OrderConfirmed(), new OrderShipped()], new CancelOrder(), "Cannot cancel shipped or delivered order" },
        { [Placed, new OrderCancelled()], new CancelOrder(), "Order is already cancelled" },
        { [Placed, OneLine], new AddLine(Guid.NewGuid(), "Other", Quantity.Create(1).Value, Money.Create(5m, "USD").Value), "Cannot mix currencies in one order" },
    };

    [Theory]
    [MemberData(nameof(Refusals))]
    public void A_command_the_state_does_not_allow_is_refused(OrderEvent[] history, OrderCommand command, string reason)
    {
        var decided = OrderDecider.Decide(command, Given(history));

        Assert.True(decided.IsFailure);
        Assert.Equal(reason, decided.Error);
    }

    [Fact]
    public void Placing_an_order_starts_it_pending_and_empty()
    {
        var command = new PlaceOrder(OrderId, Guid.NewGuid(), Tokyo, At);

        var run = OrderDecider.Run(OrderDecider.Initial, [command]);

        var order = Assert.IsType<Order>(run.Value.State);
        Assert.Equal(OrderStatus.Pending, order.Status);
        Assert.Equal(At, order.CreatedAt);
        Assert.Empty(order.Lines);
    }

    [Fact]
    public void A_shipped_order_comes_from_its_events()
    {
        var order = Assert.IsType<Order>(Given(Placed, OneLine, new OrderConfirmed(), new OrderShipped()));

        Assert.Equal(OrderStatus.Shipped, order.Status);
    }

    [Property]
    public bool Lines_for_one_product_merge_and_the_total_is_their_sum(PositiveInt[] quantities, PositiveInt price)
    {
        var lines = quantities.Select(q => Line(ProductId, q.Get % 1000 + 1, price.Get, "JPY"));
        var order = (Order)Given([Placed, .. lines]);

        var expected = quantities.Sum(q => q.Get % 1000 + 1);
        return quantities.Length == 0
            ? order.Lines.IsEmpty && order.Total.Amount == 0
            : order.Lines.Count == 1
              && order.Lines[0].Quantity.Value == expected
              && order.Total.Amount == (decimal)expected * price.Get;
    }
}
```

The handler is shell, so its test hands it in-memory fakes and a `FakeTimeProvider`,
and checks what was saved.

```csharp
// Application.Tests/Orders/CreateOrderHandlerTests.cs
public class CreateOrderHandlerTests
{
    private sealed class InMemoryOrderStore : IOrderStore
    {
        public Dictionary<Guid, Order> Saved { get; } = [];

        public Task<OrderState> Load(Guid orderId, CancellationToken ct) =>
            Task.FromResult<OrderState>(Saved.TryGetValue(orderId, out var order) ? order : OrderDecider.Initial);

        public Task Save(Order order, CancellationToken ct)
        {
            Saved[order.Id] = order;
            return Task.CompletedTask;
        }
    }

    private sealed class InMemoryCatalog(params ProductInfo[] products) : IProductCatalog
    {
        public Task<ProductInfo?> Find(Guid productId, CancellationToken ct) =>
            Task.FromResult(products.FirstOrDefault(p => p.Id == productId));
    }

    private static readonly ProductInfo Pen = new(Guid.NewGuid(), "Pen", 120m);
    private readonly InMemoryOrderStore _store = new();
    private readonly FakeTimeProvider _time = new(new DateTimeOffset(2026, 10, 15, 9, 0, 0, TimeSpan.Zero));

    private CreateOrderHandler Handler() =>
        new(_store, new InMemoryCatalog(Pen), _time, NullLogger<CreateOrderHandler>.Instance);

    private static CreateOrderRequest Request(Guid productId, int quantity) =>
        new(Guid.NewGuid(), "1-1 Chiyoda", "Tokyo", "100-0001", "Japan", [new CreateOrderItem(productId, quantity)]);

    [Fact]
    public async Task A_valid_request_saves_a_pending_order_stamped_with_the_clock()
    {
        var result = await Handler().Handle(Request(Pen.Id, 3), CancellationToken.None);

        var order = _store.Saved[result.Value];
        Assert.Equal(OrderStatus.Pending, order.Status);
        Assert.Equal(_time.GetUtcNow(), order.CreatedAt);
        Assert.Equal(360m, order.Total.Amount);
    }

    [Fact]
    public async Task An_unknown_product_saves_nothing()
    {
        var result = await Handler().Handle(Request(Guid.NewGuid(), 1), CancellationToken.None);

        Assert.True(result.IsFailure);
        Assert.Empty(_store.Saved);
    }

    [Fact]
    public async Task A_quantity_the_value_object_refuses_saves_nothing()
    {
        var result = await Handler().Handle(Request(Pen.Id, 0), CancellationToken.None);

        Assert.Equal("Quantity must be positive", result.Error);
        Assert.Empty(_store.Saved);
    }
}
```

The integration test runs the adapter against a real database,
here SQLite in memory,
and checks that what was saved comes back as the same order.

```csharp
// Infrastructure.Tests/Persistence/EfOrderStoreTests.cs
public sealed class EfOrderStoreTests : IDisposable
{
    private readonly SqliteConnection _connection = new("DataSource=:memory:");

    public EfOrderStoreTests() => _connection.Open();

    public void Dispose() => _connection.Dispose();

    private AppDbContext Context()
    {
        var db = new AppDbContext(new DbContextOptionsBuilder<AppDbContext>().UseSqlite(_connection).Options);
        db.Database.EnsureCreated();
        return db;
    }

    [Fact]
    public async Task An_order_saved_twice_reads_back_as_its_last_state()
    {
        var address = Address.Create("1-1 Chiyoda", "Tokyo", "100-0001", "Japan").Value;
        var at = new DateTimeOffset(2026, 10, 15, 9, 0, 0, TimeSpan.Zero);
        var created = OrderDecider.Run(OrderDecider.Initial,
        [
            new PlaceOrder(Guid.NewGuid(), Guid.NewGuid(), address, at),
            new AddLine(Guid.NewGuid(), "Pen", Quantity.Create(2).Value, Money.Create(120m).Value),
        ]);
        var order = (Order)created.Value.State;
        await new EfOrderStore(Context()).Save(order, CancellationToken.None);

        var confirmed = (Order)OrderDecider.Run(order, [new ConfirmOrder()]).Value.State;
        await new EfOrderStore(Context()).Save(confirmed, CancellationToken.None);

        var loaded = Assert.IsType<Order>(await new EfOrderStore(Context()).Load(order.Id, CancellationToken.None));
        Assert.Equal(confirmed with { Lines = [] }, loaded with { Lines = [] });
        Assert.Equal(confirmed.Lines, loaded.Lines);
    }
}
```
