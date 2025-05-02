import pandas as pd
import dash
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
import gc

from dash_components import callbacks, layout

app = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.FONT_AWESOME], )

# Code I used to merge Census Data:
# # List of file info with paths, weight columns, and periods
# survey_paths = [
#     {"survey_path": "dash_components/assets/pulse2020_puf_01.csv", "period": "May 2020"},
#     {"survey_path": "dash_components/assets/pulse2020_puf_06.csv", "period": "June 2020"},
#     {"survey_path": "dash_components/assets/pulse2020_puf_20.csv", "period": "Dec 2020"},
#     {"survey_path": "dash_components/assets/pulse2021_puf_32.csv", "period": "June 2021"},
#     {"survey_path": "dash_components/assets/pulse2021_puf_40.csv", "period": "Dec 2021"},
#     {"survey_path": "dash_components/assets/pulse2022_puf_46.csv", "period": "June 2022"},
#     {"survey_path": "dash_components/assets/pulse2022_puf_52.csv", "period": "Dec 2022"},
#     {"survey_path": "dash_components/assets/pulse2023_puf_58.csv", "period": "June 2023"},
#     {"survey_path": "dash_components/assets/hps_04_00_01_puf.csv", "period": "Jan 2024"},
#     {"survey_path": "dash_components/assets/hps_04_01_06_puf.csv", "period": "June 2024"},
#     {"survey_path": "dash_components/assets/HPS_DECEMBER2024_PUF.csv", "period": "Dec 2024"},
#
# ]
#
# desired_columns = {
#     "SCRAM": ["SCRAM"],
#     "TBIRTH_YEAR": ["TBIRTH_YEAR", "TBIRTH_YEAR1"],
#     "HLTHSTATUS": ["HLTHSTATUS"],
#     "SATISFACTION": ["SATISFACTION"],
#     "REMEMBERING": ["REMEMBERING"],
#     "EGENDER": ["EGENDER"],
#     "SELFCARE": ["SELFCARE"],
#     "UNDERSTAND": ["UNDERSTAND"],
#     "ANXIOUS": ["ANXIOUS"],
#     "WORRY": ["WORRY"],
#     "INTEREST": ["INTEREST"],
#     "DOWN": ["DOWN"],
#     "EST_ST": ["EST_ST"],
#     "PWEIGHT": ["PWEIGHT"],
#     "SOCIAL1": ["SOCIAL1", "SOCIAL1_first"],
#     "SOCIAL2": ["SOCIAL2", "SOCIAL2_first"],
#     "SOCnew1": ["SOCnew1"],
#     "SOCnew2": ["SOCnew2"],
#     "THHLD_NUMADULT": ["THHLD_NUMADULT"],
#     "MS": ["MS", "MARTIAL1"],
#     "SUPPORT1": ["SUPPORT1", "SUPPORT1EXP"],
#     "SUPPORT2": ["SUPPORT2"],
#     "SUPPORT3": ["SUPPORT3"],
#     "SUPPORT4": ["SUPPORT4"],
#     "EXPENS_DIF": ["EXPENS_DIF"],
#     "TSPNDFOOD": ["TSPNDFOOD"],
#     "TSPNDPRPD": ["TSPNDPRPD"],
#     "TRENTAMT": ["TRENTAMT"],
#     "RENTCHNG": ["RENTCHNG"],
#     "TMNTHSBHND": ["TMNTHSBHND"],
#     "ENERGY": ["ENERGY"],
#     "HSE_TEMP": ["HSE_TEMP"],
#     "ENRGY_BILL": ["ENRGY_BILL"],
#     "INCOME": ["INCOME"]
#
# }
# dataframes = []
#
# # Loop over each survey file and process
# for info in survey_paths:
#     survey_path = info["survey_path"]
#     period = info["period"]
#
#     print(f"Processing {survey_path} for period {period}")
#
#     # Read the survey file into a DataFrame
#     df = pd.read_csv(survey_path)
#     print(f"Loaded {survey_path} with columns: {df.columns.tolist()}")
#
#     rename_map = {}
#     for standard_name, options in desired_columns.items():
#         for option in options:
#             if option in df.columns:
#                 rename_map[option] = standard_name
#                 break  # Only map the first match
#
#     # Rename the columns based on the mapping
#     df = df.rename(columns=rename_map)
#
#     # Keep only the standardized columns we care about (if they exist)
#     available_columns = [col for col in desired_columns.keys() if col in df.columns]
#     cleaned_df = df[available_columns].copy()  # Explicitly create a copy
#
#     # Add a PERIOD column for each row
#     cleaned_df.loc[:, "PERIOD"] = period  # This will no longer trigger a warning
#
#     print(f"After adding PERIOD for {period}:")
#     print(cleaned_df.head())  # Check if period is added correctly
#
#     # Store the cleaned dataframe
#     dataframes.append(cleaned_df)
#
# # Now merge all the cleaned dataframes together after the loop ends
# print(f"Number of dataframes accumulated: {len(dataframes)}")  # Check how many dataframes are being added
#
# merged_census_all = pd.concat(dataframes, ignore_index=True)
#
# # Save to a new CSV
# merged_census_all.to_csv("merged_census_all.csv", index=False)
#
# print("Merged all survey files and saved!")


# Assuming the merged file is in `merged_census`
merged = pd.read_csv("dash_components/assets/merged_census_all.csv")
survey_df = merged
# survey_df = merged[
#     (merged["TBIRTH_YEAR"] >= 1925) &
#     (merged["TBIRTH_YEAR"] <= 1965)
# ]

survey_columns = [col for col in survey_df.columns if col not in ["PERIOD", "SCRAM", "PWEIGHT"] and survey_df[col].nunique() < 20 and survey_df[col].notna().sum() > 0]

# Define weight column (adjust for your specific case, e.g., 'PWEIGHT0' or 'PWEIGHT1')
weight_col = "PWEIGHT"  # Change as needed depending on the dataset/period

# Define columns to exclude (e.g., PWEIGHT columns and others you don't want in the analysis)
non_weight_cols = [col for col in merged.columns if
                   not col.startswith("PWEIGHT") or col == weight_col or col.startswith("HWEIGHT")]
merged = merged[non_weight_cols]

# List of categorical columns (excluding weight columns)
categorical_columns = [
    col for col in merged.columns
    if col != weight_col and
       merged[col].nunique() < 20 and  # Categorical columns with fewer than 20 unique values
       merged[col].dtype in ["float64", "int64", "object"]  # Basic types (e.g., integer, float, or object)
]

# For storing results (percentage distribution of categorical data)
invalid_values = [".m", "-99", "-88"]  # Exclude missing or invalid values
weighted_results = {}

# Iterate over categorical columns to calculate weighted percentages
for col in categorical_columns:
    # Exclude missing/invalid values (-99 or null)
    valid = merged[(merged[col].notnull()) & ~merged[col].isin(invalid_values)]

    # Weighted counts by category
    counts = valid.groupby(col)[weight_col].sum()

    # Calculate the weighted percentages
    percentages = counts / counts.sum() * 100

    # Store the results
    weighted_results[col] = percentages

# Print the weighted results (percentage distribution for each categorical column)
# print("Weighted Results:", weighted_results)
#
# # Check the first few rows to confirm
# print("Merged Data Sample:", merged.head())

# Optionally, save the merged and processed file
merged.to_csv("merged_file_processed.csv", index=False)

app.layout = layout.create_layout()

callbacks.register_callback(app)


if __name__ == '__main__':
    app.run(debug=True)
