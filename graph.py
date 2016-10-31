'''
Should be used in iPython notebook only
'''

from dateutil import parser
import pandas as pd
import plotly
from plotly import tools
from plotly.tools import FigureFactory as ff
from plotly.offline import init_notebook_mode, iplot
from plotly.graph_objs import *

init_notebook_mode(connected=True)

PRICE = None
VOLUME = None
TIME = None

def config(price, volume, time):
    global PRICE, VOLUME, TIME
    PRICE = price
    VOLUME = volume
    TIME = time

def make_one_candle(data):
    return {
        'open': data.iloc[0][PRICE],
        'high': data[PRICE].max(),
        'low': data[PRICE].min(),
        'close': data.iloc[-1][PRICE],
        'volume': data[VOLUME].sum(),
        'time': data.iloc[0][TIME],
    }

def build_candles(data, frame):
    ret = []
    base_time = parser.parse(data.iloc[0][TIME])
    base_idx = 0
    idx = 0
    while idx < len(data):
        time = parser.parse(data.iloc[idx][TIME])
        if (time - base_time).seconds > frame:
            ret.append(make_one_candle(data.iloc[base_idx: idx]))
            base_idx = idx
            base_time = time
        else:
            idx += 1
    ret.append(make_one_candle(data.iloc[base_idx: idx-1]))
    return pd.DataFrame(ret)

def draw(candles):
    # build the OCHL graph
    times = candles['time'].apply(parser.parse)
    fig_increasing = ff.create_candlestick(candles['open'], candles['high'], candles['low'], candles['close'], dates=times,
        direction='increasing',
        marker=Marker(color='#ff6666'),                                       
        line=Line(color='#ff6666'))
    fig_decreasing = ff.create_candlestick(candles['open'], candles['high'], candles['low'], candles['close'], dates=times,
        direction='decreasing',
        marker=Marker(color='#39ac73'),
        line=Line(color='#39ac73'))

    fig = fig_increasing
    fig['data'].extend(fig_decreasing['data'])

    # build the volume graph
    volume_chart = Bar(x = times, y = candles['volume'], marker= Marker(color = "#ff9933"))
    g = tools.make_subplots(rows=2, cols=1, shared_xaxes=True)
    g.append_trace(fig['data'][0], 1, 1)
    g.append_trace(fig['data'][1], 1, 1)
    g.append_trace(volume_chart, 2, 1)
    g.layout['yaxis2']['domain'] = [0.0, 0.25]
    g.layout['yaxis1']['domain'] = [0.3, 1.0]
    g.layout['paper_bgcolor']='#1E2022'
    g.layout['plot_bgcolor'] = "#3E3E3E"
    g.layout['font'] = Font(color = "#3E3E3E")
    g.layout['xaxis1']['tickfont'] = Font(color="#B3A78C")
    g.layout['yaxis1']['tickfont'] = Font(color="#B3A78C")
    g.layout['yaxis2']['tickfont'] = Font(color="#B3A78C")
    g.layout['showlegend'] = False
    iplot(g)
