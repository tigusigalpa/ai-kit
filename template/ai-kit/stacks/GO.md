# Go

Confirm go.mod/toolchain, module boundaries, supported platforms, vendoring, and actual CI before editing.
- Keep package boundaries simple; expose small interfaces at consumers. Do not force a speculative internal/pkg layout.
- Propagate context.Context through I/O. Honor cancellation in handlers/workers; use configured http.Client and server timeouts, close response bodies, and bound payloads.
- Wrap errors with %w when callers must inspect the cause; use errors.Is/As and keep errors actionable. Document nil/zero-value behavior for public types.
- Make goroutine ownership/termination explicit. Use structured cancellation (such as errgroup when already appropriate), bounded concurrency, and clear synchronization.
- Use log/slog or the established logger with structured fields and secret redaction.
- Use table-driven tests and httptest for HTTP contracts; cover cancellation, timeout, race-sensitive scenarios, and errors.
- Run gofmt, targeted tests, go test ./..., and go vet as appropriate; use the project's staticcheck/golangci-lint configuration. New CI should include supported -race scenarios and govulncheck.
- Preserve go.mod/go.sum and deliberate vendor/modules.txt. Review go mod tidy diffs; do not add unrelated dependency churn.

Example preserving a cause:

~~~go
return fmt.Errorf("load account: %w", err)
~~~

Sources: [HTTP client](https://pkg.go.dev/net/http#Client), [Go security](https://go.dev/doc/security/best-practices), [module reference](https://go.dev/doc/modules/gomod-ref).
