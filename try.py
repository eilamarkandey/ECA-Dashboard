import pystata
import pandas as pd

# Load your CSV file using pandas (to inspect it before passing to Stata)
df = pd.read_csv("C:/Users/eilam/OneDrive/CEC/ECA Campaigns_FY25_ALL.xlsx")

# Write the DataFrame to a Stata-compatible format (a .dta file)
df.to_stata("temp.dta", write_index=False)

# Now we use PyStata to run Stata code
pystata.config.init("C:/Program Files/Stata17/StataMP-64.exe")  # Adjust path to your Stata executable

# Stata commands to split the 'start date' and 'end date' columns
stata_code = """
use temp.dta, clear

* Split the 'start date' and 'end date' columns
gen startdate = substr(start_date, 1, strpos(start_date, ",") - 1)
gen starttime = substr(start_date, strpos(start_date, ",") + 1, .)

gen enddate = substr(end_date, 1, strpos(end_date, ",") - 1)
gen endtime = substr(end_date, strpos(end_date, ",") + 1, .)

* Convert dates to proper Stata date format
gen startdate_clean = date(startdate, "MDY")
gen enddate_clean = date(enddate, "MDY")

format startdate_clean %td
format enddate_clean %td

* Drop the temporary columns
drop start_date end_date startdate enddate

save temp_clean.dta, replace
"""

# Run the Stata commands via PyStata
pystata.run(stata_code)

# After running the Stata commands, load the cleaned data back into Python
df_cleaned = pd.read_stata("temp_clean.dta")

# Display the cleaned dataframe
print(df_cleaned[['startdate_clean', 'enddate_clean']].head())

# Optionally, save it back as a CSV file
df_cleaned.to_csv("cleaned_file.csv", index=False)
