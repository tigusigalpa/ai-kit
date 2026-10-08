# Go: apply only to a confirmed Go project

- Check the version in `go.mod`, package structure, and API conventions. Preserve package boundaries and simple interfaces where they provide value.
- Propagate `context.Context` through I/O calls, honoring cancellation and timeouts. Return errors with useful context and check them with `errors.Is/As` when this is part of the contract.
- For concurrent code, check data ownership, goroutine termination, races, and locking. Use the race detector for affected scenarios when the environment supports it.
- Preserve `gofmt` formatting; run targeted tests, followed by `go test ./...` when appropriate for project size. Take additional checks from CI.
- For storage changes, apply the shared migrations section in `../ENGINEERING.md`; do not assume a particular ORM or database.
