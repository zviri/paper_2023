import pyparsing as pp
from datetime import date

def to_int(t):
    return int(t[0])

def to_date(result):
    try:
        return date(result["year"], result["month"], result["day"])
    except ValueError:
        return None

date_ = (
    pp.Word(pp.nums, min=1, max=2).setParseAction(to_int)("day") + "." 
    + pp.Word(pp.nums, min=1, max=2).setParseAction(to_int)("month") + "." 
    + pp.Word(pp.nums, exact=4).setParseAction(to_int)("year")
).setParseAction(to_date)("date")