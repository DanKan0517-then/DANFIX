"""
Parser — builds a simple AST over token lists produced by the Lexer.

AST structure:
  Document
    └── Paragraph (one per double-newline block)
          └── Sentence (one per sentence-ending punctuation)
                └── Token nodes
"""

from .lexer import TOKEN_SENTENCE_END


class ASTNode:
    def __init__(self, node_type, children=None, tokens=None):
        self.node_type = node_type
        self.children  = children or []
        self.tokens    = tokens   or []

    def __repr__(self):
        return f'ASTNode({self.node_type}, children={len(self.children)}, tokens={len(self.tokens)})'


class Parser:
    def parse(self, tokens: list) -> ASTNode:
        document   = ASTNode('Document')
        paragraph  = ASTNode('Paragraph')
        sentence   = ASTNode('Sentence')

        for tok in tokens:
            sentence.tokens.append(tok)

            if tok.type == TOKEN_SENTENCE_END:
                paragraph.children.append(sentence)
                sentence = ASTNode('Sentence')

        # Flush any remaining tokens that didn't end with punctuation
        if sentence.tokens:
            paragraph.children.append(sentence)

        document.children.append(paragraph)
        return document

    def to_dict(self, node: ASTNode) -> dict:
        """Serialise the AST to a plain dict (for the JSON response)."""
        return {
            'type': node.node_type,
            'tokens': [
                {'type': t.type, 'value': t.value, 'pos': t.position}
                for t in node.tokens
            ],
            'children': [self.to_dict(c) for c in node.children],
        }
