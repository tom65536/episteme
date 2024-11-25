"""Test cases for the parser."""

import pathlib

import pytest

from episteme.parser import create_parser


@pytest.fixture
def epi_script() -> str:
    """Load the script file ``epi_script.epic``.

    Returns
    -------
    str
        the loaded source
    """
    return (pathlib.Path(__file__).parent / 'epi_script.epic').read_text(
        encoding='utf-8',
    )


def test_parser(epi_script: str) -> None:
    """Check whether the given script gets parsed without errors.

    Parameter
    ---------
    epi_script ; str
        the script to be parsed
    """
    parser = create_parser()

    result = parser.parse(epi_script)

    assert result is not None


def test_atom() -> None:
    """Check the atoms syntax."""
    parser = create_parser()

    result = parser.parse('1')

    assert result is not None
