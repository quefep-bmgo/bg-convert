from bgconvert import __version__
from bgconvert.cli import build_parser


def test_version_is_available() -> None:
    assert __version__


def test_parser_has_a_program_name() -> None:
    assert build_parser().prog == "bgconvert"
