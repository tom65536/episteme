"""Parser module."""

from collections.abc import Iterator

import regex
from lark import Lark
from lark.indenter import Indenter
from lark.lark import PostLex
from lark.lexer import Token

__all__ = [
    'DocExtractor',
    'PostLexChain',
    'create_parser',
]


def create_parser(start: str = 'start') -> Lark:
    """Create a parser for the EPISTEME language.

    Parameter
    --------
    start : str
        start symbol (Default ``start``)

    Returns
    -------
    Lark
        generated cluster
    """
    indenter = EpistemeIndenter()
    doc_extractor = DocExtractor()
    pipeline = PostLexChain(indenter, doc_extractor)
    return Lark.open_from_package(
        'episteme',
        'core.lark',
        ('grammar',),
        debug=True,
        g_regex_flags=regex.VERSION1,
        postlex=pipeline,
        regex=True,
        start=start,
        strict=True,
    )


class DocExtractor(PostLex):
    """Inject documentation before the next definition.

    All comments immediately preceding a definition without
    a blank line in between are considered documentation.

    Attributes
    ----------
    def_tokens : list[str]
        list of token types denoting a definition in the source code
    neutral_tokens: list[str]
        list of token not modifying the state
    new_line : str
        token type indicating tokens with line break
    doc_token : str
        token type of the token to be generated
    comment_strip : str
        regular expression denoting the begin of a comment line
    comment_skip : str
        regular expression denoting comments to be skipped, e.g. shebang

    """

    def_tokens: list[str] = ['DEF']
    neutral_tokens: list[str] = ['_INDENT', '_DEDENT']
    new_line: str = '_NEWLINE'
    doc_token: str = 'DOC'
    comment_strip: str = '^\\s*[#\uFE5F\uFF03]'
    comment_skip: str = '^\\s*[#\uFE5F\uFF03]!'

    def __init__(self) -> None:
        self._acc: str = ''
        self._mod: bool = True
        self._comment_strip: regex.Pattern = regex.compile(self.comment_strip)
        self._comment_skip: regex.Pattern = regex.compile(self.comment_skip)

    def process(self, stream: Iterator[Token]) -> Iterator[Token]:
        """Process the tokens of a stream.

        Parameter
        ---------
        stream : Iterator[Token]
            stream of tokens to be processed

        Yields
        ------
        Token
            processed tokens
        """
        self._acc = ''
        self._mod = True
        self._comment_strip = regex.compile(self.comment_strip)
        self._comment_skip = regex.compile(self.comment_skip)
        return self._process(stream)

    def _process(self, stream: Iterator[Token]) -> Iterator[Token]:
        for token in stream:
            if token.type == self.new_line:
                yield from self._handle_nl(token)
            elif token.type in self.def_tokens:
                yield from self._emit_doc(token)
            elif token.type not in self.neutral_tokens:
                yield from self._ditch(token)
            yield token

    def _handle_nl(self, nl: Token) -> Iterator[Token]:
        for line in nl.splitlines(keepends=True):
            mtch = self._comment_skip.match(line)
            if mtch:
                continue

            mtch = self._comment_strip.match(line)
            if mtch:
                last = mtch.end()
                self._acc += line[last:]
            elif '\n' in line:
                yield from self._ditch(nl)

    def _ditch(self, token: Token) -> Iterator[Token]:
        if self._mod:
            yield from self._emit_doc(token)
        self._mod = False
        self._acc = ''

    def _emit_doc(self, token: Token) -> Iterator[Token]:
        yield Token.new_borrow_pos(
            self.doc_token,
            self._acc,
            token,
        )
        self._acc = ''
        self._mod = False


class EpistemeIndenter(Indenter):
    """A postlexer that "injects" _INDENT/_DEDENT tokens.

    The indenter is based on indentation, according to the Python syntax.

    See also: the ``postlex`` option in `Lark`.
    """

    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['(', '[', '{', 'STRING_LEFT']
    CLOSE_PAREN_types = [')', ']', '}', 'STRING_RIGHT']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8


class PostLexChain(PostLex):
    """Chain of post-lexers.

    Parameter
    ---------
    pl : PostLex
        post-lexer to be added to the chain
    """

    def __init__(self, *pl: PostLex) -> None:
        self._pl = reversed(pl)

    def process(self, stream: Iterator[Token]) -> Iterator[Token]:
        """Process the tokens of a stream.

        Applies the chin of post-lexers to each token
        by folding each post-lexer into the previous one.

        Parameter
        ---------
        stream : Iterator[Token]
            stream of tokens to be processed

        Yields
        ------
        Token
            processed tokens
        """
        result = stream
        for post_lex in self._pl:
            result = post_lex.process(result)
        return result
