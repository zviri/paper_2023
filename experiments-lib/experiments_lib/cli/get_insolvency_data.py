import click
from pathlib import Path
import pandas as pd
from loguru import logger
from experiments_lib.db import SQLQueryServiceFactory
from pydantic import BaseSettings

class Settings(BaseSettings):
    ISIR_DB_URL: str


@click.command()
@click.argument("output_insolvency_data_path", type=Path)
def main(output_insolvency_data_path: Path):
    settings = Settings()
    sql_service_factory = SQLQueryServiceFactory(settings.ISIR_DB_URL)

    logger.info("Starting to extract insolvency data")
    with sql_service_factory.create() as query_service:
        rows = query_service.query(
            """
            SELECT
                it.id AS insolvency_id,
                rt.name AS region
            FROM insolvency_tab_mv it 
                JOIN regions_tab rt
                ON it.region_id=rt.id
            """
        )
        regions_df = pd.DataFrame(rows)
        regions_df = regions_df.groupby("insolvency_id").max().reset_index()

    logger.info(f"Saving data about {len(regions_df)} insolvencies")
    regions_df.to_csv(output_insolvency_data_path, index=False)

if __name__ == "__main__":
    main()
