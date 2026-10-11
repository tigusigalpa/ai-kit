# Rust

Confirm the toolchain (rust-toolchain.toml), workspace members, supported targets, and configured checks before editing.
- Follow ownership and borrowing: prefer references over cloning, add explicit lifetimes only where inference fails, and reach for Rc/Arc/RefCell for a diagnosed need, not by default.
- Keep `unsafe` behind a reviewed boundary: minimal blocks, a safety comment, and encapsulation behind a safe API; never add unsafe to silence the borrow checker.
- Use Result<T, E> for recoverable failures with meaningful errors (thiserror for libraries, anyhow for applications when already used); panic only on programmer errors, never on user input.
- Prefer exhaustive matches, iterators, and small focused functions; respect the edition and MSRV before adopting new syntax.
- Use structured logging (tracing/log) with secret redaction; keep secrets out of panics and error text.
- Write unit tests beside the code and integration tests under tests/; cover error paths and concurrency. Run cargo fmt, cargo clippy, and cargo test; deny warnings only when CI already does.
- Keep Cargo.lock for binaries and applications; review dependency additions (cargo audit where configured) and preserve rust-toolchain.toml and the workspace layout.

Example of an explicit error boundary:

~~~rust
return Err(BuildError::MissingManifest(path.display().to_string()));
~~~

Sources: [Cargo book](https://doc.rust-lang.org/cargo/), [Rust API guidelines](https://rust-lang.github.io/api-guidelines/), [Clippy](https://doc.rust-lang.org/clippy/).
