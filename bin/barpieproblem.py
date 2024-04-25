import logging
import pandas as pd
import datetime
import dash
from dash import Dash,DiskcacheManager,Patch, CeleryManager, dcc, html, Input, Output, State, MATCH, ALL, ctx,clientside_callback, ClientsideFunction
from flask_caching import Cache
from celery import Celery
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State 
import dash_daq as daq
import dash_trich_components as dtc
from dash.exceptions import PreventUpdate
import glob
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash_breakpoints import WindowBreakpoints
import json
from uuid import uuid4
import polars as pl
from dash_extensions.enrich import DashProxy,RedisBackend, Output, Input, State, Serverside, html, dcc, \
    ServersideOutputTransform
#from flask_caching import Cache
import redis
import dash_loading_spinners as dls
import subprocess
import numpy as np

data = {
    'teller': list(range(1, 11)),  # integers from 1 to 10
    'level1': [str(x * 10) for x in range(1, 11)],  # strings '10' to '100' in steps of 10
    'level2': [str(x * 15) for x in range(1, 11)],  # strings '15' to '150' in steps of 15
    'level3': [str(x * 18) for x in range(1, 11)],  # strings '18' to '180' in steps of 18
    'level4': [str(x * 22) for x in range(1, 11)]   # strings '22' to '220' in steps of 22
}
print(data)


app.layout = html.Div([
    html.H1("Plotly Dropdown Example"),
    
    # Dropdown with two options
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'level1', 'value': 'level1'},
            {'label': 'level2', 'value': 'level2'}
        ],
        value='level1'  # Default selected option
    ),

    html.Div(id='selected-option-output')
])

# Define a callback to update the output based on the selected dropdown value
@app.callback(
    dash.dependencies.Output('selected-option-output', 'children'),
    [dash.dependencies.Input('my-dropdown', 'value')]
)
def update_output(selected_option):
    return f'You have selected: {selected_option}'



@app.callback(
    Output('graph-level0compare', 'figure'),
    [
     Input('button1', 'value'),
     Input('button2', 'value'),
     ],prevent_initial_call=True
)
def update_level0Graph(button1,button2): #,hoverData,*args
    traces = []
    countiterations = data.level1.nunique()
    if countiterations==1:
        print('countiterations==1 traces')
        traces.append(dict(
            values=sum(data.teller),
            labels=data.level1,
            type = 'pie',
            hole=.7,
            margin=dict(t=50, b=30, l=0, r=0), 
            showlegend=False,
            font=dict(size=17, color='white'),
            textposition='outside',
            textinfo='percent+label', 
            rotation=50,
            marker=dict(
               # colors= FilterColor
            )
        ))
    else:
        print('countiterations>1 traces')
        for j in data.eval(button2).unique():
            opacity = '1'
            df_by_Level0Name = data[data[button2] == j]
            traces.append(dict(
                #df_by_Level0Name,
                y=df_by_Level0Name.eval(button1), #Filter1_0,
                x=sum(df_by_Level0Name.teller),
                text=sum(df_by_Level0Name.teller),
                text_auto=True,
                type='pie' if countiterations==1 else 'bar',
                marker=dict(
                    opacity=opacity,
                    color_discrete_map='identity',
                    line=dict(width=0.1,
                              color_discrete_map='identity',
                              opacity=1,
                              ),
                ),
                #orientation="v",
                #orientation="h",
                orientation="v" if countiterations==1 else "h",
                name=j,
                transforms=[dict(
                    type='aggregate',
                    groups=df_by_Level0Name.eval(button_group),
                    aggregations=[
                        dict(target='Numerator', func=AggregateNumDenom(AggregateNum)),  
                        dict(target='Denominator', func=AggregateNumDenom(AggregateDenom))  
                    ]
                ),
                ]
        ))
    if data000.empty:
        return {"layout": dict(
            xaxis = dict(visible=False),
            yaxis = dict(visible=False),
            annotations=[
                            dict(
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=0.5,
                                text="No data available",
                                showarrow=False,
                                font=dict(size=26,color=fontcolor),
                )
            ],
            plot_bgcolor=graphcolor,
            paper_bgcolor=graphcolor)
        }
    elif countiterations==1:
        print('countiterations==1 layout')
        return {
            'data': traces,
            'layout': dict(
                font=dict(
                        size=15,
                    ),
                margin={'l': 140, 'b': 25, 't': 37, 'r': 40},
                annotations = [dict(
                         align='center',
                         xref = "paper", yref = "paper",
                         showarrow = False, 
                         font=dict(
                            family="Courier New, monospace",
                            size=26,
                            color="#ffffff"
                            ),
                         text=button_group,#<i class='material-icons'>gender</i>
                )],
                plot_bgcolor=graphcolor,
                paper_bgcolor=graphcolor
            )
        } 
    else:
        print('countiterations>1 layout')
        returndit= {
            'data': traces,
            'layout': dict(
                dragmode='select',
                clickmode='event+select',
                barnorm=eval(PercentageTotalSwitchDEF(PercentageTotalSwitchNoTime)),
                barmode='stack', #aanzetten indien tweede per
                clear_on_unhover=True,
                type='bar',
                xaxis=dict(type='string',
                           title='',
                           showgrid=False,
                           gridwidth=0,
                           fixedrange=True,
                           showline=False,
                           tickformat=eval(Notation[0]),
                           visible=False,
                           color=fontcolor,
                           font=dict(
                               size=14,
                           )
                           ),
                yaxis=dict(title='',
                           showline=False,
                           showgrid=False,
                           categoryorder="total ascending",
                           gridwidth=0,
                           color=fontcolor,
                           ),
                margin={'l': 140, 'b': 25, 't': 37, 'r': 40},
                showlegend=False if button_group1==button_group else True,
                legend=dict(
                        font=dict(
                        color=fontcolor  # Change the font color here
                            )
                        ),
                autosize=True,
                plot_bgcolor=graphcolor,
                paper_bgcolor=graphcolor,
                modebar=dict(
                    bgcolor='transparent',
                    color=BeautifulSignalColor,
                ),
                font=dict(
                    size=15,
                ),
                title=title,
                hovermode='x-unified',
                transition={'duration': 500},
                style={'overflow': 'auto'}
            )
        }
        print(returndit)
        return returndit
    
    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)