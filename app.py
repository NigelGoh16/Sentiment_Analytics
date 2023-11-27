import base64
import datetime
import io

import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

from functions import simple_prediction, custom_prediction, word_cloud, word_table, yt_videos, yt_comments

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "z-index": "8000"}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",}

sidebar = html.Div([
        html.H2("Sentiment Analysis", className="display-5"),
        html.Hr(),
        html.P("Analysis Section", className="lead"),
        dbc.Nav([
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Simple Analysis", href="/page-1", active="exact"),
            dbc.NavLink("Custom Analysis", href="/page-2", active="exact"),
            dbc.NavLink("Youtube Analysis", href="/page-3", active="exact")
            ], vertical=True, pills=True),
        html.Hr(),
        html.Br(),
        html.P("Analysis Data History", className="lead"),
        dbc.Nav([
            dbc.NavLink("Simple Analysis", href="/page-4", active="exact", disabled=True),
            dbc.NavLink("Custom Analysis", href="/page-5", active="exact", disabled=True),
            dbc.NavLink("Youtube Analysis", href="/page-6", active="exact", disabled=True),
        ], vertical=True, pills=True)],
    style=SIDEBAR_STYLE,)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

def table_style(df, size=15, tooltip=0, row_selectable=False, row_deletable=False):
    if tooltip==0:
        table = dash_table.DataTable(
            id='datatable-interact',
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=size,
            style_data={'whiteSpace': 'normal',},
            css=[{'selector': '.dash-spreadsheet td div','rule': '''line-height: 15px; max-height: 36px; min-height: 30px; height: 40px; display: block; overflow-y: hidden; padding: 4px; width: fit-content; max-width: 350px;'''},
                {'selector': '.dash-table-tooltip', 'rule': '''width: fit-content; max-width: 1100px; position: fixed; bottom: 10; right: 10;'''}],
            tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
            tooltip_duration=None,
            style_cell={'textAlign': 'left'},
            filter_action="native",
            filter_options={"placeholder_text": "Filter column..."},
            sort_action="native",
            sort_mode='multi',
            row_selectable=row_selectable,
            selected_rows=[],
            row_deletable=row_deletable
        )
    else:
        table = dash_table.DataTable(
            id='datatable-interact',
            data=df.to_dict('records'), columns=[{'name': i, 'id': i} for i in df.columns], page_size=size, style_data={'whiteSpace': 'normal',},
            css=[{'selector': '.dash-spreadsheet td div','rule': '''line-height: 15px; max-height: 36px; min-height: 30px; height: 40px; display: block; overflow-y: hidden; padding: 4px'''}, {'selector': '.dash-table-tooltip', 'rule': '''width: fit-content; max-width: 1100px;'''}],
            style_cell={'textAlign': 'left'}
        )
    return table

