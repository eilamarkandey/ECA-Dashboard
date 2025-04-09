import pandas as pd
 ##WORKING
# Define the file path to the Excel file
file_path = r"C:\Users\eilam\OneDrive\CEC\ECA Campaigns_FY25_ALL.xlsx"

# Read the Excel file into a pandas DataFrame
df = pd.read_excel(file_path, engine='openpyxl')

# Ensure required columns exist
required_columns = ['Interaction Type', 'Start Date and Time', 'Parent Campaign Name']
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Column '{col}' is not in the Excel file.")

# Clean 'Interaction Type' column
df['Interaction Type'] = df['Interaction Type'].astype(str).str.strip()

# Replace potential unwanted characters
df['Interaction Type'] = df['Interaction Type'].str.replace(r'\u2014', '-', regex=False)
df['Interaction Type'] = df['Interaction Type'].str.replace('â€', '', regex=False)
df['Interaction Type'] = df['Interaction Type'].str.replace('–', '-', regex=False)

# Clean all columns to avoid unexpected encoding issues
df = df.applymap(lambda x: str(x).replace('â€', '') if isinstance(x, str) else x)

# Filter for specific interaction types
filtered_data = df[df['Interaction Type'].isin([ 
    "1st Time Inquiry - Requested by Org or Group", 
    "1st Time Outreach - Initiated by ECA Staff"
])]

# Ensure 'Parent Campaign Name' is a string and strip spaces
filtered_data['Parent Campaign Name'] = filtered_data['Parent Campaign Name'].astype(str).str.strip()

# **Filter for only rows that START with "PARENT1:" or "PARENT 1:" (ensures no extra values slip in)**
filtered_data = filtered_data[filtered_data['Parent Campaign Name'].str.match(r'^(PARENT1:|PARENT 1:)', case=False, na=False)]

# Display results
print(f"Filtered data after applying 'Parent Campaign Name' filter:")
print(filtered_data[['Parent Campaign Name']].head(20))  # Check if only PARENT1 entries are present

# Convert 'Start Date and Time' to datetime format
filtered_data['Start Date and Time'] = pd.to_datetime(filtered_data['Start Date and Time'], errors='coerce')

# Drop rows where the date conversion failed
filtered_data = filtered_data.dropna(subset=['Start Date and Time'])

# Format 'Start Date and Time' to MM/DD/YYYY
filtered_data['Start Date and Time'] = filtered_data['Start Date and Time'].dt.strftime('%m/%d/%Y')

# Sort by 'Start Date and Time' in descending order (latest first)
filtered_data = filtered_data.sort_values(by='Start Date and Time', ascending=False)

# Save to CSV
output_path = r"C:\Users\eilam\OneDrive\CEC\filtered_interactions.csv"
filtered_data.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Filtered and sorted data saved to: {output_path}")
