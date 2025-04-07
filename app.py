import pandas as pd

# # Replace 'path_to_your_file.csv' with your file location.
# # df = pd.read_csv('repwgt_puf_DECEMBER2024.csv')
# df = pd.read_csv("HPS_DECEMBER2024_PUF.csv")
# print(df.head().to_string())
# # Suppose you want to estimate the total count for a particular week weight:
# #total_population_estimate = df["PWEIGHT65"].sum()
# # print("Estimated population count:", total_population_estimate)
#
# print(df.columns)
#
# print(df.info())
# print(df.describe())

# Load the two CSV files
weights = pd.read_csv("repwgt_puf_DECEMBER2024.csv")
responses = pd.read_csv("HPS_DECEMBER2024_PUF.csv")

# Merge files on the identifier column
merged = pd.merge(responses, weights, on="SCRAMID", how="left")

# Check the first few rows to confirm
print(merged.head())

# Save the merged data to a new file (if needed)
merged.to_csv("merged_file.csv", index=False)
import dash
from dash import Dash, dcc, html, dash_table

app.layout = html.Div([
    dash_table.DataTable(
        data=merged.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in merged.columns],
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
])