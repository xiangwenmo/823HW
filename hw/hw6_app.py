import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import itertools as it

app = dash.Dash()

table17 = pd.read_excel('/home/moluosirius/mysite/data/sed17-sr-tab017.xlsx', skiprows = 3)
table17 = table17.rename(columns = {'Field of study and citizenship status':'Fields'})
table17["Major"] = list(it.chain.from_iterable(it.repeat(x, 4) for x in table17.Fields if x not in
                                               ["U.S. citizen or permanent resident","Temporary visa holder",
                                               'Unknown']))
status = pd.concat([table17[table17.Fields=="U.S. citizen or permanent resident"],
                    table17[table17.Fields=="Temporary visa holder"], table17[table17.Fields=="Unknown"]], axis = 0)
status = status.rename(columns = {'Fields': 'Status'})
fields = status.Major.unique().tolist()
statusg = status.groupby(['Major', 'Status']).sum()
statusp = statusg.groupby(level = 0).apply(lambda g: g/g.sum()).round(3)
grp = statusp.unstack()
grp.columns = ['%s%s' % (a, '_%s' % b) for a, b in grp.columns]
years = statusg.columns.tolist()
grp_temp = grp.filter(regex = 'Temporary')
grp_us = grp.filter(regex = 'U.S.')
grp_unk = grp.filter(regex = 'Unknown')

table12 = pd.read_excel('/home/moluosirius/mysite/data/sed17-sr-tab012.xlsx', skiprows=4)
table12.columns = ['Fields', '1987N', '1987P','1992N','1992P','1997N','1997P','2002N','2002P','2007N','2007P',
                  '2012N','2012P','2017N','2017P']
field_trend=(
    table12.loc[table12['Fields'].isin(fields[1:])].
    set_index("Fields").
    filter(regex = 'P')
)
field_trend.columns = field_trend.columns.str.replace(pat='P', repl='')

field_num=(
    table12.loc[table12['Fields'].isin(fields[1:])].
    set_index("Fields").
    filter(regex = 'N')
)
field_num.columns = field_num.columns.str.replace(pat='N', repl='')

app.layout = html.Div([
    html.H1(children='Doctorate Recipients from US universities'),
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='Majors',
                options=[{'label': i, 'value': i} for i in fields],
                value=fields[0]
            )
        ],
        style={'width': '45%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='Fields',
                options=[{'label': i, 'value': i} for i in fields[1:]],
                value=fields[1]
            ),

        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(id='citizenship'),
    ], style={'width': '45%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='percent-fields'),
        dcc.Graph(id='number-fields'),
    ], style={'display': 'inline-block', 'width': '49%', 'float': 'right'})
])

@app.callback(
    dash.dependencies.Output('percent-fields', 'figure'),
    [dash.dependencies.Input('Fields', 'value')])
def update_percent_graph(field):
    return {
        'data': [go.Scatter(
            x=years,
            y=field_trend.loc[field,:].values,
            mode='lines+markers'
        )],
        'layout': {
            'height': 230,
            'margin': {'l': 30, 'b': 30, 'r': 5, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': 'Doctorates awarded share in broad fields of study'
            }]
        }
    }

@app.callback(
    dash.dependencies.Output('number-fields', 'figure'),
    [dash.dependencies.Input('Fields', 'value')])
def update_number_graph(field):
    return {
        'data': [go.Scatter(
            x=years,
            y=field_num.loc[field,:].values,
            mode='lines+markers'
        )],
        'layout': {
            'height': 230,
            'margin': {'l': 30, 'b': 30, 'r': 5, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': 'Doctorates awarded number in broad fields of study'
            }]
        }
    }

@app.callback(
    dash.dependencies.Output('citizenship', 'figure'),
    [dash.dependencies.Input('Majors', 'value')])
def update_citizen_graph(major):
    trace1 = go.Bar(x=years,
                    y=grp_temp.loc[major,:].values,
                    name='Temporary visa holder')
    trace2 = go.Bar(x=years,
                    y=grp_us.loc[major,:].values,
                    name='U.S. citizen or permanent resident')
    trace3 = go.Bar(x=years,
                    y= grp_unk.loc[major,:].values,
                    name='Unknown')
    return {
        'data': [trace1, trace2, trace3],
        'layout': go.Layout(
            barmode='stack',
            xaxis=dict(tickvals=statusg.columns.tolist()),
            yaxis={
                'title': 'Percent of PhDs awarded by citizenship'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server()
