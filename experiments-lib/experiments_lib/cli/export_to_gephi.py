import click
from pathlib import Path
from loguru import logger
import networkx as nx


@click.command()
@click.argument("graph_path", type=Path)
@click.argument("gexf_output_path", type=Path)
def main(
    graph_path: Path,
    gexf_output_path: Path,
):
    g = nx.read_gpickle(graph_path)
    logger.info(f"Loaded graph with {len(g.nodes)} nodes and {len(g.edges)} edges")

    for node_id in g.nodes:
        g.nodes[node_id]["node_type"] = (
            g.nodes[node_id]["label"]
            if g.nodes[node_id]["label"] != "debtor"
            else "others"
        )

    logger.info("Calculating page rank...")
    for k, v in nx.pagerank(g, weight="value").items():
        g.nodes[k]["pagerank"] = v

    logger.info(f"Writing output file to {gexf_output_path}")
    nx.write_gexf(g, gexf_output_path)


if __name__ == "__main__":
    main()
