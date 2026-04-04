---
name: prefer-make
description: Use before running any Go toolchain command (`go build`, `go test`, `go run`, `go vet`, `go fmt`, `golangci-lint`). Substitutes make targets when a Makefile is present.
user-invocable: true
---

# Build with Make

This project uses a Makefile. **Always prefer `make` targets over running `go` commands directly.**

## Rules

1. **Check the Makefile first** before running any `go build`, `go test`, `go run`, `go vet`, `go fmt`, or `golangci-lint` command. Look for a corresponding target.
2. **Use the Makefile target** instead of the raw `go` command. For example:
   - `make build` instead of `go build ./...`
   - `make test` instead of `go test ./...`
   - `make lint` instead of `golangci-lint run`
   - `make run` instead of `go run main.go`
   - `make fmt` instead of `go fmt ./...`
3. **Run `make help` to discover targets.** If that fails, read the Makefile directly.
4. **Fall back to raw `go` commands only** if no relevant Makefile target exists for the task.

## Verification procedure

1. Before executing, confirm the target exists by checking `make help` output or the Makefile.
2. After execution, verify the command exited with status 0 and produced expected output.

## Common mistakes to watch for

- **Assuming target names without checking.** Don't guess that `make unit-test` exists — read the Makefile. Target names vary across projects.
- **Adding flags to make targets that already set them.** For example, running `make test ARGS="-v -race"` when the Makefile already passes `-race`. Check what the target does before adding flags.
- **Running raw `go test ./specific/pkg/...` for a subset** when the Makefile has a target that accepts a package argument (e.g., `make test PKG=./specific/pkg/...`).
