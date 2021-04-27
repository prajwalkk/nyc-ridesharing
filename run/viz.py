# conda install psutil requests 
# conda install -c plotly plotly-orca
# conda install matplotlib
import plotly.graph_objects as go
import plotly.io as pio
# png_renderer = pio.renderers["png"]
# pio.renderers.default = "png"

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
pool_sizes = [300, 420, 600]

def load_edges_single_pool(poolSize):

    # loop load edge files for a particular poolSize
    


    fig = dict({
    "data": [{"type": "bar",
              "x": ['Jan', 'Feb', 'March'],
              "y": [1, 3, 2]}],
    "layout": {"title": {"text": "A Figure Specified By Python Dictionary"}}
    })
    pio.show(fig)
    # fig.show()


load_edges()

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