import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
import csv

# Initialization code
interzonal_dist = pd.read_csv("../data/interzonal.csv")
lgd_flag = {
    "pickup": 'PULocationID',
    "dropoff": 'DOLocationID'
}

def generate_data(time_str):

    conn_string = "postgresql://nycrideshare:nycrideshare@127.0.0.1:5432/nyc_taxi"
    nyc_database = create_engine(conn_string)

    query = \
        f"""select 
        id,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        passenger_count,
        "PULocationID",
        "DOLocationID"
        from nyc_taxi_schema.get_cust_between_timestamps_lgd('{time_str}', '1 MONTHS');"""

    # Get the dataframe
    df_temp = pd.read_sql_query(query, nyc_database)
    # Add the distance to all the the rows
    df_temp["Distance"] = df_temp.apply(lambda row: interzonal_dist.iloc[row["PULocationID"]-1, row["DOLocationID"]-1], axis=1)

    return df_temp.set_index("id", drop=True)

def data_iterator(df, ts_start, ts_end, delta_in_seconds, flag):
    '''
    This function is a generator function that returns filtered df rows between the paramerters passed

    [ts_start]: datetime - start timestamp
    [ts_end]: datetime - end timestamp
    [delta_in_minutes]: int - The value specifies the timedelta for the poolsize
    [flag]: string: it's value is either "pickup" or "drop"
    '''
    current = ts_start
    delta = timedelta(seconds=delta_in_seconds)
    while current < ts_end:
        yield df[
            (df['tpep_pickup_datetime'] >= current) &
            (df['tpep_pickup_datetime'] < current + delta) &
            (df[lgd_flag[flag]] == 138)
        ]

        current += delta

def check_passenger_count(pool, indexA, indexB, max_passenger_count):

    row1 = pool.loc[indexA, :]
    row2 = pool.loc[indexB, :]
    Pa, Pb = row1["passenger_count"], row2["passenger_count"]
    return (max_passenger_count - (Pa + Pb) >= 0)

def calc_distance_weight(row1, row2, flag):

    Da = row1["Distance"]
    Db = row2["Distance"]
    column_name = "DOLocationID" if flag=="pickup" else "PULocationID"
    Dab = interzonal_dist.iloc[
        row1[column_name]-1, 
        row2[column_name]-1
    ]
    Dba = interzonal_dist.iloc[
        row1[column_name]-1, 
        row2[column_name]-1
    ]
    Dmin = min(Da + Dab, Db + Dba)
    savings = Da + Db - Dmin
    return savings / (Da + Db)
    
def calc_time_weight(row1, row2, pool_size):

    Ta = row1["tpep_pickup_datetime"]
    Tb = row2["tpep_pickup_datetime"]
    Tab = abs(Tb - Ta).seconds
    return (pool_size - Tab) / pool_size

def calc_edge_weight(pool, indexA, indexB, distance_fn, time_fn, flag, pool_size):

    row1 = pool.loc[indexA, :]
    row2 = pool.loc[indexB, :]

    weight = distance_fn(row1, row2, flag) + time_fn(row1, row2, pool_size)
    return weight

def save_edges(edges, pool, fileWriter):

    writer=csv.writer(fileWriter, delimiter=',',lineterminator='\n')

    for pairs in edges:
        edge_row = list(pairs)
        writer.writerow(edge_row)

