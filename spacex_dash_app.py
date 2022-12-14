# Install the required things
import subprocess, sys

# Import required libraries with the possibility of having to install them with pip.

try:
    import pandas as pd
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])    
    import pandas as pd

try:
    import dash
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'dash'])
    import dash

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'dash'])
    import numpy as np

from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Add a column which combines the launch site name with the outcome
# and a dummy variable of 1 for each row. This seems necessary in
# order to have plotly render a pie chart which correctly shows the
# percentages of successful landings compared to unsuccesful landings
# for each launch site.

success = []
dummy = np.ones(spacex_df.shape[0], dtype=int)

for r in range(0,spacex_df.shape[0]):
    LS = spacex_df.loc[r,'Launch Site']
    S =  spacex_df.loc[r,'class']
    if S == 1:
        success.append(LS + ' Success')
    else:
        success.append(LS + ' Failure')

spacex_df['LS Status'] = success
spacex_df['dummy'] = dummy

# Create launch site options list
ls_ddopt = ['ALL'] # create the ALL sites entry
for col in spacex_df['Launch Site'].unique(): # add entries for each launch site
    ls_ddopt.append(col)

# DEBUG
# print('Type ls_ddopt', type(ls_ddopt))
# for debug in ls_ddopt:
#     print('Debug ls_ddopt', debug, 'is type', type(debug))


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.H2("Select launch site:"),
                                html.Div( dcc.Dropdown(                                         
                                            options = ls_ddopt,
                                            value='ALL',
                                            id='site-dropdown',              
                                            placeholder='Select a launch site.',
                                            searchable=True
                                                    ),
                                        # style={'width':'80%', 'padding':'3px','textAlign':'center'}),
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),


                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(
                                    dcc.RangeSlider(
                                    min_payload, # Range based on min and max
                                    max_payload,
                                    # ((max_payload - min_payload)//100), # step based on min and max 
                                    value=[min_payload,max_payload], # default values
                                    id='payload-slider',
                                    )
                                    ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))

                                
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
                )
def get_pie_chart(entered_site):
    # print('Debug: entered_site:', entered_site)
    if entered_site == 'ALL':
        filtered_df = spacex_df[['Launch Site','class']]

        fig = px.pie(filtered_df,
        values='class', 
        names='Launch Site', # filtered_df['Launch Site'].unique(), 
        title='Percentage of successful landings by launch site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site][['LS Status','dummy']]
        # print('Debug: filtered_df.head() ', filtered_df.head())
        fig = px.pie(filtered_df,
        values='dummy',
        names='LS Status',
        title='Launch site {} landing success rate'.format(entered_site))
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='payload-slider', component_property='value'),
    Input(component_id='site-dropdown', component_property='value')
                )
def get_scatter_chart(payloads, entered_site): # parameters in order of Inputs in the callback decorator
    # print('Debug: entered_site:', entered_site, ' range ', payloads)
    
    if entered_site == 'ALL':
        # filtered_df = spacex_df[['Payload Mass (kg)','Booster Version Category', 'class']]

        fig = px.scatter(spacex_df,
                         x='Payload Mass (kg)',
                         y='class',
                         labels={'class': '1 = Success, 0 = Failure'},
                         color='Booster Version Category', # filtered_df['Launch Site'].unique(), 
                         title='Success vs. Failure for all launch sites by payload')
        return fig
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site']==entered_site) &
                                (spacex_df['Payload Mass (kg)'].between(payloads[0],payloads[1]))]
        # print('Debug: filtered_df.head() ', filtered_df.head())
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',                 
                         y='class',
                         labels={'class': '1 = Success, 0 = Failure'},
                         color='Booster Version Category',
                         title='Success vs. Failure for launch site {} by payload'.format(entered_site))
        return fig

    
    

# Run the app
if __name__ == '__main__':
    app.run_server(host='localhost', debug=True)
