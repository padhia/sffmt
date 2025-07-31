"""Unit tests for sffmt."""

import io
import logging
from pathlib import Path

import pytest

from sffmt import Payload, start


@pytest.fixture
def sample_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create two sample SQL files and an output directory."""
    file1 = tmp_path / "a.sql"
    file2 = tmp_path / "b.sql"
    file1.write_text("select 1")
    file2.write_text("select 2")
    outdir = tmp_path / "out"
    outdir.mkdir()
    return file1, file2, outdir


def test_stdin_to_stdout() -> None:
    assert Payload.of([]) == [Payload(None, None)]


def test_stdin_to_file(tmp_path: Path) -> None:
    target = tmp_path / "result.sql"
    assert Payload.of([], target) == [Payload(None, target)]


def test_stdin_to_dir_raises(sample_files: tuple[Path, Path, Path]) -> None:
    _, _, outdir = sample_files
    with pytest.raises(ValueError, match="output must be a file"):
        Payload.of([], outdir)


def test_single_file_to_stdout(sample_files: tuple[Path, Path, Path]) -> None:
    file1, _, _ = sample_files
    assert Payload.of([file1]) == [Payload(file1, None)]


def test_single_file_to_file(sample_files: tuple[Path, Path, Path], tmp_path: Path) -> None:
    file1, _, _ = sample_files
    target = tmp_path / "result.sql"
    assert Payload.of([file1], target) == [Payload(file1, target)]


def test_single_file_to_dir(sample_files: tuple[Path, Path, Path]) -> None:
    file1, _, outdir = sample_files
    assert Payload.of([file1], outdir) == [Payload(file1, outdir / file1.name)]


def test_multiple_files_to_stdout(sample_files: tuple[Path, Path, Path]) -> None:
    file1, file2, _ = sample_files
    assert Payload.of([file1, file2]) == [Payload(file1, None), Payload(file2, None)]


def test_multiple_files_to_existing_dir(sample_files: tuple[Path, Path, Path]) -> None:
    file1, file2, outdir = sample_files
    assert Payload.of([file1, file2], outdir) == [
        Payload(file1, outdir / file1.name),
        Payload(file2, outdir / file2.name),
    ]


def test_multiple_files_to_new_dir(sample_files: tuple[Path, Path, Path], tmp_path: Path) -> None:
    file1, file2, _ = sample_files
    new_dir = tmp_path / "new_out_dir"
    assert Payload.of([file1, file2], new_dir) == [
        Payload(file1, new_dir / file1.name),
        Payload(file2, new_dir / file2.name),
    ]


def test_multiple_files_to_file_raises(sample_files: tuple[Path, Path, Path], tmp_path: Path) -> None:
    file1, file2, _ = sample_files
    with pytest.raises(ValueError, match="output must be a directory"):
        Payload.of([file1, file2], file1)

    with pytest.raises(ValueError, match="output must be a directory"):
        Payload.of([file1, file2], tmp_path / "nonexistent.sql")


def test_in_place(sample_files: tuple[Path, Path, Path]) -> None:
    file1, file2, _ = sample_files
    assert Payload.of([file1, file2], in_place=True) == [
        Payload(file1, file1),
        Payload(file2, file2),
    ]


def test_in_place_conflicts(sample_files: tuple[Path, Path, Path]) -> None:
    file1, _, outdir = sample_files
    with pytest.raises(ValueError, match="cannot specify both --in-place and --output"):
        Payload.of([file1], outdir, in_place=True)

    with pytest.raises(ValueError, match="cannot use --in-place with stdin"):
        Payload.of([], in_place=True)


def test_payload_format_to_stdout(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("select a, b from tbl where x = 1; select 2;"))
    Payload(None, None).format()
    assert capsys.readouterr().out == "SELECT\n  a,\n  b\nFROM tbl\nWHERE\n  x = 1;\n\nSELECT\n  2;\n"


def test_payload_format_creates_parent_dirs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir" / "out.sql"
    monkeypatch.setattr("sys.stdin", io.StringIO("select 1"))
    Payload(None, target).format()
    assert target.read_text() == "SELECT\n  1;\n"


def test_payload_format_comment_only_does_not_emit_bare_semicolon(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("-- just a comment"))
    Payload(None, None).format()
    assert capsys.readouterr().out == "\n"


def test_start_in_place(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("select id from users")
    start([sql_file], in_place=True)
    assert sql_file.read_text() == "SELECT\n  id\nFROM users;\n"


def test_start_empty_input_logs_warning(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("   \n  "))
    with caplog.at_level(logging.WARNING, logger="sffmt"):
        start([])
    assert "no text was entered" in caplog.text


def test_start_invalid_sql_exits_cleanly(tmp_path: Path) -> None:
    sql_file = tmp_path / "bad.sql"
    sql_file.write_text("select * from (")
    with pytest.raises(SystemExit, match="failed to format"):
        start([sql_file])


def test_start_invalid_dialect_exits_cleanly(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("select 1")
    with pytest.raises(SystemExit, match="failed to format"):
        start([sql_file], read="invalid_dialect")
