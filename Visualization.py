import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash.dependencies import Output, Input
import os

# Dark theme by default
pio.templates.default = "plotly_dark"

necessary_columns = ['year', 'type_of_violence', 'region', 'latitude', 'longitude', 'deaths_a', 'deaths_b', 'deaths_civilians', 'best', 'conflict_name', 'country']
df = pd.read_parquet('combined_ged_event_data.parquet', engine='pyarrow', columns=necessary_columns)


# Decades function
def create_decade(year):
    return f'{(year // 10) * 10}s'
df['decade'] = df['year'].apply(create_decade)

# Filters:
available_years = ['All'] + sorted(df['year'].unique())
available_decades = ['All'] + sorted(df['decade'].unique())
available_regions = ['All'] + sorted(df['region'].unique())
available_types_of_violence = {
    'All': 'All Types',
    1: 'State-based conflict',
    2: 'Non-state conflict',
    3: 'One-sided violence'
}

violence_type_labels = {
    1: 'State-based conflict',
    2: 'Non-state conflict',
    3: 'One-sided violence'
}

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Conflict Data Analysis", id='page-title', style={'textAlign': 'left'}), width=8
        ),
        dbc.Col([
            html.Label('Dark Mode', style={'color': 'white', 'marginRight': '10px'}),
            dbc.Switch(id='theme-switch', value=True, style={'display': 'inline-block'})
        ], width=3, style={'textAlign': 'right'})
    ], className="mb-4"),

    # Filters:
    dbc.Row([
        dbc.Col([
            html.Label("Select Year", id='year-label', style={'color': 'white'}),
            dcc.Dropdown(id='year-filter', options=[{'label': str(year), 'value': year} for year in available_years],
                         value=['All'], multi=True, clearable=False)
        ], width=3),
        dbc.Col([
            html.Label("Select Decade", id='decade-label', style={'color': 'white'}),
            dcc.Dropdown(id='decade-filter',
                         options=[{'label': decade, 'value': decade} for decade in available_decades],
                         value='All', clearable=False)
        ], width=3),
        dbc.Col([
            html.Label("Select Region", id='region-label', style={'color': 'white'}),
            dcc.Dropdown(id='region-filter',
                         options=[{'label': region, 'value': region} for region in available_regions],
                         value='All', clearable=False)
        ], width=3),
        dbc.Col([
            html.Label("Select Type of Violence", id='violence-label', style={'color': 'white'}),
            dcc.Dropdown(id='violence-filter', options=[{'label': v_label, 'value': v_key} for v_key, v_label in
                                                        available_types_of_violence.items()],
                         value='All', clearable=False)
        ], width=3)
    ]),

    # Graphs:
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series-graph'), width=6),
        dbc.Col(dcc.Graph(id='mortality-pie-chart'), width=6)
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='event-map'), width=12)
    ])
], fluid=True, id='page-content', style={'backgroundColor': '#2b2b2b'})


# Callback theme:
@app.callback(
    [Output('page-content', 'style'),
     Output('page-title', 'style'),
     Output('year-label', 'style'),
     Output('decade-label', 'style'),
     Output('region-label', 'style'),
     Output('violence-label', 'style')],
    [Input('theme-switch', 'value')]
)
def update_theme(is_dark):
    if is_dark:
        page_style = {'backgroundColor': '#2b2b2b'}
        text_style = {'color': 'white'}
    else:
        page_style = {'backgroundColor': '#ffffff'}
        text_style = {'color': 'black'}

    return page_style, text_style, text_style, text_style, text_style, text_style


# Callback graphs:
@app.callback(
    [Output('time-series-graph', 'figure'),
     Output('mortality-pie-chart', 'figure'),
     Output('event-map', 'figure')],
    [Input('year-filter', 'value'),
     Input('decade-filter', 'value'),
     Input('region-filter', 'value'),
     Input('violence-filter', 'value'),
     Input('theme-switch', 'value')]
)
def update_graphs(selected_years, selected_decade, selected_region, selected_violence_type, is_dark):
    template = 'plotly_dark' if is_dark else 'plotly'
    filtered_df = df.copy()
    if 'All' not in selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    if selected_decade != 'All':
        filtered_df = filtered_df[filtered_df['decade'] == selected_decade]
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if selected_violence_type != 'All':
        filtered_df = filtered_df[filtered_df['type_of_violence'] == selected_violence_type]

    # Line graph
    conflicts_per_year = filtered_df.groupby('year')['conflict_name'].nunique().reset_index(
        name='unique_conflict_count')
    time_series_fig = px.line(conflicts_per_year, x='year', y='unique_conflict_count',
                              title='Number of Unique Conflicts Over Years',
                              labels={'year': 'Year', 'unique_conflict_count': 'Number of Unique Conflicts'},
                              template=template)
    time_series_fig.update_layout(xaxis=dict(tickmode='linear'))

    # Pie Chart
    total_deaths = filtered_df[['deaths_a', 'deaths_b', 'deaths_civilians']].sum().reset_index()
    total_deaths.columns = ['death_type', 'death_count']
    total_deaths['death_type'] = total_deaths['death_type'].map({
        'deaths_a': 'Side A Deaths',
        'deaths_b': 'Side B Deaths',
        'deaths_civilians': 'Civilian Deaths'
    })
    pie_chart_fig = px.pie(total_deaths, values='death_count', names='death_type',
                           title='Distribution of Deaths by Category',
                           color='death_type', color_discrete_map={
            'Side A Deaths': '#A9A9A9',
            'Side B Deaths': '#2F4F4F',
            'Civilian Deaths': '#DC143C'
        }, template=template)
    pie_chart_fig.update_traces(textinfo='label+percent', showlegend=True)

    # Map
    filtered_df['type_of_violence'] = filtered_df['type_of_violence'].map(violence_type_labels)
    event_map_fig = px.scatter_mapbox(filtered_df, lat='latitude', lon="longitude", size="best", color="region",
                                      hover_name="country",
                                      hover_data={"year": True, "type_of_violence": True, "best": ':.0f'},
                                      zoom=1, height=600, title="Geographical Distribution of Conflict Events",
                                      mapbox_style="carto-darkmatter" if is_dark else "carto-positron",
                                      template=template)
    event_map_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,1)')
    event_map_fig.update_traces(
        hovertemplate="<b>Country: %{hovertext}</b><br>" +
                      "Year: %{customdata[0]}<br>" +
                      "Type of Violence: %{customdata[1]}<br>" +
                      "Most Likely Deaths: %{marker.size}<br>")

    return time_series_fig, pie_chart_fig, event_map_fig


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=int(os.environ.get("PORT", 8050)))

