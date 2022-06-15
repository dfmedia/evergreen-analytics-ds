# Standard library imports
import os, sys
import dash

# Third party
from dash import Dash
# import dash_table
from dash import Dash, dash_table, dcc, html
# import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from flask import Flask

# Third party
# import dash, flask, psycopg2, dash_table, pickle, boto3, uuid, io
# import dash_core_components as dcc
# import pandas  as pd
# import dash_html_componentsf as html
# from flask import Flask
# import dash_daq as daq
# from dash.dependencies import Input, Output
# from sqlalchemy import create_engine
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# from dash import Dash
# from dash.dependencies import Input, Output
# import pandas as pd




### setup database
redshift_endpoint = os.environ.get('REDSHIFT_ENDPOINT')
redshift_user = os.environ.get('REDSHIFT_USER')
redshift_pass = os.environ.get('REDSHIFT_PASS')

port = 5439
dbname = "arthur2"

# create engine
# engine_string = "postgresql://%s:%s@%s:%d/%s" \
# % (redshift_user, redshift_pass, redshift_endpoint, port, dbname)
# engine = create_engine(engine_string)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


div_style = {'float': 'left',
'width': '75%'}


server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

df = pd.read_csv('two_weeks_merged.csv')

df = df.drop(columns=['Unnamed: 0', 'labels'])

# df = df[['slug','1','2','3','4','5','6']]



app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in ["slug", "0", "1","2","3","4","5","6"]
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        # column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ),
    html.Div(id='datatable-interactivity-container')
])

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))




def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.


    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    # default to only showing 10 rows
    dff = df.head() if rows is None else pd.DataFrame(rows[0:10])

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]
    # print(dff.columns)

    # transpose small dataframe
    df_small_trans = pd.DataFrame()
    col_str = list(dff.drop(columns=['slug']).columns)
    col_int = [int(x) + 1 for x in col_str]
    df_small_trans['days'] = col_int
    for i in dff['slug']:
        df_small_trans[i] = list(dff[dff['slug'] == i].drop(columns=['slug']).iloc[0])
    df_small_trans.sort_values(by="days", inplace=True)

    # create graph
    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": df_small_trans["days"],
                        "y": df_small_trans[column],
                        "type": "line",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in list(df_small_trans.drop(columns=['days']).columns) if column in df_small_trans
    ]

# def generate_table(dataframe, max_rows=10):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ])



# app.layout = html.Div([
#     html.H4(children='Views per Day'),
#     generate_table(df[['slug', '0', '1','2','3','4','5','6']])
# ])


if __name__ == '__main__':
    app.run_server(debug=True)

# df = pd.read_csv('two_weeks_merged.csv')
#
#
# app.layout = dash_table.DataTable(df.to_dict('slug'))
