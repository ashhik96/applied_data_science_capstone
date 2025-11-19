# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Build list of launch site options (Task 1 helper)
launch_sites = spacex_df['Launch Site'].unique()
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options += [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie chart for total successful launches / success vs failure
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # TASK 4: Scatter chart to show correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If ALL sites selected, show total success launches for each site
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            filtered_df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # For a specific site, show success (1) vs failed (0) counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Total Launch Outcomes for site {entered_site}'
        )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter(entered_site, payload_range):
    low, high = payload_range
    # Filter by payload range first
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # If ALL sites selected, use all sites
    if entered_site == 'ALL':
        title = 'Correlation between Payload and Success for all Sites'
    else:
        df_filtered = df_filtered[df_filtered['Launch Site'] == entered_site]
        title = f'Correlation between Payload and Success for site {entered_site}'

    fig = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
