# Link to published dashboard: 

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import flask

world_cup_data = pd.DataFrame({
    "year": [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
    "winners": ["Uruguay", "Italy", "Italy", "Uruguay", "Germany", "Brazil", "Brazil", "England", "Brazil", "Germany", "Argentina", "Italy", "Argentina", "Germany", "Brazil", "France", "Brazil", "Italy", "Spain", "Germany", "France", "Argentina"],
    "runner_ups": ["Argentina", "Czechoslovakia", "Hungary", "Brazil", "Hungary", "Sweden", "Czechoslovakia", "Germany", "Italy", "Netherlands", "Netherlands", "Germany", "Germany", "Argentina", "Italy", "Brazil", "Germany", "France", "Netherlands", "Argentina", "Croatia", "France"]
})
wins_count = world_cup_data['winners'].value_counts().reset_index()
wins_count.columns = ['country', 'wins']

server = flask.Flask(__name__)
app = Dash(__name__, server=server)

app.layout = html.Div([
    html.H1("FIFA Soccer World Cup winners and runner-ups", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='map-type',
        options=[
            {'label': 'Countries that have won a World Cup', 'value': 'wins'},
            {'label': 'The winner and the runner-up by year', 'value': 'years'}
        ],
        value='wins',
        style={'width': '100%', 'margin': '25px auto'}
    ),
    dcc.Dropdown(
        id='year-selector',
        options=[{'label': year, 'value': year} for year in world_cup_data['year']],
        value=2022,
        style={'width': '100%', 'margin': '25px auto', 'display': 'none'}
    ),
    dcc.Graph(id='world-map'),
    html.Div(id='results-info', style={'margin': '25px', 'textAlign': 'center'})
])

@app.callback(
    [Output('world-map', 'figure'),
     Output('year-selector', 'style'),
     Output('results-info', 'children')],
    [Input('map-type', 'value'),
     Input('year-selector', 'value')]
)
def update_map(map_type, selected_year):
    if map_type == 'wins':
        fig = px.choropleth(
            wins_count,
            locations="country",
            locationmode="country names",
            color="wins",
            hover_name="country",
            hover_data=["wins"],
            color_continuous_scale=px.colors.sequential.Greens,
            title="Wins by Country",
            labels={'wins': 'Number of Wins'},
            projection="natural earth"
        ) 
        style = {'width': '100%', 'margin': '25px auto'}
        info = html.Div([
            html.H3("Country and the number of times it has won a World Cup"),
            html.Ul([html.Li(f"{row['country']}: {row['wins']}") 
                    for _, row in wins_count.iterrows()])
        ])   
    else:
        year_data = world_cup_data[world_cup_data['year'] == selected_year].iloc[0]
        results_df = pd.DataFrame({
            'country': [year_data['winners'], year_data['runner_ups']],
            'result': ['Winner', 'Runner-up'],
            'wins': [1, 1] 
        })
        fig = px.choropleth(
            results_df,
            locations="country",
            locationmode="country names",
            color="result",
            hover_name="country",
            color_discrete_map={'Winner': 'blue', 'Runner-up': 'red'},
            title=f"{selected_year} Winner and Runner-up",
            projection="natural earth"
        )
        style = {'width': '100%', 'margin': '25px auto'}
        info = html.Div([
            html.H3(f"{selected_year} World Cup Final"),
            html.P(f"Winner: {year_data['winners']}", style={'color': 'blue', 'fontWeight': 'bold'}),
            html.P(f"Runner-up: {year_data['runner_ups']}", style={'color': 'red'})
        ])
    fig.update_geos(
        showcountries=True, 
        showcoastlines=True,
        countrycolor="black",
        showocean=True,
        oceancolor="skyblue"
    )
    fig.update_layout()
    return fig, style, info
if __name__ == '__main__':
    app.run_server(debug=True)
