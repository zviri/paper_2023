from datetime import date
import click
import os
from pathlib import Path
from experiments_lib.models.creditor_category import (
    CREDITOR_2_CATEGORY,
    CreditorCategory,
)
import pandas as pd
from loguru import logger
from experiments_lib.db import SQLQueryServiceFactory
from pydantic import BaseSettings
from dateutil.relativedelta import relativedelta
from datetime_truncate import truncate_quarter

class Settings(BaseSettings):
    ISIR_DB_URL: str


@click.command()
@click.argument("due_dates_path", type=Path)
@click.argument("output_nodes_path", type=Path)
@click.argument("output_edges_path", type=Path)
def main(due_dates_path: Path, output_nodes_path: Path, output_edges_path: Path):
    settings = Settings()
    sql_service_factory = SQLQueryServiceFactory(settings.ISIR_DB_URL)

    logger.info("Starting to build graph")

    insolvencies_df = _get_insolvencies(sql_service_factory)
    logger.info(f"Found {len(insolvencies_df)} insolvencies")

    receivables_df = _get_receivables(sql_service_factory)
    logger.info(f"Found {len(receivables_df)} receivables")

    due_dates_df = pd.read_parquet(due_dates_path)
    due_dates_df = due_dates_df[
        (due_dates_df["due_date"] >= date(2000, 1, 1))
        & (due_dates_df["due_date"] <= date(2022, 12, 31))
    ]
    due_dates_df.due_date = pd.to_datetime(due_dates_df.due_date)
    logger.info(f"Loaded {len(due_dates_df)} due date records")

    receivables_with_due_dates_df = receivables_df.merge(due_dates_df, on="file_id")
    logger.info(
        f"Found {len(receivables_with_due_dates_df)} receivables with due dates"
    )

    edges_df = (
        insolvencies_df.merge(
            receivables_with_due_dates_df,
            on="insolvency_id",
            suffixes=("_deb", "_cred"),
        )[["id_deb", "id_cred", "due_date", "value", "insolvency_id", "publish_date"]]
        .rename(columns={"id_deb": "src_id", "id_cred": "dst_id"})
        .sort_values(by="due_date")
    )
    edges_df = edges_df[edges_df["src_id"] != edges_df["dst_id"]]
    logger.info(f"Number of edges found: {len(edges_df)}")

    edges_first_occurence_df = edges_df.loc[
        edges_df.groupby(by=["src_id", "dst_id"]).due_date.idxmin()
    ].copy()
    min_year = edges_first_occurence_df.due_date.min()
    
    def _get_diff_months(end_date, min_date):
        delta = relativedelta(end_date, min_date)
        return delta.years * 12 + delta.months

    total_debt_per_debtor_df = edges_first_occurence_df.groupby("src_id")[["value"]].agg(
        value_sum=("value", "sum")
    ).reset_index()
    edges_first_occurence_df = edges_first_occurence_df.merge(total_debt_per_debtor_df, on="src_id")
    edges_first_occurence_df["value_percentage"] = edges_first_occurence_df.apply(
        lambda row: row["value"] / row["value_sum"] * 100 if row["value_sum"] > 0 else 100, 
        axis=1
    )

    edges_first_occurence_df["label_monthly"] = edges_first_occurence_df["due_date"].apply(
        lambda pdate: _get_diff_months(pdate, min_year) 
    )
    edges_first_occurence_df["label_custom"] = edges_first_occurence_df["due_date"].apply(
        lambda pdate: 1 + (_get_diff_months(pdate, date(2019, 1, 1)) // 3) if pdate.year >= 2019 else 0
    )
    edges_first_occurence_df["label_custom2"] = edges_first_occurence_df["due_date"].apply(
        lambda pdate: 1 + (_get_diff_months(pdate, date(2000, 1, 1)) // 3) if pdate.year >= 2000 else 0
    )

    def _get_diff_years(end_date, min_date):
        return  end_date.year - min_date.year + 1
    edges_first_occurence_df["label_yearly"] = edges_first_occurence_df["due_date"].apply(
        lambda pdate: _get_diff_years(pdate, min_year) 
    )

    logger.info(
        f"Number of reduced edges to first occurences: {len(edges_first_occurence_df)}"
    )
    os.makedirs(output_edges_path.parents[0], exist_ok=True)
    edges_first_occurence_df.to_csv(output_edges_path, index=False)

    nodes_df = edges_first_occurence_df.src_id.append(
        edges_first_occurence_df.dst_id, ignore_index=True
    ).drop_duplicates()
    nodes_df = nodes_df.to_frame().reset_index(drop=True).reset_index()
    nodes_df.columns = ["idx", "id"]
    node_names_df = (
        insolvencies_df[["id", "debtor_name", "person_type", "proposal_timestamp"]]
        .rename(columns={"debtor_name": "name"})
        .append(
            receivables_df[["id", "creditor", "person_type"]]
            .reset_index()
            .rename(columns={"creditor": "name"}),
            ignore_index=True,
        )
        .groupby("id")[["name", "person_type", "proposal_timestamp"]]
        .last()
        .reset_index()
    )
    nodes_with_names_df = nodes_df.merge(node_names_df, on="id")
    nodes_with_names_df["category"] = nodes_with_names_df["id"].apply(
        lambda id_: CREDITOR_2_CATEGORY.get(id_, CreditorCategory.OTHER).value
    )
    assert len(nodes_with_names_df) == len(nodes_df)
    assert not (set(edges_df.src_id) - set(nodes_with_names_df.id))
    assert not (set(edges_df.dst_id) - set(nodes_with_names_df.id))

    logger.info(f"Number of nodes found: {len(nodes_df)}")
    nodes_with_names_df.to_csv(output_nodes_path, index=False)


def _get_insolvencies(sql_service_factory):
    with sql_service_factory.create() as query_service:
        rows = query_service.query(
            """
            SELECT
                id AS insolvency_id,
                debtor_name,
                birth_number_hash_code,
                creditor_name2creditor_id(debtor_name) AS string_id,
                ico,
                reference_number,
                proposal_timestamp::DATE,
                person_type
            FROM insolvency_tab_mv
            WHERE EXTRACT(YEAR FROM proposal_timestamp) BETWEEN 2020 AND 2022
            """
        )
        insolvencies_df = pd.DataFrame(rows)

    insolvencies_df["id"] = insolvencies_df["birth_number_hash_code"].apply(
        lambda b: str(int(b)) if pd.notna(b) else b
    )
    insolvencies_df["id"] = insolvencies_df["id"].fillna(
        insolvencies_df["ico"].apply(lambda ico: ico.lstrip("0") if ico else ico)
    )
    insolvencies_df["id"] = insolvencies_df["id"].fillna(insolvencies_df["string_id"])
    assert insolvencies_df["id"].isna().sum() == 0

    return insolvencies_df


def _get_receivables(sql_service_factory):
    with sql_service_factory.create() as query_service:
        rows = query_service.query(
            """
            SELECT
                insolvency_id,
                creditor_string_id AS string_id,
                ico,
                publish_date::DATE,
                creditor,
                ft.file_id,
                form AS person_type,
                rvt.total AS value
            FROM file_tab_mv ft 
                JOIN subjects_tab st ON ft.creditor=st.name
                JOIN receivable_value_tab rvt ON ft.id=rvt.file_id
            WHERE EXTRACT(YEAR FROM publish_date) BETWEEN 2020 AND 2022
                AND rvt.total IS NOT NULL
            """
        )
        receivables_df = pd.DataFrame(rows)
        mapping_df=pd.read_csv("data/interim/file_id_mapping.csv")
        receivables_df = receivables_df.merge(mapping_df, on="file_id")
        receivables_df["file_id"] = receivables_df["ws_file_id"]
        receivables_df = receivables_df.drop(columns="ws_file_id")
        pt_mapping={
            "P": "L",
            "F": "N"
        }
        receivables_df["person_type"] = receivables_df["person_type"].apply(pt_mapping.get)

    receivables_df["id"] = receivables_df["ico"].apply(
        lambda ico: ico.lstrip("0") if ico else ico
    )
    receivables_df["id"] = receivables_df["id"].fillna(receivables_df["string_id"])
    receivables_df = receivables_df[receivables_df["id"].notna()].copy()

    return receivables_df


if __name__ == "__main__":
    main()
