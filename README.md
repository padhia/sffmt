# sffmt

Format and transpile SQL statements from the command line. `sffmt` is a lightweight CLI wrapper around [sqlglot](https://github.com/tobymao/sqlglot), defaulting to the `snowflake` dialect.

## Features

- Pretty-print one or more SQL statements from `stdin` or files.
- Format files in place (`-i` / `--in-place`) or write formatted output to a file or directory (`-o` / `--output`).
- Transpile between any SQL dialects supported by `sqlglot` using `--read` and `--write`.

## Installation

### Using `uv` or `pip`

```bash
# Run or install globally as a CLI tool with uv
uv tool install git+https://github.com/padhia/sffmt

# Or install with pip
pip install git+https://github.com/padhia/sffmt
```

### Using Nix

```bash
# Run directly without installing
nix run github:padhia/sffmt -- --help

# Or install into your profile
nix profile install github:padhia/sffmt
```

You can also use the provided flake overlay (`overlays.default`) in your own Nix configuration, which adds `pkgs.sffmt` and `pkgs.python3Packages.sffmt`.

## Usage

```text
usage: sffmt [-h] [--read dialect] [--write dialect] [-o path] [-i] [--version] [path ...]

Format SQL statements

positional arguments:
  path                SQL files; stdin if omitted

options:
  -h, --help          show this help message and exit
  --read dialect      SQL dialect (default snowflake)
  --write dialect     SQL dialect (default snowflake)
  -o, --output path   output file/dir
  -i, --in-place      format files in place
  --version           show program's version number and exit
```

### Examples

**Format SQL from `stdin` to `stdout`:**

```bash
echo "select a, b from my_table where id = 1" | sffmt
```

```sql
SELECT
  a,
  b
FROM my_table
WHERE
  id = 1;
```

**Format one or more files in place:**

```bash
sffmt -i query.sql
sffmt --in-place queries/*.sql
```

**Format a file and write to a specific output file:**

```bash
sffmt query.sql -o formatted/query.sql
```

**Format multiple files into an output directory:**

```bash
sffmt a.sql b.sql -o formatted_queries/
```

**Transpile between SQL dialects (e.g., PostgreSQL to Snowflake):**

```bash
sffmt --read postgres --write snowflake input.sql -o output.sql
```

## Development

### Environment Setup

#### With Nix (Recommended)

Entering the Nix development shell automatically creates `./.venv`, links the Nix-provided dependencies (`sqlglot`, `setuptools`), and installs `sffmt` in editable mode:

```bash
nix develop
```

If you use `direnv`, run `direnv allow` to activate the environment automatically.

#### With `uv`

If you aren't using Nix, you can manage the virtual environment with `uv` (requires Python $\ge 3.14$):

```bash
uv sync
```

### Running Tests

Run the unit test suite using `pytest`:

```bash
pytest
```

### Linting & Formatting

Code style and import sorting are enforced with `ruff` (configured in `pyproject.toml`):

```bash
ruff check .
ruff format --check .
```

### Building

```bash
# Build Python sdist and wheel with uv
uv build

# Or build the Nix package
nix build
```

### Releasing

Pushing a version tag matching `v*` (e.g., `v0.1.0`) triggers the GitHub Actions workflow in `.github/workflows/release.yaml` to build distributions with `uv build` and publish a GitHub Release.
