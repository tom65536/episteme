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


@pytest.mark.parametrize(
    ('expr', 'expected_type'),
    [
        ('1', 'DECIMAL_LITERAL'),
        ('123k', 'DECIMAL_LITERAL'),
        ('123_000', 'DECIMAL_LITERAL'),
        ('\u0CE8_000', 'DECIMAL_LITERAL'),
        ('16$C0FFEE', 'RADICAL_LITERAL'),
        ('foo', 'IDENTIFIER'),
        ('foo_bar', 'IDENTIFIER'),
        ('δx_π', 'IDENTIFIER'),
        ('\\∇', 'IDENTIFIER'),
        ('\\and', 'IDENTIFIER'),
        ('\\"LATIN CAPITAL LETTER MIDDLE-WELSH LL"', 'STRIDENT'),
        ('\\16$1EFA', 'STRESC'),
        ('7.3E-6p', 'FLOAT_LITERAL'),
    ],
)
def test_expr(expr: str, expected_type: str) -> None:
    """Check the expression syntax."""
    parser = create_parser('test_expr')

    result = parser.parse(expr)

    assert result is not None
    assert result.data == 'test_expr'
    assert result.children[0].type == 'DOC'
    assert result.children[1].type == expected_type, result.pretty()
