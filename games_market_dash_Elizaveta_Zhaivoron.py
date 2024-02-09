from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc


PALETTE = px.colors.sequential.Plasma

df = pd.read_csv('./games.csv').dropna()

df['Year_of_Release'] = df['Year_of_Release'].astype(int)

# check if scores can be converted to numeric and remove rows that cannot
for column in ['Critic_Score', 'User_Score']:
    df = df[pd.to_numeric(df[column], errors='coerce').notnull()]

df = df.loc[
    (
        df['Year_of_Release'] >= 2000
    ) & (
        df['Year_of_Release'] <= 2022
    )
]

df['User_Score'] = pd.to_numeric(df['User_Score'])
df['Critic_Score'] = pd.to_numeric(df['Critic_Score'])


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

default_style = {
    "padding": 10,
}

min_year = df['Year_of_Release'].min()
max_year = df['Year_of_Release'].max()

app.layout = html.Div([
    html.H1(
        "Games Dashboard",
        style=default_style,
    ),
    html.Hr(),
    html.P(
        children='This dashboard allows you to find out various statistics about the games dataset. You can  select different filters: Platform (multi-choice), Genre (multi-choice), Year of release (range from and to). Total number of games, average players score, average critics score, and the number of games by year and platform, critics and players rating by genre, and games age ratings by genre plots will change corresponding to the specified filters.',
        style=default_style,
    ),
    dbc.Row(
        [
            dbc.Col(
                children=[
                    html.Label('Platform'),
                    dcc.Dropdown(
                        df['Platform'].unique().tolist(),
                        [],
                        multi=True,
                        id='platform-dropdown'
                    ),
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.Label('Genre'),
                    dcc.Dropdown(
                        df['Genre'].unique().tolist(),
                        [],
                        multi=True,
                        id='genre-dropdown',
                    ),
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.Label('Year of release'),
                    dcc.RangeSlider(
                        min_year,
                        max_year,
                        1, 
                        value=[min_year,max_year], 
                        id='release-slider',
                        marks={
                            i: '{}'.format(i) for i in df['Year_of_Release'].unique().tolist()
                        }
                    ),
                ],
                width=4
            ),
        ],
        align="center",
        style=default_style
    ),
    dbc.Row(
        [
            dbc.Col(
                children=[
                    html.Label('Total number of games'),
                    html.H1(
                        '',
                        id='count-games'
                    )
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.Label("Average players' score"),
                    html.H1(
                        '',
                        id='avg-players'
                    )
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.Label("Average critics' score"),
                    html.H1(
                        '',
                        id='avg-critics'
                    )
                ],
                width=4
            ),
        ],
        align="center",
        style=default_style
    ),
    dbc.Row(
        [
            dbc.Col(
                children=[
                    html.Label("Games by year"),
                    dcc.Graph(id='stacked-by-year'),
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.Label("Scores by genre"),
                    dcc.Graph(id='scatter-by-genre'),
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.Label("Average critics' score by genre"),
                    dcc.Graph(id='graph-critics-by-genre'),
                ],
                width=4
            ),
        ],
        align="center",
        style=default_style
    ),
])

@callback(
    Output(component_id='count-games', component_property='children'),
    Output(component_id='avg-players', component_property='children'),
    Output(component_id='avg-critics', component_property='children'),
    Output('stacked-by-year', 'figure'),
    Output('scatter-by-genre', 'figure'),
    Output('graph-critics-by-genre', 'figure'),
    Input('platform-dropdown', 'value'),
    Input('genre-dropdown', 'value'),
    Input('release-slider', 'value'),
)
def callback(platforms, genres, years):
    local_df = df.copy()
    if len(platforms) != 0:
        local_df = local_df.loc[local_df['Platform'].isin(platforms)]
    if len(genres) != 0:
        local_df = local_df.loc[local_df['Genre'].isin(genres)]
    if len(years) != 0:
        local_df = local_df.loc[
            (
                df['Year_of_Release'] >= years[0]
            ) & (
                df['Year_of_Release'] <= years[1]
            )
        ]
    first_df = local_df.groupby(['Platform','Year_of_Release']).count().reset_index()
    first_fig = px.area(
        first_df,
        x="Year_of_Release",
        y="Name",
        color="Platform", 
        line_group="Platform",
        color_discrete_sequence=PALETTE,
        labels={
            "Year_of_Release": "Year",
            "Name": "Number of games",
        },
    )
    second_fig = px.scatter(
        local_df,
        x='User_Score',
        y='Critic_Score',
        color='Genre',
        color_discrete_sequence=PALETTE,
        labels={
            "User_Score": "User score",
            "Critic_Score": "Critic score",
            "Genre": "Game's genre"
        },
    )
    third_df = local_df.groupby(['Genre'])['Rating'].agg(pd.Series.mode).reset_index()
    third_fig = px.line(
        third_df,
        x='Genre',
        y='Rating',
        color_discrete_sequence=PALETTE,
        labels={
            "index": "Genres",
            "value": "Average critics score",
            "Genre": "Game's genre"
        },
    )

    return [
        len(local_df["Name"].unique().tolist()),
        round(local_df["User_Score"].mean(), 2),
        round(local_df["Critic_Score"].mean(), 2),
        first_fig,
        second_fig,
        third_fig,
    ]



if __name__ == '__main__':
    app.run(debug=True)