def general_page(title, desc, placeholder="", button_text="", type=0):
    if type == 0:
        page =  [
                html.H1(title, style={'textAlign':'center'}),
                html.P(desc, className="lead", style={'textAlign':'center'}),
                html.Div(className='mx-auto d-grid col-6 p-2', children=[
                    dcc.Input(id='text', type='text', placeholder=placeholder)]),
                html.Br(),
                html.Div(className='d-flex justify-content-center', children=[
                    html.Button(button_text, id='button')]),
                html.Br(),
                html.Div(id='output', style={'textAlign':'center'})
                ]
    elif type == 1:
        page =  [
                html.H1(title, style={'textAlign':'center'}),
                html.P(desc, className="lead", style={'textAlign':'center'}),
                dcc.Upload(id='upload-data', 
                    className='d-flex justify-content-center mx-auto  d-grid col-6 p-4  bg-light border border-dashed rounded-3', 
                    children=html.Div(['Drag and Drop or ', html.A('Select Files')]), 
                    multiple=True,),
                html.Div(id='output-datatable')
                ]
    elif type == 2:
        page = [        
                html.Div(children=[
                    html.Div(children=[
                        html.Img(src=app.get_asset_url('Word gif.gif'))
                    ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),
                    html.Div(children=[
                        html.H1('Uncover the Emotional Pulse of the Web with', className='text-center base-light bebas'),
                        html.H1('Sentiment Analytics', className='text-center base-light bebas'),
                        html.P("Delve into the world of sentiment analysis and uncover the hidden emotions that drive online conversations. Our powerful web app empowers you to effortlessly analyze text, process custom files, and even extract insights from YouTube comment data.", className="lead text-center base-light"),
                        html.Br()
                    ], style={'position': 'absolute','top': '5px', 'padding-top': '10px', 'width': '83%', 'z-index': 1, 'background-color': '#212529', 'opacity': 0.9}),
                    html.Div(children=[
                        html.Div(children=[
                            html.Div(children=[
                                html.H1('Simple Analysis', className='text-center bebas'),
                                html.P('Instantly gauge the sentiment of any text snippet, from a sentence to a whole paragraph.', className='text-center'),
                                html.Div(className='d-flex justify-content-center', children=[
                                    html.A(children=[html.Button(id='simple-dir', children='Try Now!', className='btn btn-outline-light')], href="/simple-analysis")])
                            ], className='col-md-4 border div-home-dir'),
                            html.Div(children=[
                                html.H1('Custom Analysis', className='text-center bebas'),
                                html.P('Upload and analyze your own text files to gain a deeper understanding of their emotional content.', className='text-center'),
                                html.Div(className='d-flex justify-content-center', children=[
                                    html.A(children=[html.Button(id='custom-dir', children='Try Now!', className='btn btn-outline-light')], href="/custom-analysis")])
                            ], className='col-md-4 border div-home-dir'),
                            html.Div(children=[
                                html.H1('YouTube Analysis', className='text-center bebas'),
                                html.P('Tap into the vast trove of YouTube comments and uncover the underlying sentiment of online discussions.', className='text-center'),
                                html.Div(className='d-flex justify-content-center', children=[
                                    html.A(children=[html.Button(id='yt-dir', children='Try Now!', className='btn btn-outline-light')], href="/youtube-analysis")])
                            ], className='col-md-4 border div-home-dir'),
                        ], className='d-flex justify-content-between')
                    ], style={'position': 'absolute', 'width': '83%', 'z-index': 1, 'bottom': '10px'})
                ])
                ]
    return page

app.layout = html.Div([dcc.Location(id="url"), 
                       sidebar, 
                       content])

@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    [Input("url", "pathname")],
     prevent_initial_call=True
)
def render_page_content(pathname):
    general = []
    if pathname == "/":
        return [html.H1('Sentiment Data Analysis', style={'textAlign':'center'})]
    elif pathname == "/page-1":
        title, desc, placeholder, button_text = "Simple Analysis", "A simple text-based sentiment analysis", "Enter your text here", "Predict"
        return general_page(title, desc, placeholder, button_text)
    elif pathname == "/page-2":
        title, desc = "Custom Analysis", "A custom file-based sentiment analysis"
        return general_page(title, desc, type=1)
    elif pathname == "/page-3":
        title, desc, placeholder, button_text = "YouTube Analysis", "A YouTube-based sentiment analysis", "  Search for youtube videos with specific terms (For multiple terms, split it with \',\') ", "Search"
        return general_page(title, desc, placeholder, button_text)

@app.callback(Output('output-datatable', 'children'),
              [Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.P("Insert data column"),
        dcc.Dropdown(id='column-data',
                    options=[{'label':x, 'value':x} for x in df.columns]),
        html.Br(), html.Br(),
        html.Button(id="predict-button", children="Create Predictions"),
        html.Hr(),
        table_style(df),
        dcc.Store(id='stored-file', data=df.to_dict('records'), storage_type='session'),
        html.Hr(), 
    ])

@app.callback(
    Output('output', 'children'),
    Input('button', 'n_clicks'),
    Input("url", "pathname"),
    State('text', 'value'))
def page_buttons(btn, url, text):
    if btn is None:
        return dash.no_update
    else:
        if url == '/page-1':
            return simple_prediction(text)
        elif url == '/page-3':
            terms_list = text.split(',')
            videos_df = yt_videos(terms_list)
            return dbc.Container([
                dbc.Row([
                    dbc.Col(table_style(videos_df, row_selectable='multi'), md=12)]),
                dbc.Row([
                    html.Div(className='d-flex justify-content-center', children=[
                        html.Button('Add Video', id='video-button')]),
                dbc.Row([
                    html.Div(id='video-df', children=[])]),
                dcc.Store(id='stored-video-df', data=videos_df.to_dict('records'), storage_type='session')
            ])])

