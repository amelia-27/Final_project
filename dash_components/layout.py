import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import pandas as pd
import dash_bootstrap_components as dbc
import openpyxl as xl


merged = pd.read_csv("merged_census_all.csv")
survey_df = merged
# survey_df = merged[
#     (merged["TBIRTH_YEAR"] >= 1990) &
#     (merged["TBIRTH_YEAR"] <= 2025)
#     ]


survey_columns = [col for col in survey_df.columns if
                  col not in ["PERIOD", "SCRAM", "PWEIGHT"] and survey_df[col].nunique() < 20]

#_____ data ingestion for survey text (got help with this part)

meta_df = pd.read_excel("dash_components/assets/dictionary.xlsx")

# Standardize column names just in case
meta_df.columns = [col.strip().lower().replace(" ", "_") for col in meta_df.columns]


# Build dictionary of question texts and values
QUESTION_TEXTS = meta_df.set_index("puf_variable_name")["variable_label"].to_dict()
RESPONSE_STRINGS = meta_df.set_index("puf_variable_name")["values"].to_dict()
def parse_response_options(value_string):
    if pd.isna(value_string):
        return []

    lines = value_string.strip().split("\n")
    parsed = []

    for line in lines:
        cleaned = line.strip().lstrip("-").replace("<.m>", "Missing").replace(")", ") ")
        parsed.append(cleaned)

    return parsed
#_________ ingestion finished

def create_layout():
    return dbc.Container([
        html.H2("Census Survey Response Trends", style={
        "textAlign": "center",
        "backgroundColor": "#007BFF",
        "color": "white",
        "padding": "15px",
        "fontSize": "30px",
        "fontWeight": "bold",
       # "borderRadius": "6px"
        }),
        html.H3("Amelia Ubben | CS150", style={"textAlign": "center",
        "backgroundColor": "#007BFF",
        "color": "white",
        "padding": "15px",
        "fontSize": "24px",
        "fontWeight": "bold",
      #  "borderRadius": "6px",
        "marginBottom": "20px"}),
        dbc.Row(
            dbc.Col(
                html.Div(id="question-description",
                         style={"marginTop": "10px", "backgroundColor": "#f9f9f9", "padding": "10px",
                                "borderRadius": "8px"}),
                width=4,
            ),
        ),
        dbc.Row(
            [
                dbc.Col(
                    # html.Label("Select a survey question:"),
                    dcc.Dropdown(
                        id="question-selector",
                        placeholder="Select a Question...",
                        options=[
                            {"label": col, "value": col} for col in survey_columns
                        ]
                    ), width=4,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="survey-response-select",
                        placeholder="Select a survey response value",
                    ),   width = 4,
                ),

            ],
        ),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id="survey-line",
                    style={"width": "100%", "height": "600px"},
                    responsive=True,
                )
            ),
        ]),

        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id="category-selector",
                    placeholder="Select a category...",
                    options=[
                        {"label": col, "value": col} for col in survey_columns
                    ],
                ), width=4
            ),
        ),

        # Graph for the box plot
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="boxplot-graph"),
            )
        ),
    ],
    fluid = True,
    )

    # implement these tabs later
    # #Tabs
    # intro_card = dbc.Card(
    #     [
    #         dbc.CardHeader("Investigation of Lonliness"),
    #         html.Div(page_component), # put the component here thats going in tab
    #     ],
    #     className="mt-4",
    # )
    #
    # results_card = dbc.Card(
    #     [
    #         dbc.CardHeader("My Portfolio Returns - Rebalanced Annually"),
    #         html.Div(total_returns_table),
    #     ],
    #     className="mt-4",
    # )
    # results_card = dbc.Card(
    #     [
    #         dbc.CardHeader("My Portfolio Returns - Rebalanced Annually"),
    #         html.Div(total_returns_table),
    #     ],
    #     className="mt-4",
    # )
    # results_card = dbc.Card(
    #     [
    #         dbc.CardHeader("My Portfolio Returns - Rebalanced Annually"),
    #         html.Div(total_returns_table),
    #     ],
    #     className="mt-4",
    # )
    #
    # #building tabs - source: chapter 6 project
    # tabs = dbc.Tabs(
    #     [
    #         dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
    #         dbc.Tab(
    #             [asset_allocation_text, slider_card, input_groups, time_period_card],
    #             tab_id="tab-2",
    #             label="Play",
    #             className="pb-4",
    #         ),
    #         dbc.Tab([results_card, data_source_card], tab_id="tab-3", label="Results"
    #         ),
    #         dbc.Tab( [history_card],
    #             tab_id = "tab-4",
    #             label = "History"
    #         ),
    #     ],
    #     id="tabs",
    #     active_tab="tab-2",
    #     className="mt-2",
    # )
