# coding=utf-8
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import requests
import pandas as pd
from polymatica import Polymatica



def main():
    # Создаем объект Polymatica
    poly = Polymatica('admin1', 'admin1', requests.Session(), "http://10.0.11.150:8080/")

    if poly.retcode == -1:
        print('Ошибка авторизации')
        exit()

    if poly.retcode == -2:
        print('Невозможно открыть слой')
        exit()

    if poly.retcode == -3:
        print('Не найден куб uni...')
        exit()

    if poly.retcode == -4:
        print('Невозможно открыть куб uni...')
        exit()

    if poly.retcode == -5:
        print('Размерности не получены')
        exit()

    cube_name_1 = poly.get_cube_1('Uni45')# Вводим название куба ()
    cube_name_2 = poly.get_cube_2('Uni3')
    cube_name_3 = poly.get_cube_3('Uni12')

    dimensions_and_facts_names_1 = poly.get_the_dimensions_and_facts_1(['CATEGORY_SHORT_NAME', 'BANNER_SHORT_NAME'], ['Loss qty']) #ЭТО НАШ ФРЕЙМ ДАННЫХ!!!!!!
    dimensions_and_facts_names_2 = poly.get_the_dimensions_and_facts_2(['CATEGORY_SHORT_NAME'], ['Closing Stock(Proj.)', 'Total Shortfall', 'UFO'])
    dimensions_and_facts_names_3 = poly.get_the_dimensions_and_facts_3(['CATEGORY_SHORT_NAME', 'Week for report'], ['Loss qty', 'DR, %'])

    app = dash.Dash()

    app.css.append_css({"external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"})

    colors = ['#5F9EA0', '#4682B4', '#B0C4DE', '#B0E0E6', '#ADD8E6', '#87CEEB', '#87CEFA', '#00BFFF', '#1E90FF','#6495ED', '#7B68EE', '#4169E1']

    group = dimensions_and_facts_names_3.groupby('Week for report').mean().reset_index()

    app.layout = html.Div(style={'backgroundColor': '#FFFFFF'}, children=[
        html.Div([
            html.H1(),
            dcc.Dropdown(
                id='country-dropdown1',
                options=[{'label': i, 'value': i} for i in dimensions_and_facts_names_1.CATEGORY_SHORT_NAME.unique()],
                multi=True,
                value=dimensions_and_facts_names_1.CATEGORY_SHORT_NAME.unique(),
                placeholder='Выберите категорию:'
            )
        ]
        ),
        html.Div([
            dcc.Graph(
                id='graph_0',
                figure={
                    'data': [
                        go.Scatter(
                            x=group['Week for report'],
                            y=group['DR, %'],
                            marker=dict(color='#FFD700'),
                        )],
                    'layout': go.Layout(
                        plot_bgcolor='#696969',
                        paper_bgcolor='#696969',
                        font=dict(family='Courier New, monospace', size=9, color='#FFFFFF'),
                        title='Line Graph Week for Report and DR %',
                        xaxis={'title': 'Week for report', 'linecolor': '#FFFFFF'},
                        yaxis={'title': 'DR %', 'linecolor': '#FFFFFF'}
                    ),
                }
            ),
        ], className='col-md-4'),
        html.Div([
            dcc.Graph(
                id='graph_1')
        ], className='col-md-4'),
        html.Div([
            dcc.Graph(
                id='graph_3')
        ], className='col-md-4'),
        html.Div([
            dcc.Graph(
                id='graph_4')
        ], className='col-md-4'),
        html.Div([
            dcc.Graph(
                id='graph_5')],
            className='col-md-4'),
        html.Div([
            dcc.Graph(
                id='graph_6')
        ], className='col-md-4')
    ])
    @app.callback(
        dash.dependencies.Output('graph_3', 'figure'),
        [dash.dependencies.Input('country-dropdown1', 'value')])
    def update_graph(country_values):
        dff = dimensions_and_facts_names_1.loc[dimensions_and_facts_names_1['CATEGORY_SHORT_NAME'].isin(country_values)]

        return {
            'data': [go.Bar(
                x=dff[dff['BANNER_SHORT_NAME'] == i]['Loss qty'],
                y=dff[dff['BANNER_SHORT_NAME'] == i]['CATEGORY_SHORT_NAME'],
                orientation='h',
                name=i,
                marker={
                    'color': colors[color]
                }
            ) for i, color in zip(dff['BANNER_SHORT_NAME'].unique(), range(len(dff['BANNER_SHORT_NAME'].unique())))],
            'layout': go.Layout(
                plot_bgcolor='#696969',
                paper_bgcolor='#696969',
                font=dict(family='Courier New, monospace', size=9, color='#FFFFFF'),
                barmode='stack',
                title='Loss Qty in CS, by Category and Banner',
                xaxis={'title': 'Loss Qty', 'linecolor':'#FFFFFF'},
                yaxis={'title': 'Category', 'linecolor':'#FFFFFF'},


            ),
        }

    @app.callback(
        dash.dependencies.Output('graph_6', 'figure'),
        [dash.dependencies.Input('country-dropdown1', 'value'),
         ])
    def update_graph(country_values):
        dff = dimensions_and_facts_names_1.loc[dimensions_and_facts_names_1['CATEGORY_SHORT_NAME'].isin(country_values)]
        return {
            'data': [go.Bar(
                x=dff[dff['CATEGORY_SHORT_NAME'] == i]['Loss qty'],
                y=dff[dff['CATEGORY_SHORT_NAME'] == i]['BANNER_SHORT_NAME'],
                orientation='h',
                name=i,
                marker={
                    'color': colors[color]
                }
            ) for i, color in zip(dff['CATEGORY_SHORT_NAME'].unique(), range(len(dff['CATEGORY_SHORT_NAME'].unique())))],
            'layout': go.Layout(
                plot_bgcolor='#696969',
                paper_bgcolor='#696969',
                font=dict(family='Courier New, monospace', size=9, color='#FFFFFF'),
                barmode='stack',
                title='Loss Qty in CS, by Banner and Category',
                xaxis={'title': 'Loss Qty', 'linecolor':'#FFFFFF'},
                yaxis={'title': 'Banner', 'linecolor':'#FFFFFF'},
            ),
        }

    @app.callback(
        dash.dependencies.Output('graph_5', 'figure'),
        [dash.dependencies.Input('country-dropdown1', 'value'),
         ])
    def update_graph(country_values):
        dff = dimensions_and_facts_names_2.loc[dimensions_and_facts_names_2['CATEGORY_SHORT_NAME'].isin(country_values)]

        traces = []

        traces.append({'x': dff['UFO'],
                       'y': dff['CATEGORY_SHORT_NAME'],
                       'type': 'bar',
                       'orientation': 'h',
                       'name': 'UFO',
                       'marker': {'color': '#5F9EA0'}})
        traces.append({'x': dff['Total Shortfall'],
                       'y': dff['CATEGORY_SHORT_NAME'],
                       'type': 'bar',
                       'orientation': 'h',
                       'name': 'Total Shortfall',
                       'marker': {'color': '#4682B4'}})
        traces.append({'x': dff['Closing Stock(Proj.)'],
                       'y': dff['CATEGORY_SHORT_NAME'],
                       'type': 'bar',
                       'orientation': 'h',
                       'name': 'Closing Stock(Proj.)',
                       'marker': {'color': '#B0C4DE'}})

        figure = {
            'data': traces,
            'layout':
                go.Layout(
                    plot_bgcolor='#696969',
                    paper_bgcolor='#696969',
                    font=dict(family='Courier New, monospace', size=8, color='#FFFFFF'),
                    title='Projected Losses And Total Shortfall In CS, By Category',
                    barmode='stack',
                    xaxis={'title': 'CS', 'linecolor':'#FFFFFF'},
                    yaxis={'title': 'Category', 'linecolor': '#FFFFFF'})

        }
        return figure

    @app.callback(
        dash.dependencies.Output('graph_4', 'figure'),
        [dash.dependencies.Input('country-dropdown1', 'value'),
         ])
    def update_graph(country_values):
        dff = dimensions_and_facts_names_3.loc[dimensions_and_facts_names_3['CATEGORY_SHORT_NAME'].isin(country_values)]

        group = dimensions_and_facts_names_3.groupby('Week for report').mean().reset_index()

        traces = []

        traces.append({'x': group['Week for report'],
                       'y': group['DR, %'],
                       'type': 'scatter',
                       'name': 'DR, %',
                       'yaxis': 'y2',
                       'marker': {'color': '#FFD700', 'opacity': 0.5}})

        for i, color in zip(dff['CATEGORY_SHORT_NAME'].unique(), range(len(dff['CATEGORY_SHORT_NAME'].unique()))):
            traces.append({'x': dff[dff['CATEGORY_SHORT_NAME'] == i]['Week for report'],
                           'y': dff[dff['CATEGORY_SHORT_NAME'] == i]['Loss qty'],
                           'type': 'bar',
                           'name': i,
                           'marker': {'color': colors[color]}})

            figure = {
            'data': traces,
            'layout':
                go.Layout(
                    #showlegend=False,
                    plot_bgcolor='#696969',
                    paper_bgcolor='#696969',
                    font=dict(family='Courier New, monospace', size=9, color='#FFFFFF'),
                    title='Loss Qty In CS, By Week',
                    barmode='stack',
                    xaxis={'title': 'Week for report', 'linecolor': '#FFFFFF'},
                    yaxis={'title': 'Loss qty', 'side': 'left', 'linecolor': '#FFFFFF'},
                    yaxis2={'overlaying': 'y', 'linecolor': '#FFFFFF', 'showticklabels': False},
                    #legend=dict( y=-0.3)
                ),
        }
        return figure

    @app.callback(
        dash.dependencies.Output('graph_1', 'figure'),
        [dash.dependencies.Input('country-dropdown1', 'value')])
    def update_graph(country_values):
        dff = dimensions_and_facts_names_2.loc[dimensions_and_facts_names_2['CATEGORY_SHORT_NAME'].isin(country_values)]
        return {
            'data': [go.Pie(
                values=dff['Total Shortfall'],
                labels=dff['CATEGORY_SHORT_NAME'],
                hoverinfo='label+percent',
                marker=dict({
                    'colors':colors

                })

            )
            ],
            'layout': go.Layout(
                plot_bgcolor='#696969',
                paper_bgcolor='#696969',
                font=dict(family='Courier New, monospace', size=9, color='#FFFFFF'),
                barmode='stack',
                title='Category and Total Shortfall in Percent',
            )
        }

    app.run_server()


if __name__ == "__main__":
    main()






    


