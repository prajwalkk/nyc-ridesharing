import argparse
from datetime import datetime
from dateutil.relativedelta import *
from itertools import combinations
import networkx as nx
from utils import *
import logging
import os
import numpy as np
import time
import json


def run(args):

    pool_sizes = [300, 420, 600] # pool sizes
    start_time = datetime.strptime(args.start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = start_time + relativedelta(months=+1)

    logging.info(
        f"Extracting one month data starting from {args.start_time_str}")
    df = generate_data(args.start_time_str)
    logging.info(f"Extracted data")

    # Storing run-time statistics
    runtime_stats = {}
    total_runtime, max_runtime, min_runtime = 0, 0, float('inf')
    max_rows_in_pool, min_rows_in_pool = 0, 0, float('inf')

    month_dir = os.path.join("output", start_time.strftime("%b"))

    # loop over flag
    for flag in ["pickup", "dropoff"]:

        out_dir = os.path.join(month_dir, flag)
        os.makedirs(out_dir, exist_ok=True)

        # loop over pool sizes
        for pool_size in pool_sizes:

            # Output file
            out_file = os.path.join(out_dir, f'edges_result_{pool_size}.csv')

            with open(out_file, 'w') as fileWriter:

                completed_rows = 0 # number of processed rows

                # loop over pools
                for (i, pool) in enumerate(
                    data_iterator(
                        df, start_time, end_time, pool_size, flag
                    )
                ):

                    # Some logging
                    completed_rows += len(pool)

                    completion_status = np.round(completed_rows / len(df), 2)
                    logging.info(f"Pool size = {pool_size}, Flag = {flag}, Pool = {i+1}, Processed = {completion_status}%")

                    tic = time.perf_counter() # start permormance measure

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

                    toc = time.perf_counter() # end performance measure

                    # calculate run-time stats
                    runtime = toc - tic
                    total_runtime += runtime
                    max_runtime = max(max_runtime, runtime)
                    min_runtime = min(min_runtime, runtime)
                    min_rows_in_pool = min(min_rows_in_pool, len(pool))
                    max_rows_in_pool = max(max_rows_in_pool, len(pool))

                    # save edges to file
                    save_edges(edge_set, missing_val, pool, fileWriter)

                # store run-time stats in JSON
                avg_runtime = total_runtime / (i + 1)
                runtime_stats["total_runtime"] = total_runtime
                runtime_stats["avg_runtime"] = avg_runtime
                runtime_stats["num_pools"] = i + 1
                runtime_stats["max_runtime"] = max_runtime
                runtime_stats["min_runtime"] = min_runtime
                runtime_stats["max_rows_in_pool"] = max_rows_in_pool

                json_file = os.path.join(out_dir, f'pool_stats_{pool_size}.csv')
                with open(json_file, 'w') as fp:
                    json.dump(runtime_stats, fp)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Simulation of a single month")
    parser.add_argument("--start_time_str", type=str,
                        default="2019-01-01 00:00:00", help="Start time for data")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    run(args)
