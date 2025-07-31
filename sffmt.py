"""Format SQL statements."""

import sys
from argparse import ArgumentParser, ArgumentTypeError
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Any, Self

from sqlglot import transpile  # type: ignore
from sqlglot.errors import SqlglotError  # type: ignore

__version__ = "0.1.0"
DEFAULT_DIALECT = "snowflake"
logger = getLogger("sffmt")


@dataclass(frozen=True)
class Payload:
    """Contains input and output payloads for processing."""

    input: Path | None
    output: Path | None

    def format(self, in_dialect: str = DEFAULT_DIALECT, out_dialect: str = DEFAULT_DIALECT) -> None:
        """Read SQL from input, format it, and write to output or stdout."""
        contents = (sys.stdin.read() if self.input is None else self.input.read_text()).strip()
        if not contents:
            logger.warning(f"'{self.input}' is empty" if self.input else "no text was entered")
            return

        statements = [f"{s};" for s in transpile(contents, read=in_dialect, write=out_dialect, pretty=True) if s and s.strip()]
        formatted_sql = "\n\n".join(statements)

        if self.output is not None:
            self.output.parent.mkdir(parents=True, exist_ok=True)
            self.output.write_text(f"{formatted_sql}\n")
        else:
            print(formatted_sql)

    @classmethod
    def of(
        cls,
        files: list[Path],
        output: Path | None = None,
        *,
        in_place: bool = False,
    ) -> list[Self]:
        """Resolve input files and output destination into Payload instances."""
        if in_place:
            if output is not None:
                raise ValueError("cannot specify both --in-place and --output")
            if not files:
                raise ValueError("cannot use --in-place with stdin")
            return [cls(f, f) for f in files]

        match files:
            case []:
                if output is not None and output.is_dir():
                    raise ValueError("output must be a file")
                return [cls(None, output)]
            case [single]:
                outf = output / single.name if (output is not None and output.is_dir()) else output
                return [cls(single, outf)]
            case _:
                if output is None:
                    return [cls(f, None) for f in files]
                if output.is_dir() or (not output.exists() and not output.suffix):
                    return [cls(f, output / f.name) for f in files]
                raise ValueError("output must be a directory")


def start(
    files: list[Path],
    output: Path | None = None,
    read: str = DEFAULT_DIALECT,
    write: str = DEFAULT_DIALECT,
    in_place: bool = False,
) -> None:
    """Script entry-point."""
    try:
        payloads = Payload.of(files, output, in_place=in_place)
    except ValueError as err:
        raise SystemExit(str(err)) from err

    for item in payloads:
        try:
            item.format(in_dialect=read, out_dialect=write)
        except (SqlglotError, ValueError, OSError) as err:
            source = f"'{item.input}'" if item.input else "stdin"
            raise SystemExit(f"failed to format {source}: {err}") from err


def getargs() -> dict[str, Any]:
    """Get run-time script arguments."""

    def existing_file(x: str) -> Path:
        if (p := Path(x)).is_file():
            return p
        raise ArgumentTypeError(f"{x} is not an existing file")

    parser = ArgumentParser(prog="sffmt", description="Format SQL statements", suggest_on_error=True)
    parser.add_argument("files", metavar="path", nargs="*", type=existing_file, help="SQL files; stdin if omitted")
    parser.add_argument("--read", metavar="dialect", default=DEFAULT_DIALECT, help=f"SQL dialect (default {DEFAULT_DIALECT})")
    parser.add_argument("--write", metavar="dialect", default=DEFAULT_DIALECT, help=f"SQL dialect (default {DEFAULT_DIALECT})")
    parser.add_argument("-o", "--output", metavar="path", type=Path, help="output file/dir")
    parser.add_argument("-i", "--in-place", action="store_true", help="format files in place")
    parser.add_argument("--version", action="version", version=__version__)

    return vars(parser.parse_args())


def main() -> None:
    """CLI entry-point."""
    start(**getargs())
