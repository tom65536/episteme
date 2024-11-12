

from episteme.parser import create_parser


def test_parser() -> None:

    parser = create_parser()
    ast = parser.parse(""" x y z """)
