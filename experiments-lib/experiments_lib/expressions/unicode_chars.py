import pyparsing as pp

UNICODE_CHARS = pp.pyparsing_unicode.Latin1.alphas + pp.pyparsing_unicode.LatinA.alphas
UNICODE_LOWER_CASE_CHARS = "".join([c for c in UNICODE_CHARS if c == c.lower()])
UNICODE_UPPER_CASE_CHARS = "".join([c for c in UNICODE_CHARS if c == c.upper()])
