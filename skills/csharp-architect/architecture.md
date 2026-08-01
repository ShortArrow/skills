# Architecture Reference

## Layer Details

### Domain Layer

The innermost layer, and the core of the business logic.

**Depends on** nothing. Plain C# only.

**Holds:**
- Entities
- Value Objects
- Domain Services
- Domain Events
- Repository Interfaces
- Specifications

```csharp
// The Domain layer must not contain
// - framework coupling (EF Core attributes and the like)
// - infrastructure (HttpClient, file I/O)
// - presentation (ViewModels)
```

### Application Layer

Implements the use cases, orchestrating the Domain.

**Depends on** the Domain layer only.

**Holds:**
- Commands / Queries (CQRS)
- Handlers
- DTOs
- Application Services
- Validators
- Mappers

```csharp
// The Application layer is responsible for
// + implementing use cases
// + transaction control
// + authorisation checks
// - business rules — those belong to the Domain
// - infrastructure detail
```

### Infrastructure Layer

Implements everything that reaches outside the process.

**Depends on** the Domain and Application layers.

**Holds:**
- Repository implementations
- External service implementations
- Database Context
- Message queue implementations
- File system access

```csharp
// Infrastructure supplies
// + implementations of the repository interfaces
// + external API clients
// + database access
// - business logic
```

### Presentation Layer

The user interface, under MVVM.

**Depends on** the Application layer.

**Holds:**
- Views (XAML/Razor)
- ViewModels
- Converters
- Behaviors

```csharp
// Presentation is responsible for
// + UI logic
// + input validation at the UI level
// + navigation
// - business logic
// - data access
```

## Project Structure

```
Solution/
├── src/
│   ├── Domain/
│   │   ├── Entities/
│   │   ├── ValueObjects/
│   │   ├── Services/
│   │   ├── Events/
│   │   ├── Repositories/          # interfaces only
│   │   └── Specifications/
│   │
│   ├── Application/
│   │   ├── Commands/
│   │   ├── Queries/
│   │   ├── Handlers/
│   │   ├── DTOs/
│   │   ├── Validators/
│   │   ├── Mappers/
│   │   └── Interfaces/            # application service interfaces
│   │
│   ├── Infrastructure/
│   │   ├── Persistence/
│   │   │   ├── DbContext.cs
│   │   │   ├── Configurations/    # EF Core configurations
│   │   │   └── Repositories/      # repository implementations
│   │   ├── Services/              # external service implementations
│   │   └── DependencyInjection.cs
│   │
│   └── Presentation/
│       ├── ViewModels/
│       ├── Views/
│       ├── Converters/
│       └── App.xaml
│
└── tests/
    ├── Domain.Tests/
    ├── Application.Tests/
    ├── Infrastructure.Tests/
    └── Presentation.Tests/
```

## Dependency Injection Setup

```csharp
// Infrastructure/DependencyInjection.cs
public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // DbContext
        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlServer(configuration.GetConnectionString("Default")));

        // Repositories
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IOrderRepository, OrderRepository>();

        // External Services
        services.AddHttpClient<IPaymentService, PaymentService>();

        return services;
    }
}

// Application/DependencyInjection.cs
public static class DependencyInjection
{
    public static IServiceCollection AddApplication(
        this IServiceCollection services)
    {
        // MediatR (CQRS)
        services.AddMediatR(cfg =>
            cfg.RegisterServicesFromAssembly(Assembly.GetExecutingAssembly()));

        // Validators
        services.AddValidatorsFromAssembly(Assembly.GetExecutingAssembly());

        return services;
    }
}
```

## Cross-Cutting Concerns

### Logging

```csharp
// ILogger is used from the Application layer
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, Guid>
{
    private readonly ILogger<CreateOrderHandler> _logger;

    public async Task<Guid> Handle(CreateOrderCommand request, CancellationToken ct)
    {
        _logger.LogInformation("Creating order for user {UserId}", request.UserId);
        // ...
    }
}
```

### Validation

```csharp
// FluentValidation, in the Application layer
public class CreateOrderCommandValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderCommandValidator()
    {
        RuleFor(x => x.UserId).NotEmpty();
        RuleFor(x => x.Items).NotEmpty();
        RuleForEach(x => x.Items).ChildRules(item =>
        {
            item.RuleFor(x => x.ProductId).NotEmpty();
            item.RuleFor(x => x.Quantity).GreaterThan(0);
        });
    }
}
```

### Exception Handling

```csharp
// Domain Exceptions
public class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}

public class EntityNotFoundException : DomainException
{
    public EntityNotFoundException(string entity, object id)
        : base($"{entity} with id '{id}' was not found.") { }
}

// Caught and handled in the Application layer
```
