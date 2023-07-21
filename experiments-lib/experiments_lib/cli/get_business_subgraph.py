from datetime import date
import click
import os
from pathlib import Path
import pandas as pd
from loguru import logger
import networkx as nx
from tqdm import tqdm

tqdm.pandas()


@click.command()
@click.argument("nodes_path", type=Path)
@click.argument("edges_path", type=Path)
@click.argument("output_graph", type=Path)
def main(nodes_path: Path, edges_path: Path, output_graph: Path):
    nodes_df = pd.read_csv(nodes_path)
    nodes_df["id"] = nodes_df["id"].apply(str)
    logger.info(f"Loaded {len(nodes_df)} nodes")
    edges_df = pd.read_csv(edges_path)
    edges_df["src_id"] = edges_df["src_id"].apply(str)
    edges_df["dst_id"] = edges_df["dst_id"].apply(str)
    logger.info(f"Loaded {len(edges_df)} nodes")

    g = nx.DiGraph()
    nodes_df.progress_apply(
        lambda row: g.add_node(
            row["id"],
            idx=row["idx"],
            name=row["name"],
            person_type=row["person_type"],
            label=row["category"],
        ),
        axis=1,
    )
    edges_df.progress_apply(
        lambda row: g.add_edge(
            row["src_id"],
            row["dst_id"],
            insolvency_id=row["insolvency_id"],
            due_date=row["due_date"],
            publish_date=row["publish_date"],
            label=row["label_custom"],
            value=row["value"],
            value_percentage=row["value_percentage"],
        ),
        axis=1,
    )

    logger.info("Selecting subgraph with edges in form LegalPerson -> LegalPerson")
    nodes_data = g.nodes(data=True)
    target_edges = [
        e
        for e in g.edges
        if (
            nodes_data[e[0]]["person_type"] == "L"
            and nodes_data[e[1]]["person_type"] == "L"
            and e[0]
            not in [
                "35975041",  # Arca Investment
                "25570722",  # Tenza a.s.
                "25877950",  # Vitkovice Heavy Machinery
                "63469511",  # NWT Computer s. r. o.
                "25083325",  # Sberbank CZ, a.s.
                "28714989",  # RAF STAVBY s.r.o.
                "25968807",  # MATEX HK s.r.o.
                "43224806",  # TRATEC - CS, s. r. o.
                "64617874",  # STAMONT - POZEMNÍ STAVITELSTVÍ s.r.o.
                "49433946",  # MICO spol. s r.o.
                "25971689",  # Plastic Parts & Technology s.r.o.
                "45309183",  # D2Automation s.r.o.
                "25625381",  # FANS, a.s.
                "45795908",  # České aerolinie a. s.
                "26731177",  # ZK - TERMOCHEM s.r.o. 
                "1955861",   # Iceland Czech, a.s.
                "45022542",  # CEREPA, a. s.
                "27094359",  # ACG-Real s.r.o.
                "3630749",  # Ray Energy a.s.
            ]
        )
    ]

    business_subgraph = g.edge_subgraph(target_edges).copy()

    logger.info(f"Subgraph has {len(business_subgraph.nodes)} nodes")
    logger.info(f"Subgraph has {len(business_subgraph.edges)} edges")

    in_degrees_df = pd.DataFrame(
        business_subgraph.in_degree(), columns=["id", "in_degree"]
    )
    in_degrees_df = in_degrees_df.merge(nodes_df, on="id", how="left")
    in_degrees_df = in_degrees_df.sort_values(by="in_degree", ascending=False)
    logger.info(in_degrees_df[["id", "in_degree", "name"]][:20].to_string())

    nx.write_gpickle(business_subgraph, output_graph)


if __name__ == "__main__":
    main()
