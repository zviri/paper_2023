import pyparsing as pp
from experiments_lib.expressions.date_expr import date_
from experiments_lib.expressions.caseless_accentless_literal import (
    CaselessAccentlessLiteral as CAL,
)
from experiments_lib.expressions.sequence import sequence

contract_number = pp.Word(pp.nums)
due_date = (
    sequence("smlouva o uveru")
    + (CAL("c") + pp.Optional("."))
    + contract_number
    + sequence("ze dne")
    + date_
)
