# .NET

Confirm target frameworks (global.json, *.csproj/*.fsproj), solution layout, and configured checks before editing.
- Respect nullable reference types and the project's existing warning policy; do not silence nullable or analyzer warnings without a documented reason.
- Use async/await for I/O end to end and propagate CancellationToken; avoid sync-over-async (Task.Result, .Wait) and unbounded parallelism.
- Manage IDisposable/IAsyncDisposable with using/await using so handles and connections close deterministically.
- Throw typed exceptions, preserve inner exceptions, and validate arguments at public boundaries (ArgumentNullException.ThrowIfNull and explicit messages).
- Prefer records and LINQ where they clarify intent; keep hot paths allocation-conscious without premature optimization.
- Use ILogger with structured properties and secret redaction; no secrets in exceptions or log output.
- Test with the configured xUnit/NUnit/MSTest setup, covering async and error paths; use WebApplicationFactory/TestServer for HTTP contracts.
- Run dotnet build/test plus the project's format and analyzer commands; pin SDKs with global.json when the repository does and review dependency upgrades.

Sources: [C# language reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/), [nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references), [.NET CLI](https://learn.microsoft.com/en-us/dotnet/core/tools/).
