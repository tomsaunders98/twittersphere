# -*- coding: utf-8 -*-
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



app = dash.Dash(__name__)
people = pd.read_csv("BNOCSFINAL1.csv")

accountlist = people["name"].unique().tolist()
typelist = people["type"]
tweets = pd.read_csv("tweets.csv")

axistitle = {
    "totalengagementrate" : "Engagement Rate",
    "ratiod" : "Likeability Rating",
    "followers_count" : "Number of Followers",
    "mentions" : "Number of Mentions",
    "listed_count" : "Number of Lists an Account is in"
}


app.layout = html.Div(
    children = [
    html.Div(
        className = "selectormain",
        children=[
        html.Div(
            [
                html.P("Compare on X-Axis:"),
                dcc.Dropdown(
                    id='xaxis-type',
                    options=[
                        {'label': 'Engagement', 'value': 'totalengagementrate'},
                        {'label': 'Likeability', 'value': 'ratiod'},
                        {'label': 'Follower Count', 'value': 'followers_count'},
                        {'label': 'Mentions', 'value': 'mentions'},
                        {'label': 'List Count', 'value': 'listed_count'}
                    ],
                    value='totalengagementrate'
                ),
            ],
            className="selector",
        ),
        html.Div(
            [
                html.P("Compare on Y-Axis:"),
                dcc.Dropdown(
                    id='yaxis-type',
                    options=[
                        {'label': 'Engagement', 'value': 'totalengagementrate'},
                        {'label': 'Likeability', 'value': 'ratiod'},
                        {'label': 'Follower Count', 'value': 'followers_count'},
                        {'label': 'Mentions', 'value': 'mentions'},
                        {'label': 'List Count', 'value': 'listed_count'}
                    ],
                    value='ratiod'
                ),
            ],
            className="selector",
        ),
            html.Div(
            [
                html.P("Select Data Type to Compare:"),
                dcc.Dropdown(
                    id='datatype',
                    options=[
                        {'label': 'Journalists', 'value': 'journo'},
                        {'label': 'Politicians', 'value': 'pol'},
                        {'label': 'News Organisations', 'value': 'news'},
                        {'label': 'Issue Groups', 'value': 'issue'},
                        {'label': 'Government Accounts', 'value': 'gov'},
                        {'label': 'Everyone Else', 'value': 'other'},
                        {'label': 'All Accounts', 'value': 'all'}

                    ],
                    value='journo'
                ),
            ],
            className="selector",
        ),
            html.Div(
            [
                html.P("Select Amount to Compare:"),
                dcc.Dropdown(id='num-dropdown', value='all'),
            ],
            className="selector",
        ),
        html.Div(
            [
                html.P("Enter Divisive Issue:"),
                dcc.Input(id="input-1", type="text"),
            ],
            className="selector",
        ),
        html.Div(
            [
                html.P("Compare Specific Accounts:"),
                dcc.Dropdown(
                    id="my-multi-dynamic-dropdown",
                    options=[{"label": i, "value": i} for i in accountlist],
                    multi=True),
            ],
            className="selector",
        ),
    ],
    ),
    dcc.Graph(id='DivisiveGraph'),


])

@app.callback(
    dash.dependencies.Output('num-dropdown', 'options'),
    [dash.dependencies.Input('datatype', 'value')]
)
def update_date_dropdown(name):
    if name == "all":
        num = len(typelist)
    else:
        test = typelist.str.match(name)
        num = len(test[test == True].index)
    numbers = ["all"]
    x = 0
    while x < num:
        if x + 50 > num:
            val = str(x) + " - " + str(num) + " (sorted by x-axis)"
        else:
            val = str(x) + " - " + str(x + 50)  + " (sorted by x-axis)"
        numbers.append(val)
        x = x + 50

    return [{'label': i, 'value': i} for i in numbers]


@app.callback(
    Output('DivisiveGraph', 'figure'),
    [Input('xaxis-type', 'value'),
    Input('yaxis-type', 'value'),
    Input('datatype', 'value'),
    Input('num-dropdown', 'value'),
    Input('input-1', 'value'),
    Input('my-multi-dynamic-dropdown', 'value')])
def update_graph(xaxis_type, yaxis_type,datatype, num_dropdown,input_1,my_multi_dynamic_dropdown ):
    accountcompare = my_multi_dynamic_dropdown
    if accountcompare:
        dataselect = people[people["name"].isin(accountcompare)]
    else:
        if datatype != "all":
            dataselect = people["type"].str.match(datatype)
            dataselect = people[dataselect == True]
        else:
            dataselect = people
        amount = num_dropdown
        if amount != "all":
            dataselect = dataselect.sort_values(by=[xaxis_type]).reset_index()
            nums = amount.split()
            dataselect = dataselect[(dataselect.index >= int(nums[0])) & (dataselect.index <= int(nums[2]))]

    df = pd.DataFrame(columns=["text"])
    dataselect["reach"] = dataselect["reach"]*(10/7305310427)
    df["text"] = dataselect["name"] + "<br>@" + dataselect["handle"] + "<br>" + "[" + dataselect["lastdate"] + " - " + dataselect["firstdate"] + "]"
    if input_1:
        tw1 = tweets[tweets['tweet'].str.contains(input_1)]
        DivisiveInd = int((1-(tw1["Neutral"].sum() / len(tw1["id"]))) * 100)
        dataselect = dataselect.assign(colourval=DivisiveInd)

    return {
        'data': [dict(
            x=dataselect[xaxis_type].values,
            y=dataselect[yaxis_type].values,
            text=df["text"],
            hoverinfo='text',
            mode='markers',
            marker={
                'size': dataselect["reach"].values,
                'sizemode' : 'area',
                'sizeref' : 2. * dataselect["reach"].max()/ (100. ** 2),
                'sizemin' : 4,
                'opacity': 0.5,
                'color' : dataselect["colourval"].values,
                'colorscale' : 'Reds',
                'cmax' : 100,
                'cmin' : 0,
                'colorbar': {
                    'title': "Divisive Level",
                    'ticksuffix': "% divisive"
                },
                'showscale' : True,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': axistitle.get(xaxis_type),
                'type': 'linear'
            },
            yaxis={
                'title': axistitle.get(yaxis_type),
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)