@app.callback(
    Output('output', 'children',allow_duplicate=True),
    [Input('datatable-interact', 'selected_rows'),
    State('stored-video-df','data'),
    Input('video-button', 'n_clicks')],
    prevent_initial_call=True)
def video_data(all_rows, video_dict, btn):
    if btn is None:
        return dash.no_update
    else:
        return dbc.Container([
            dbc.Row([
                dbc.Col(table_style(filtered_df:=(pd.DataFrame(video_dict)).loc[all_rows, ['Video_ID', 'Title']]), md=12)]),
            html.Br(),
            dbc.Row([
                dbc.Col(table_style(comments_df:=yt_comments(filtered_df, order='relevance')), md=12)]),
            dbc.Row([
                html.Div(className='d-flex justify-content-center', children=[html.Button('Predict', id='yt-predict')])]),
            dcc.Store(id='stored-comment-df', data=comments_df.to_dict('records'), storage_type='session')])

@app.callback(
    Output('page-content','children',allow_duplicate=True),
    [Input('yt-predict','n_clicks'),
    State('stored-comment-df','data')],
    prevent_initial_call=True)
def youtube_preds(n, data):
    if n is None:
        return dash.no_update
    else:
        fig1 = px.bar(new_data := custom_prediction(df := pd.DataFrame(data), x_data:="Comment"), x=new_data['Predictions'].unique().tolist(), y=new_data['Predictions'].value_counts().tolist())
        fig1.update_layout(title='Sentiment Counts', xaxis_title='Sentiment', yaxis_title='Count', titlefont=dict(family='Arial', size=20, color='black'), width=600, height=500)
        fig2 = px.scatter(custom_prediction(df, x_data:="Comment", type=1).groupby(['Date', 'Video_Title']), x='Date', y='Average_Predictions', color='Video_Title', size='Number_Of_Comments')
        fig2.update_layout(title='Sentiment Over Time', yaxis_title='Average Sentiment Polarity', titlefont=dict(family='Arial', size=20, color='black'))
        image_data, word_data = word_cloud(new_data, x_data), word_table(new_data, x_data)
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig1), md=6),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Sentiment Word Cloud", style={'font-family': 'Arial', 'font-size': '20px', 'color': 'black', 'background-color':'white'}),
                    dbc.CardBody(html.Img(src="data:image/png;base64," + image_data))], style={'border-color':'white', 'padding-top': 15}), md=6),]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig2), md=12)]),
            dbc.Row([
                dbc.Col(table_style(new_data[[x_data, 'Predictions']]), md=6),
                dbc.Col(table_style(word_data, tooltip=1), md=6)]),
            dbc.Row([
                html.Div(children=[html.A(children=[html.Button(id='yt-back', children='Reset', className='btn btn-outline-danger')], href="/youtube-analysis")], className='d-flex justify-content-center pt-2 pb-4')])])

@app.callback(
    Output('page-content','children',allow_duplicate=True),
    [Input('predict-button','n_clicks'),
    State('stored-file','data'),
    State('column-data','value')],
    prevent_initial_call=True)
def custom_preds(n, data, x_data):
    if n is None:
        return dash.no_update
    else:
        fig1 = px.bar(new_data:= custom_prediction(pd.DataFrame(data), x_data), x=new_data['Predictions'].unique().tolist(), y=new_data['Predictions'].value_counts().tolist())
        fig1.update_layout(title='Sentiment Counts', xaxis_title='Sentiment', yaxis_title='Count', titlefont=dict(family='Arial', size=20, color='black'), width=600, height=500)
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig1), md=6),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Sentiment Word Cloud", style={'font-family': 'Arial', 'font-size': '20px', 'color': 'black', 'background-color':'white'}),
                    dbc.CardBody(html.Img(src="data:image/png;base64," + word_cloud(new_data, x_data)))], style={'border-color':'white', 'padding-top': 15}), md=6),]),
            dbc.Row([
                dbc.Col(table_style(new_data[[x_data, 'Predictions']]), md=6),
                dbc.Col(table_style(word_table(new_data, x_data), tooltip=1), md=6)]),
            dbc.Row([
                html.A(children=[html.Button(id='custom-back', children='Reset', className='btn btn-primary')], href="/custom-analysis"), html.Br()], className='d-flex justify-content-center pb-4')])

if __name__=='__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)