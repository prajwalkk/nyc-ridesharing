# conda install psutil requests 
# conda install -c plotly plotly plotly-orca
# conda install matplotlib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plotly.graph_objects as go
import plotly.io as pio
import logging
import utils
from time import strptime
# png_renderer = pio.renderers["png"]
# pio.renderers.default = "png"

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
# MONTHS = ['Jun']
DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
pool_sizes = [300, 420, 600]


def load_edges_single_pool(poolSize):

    print(f'Processing pool size - {poolSize}')

    TOTAL_DIST_ORIGINAL = 0
    TOTAL_DIST_POOLED = 0

    VZ_DIST_ORIGINAL = []
    VZ_DIST_POOLED = []
    VZ_DIST_SAVED = []
    VZ_DIST_SAVED_PERCENT = []
    VZ_RIDES_SAVED = []

    # loop thru edge_files for a particular poolSize and load them in df_pairs
    for month in MONTHS:

        # query PSQL DB and get the data for MONTHS and load them in df_data
        month_id= strptime(month, '%b').tm_mon
        df_data = utils.generate_data(f"2019-0{month_id}-01 00:00:00")

        TOTAL_DIST_ORIGINAL = 0
        TOTAL_DIST_POOLED = 0

        len_of_trips_pooled = 0

        for action in ["pickup","dropoff"]:
            print(f"Processing {month}-{action}")

     

            fp = f'./output/{month}/{action}/edges_result_{poolSize}.csv'
            df_pairs = pd.read_csv(fp, header = None, names=['p1', 'p2'])       
            
            # for each record in df_pairs
            for idx in range(len(df_pairs)) :

                if idx % 100000 == 0: 
                    print(idx)

                p1, p2 = df_pairs.iloc[idx, 0], df_pairs.iloc[idx, 1]

                p1_data = df_data.loc[p1,:]

                # if p2 is not NaN, retrieve the data
                if not np.isnan(p2):
                    p2_data = df_data.loc[p2,:]
                else:
                    p2_data = None

                OSRM_dist_P1_dropoff = utils.getOSRMComputedDistance( p1_data.loc['PULocationID'], p1_data.loc['DOLocationID'] )

                if p2_data is not None:
                    OSRM_dist_P2_dropoff = utils.getOSRMComputedDistance( p2_data.loc['PULocationID'], p2_data.loc['DOLocationID'] )
                    OSRM_dist_P1_P2 = utils.getOSRMComputedDistance( p1_data.loc['PULocationID'], p2_data.loc['PULocationID'] )

                    # use this variable to count if 2 rides are pooled
                    len_of_trips_pooled += 1
                else:
                    OSRM_dist_P2_dropoff = 0
                    OSRM_dist_P1_P2 = 0

                distance_original = OSRM_dist_P1_dropoff + OSRM_dist_P2_dropoff
                distance_pooled = OSRM_dist_P1_P2 + OSRM_dist_P2_dropoff

                TOTAL_DIST_ORIGINAL += distance_original
                TOTAL_DIST_POOLED += distance_pooled


            # insert them into viz arrays 
        VZ_DIST_ORIGINAL.append(TOTAL_DIST_ORIGINAL)
        VZ_DIST_POOLED.append(TOTAL_DIST_POOLED)

        saved_dist = TOTAL_DIST_ORIGINAL - TOTAL_DIST_POOLED
        VZ_DIST_SAVED.append(saved_dist)
        VZ_DIST_SAVED_PERCENT.append(saved_dist/TOTAL_DIST_ORIGINAL)
        VZ_RIDES_SAVED.append( len_of_trips_pooled / len(df_data))

    
    # create the graph here 
    labels = MONTHS
    x = np.arange(len(labels))  # the label locations
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, [dist / 1000000 for dist in VZ_DIST_ORIGINAL], width, label='INDIVIDUAL DISTANCES', align='center')
    rects2 = ax.bar(x, [dist / 1000000 for dist in VZ_DIST_POOLED], width, label='POOLED DISTANCE', align='center')
    rects3 = ax.bar(x + width, [dist / 1000000 for dist in VZ_DIST_SAVED], width, label='SAVED DISTANCE', align='center')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Distance in Miles')
    ax.yaxis.set_major_formatter('{x}M')
    ax.set_title(f'Distance savings({poolSize} secs)- Individual vs Pooled Rides')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    fig.tight_layout()

    plt.show()


    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, [dist * 100 for dist in VZ_DIST_SAVED_PERCENT], width, label='% DISTANCES Saved', align='center')
    rects2 = ax.bar(x, [rides * 100 for rides in VZ_RIDES_SAVED], width, label='% Trips Saved', align='center')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Percentage')
    ax.set_title(f'Utilization % ({poolSize} secs)-')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    fig.tight_layout()

    plt.show()


for pool in pool_sizes: 
    load_edges_single_pool(pool)




def load_viz():
    labels = ['Jan', 'Feb']

    x = np.arange(len(labels))  # the label locations
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, [100, 120], width, label='VZ_DIST_ORIGINAL', align='center')
    rects2 = ax.bar(x, [80, 98], width, label='VZ_DIST_POOLED', align='center')
    rects3 = ax.bar(x+ width, [20, 22], width, label='VZ_DIST_SAVED', align='center')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Distance')
    ax.yaxis.set_major_formatter('{x} km')
    ax.set_title(f'Distance savings ({poolSize} secs)- Individual vs Pooled Rides')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)

    fig.tight_layout()

    plt.show()


# ----------------------------------
# Visualizations required 
# 1. X- Months  Y- Utilization, Trips saved 
#   A. Pool 5
#   B. Pool 7
#   A. Pool 10
#
# 2. X- Days of Week  Y- Utilization, Trips saved 
#   A. Pool 5
#   B. Pool 7
#   A. Pool 10
#
# 3. X- Average computation time  Y- Pools
#   A. Months
# ----------------------------------  