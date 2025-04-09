import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import json
import traceback
import re
import os

def load_data():
    # Use relative paths from the current file
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, 'data')
    
    # Define file paths relative to data directory
    input_path = os.path.join(data_path, 'ECA Campaigns_FY25_ALL_v2.xlsx')
    members_path = os.path.join(data_path, 'ECA Campaign Members_FY25_ALL.xlsx')
    
    # Define Stata's epoch
    STATA_EPOCH = pd.Timestamp('1960-01-01')
    
    # Load data
    df = pd.read_excel(input_path)
    
    # Convert column names to lowercase and fix spaces
    df.columns = df.columns.str.lower().str.replace(' ', '')

    # Split date and time columns
    df['startdate'] = df['startdateandtime'].str.split(',').str[0]
    df['enddate'] = df['enddateandtime'].str.split(',').str[0]
    df['starttime'] = df['startdateandtime'].str.split(',').str[1]
    df['endtime'] = df['enddateandtime'].str.split(',').str[1]

    # Drop original date and time columns
    df.drop(columns=['startdateandtime', 'enddateandtime'], inplace=True)

    # Convert date columns to datetime and then to Stata format (days since 1960-01-01)
    df['num_startdate'] = pd.to_datetime(df['startdate'], format='%m/%d/%Y', errors='coerce')
    df['num_startdate'] = (df['num_startdate'] - STATA_EPOCH).dt.days

    # Create a unique Parent Campaign ID
    df['parents_id'] = df['parentcampaignname'].astype('category').cat.codes

    # Sort and generate campaign sequence numbers
    df.sort_values(by=['parentcampaignname', 'num_startdate'], inplace=True)
    df['num_campaigns'] = df.groupby('parentcampaignname').cumcount() + 1

    # Create binary columns for activity types
    df['meeting'] = (df['ecaactivitytype'] == 'Meeting').astype(int)
    df['event'] = (df['ecaactivitytype'] == 'Event').astype(int)

    # Create binary columns for interaction types
    df['firsttime'] = ((df['interactiontype'] == "1st Time Inquiry – Requested by Org or Group") | 
                       (df['interactiontype'] == "1st Time Outreach – Initiated by ECA Staff")).astype(int)
    df['frst_inquiry'] = (df['interactiontype'] == "1st Time Inquiry – Requested by Org or Group").astype(int)
    df['frst_outreach'] = (df['interactiontype'] == "1st Time Outreach – Initiated by ECA Staff").astype(int)
    df['followup_mtg'] = (df['interactiontype'] == "Follow Up Project Planning or Problem-Solving Meeting").astype(int)
    df['reoccurring'] = (df['interactiontype'] == "Reoccurring activity").astype(int)
    df['repeat'] = (df['interactiontype'] == "Repeat – For Purposes of Ongoing Participation or to Rep ECA").astype(int)
    df['community_mtg'] = (df['interactiontype'] == "Community Meeting").astype(int)
    df['standalone'] = (df['interactiontype'] == "Stand alone activity").astype(int)
    df['scheduling'] = (df['interactiontype'] == "Scheduling or Show-and-Tell Visit").astype(int)
    df['concerns'] = (df['interactiontype'] == "Resident, Institutional or City Concern").astype(int)
    df['other'] = (df['interactiontype'] == "Other, such as Room Request").astype(int)

    # Read the members file
    members_df = pd.read_excel(members_path)

    # Filter members file for first-time interactions
    members_filtered = members_df[
        (members_df['Interaction Type'] == "1st Time Inquiry – Requested by Org or Group") | 
        (members_df['Interaction Type'] == "1st Time Outreach – Initiated by ECA Staff")
    ]
    members_filtered.to_excel(os.path.join(data_path, 'ECA Campaign Members_FY25_members_filtered.xlsx'), index=False)

    # Get unique parent campaigns with first-time interactions
    unique_parent_campaigns = members_filtered['Parent Campaign: Campaign Name'].unique()

    # Filter the original dataframe to include only interactions for these parent campaigns
    df_filtered = df[df['parentcampaignname'].isin(unique_parent_campaigns)]

    # Create binary columns for each interaction type for summing purposes
    interaction_types = df['interactiontype'].dropna().unique()
    for interaction in interaction_types:
        df_filtered.loc[:, interaction.lower().replace(' ', '_').replace('–', '').replace('(', '').replace(')', '')] = (df_filtered['interactiontype'] == interaction).astype(int)

    # Create a total column for the number of interactions each parent campaign has
    df_filtered['total_interactions'] = df_filtered.groupby('parentcampaignname')['interactiontype'].transform('count')

    # Calculate days from first-time interaction
    # Find the first interaction date for each campaign
    first_interactions = df_filtered[
        (df_filtered['interactiontype'] == "1st Time Inquiry – Requested by Org or Group") | 
        (df_filtered['interactiontype'] == "1st Time Outreach – Initiated by ECA Staff")
    ].groupby('parentcampaignname')['num_startdate'].min()

    # Calculate days from first interaction
    df_filtered['days_from_first'] = df_filtered.apply(
        lambda row: row['num_startdate'] - first_interactions[row['parentcampaignname']], 
        axis=1
    )

    # Mark any additional first-time interactions after day 0 as invalid
    mask = (df_filtered['days_from_first'] > 0) & (
        (df_filtered['interactiontype'] == "1st Time Inquiry – Requested by Org or Group") |
        (df_filtered['interactiontype'] == "1st Time Outreach – Initiated by ECA Staff")
    )
    df_filtered.loc[mask, 'days_from_first'] = None  # Set to None to exclude from graph

    # Save the filtered dataframe to a new Excel file
    df_filtered.to_excel(os.path.join(data_path, 'ECA Campaigns_FY25_filtered_interactions.xlsx'), index=False)

    # Filter v2 file for first-time interactions
    filtered_first_time = df[
        (df['Interaction Type'] == "1st Time Inquiry – Requested by Org or Group") | 
        (df['Interaction Type'] == "1st Time Outreach – Initiated by ECA Staff")
    ]
    filtered_first_time.to_excel(os.path.join(data_path, 'ECA Campaigns_FY25_filtered_first_time.xlsx'), index=False)

    # Calculate statistics from correct sources
    v2_first_time_total = len(filtered_first_time)  # From v2 file
    unique_eca = members_filtered[members_filtered['ECA Affiliation Name'].notna()]['ECA Affiliation Name'].nunique()  # From members file
    unique_campaigns = len(unique_parent_campaigns)  # Unique parent campaigns with first-time interactions

    return df, df_filtered, filtered_first_time, members_filtered, v2_first_time_total, unique_eca, unique_campaigns

def create_dash_app(server=None):
    # Initialize the Dash app
    if server:
        app = Dash(__name__, 
                   server=server,
                   url_base_pathname='/',  # Changed from '/dash/' to '/'
                   external_stylesheets=[dbc.themes.BOOTSTRAP])
    else:
        app = Dash(__name__, 
                  external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Load data
    df, df_filtered, filtered_first_time, members_filtered, v2_first_time_total, unique_eca, unique_campaigns = load_data()
    
    # Your existing layout code here
    app.layout = html.Div([
        # ... your existing layout ...
    ])
    
    # Your existing callbacks here
    @app.callback(
        # ... your existing callbacks ...
    )
    def update_something(value):
        # ... callback logic ...
        pass
    
    return app

# This will only run when testing locally
if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=True)





