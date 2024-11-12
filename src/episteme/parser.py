"""Parser module."""

from lark import Lark


def create_parser() -> Lark:
    """Create a parser for the EPISTEME language.

    Returns
    -------
    Lark
        generated cluster
    """
    return Lark.open_from_package(
        'episteme',
        'core.lark',
        ('grammar',),
        strict=True,
    )
