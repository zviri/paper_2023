from pyparsing import Literal
from pyparsing import ParseException
from experiments_lib.util.strings import remove_accents

class CaselessAccentlessLiteral(Literal):
    def __init__(self, matchString):
        super().__init__(self._preprocess(matchString))
        # Preserve the defining literal.
        self.returnString = matchString
        self.errmsg = "Expected " + self.name

    def parseImpl(self, instring, loc, doActions=True):
        if self._preprocess(instring[loc : loc + self.matchLen]) == self.match:
            return loc + self.matchLen, self.returnString
        raise ParseException(instring, loc, self.errmsg, self)

    def _preprocess(self, string: str) -> str:
        return remove_accents(string).upper()
