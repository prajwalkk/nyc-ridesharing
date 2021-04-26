import argparse
from datetime import datetime
from dateutil.relativedelta import *
from itertools import combinations
import networkx as nx
from utils import *
import logging

def run(args):

    pool_sizes = [300, 420, 600]
    start_time = datetime.strptime(args.start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = start_time + relativedelta(months=+1)

    logging.info(f"Extracting one month data starting from {args.start_time_str}")
    df =  generate_data(args.start_time_str)
    logging.info(f"Extracted data")

    for pool_size in pool_sizes:

        for flag in ["pickup", "dropoff"]:

            for (i, pool) in enumerate(
                data_iterator(
                    df, start_time, end_time, pool_size, flag
                )
            ):

                logging.info(f"Pool size = {pool_size}, Flag = {flag}, Pool = {i+1}")
                G = nx.Graph()
                index_list = pool.index.tolist()
                G.add_nodes_from(index_list)

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

                edge_set = nx.algorithms.matching.max_weight_matching(G)
                no_of_nodes = set(G.nodes)

                pairs = set()

                for i in edge_set:
                    tmp_set = set(i)
                    pairs = pairs.union(tmp_set)
                missing_val = no_of_nodes.difference(pairs)
                edge_set.union(missing_val)

                show_viz(edge_set, pool)

if __name__== "__main__":

    parser = argparse.ArgumentParser(description="Simulation of a single month")
    parser.add_argument("--start_time_str", type=str, default="2019-01-01 00:00:00", help="Start time for data")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    run(args)