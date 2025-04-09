import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample campaign data
campaigns_data = {
    'startdateandtime': [
        '1/1/2024, 9:00 AM',
        '1/2/2024, 10:00 AM',
        '1/3/2024, 2:00 PM',
        '1/4/2024, 3:00 PM',
        '1/5/2024, 11:00 AM'
    ],
    'enddateandtime': [
        '1/1/2024, 10:00 AM',
        '1/2/2024, 11:00 AM',
        '1/3/2024, 3:00 PM',
        '1/4/2024, 4:00 PM',
        '1/5/2024, 12:00 PM'
    ],
    'parentcampaignname': [
        'Campaign A',
        'Campaign A',
        'Campaign B',
        'Campaign B',
        'Campaign C'
    ],
    'ecaactivitytype': [
        'Meeting',
        'Event',
        'Meeting',
        'Event',
        'Meeting'
    ],
    'interactiontype': [
        '1st Time Inquiry – Requested by Org or Group',
        'Follow Up Project Planning or Problem-Solving Meeting',
        '1st Time Outreach – Initiated by ECA Staff',
        'Community Meeting',
        'Reoccurring activity'
    ]
}

# Create sample members data
members_data = {
    'Parent Campaign: Campaign Name': [
        'Campaign A',
        'Campaign B',
        'Campaign C'
    ],
    'Interaction Type': [
        '1st Time Inquiry – Requested by Org or Group',
        '1st Time Outreach – Initiated by ECA Staff',
        'Reoccurring activity'
    ],
    'ECA Affiliation Name': [
        'Affiliation 1',
        'Affiliation 2',
        'Affiliation 3'
    ]
}

# Create DataFrames
campaigns_df = pd.DataFrame(campaigns_data)
members_df = pd.DataFrame(members_data)

# Save to Excel files in the data directory
campaigns_df.to_excel('data/ECA Campaigns_FY25_ALL_v2.xlsx', index=False)
members_df.to_excel('data/ECA Campaign Members_FY25_ALL.xlsx', index=False)