# -*- coding: utf-8 -*-
"""

@author: MinBin

"""
# import packages
import dash
import dash_html_components as html

import numpy as np
import pandas as pd

############################################################
# load data
distance_matrix = pd.read_csv('matrix.csv', index_col=0)
############################################################
# highlight method (for dataframe)

std = np.std(distance_matrix.values.flatten())
mean = np.mean(distance_matrix.values.flatten())
small_dist = np.where(np.logical_and(
    distance_matrix.values > mean - std,
    distance_matrix.values < mean + std))

vals = distance_matrix.values[small_dist]
_, bins = np.histogram(vals, bins=3)

spread = np.around(bins / distance_matrix.max().max(), decimals=2).tolist()

COLORS ={
        0.00: '#ffff33',
        0.001: '#e4f6f8',
        0.75: '#ff66ff',        
        }

choose_colors = ['#62c2cc', '#fdb813', '#00ff7f', '#f68b1f']
for i, p in enumerate(spread):
    COLORS[p] = choose_colors[i]

def is_numeric(val):
    try:
        float(val)
        return True
    except ValueError:
        return False
    
def ColorRange(val,  max_val):
    if is_numeric(val):
        relative_val = val / float(max_val)
        k = min(COLORS.keys(), key = lambda c: abs(relative_val - c))
        return ('background-color', COLORS[k], k)
    
def Generate_Table(distance_matrix, max_rows=100):
    max_val = distance_matrix.max(numeric_only=True).max()
    rows = []
    d = {}

    for i in range(min(len(distance_matrix), max_rows)):
        row = []
        cols = distance_matrix.columns
        row.append(html.Tr(cols[i]))
        for col in cols:
            val = distance_matrix.iloc[i][col]
            color_key, color_val, k = ColorRange(val, max_val)
            if d.get(k, None) is None:
                d[k] = 0
            else:
                d[k] += 1
            row.append(html.Td(val, style={color_key: color_val}))
        rows.append(html.Tr(row))

    print d
    # we need an empty column in the first square because the first row is also labels
    cols = ["   "] + cols.tolist()
    table = html.Table(
        [html.Tr([html.Th(col) for col in cols])] +
        rows
        )

    return table
        
app = dash.Dash()
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})
app.scripts.config.serve_locally=True
app.layout = html.Div(
    children=[
    html.H4(children='Distance Matrix'),
    Generate_Table(distance_matrix)
    ])

if __name__ == '__main__':
    app.run_server(debug=True)

