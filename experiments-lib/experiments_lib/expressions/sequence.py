import re
from typing import Optional

import pyparsing as pp
from experiments_lib.expressions.caseless_accentless_literal import (
    CaselessAccentlessLiteral,
)

def sequence(text: str, return_value: Optional[str] = None) -> pp.ParseExpression:
    literals = re.split("\\s+", text.strip())
    sequence = pp.And(map(CaselessAccentlessLiteral, literals))
    if not return_value:
        return_value = text
    return sequence.setParseAction(lambda v: return_value)
