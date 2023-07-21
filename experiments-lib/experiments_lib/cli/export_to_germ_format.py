from cProfile import label
from datetime import date
from typing import Optional
import click
import os
from pathlib import Path
import pandas as pd
from loguru import logger
import networkx as nx
from tqdm import tqdm

tqdm.pandas()


@click.command()
@click.argument("graph_path", type=Path)
@click.argument("output_germ_path", type=Path)
@click.option("--output_label_mapping", type=Path)
def main(
    graph_path: Path,
    output_germ_path: Path,
    output_label_mapping: Optional[Path],
):
    g = nx.read_gpickle(graph_path)
    logger.info(f"Loaded graph with {len(g.nodes)} nodes and {len(g.edges)} edges")

    node_id_2_idx = dict(
        [(node_id, attrs["idx"]) for node_id, attrs in g.nodes(data=True)]
    )

    if output_label_mapping:
        label_2_idx = dict(
            map(
                lambda x: (x[1], x[0]),
                enumerate(
                    reversed(
                        list(set([(attrs["label"]) for _, attrs in g.nodes(data=True)]))
                    )
                ),
            )
        )
        logger.info(f"Writing node label mapping to {output_label_mapping}")

        label_2_idx = dict(
            [
                ("debtor", 0),
                ("bank", 1),
                ("nonbanking", 2),
                ("government", 3),
                ("insurance", 4),
                ("utilities", 4),
                ("other", 5),
            ]
        )
        pd.DataFrame(
            [
                ("debtor", 0),
                ("bank", 1),
                ("nonbanking", 2),
                ("government", 3),
                ("insurance", 4),
                ("utilities", 4),
                ("other", 5),
            ],
            columns=["idx", "label"],
        ).to_csv(output_label_mapping, index=False)
    else:
        label_2_idx = None

    save_in_germ_format(g, output_germ_path, node_id_2_idx, label_2_idx)


def save_in_germ_format(g, path, node_id_2_idx, label_2_idx):
    with open(path, "w") as ofile:
        ofile.write("t # 0\n")
        for node_id, attrs in g.nodes(data=True):
            idx = node_id_2_idx[node_id]
            if label_2_idx:
                label = f" {label_2_idx[attrs['label']]}"
            else:
                label = " 1"
            ofile.write(f"v {idx}{label}\n")

        for src_id, dst_id, attrs in g.edges(data=True):
            node_from = node_id_2_idx[src_id]
            node_to = node_id_2_idx[dst_id]
            ofile.write(
                f"e {node_from} {node_to} {attrs['label']} {get_value_label(attrs['value_percentage'])}\n"
            )
        return node_id_2_idx


def get_value_label(value_percentage):
    if value_percentage <= 11:
        return 0
    elif value_percentage <= 31:
        return 1
    elif value_percentage <= 52:
        return 2
    elif value_percentage <= 79:
        return 3
    else:
        return 4


if __name__ == "__main__":
    main()
