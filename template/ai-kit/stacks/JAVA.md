# Java (Maven/Gradle)

Confirm the build tool and version (pom.xml, build.gradle(.kts), wrapper), language level, and configured checks before editing.
- Build through the Maven/Gradle wrapper (mvnw/gradlew) so CI and contributors share one toolchain; never edit generated build output.
- Keep packages cohesive and public APIs minimal; prefer composition and small interfaces over deep inheritance.
- Use Optional as a return type only, never as fields or parameters; use streams where they clarify and loops where they perform.
- Handle checked exceptions at boundaries, wrap with context, and preserve causes; validate arguments with Objects.requireNonNull and explicit messages.
- Manage resources with try-with-resources so streams and connections close deterministically.
- Use SLF4J (or the established logger) with secret redaction; no secrets in exceptions or logs.
- Test with the configured JUnit 5/Mockito stack, covering error paths and concurrency; keep tests hermetic, repeatable, and free of real data.
- Run the wrapper's test/verify plus the project's format/static analysis; keep plugin and dependency versions pinned and review upgrades.

Sources: [Maven guides](https://maven.apache.org/guides/), [Gradle user manual](https://docs.gradle.org/current/userguide/userguide.html), [Java SE documentation](https://docs.oracle.com/en/java/javase/).
