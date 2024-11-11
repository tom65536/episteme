"""Script to generate Unicode based character classes for Esteme parser."""

import re
import unicodedata as ud


# Run over all codepoints up to this limit
MAX_CP = 0x10FFFF


# Symbols not to be included otherwise
SYNTAX = '$,.;:#()[]{}\"\'!?`\\=@'

CLASS_INFO = {
    'ID_START': (('L', 'Nl', 'Sc'), ''),
    'ID_MEDIAL': (('Pc',), '_'),
    'ID_CONT': (('L', 'Mn', 'Mc', 'Nl', 'Nd', 'Sc'), ''),
    'OPERATORS': (('Sm',), '+-*/<>^~|&%'),
    'SPACE': (('Zs',), '\t'),
    'DIGIT': (('Nd',), ''),
}

classes = {
    name: [] for name in CLASS_INFO.keys()
}


def classify(cp: int) -> None:
    try:
        ch = chr(cp)
        if ch in SYNTAX:
            return
        cl = ud.category(ch)
        for class_name, (cats, incs) in CLASS_INFO.items():
            if (
                ch in incs or
                any(cl.startswith(cat) for cat in cats)
            ):
                classes[class_name].append(cp)
    except UnicodeEncodeError:
        return


def compress_ranges(lst: list[int]) -> list[range]:
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

def encode_cp(cp):
    ch = chr(cp)
    if ch in '"\'\\':
        return f'"\\{ch}"'
    if ch == '\r':
        return '"\\r"'
    if ch == '\n':
        return '"\\n"'
    if ch == '\t':
        return '"\\t"'
    if ch == '\v':
        return '"\\v"'
    gc = ud.category(ch)
    if gc.startswith("Z") or gc.startswith("C") or gc.startswith('M'):
        return '"' + ch.encode(
            encoding='ascii',
            errors='backslashreplace'
        ).decode(encoding='utf-8') + '"'
    return f'"{ch}"'

def encode_range(rg):
    if len(rg) == 1:
        return encode_cp(rg.start)
    return encode_cp(rg.start) + ".." + encode_cp(rg.stop - 1)

def encode_list(lst):
    return (
        ('\n   |'.join(encode_range(rg)
            for rg in compress_ranges(lst)))
    )

for cp in range(MAX_CP + 1):
    classify(cp)

with open('cc.lark', 'w', encoding='utf-8') as out:
    out.write('# This file has been generated\n')
    out.write(f'# based on Unicode {ud.unidata_version}\n')
    out.write(f'# for code points up to {MAX_CP}\n')
    for name, lst in classes.items():
        pat = encode_list(lst)
        out.write(f'{name}: {pat}\n')
