"""Script to generate Unicode based character classes for Esteme parser."""

import unicodedata as ud
from collections.abc import Iterator

__all__ = []

ESCAPES = {
    '"': r'\"',
    "'": r"\'",
    '\\': r'\\',
    '\r': r'\r',
    '\n': r'\n',
    '\t': r'\t',
    '\v': r'\v',
}

# Run over all codepoints up to this limit
MAX_CP = 0x10FFFF

# Symbols not to be included otherwise
SYNTAX = '$,.;:#()[]}{\"\'!?`\\=@'

# Map non-terminals to pairs of Unicode classes and characters
# which should be included in their definitions.
CLASS_INFO = {
    'ID_START': (('L', 'Nl', 'Sc'), ''),
    'ID_MEDIAL': (('Pc',), '_'),
    'ID_CONT': (('L', 'Mn', 'Mc', 'Nl', 'Nd', 'Sc'), ''),
    'OPERATORS': (('Sm',), '+-*/<>^~|&%'),
    'SPACE': (('Zs',), '\t'),
    'DIGIT': (('Nd',), ''),
}

classes = {name: [] for name in CLASS_INFO.keys()}


def encode_list(lst: list[int]) -> str:
    """Encode a list of code points as pattern for Lark.

    Parameters
    ----------
    lst : list[int]
        list of code points

    Returns
    -------
    str
        the encoded pattern
    """
    return '\n    |'.join(encode_range(rg) for rg in compress_ranges(lst))


def compress_ranges(lst: list[int]) -> Iterator[range]:
    """Replace code points by ranges of codepoints.

    Parameters
    ----------
    lst : list[int]
        list of code points

    Yields
    ------
    range
        ranges of code points
    """
    prev = -2
    start = None

    for cp in lst:
        if cp - prev > 1:
            if start is not None:
                yield range(start, prev + 1)
            start = cp
        prev = cp
    if start is not None:
        yield range(start, prev + 1)


def encode_range(rg: range) -> str:
    """Encode a range of code points as pattern for Lark.

    Parameters
    ----------
    rg : range
        the range of code points

    Returns
    -------
    str
        the encoded pattern
    """
    if len(rg) == 1:
        return encode_code_point(rg.start)
    return encode_code_point(rg.start) + '..' + encode_code_point(rg.stop - 1)


def encode_code_point(cp: int) -> str:
    """Encode a single code point as pattern for Lark.

    Parameters
    ----------
    cp : int
        the code point

    Returns
    -------
    str
        the encoded pattern
    """
    ch = chr(cp)
    if ch in ESCAPES:
        return f'"{ESCAPES[ch]}"'
    gc = ud.category(ch)
    if gc.startswith('Z') or gc.startswith('C') or gc.startswith('M'):
        asc = ch.encode(encoding='ascii', errors='backslashreplace')
        ch = asc.decode(encoding='utf-8')
    return f'"{ch}"'


def classify(cp: int) -> None:
    """Classify a given code point.

    Modifies the global variable ``classes``.

    Parameters
    ----------
    cp : int
        the code point
    """
    try:
        ch = chr(cp)
        if ch in SYNTAX:
            return
        cl = ud.category(ch)
        for class_name, (cats, incs) in CLASS_INFO.items():
            if ch in incs or any(cl.startswith(cat) for cat in cats):
                classes[class_name].append(cp)
    except UnicodeEncodeError:
        return


for cp in range(MAX_CP + 1):
    classify(cp)

with open('cc.lark', 'w', encoding='utf-8') as out:
    out.write('# This file has been generated\n')
    out.write(f'# based on Unicode {ud.unidata_version}\n')
    out.write(f'# for code points up to {MAX_CP}\n')
    for name, lst in classes.items():
        pat = encode_list(lst)
        out.write(f'{name}: {pat}\n')
