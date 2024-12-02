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
        ('\\"LATIN CAPITAL LETTER MIDDLE-WELSH LL"', 'STRIDENT'),
        ('\\16$1EFA', 'STRESC'),
        ('7.3E-6p', 'FLOAT_LITERAL'),
        ('(3.1415)', 'FLOAT_LITERAL'),
    ],
)
def test_expr_tokens(expr: str, expected_type: str) -> None:
    """Check the expression syntax."""
    parser = create_parser('test_expr')

    result = parser.parse(expr)

    assert result is not None
    assert result.data == 'test_expr'
    assert result.children[0].type == 'DOC'
    assert (
        result.children[1].type == expected_type
    ), f'Expected {expected_type} but found {result.pretty()}'


@pytest.mark.parametrize(
    ('expr', 'expected_type'),
    [
        ('foo', 'ref'),
        ('foo_bar', 'ref'),
        ('δx_π', 'ref'),
        ('\\∇', 'ref'),
        ('it', 'ref'),
        ('\\and', 'ref'),
        ('"X `y` Z"', 'string_interpolation'),
        ('(x: 1)', 'named_tuple'),
        ('(x: 1,)', 'named_tuple'),
        ('(x: 1, y: 2)', 'named_tuple'),
        ('(x: 1, y: 2,)', 'named_tuple'),
        ('()', 'nil'),
        ('(1,)', 'tuple_expr'),
        ('(1, 2)', 'tuple_expr'),
        ('(1, 2,)', 'tuple_expr'),
        ('[]', 'list_expr'),
        ('[1]', 'list_expr'),
        ('[1,]', 'list_expr'),
        ('[1,2]', 'list_expr'),
        ('{}', 'set_expr'),
        ('{1}', 'set_expr'),
        ('{1,}', 'set_expr'),
        ('{1,2}', 'set_expr'),
        ('{:}', 'map_expr'),
        ('{1: 2}', 'map_expr'),
        ('{1: 2,}', 'map_expr'),
        ('{1: 2, 3: 4}', 'map_expr'),
        ('x.y', 'subscript'),
        ('x.y.z', 'subscript'),
        ('.σ', 'field_accessor_function'),
        ('10\'m', 'quantity_expr'),
        ('9.81\'(m/s^2)', 'quantity_expr'),
    ],
)
def test_expr_tokens(expr: str, expected_type: str) -> None:
    """Check the expression syntax."""
    parser = create_parser('test_expr')

    result = parser.parse(expr)

    assert result is not None
    assert result.data == 'test_expr'
    assert result.children[0].type == 'DOC'
    assert (
        result.children[1].data == expected_type
    ), f'Expected {expected_type} but found {result.pretty()}'
