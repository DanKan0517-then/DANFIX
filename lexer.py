import re

# Token types
TOKEN_WORD        = 'WORD'
TOKEN_NUMBER      = 'NUMBER'
TOKEN_PUNCTUATION = 'PUNCTUATION'
TOKEN_SENTENCE_END = 'SENTENCE_END'
TOKEN_UNKNOWN     = 'UNKNOWN'

class Token:
    def __init__(self, type_, value, position):
        self.type     = type_
        self.value    = value
        self.position = position   # character offset in original text

    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, pos={self.position})'


class Lexer:
    """Tokenises plain-English text into a flat list of Token objects."""

    # Order matters – more specific patterns first
    _PATTERNS = [
        (TOKEN_SENTENCE_END, r'[.!?]+'),
        (TOKEN_NUMBER,       r'\b\d+(?:[.,]\d+)*\b'),
        (TOKEN_WORD,         r"[A-Za-z]+(?:'[A-Za-z]+)*"),  # handles contractions
        (TOKEN_PUNCTUATION,  r'[,;:\-\'"()\[\]{}]'),
        (TOKEN_UNKNOWN,      r'\S'),          # any other non-whitespace
    ]

    def __init__(self):
        # Build one combined regex
        parts = [f'(?P<{name}>{pat})' for name, pat in self._PATTERNS]
        self._regex = re.compile('|'.join(parts))

    def tokenise(self, text: str) -> list:
        tokens = []
        for m in self._regex.finditer(text):
            kind  = m.lastgroup
            value = m.group()
            pos   = m.start()
            tokens.append(Token(kind, value, pos))
        return tokens
