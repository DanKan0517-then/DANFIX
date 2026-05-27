"""
Error Reporter — consumes the error list from the Semantic Analyser and produces:
  1. A structured JSON-ready report dict
  2. An auto-corrected version of the original text
"""

import re


class ErrorReporter:

    def generate_report(self, text: str, errors: list, tokens: list, ast_dict: dict) -> dict:
        """Build the full analysis payload."""

        spelling_errors = [e for e in errors if e['type'] == 'SPELLING_ERROR']
        grammar_errors  = [e for e in errors if e['type'] == 'GRAMMAR_ERROR']

        # Basic text statistics
        word_tokens = [t for t in tokens if t.type == 'WORD']
        words       = [t.value for t in word_tokens]

        sentences   = text.replace('!', '.').replace('?', '.').split('.')
        sentences   = [s.strip() for s in sentences if s.strip()]

        report = {
            'original_text':   text,
            'corrected_text':  self.auto_correct(text, errors),
            'errors':          errors,
            'stats': {
                'total_errors':    len(errors),
                'spelling_errors': len(spelling_errors),
                'grammar_errors':  len(grammar_errors),
                'word_count':      len(words),
                'sentence_count':  len(sentences),
                'unique_words':    len(set(w.lower() for w in words)),
            },
            'tokens': [
                {'type': t.type, 'value': t.value, 'pos': t.position}
                for t in tokens
            ],
            'ast': ast_dict,
        }
        return report

    def auto_correct(self, text: str, errors: list) -> str:
        """Apply best fixes from errors to produce a corrected string."""
        # Sort by position descending so character offsets don't shift
        fixable = [e for e in errors if e.get('best_fix') and e.get('word')]
        fixable.sort(key=lambda e: e.get('position', 0), reverse=True)

        corrected = text
        for error in fixable:
            word     = error['word']
            best_fix = error['best_fix']
            if not word or not best_fix or word == best_fix:
                continue

            # Use word-boundary-aware regex; handle apostrophes too
            pattern = r'(?<![A-Za-z\'])' + re.escape(word) + r'(?![A-Za-z\'])'
            try:
                corrected = re.sub(pattern, best_fix, corrected, count=1)
            except re.error:
                corrected = corrected.replace(word, best_fix, 1)

        return corrected
