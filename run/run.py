import argparse
from datetime import datetime
from dateutil.relativedelta import *
from itertools import combinations
import networkx as nx
from utils import *
import logging
import os
import numpy as np


def run(args):

    pool_sizes = [300, 420, 600]
    start_time = datetime.strptime(args.start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = start_time + relativedelta(months=+1)

    logging.info(
        f"Extracting one month data starting from {args.start_time_str}")
    df = generate_data(args.start_time_str)
    logging.info(f"Extracted data")

    month_dir = os.path.join("output", start_time.strftime("%b"))

    for flag in ["pickup", "dropoff"]:

        out_dir = os.path.join(month_dir, flag)
        os.makedirs(out_dir, exist_ok=True)

        for pool_size in pool_sizes:

            # Output file
            out_file = os.path.join(out_dir, f'edges_result_{pool_size}.csv')

            with open(out_file, 'w') as fileWriter:

                completed_rows = 0
                for (i, pool) in enumerate(
                    data_iterator(
                        df, start_time, end_time, pool_size, flag
                    )
                ):

                    # Some logging
                    completed_rows += len(pool)
                    completion_status = np.round(
                        (completed_rows / len(df)) * 100, 2)
                    logging.info(
                        f"Pool size = {pool_size}, Flag = {flag}, Pool = {i+1}, Processed = {completion_status}%")

                    # Graph construction
                    G = nx.Graph()
                    index_list = pool.index.tolist()
                    G.add_nodes_from(index_list)

                    # Compute edge weights
                    for indexA, indexB in combinations(index_list, 2):

                        if not check_passenger_count(df, indexA, indexB, 3):
                            continue
                        G.add_edge(
                            indexA,
                            indexB,
                            weight=calc_edge_weight(
                                pool,
                                indexA, indexB,
                                calc_distance_weight, calc_time_weight,
                                "pickup",
                                pool_size
                            )
                        )

                    # Run algorithm
                    edge_set = nx.algorithms.matching.max_weight_matching(G)

                    # Flatten pairs and extract lone node if present
                    no_of_nodes = set(G.nodes)
                    pairs = set()

                    for edges in edge_set:
                        tmp_set = set(edges)
                        pairs = pairs.union(tmp_set)
                    missing_val = no_of_nodes.difference(pairs)

                    save_edges(edge_set, missing_val, pool, fileWriter)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Simulation of a single month")
    parser.add_argument("--start_time_str", type=str,
                        default="2019-01-01 00:00:00", help="Start time for data")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    run(args)
