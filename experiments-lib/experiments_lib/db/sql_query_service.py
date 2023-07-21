from typing import Any
from typing import Dict
from typing import Iterable

from sqlalchemy import create_engine

##########################################################
#  Legacy raw sql service, do not use for any new stuff  #
##########################################################


class SQLQueryService:
    def __init__(self, db_string: str):
        super().__init__()
        self.db_string = db_string

    def query(self, sql: str, **sql_params) -> Iterable[Dict[str, Any]]:
        result = self.db_engine.execute(sql, **sql_params)
        col_names = result.keys()

        row = result.fetchone()
        while row:
            yield dict(zip(col_names, row))
            row = result.fetchone()

    def __enter__(self):
        self.db_engine = create_engine(self.db_string)
        return self

    def __exit__(self, type, value, traceback):
        self.db_engine.dispose()


class SQLQueryServiceFactory:
    def __init__(self, db_string: str):
        super().__init__()
        self.db_string = db_string

    def create(self) -> SQLQueryService:
        return SQLQueryService(self.db_string)
