"""
Semantic Analyser — walks the AST and annotates nodes with detected errors.

Two passes:
  1. Spelling  — pyspellchecker on every WORD token
  2. Grammar   — LanguageTool on each reconstructed sentence string
"""

from spellchecker import SpellChecker
from .lexer import TOKEN_WORD, TOKEN_SENTENCE_END

try:
    import language_tool_python
    _LT_AVAILABLE = True
except ImportError:
    _LT_AVAILABLE = False

_spell = SpellChecker()

# Only start LanguageTool once (it spawns a local JVM)
_lt = None

def _get_lt():
    global _lt
    if _lt is None and _LT_AVAILABLE:
        try:
            _lt = language_tool_python.LanguageTool('en-US')
        except Exception:
            pass
    return _lt


def _attr(match, snake, camel):
    """Return snake_case or camelCase attribute, whichever exists."""
    return getattr(match, snake, None) or getattr(match, camel, None) or ''


class SemanticAnalyser:

    def analyse(self, ast_root) -> list:
        """Return a flat list of error dicts."""
        errors = []
        for para in ast_root.children:
            for sentence in para.children:
                errors.extend(self._check_spelling(sentence))
                errors.extend(self._check_grammar(sentence))
                errors.extend(self._check_capitalisation(sentence))
        return errors

    # ── spelling ─────────────────────────────────────────────────────
    def _check_spelling(self, sentence) -> list:
        errors = []
        words = [t for t in sentence.tokens if t.type == TOKEN_WORD]
        if not words:
            return errors

        lower_words = [t.value.lower() for t in words]
        unknown     = _spell.unknown(lower_words)   # returns a set of lower-case strings

        for tok in words:
            if tok.value.lower() in unknown:
                candidates = list(_spell.candidates(tok.value.lower()) or [])
                errors.append({
                    'type':        'SPELLING_ERROR',
                    'word':        tok.value,
                    'position':    tok.position,
                    'message':     f'"{tok.value}" may be misspelled.',
                    'suggestions': candidates[:5],
                    'best_fix':    candidates[0] if candidates else tok.value,
                })
        return errors

    # ── grammar (LanguageTool) ────────────────────────────────────────
    def _check_grammar(self, sentence) -> list:
        errors = []
        lt = _get_lt()
        if lt is None:
            return errors

        sentence_text = ' '.join(t.value for t in sentence.tokens)
        try:
            matches = lt.check(sentence_text)
        except Exception:
            return errors

        for m in matches:
            rule_id = _attr(m, 'rule_id', 'ruleId')
            # Skip rules that duplicate our own checks
            if rule_id in ('MORFOLOGIK_RULE_EN_US',):
                continue

            offset      = _attr(m, 'offset', 'fromx') or 0
            error_len   = _attr(m, 'error_length', 'errorLength') or 0
            message     = _attr(m, 'message', 'msg') or ''
            replacements = _attr(m, 'replacements', 'replacements') or []
            context_text = _attr(m, 'context', 'context') or sentence_text

            # Find the absolute position inside the original text
            tok_offset = sentence.tokens[0].position if sentence.tokens else 0
            abs_pos    = tok_offset + int(offset)

            errors.append({
                'type':        'GRAMMAR_ERROR',
                'word':        str(context_text)[int(offset): int(offset) + int(error_len)] if context_text else '',
                'position':    abs_pos,
                'message':     str(message),
                'suggestions': [str(r) for r in replacements[:5]],
                'best_fix':    str(replacements[0]) if replacements else '',
                'sentence':    sentence_text,
            })
        return errors

    # ── capitalisation ────────────────────────────────────────────────
    def _check_capitalisation(self, sentence) -> list:
        tokens = [t for t in sentence.tokens if t.type == TOKEN_WORD]
        if not tokens:
            return []

        first = tokens[0]
        if first.value and first.value[0].islower():
            corrected = first.value[0].upper() + first.value[1:]
            return [{
                'type':        'GRAMMAR_ERROR',
                'word':        first.value,
                'position':    first.position,
                'message':     'Sentence should start with a capital letter.',
                'suggestions': [corrected],
                'best_fix':    corrected,
            }]
        return []
