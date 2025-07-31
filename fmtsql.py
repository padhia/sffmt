"format SQL statements"

import sys
from argparse import ArgumentParser, ArgumentTypeError
from dataclasses import dataclass
from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import Any, Self

from sqlglot import transpile  # type: ignore

__version__ = "0.1.0"
DEFAULT_DIALECT = "snowflake"
logger = getLogger("fmtsql")


@dataclass(frozen=True)
class Payload:
    """Contains input and output payloads for processing"""

    input: Path | None
    output: Path | None

    @cached_property
    def conents(self) -> str:
        return (sys.stdin.read() if self.input is None else self.input.read_text()).strip()

    @classmethod
    def of(cls: type[Self], files: list[Path], output: Path | None = None) -> list[Self] | str:
        if len(files) == 0:
            if output is not None and output.is_dir():
                return "output must be a file"
            return [cls(None, output)]

        if len(files) == 1:
            outf = None if output is None else output / files[0].name if output.is_dir() else output
            return [cls(f, outf) for f in files]

        if output is None:
            return [cls(f, None) for f in files]
        if output.is_dir():
            return [cls(f, output / f.name) for f in files]

        return "output must be a directory"


def format(sql: str, outf: Path | None = None, read: str = DEFAULT_DIALECT, write: str = DEFAULT_DIALECT):
    formatted_sql = "\n\n".join(x + ";" for x in transpile(sql, read=read, write=write, pretty=True))

    if outf is not None:
        with outf.open("w") as f:
            print(formatted_sql, file=f)
    else:
        print(formatted_sql)


def start(files: list[Path], output: Path | None, read: str = DEFAULT_DIALECT, write: str = DEFAULT_DIALECT) -> None:
    "script entry-point"

    payload = Payload.of(files, output)
    if isinstance(payload, str):
        raise SystemExit(payload)

    for x in payload:
        if x.conents != "":
            format(x.conents, x.output, read, write)
        else:
            logger.warning(f"'{x.input}' is empty" if x.input else "no text was entered")


def getargs() -> dict[str, Any]:
    "get run-time script arguments"

    def existing_file(x: str) -> Path:
        if (p := Path(x)).is_file():
            return p
        raise ArgumentTypeError(f"{x} is not an existing file")

    parser = ArgumentParser()
    parser.add_argument("files", metavar="path", nargs="*", type=existing_file, help="SQL files; stdin if omitted")
    parser.add_argument("--read", metavar="dialect", default=DEFAULT_DIALECT, help=f"SQL dialect  (default {DEFAULT_DIALECT})")
    parser.add_argument("--write", metavar="dialect", default=DEFAULT_DIALECT, help=f"SQL dialect  (default {DEFAULT_DIALECT})")
    parser.add_argument("-o", "--output", metavar="path", type=Path, help="output file/dir")
    parser.add_argument("--version", action="version", version=__version__)

    return vars(parser.parse_args())


def main():
    "cli entry-point"
    start(**getargs())
