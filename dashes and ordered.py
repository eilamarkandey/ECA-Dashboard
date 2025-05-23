import pandas as pd
from datetime import datetime
import xlsxwriter
import win32com.client
import os
import time
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import textwrap
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# ORDERS 1ST TIME AND REMOVES DASHES AND PARENT CEC 


# Define file paths
input_path = r"C:\Users\eilam\OneDrive\CEC\ECA Campaigns_FY25_ALL_v2.xlsx"
output_path = r"C:\Users\eilam\OneDrive\CEC\ECA Campaigns_FY25_BINARY.xlsx"

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
members_path = r"C:\Users\eilam\OneDrive\CEC\ECA Campaign Members_FY25_ALL.xlsx"
members_df = pd.read_excel(members_path)

# Filter members file for first-time interactions
members_filtered = members_df[
    (members_df['Interaction Type'] == "1st Time Inquiry – Requested by Org or Group") | 
    (members_df['Interaction Type'] == "1st Time Outreach – Initiated by ECA Staff")
]
members_filtered.to_excel(r"C:\Users\eilam\OneDrive\CEC\ECA Campaign Members_FY25_members_filtered.xlsx", index=False)

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
df_filtered['days_from_first'] = df_filtered.groupby('parentcampaignname')['num_startdate'].transform(lambda x: x - x.min())

# Save the filtered dataframe to a new Excel file
df_filtered.to_excel(r"C:\Users\eilam\OneDrive\CEC\ECA Campaigns_FY25_filtered_interactions.xlsx", index=False)

# Save the binary data
try:
    df.to_excel(output_path, index=False)
except PermissionError:
    print("Please close any Excel applications that might be using the file and try again.")
    exit()

# Filter v2 file for first-time interactions
v2_path = r"C:\Users\eilam\OneDrive\CEC\ECA Campaigns_FY25_ALL_v2.xlsx"
v2_df = pd.read_excel(v2_path)
filtered_first_time = v2_df[
    (v2_df['Interaction Type'] == "1st Time Inquiry – Requested by Org or Group") | 
    (v2_df['Interaction Type'] == "1st Time Outreach – Initiated by ECA Staff")
]
filtered_first_time.to_excel(r"C:\Users\eilam\OneDrive\CEC\ECA Campaigns_FY25_filtered_first_time.xlsx", index=False)

# Print summary once at the end
print("\nFiles created:")
print(f"1. Binary indicators file")
print(f"   - Saved to: {output_path}")
print(f"   - Contains all interactions with binary columns")

print(f"\n2. Filtered first-time interactions from v2 file")
print(f"   - Contains {len(filtered_first_time)} interactions")
print(f"   - Saved to: ECA Campaigns_FY25_filtered_first_time.xlsx")

print(f"\n3. Filtered first-time interactions from members file")
print(f"   - Contains {len(members_filtered)} interactions")
print(f"   - Saved to: ECA Campaign Members_FY25_members_filtered.xlsx")

print(f"\n4. Filtered interactions for parent campaigns with first-time interactions")
print(f"   - Contains {len(df_filtered)} interactions")
print(f"   - Saved to: ECA Campaigns_FY25_filtered_interactions.xlsx")

# Calculate statistics from correct sources
v2_first_time_total = len(filtered_first_time)  # From v2 file
unique_eca = members_filtered[members_filtered['ECA Affiliation Name'].notna()]['ECA Affiliation Name'].nunique()  # From members file
unique_campaigns = len(unique_parent_campaigns)  # Unique parent campaigns with first-time interactions

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_campaign_boxes():
    """Create clickable boxes for each campaign"""
    campaign_boxes = []
    
    for campaign in sorted(members_filtered['Parent Campaign: Campaign Name'].unique()):
        campaign_data = members_filtered[members_filtered['Parent Campaign: Campaign Name'] == campaign]
        
        box = dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5(campaign, className="card-title"),
                    html.P(f"People involved: {len(campaign_data)}", className="card-text"),
                    dbc.Button("View Details", 
                             id={'type': 'campaign-button', 'index': campaign},
                             color="primary")
                ])
            ], className="h-100 shadow-sm"),
            width=4,
            className="mb-4"
        )
        campaign_boxes.append(box)
    
    return campaign_boxes

# Create layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("ECA Engagement Dashboard", className="display-4 text-center mb-4"),
        html.H4("First-Time Interactions Analysis", className="text-center text-muted mb-5")
    ], className="container mt-4"),

    # Main stats row with correct data sources
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2(f"{v2_first_time_total}", className="display-3 text-primary"),
                html.P("Total First-Time Interactions", className="lead")
            ], className="text-center p-4 border rounded")
        ], width=4),
        dbc.Col([
            html.Div([
                html.H2(f"{unique_eca}", className="display-3 text-success"),
                html.P("Unique ECA Affiliations", className="lead")
            ], className="text-center p-4 border rounded")
        ], width=4),
        dbc.Col([
            html.Div([
                html.H2(f"{unique_campaigns}", className="display-3 text-info"),
                html.P("Parent Campaigns", className="lead")
            ], className="text-center p-4 border rounded")
        ], width=4),
    ], className="mb-5"),

    # Campaign boxes
    dbc.Row(
        create_campaign_boxes(),
        className="mb-4"
    ),

    # Modal for campaign details
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Campaign Details")),
        dbc.ModalBody(id="campaign-details-body"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ms-auto")
        )
    ], id="campaign-modal", size="lg"),

    # Footer
    html.Footer([
        html.P("Data source: ECA Campaign Members FY25", className="text-muted text-center")
    ], className="mt-5")

], className="container-fluid px-4 py-4")

# Callback for modal
@app.callback(
    [Output("campaign-modal", "is_open"),
     Output("campaign-details-body", "children")],
    [Input({"type": "campaign-button", "index": dash.ALL}, "n_clicks"),
     Input("close-modal", "n_clicks")],
    prevent_initial_call=True
)
def toggle_modal(campaign_clicks, close_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    trigger_id = ctx.triggered[0]["prop_id"]
    if "close-modal" in trigger_id:
        return False, ""
    
    if campaign_clicks and any(campaign_clicks):
        campaign_name = eval(trigger_id.split(".")[0])["index"]
        campaign_data = members_filtered[members_filtered['Parent Campaign: Campaign Name'] == campaign_name]
        
        details = html.Div([
            html.H4(campaign_name, className="mb-4"),
            html.H5("ECA Affiliations:", className="mb-3"),
            html.Ul([
                html.Li(f"{eca}: {', '.join(names)}")
                for eca, names in campaign_data.groupby('ECA Affiliation Name')['Full Name'].apply(list).items()
                if pd.notna(eca)  # Only include non-null ECA affiliations
            ])
        ])
        
        return True, details
    
    return False, ""

# Run the app
if __name__ == '__main__':
    print("\nDash is running on http://127.0.0.1:8050/")
    app.run_server(debug=True)

print("\nDashboard is running!")
print(f"Total First-Time Interactions (from v2): {v2_first_time_total}")
print(f"Unique ECA Affiliations (from members): {unique_eca}")
print(f"Unique Parent Campaigns (from members): {unique_campaigns}")
print("- Access the dashboard at http://127.0.0.1:8050/")
print("- Click on campaign boxes to see details")
