from urllib import response
import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import requests
import plotly.express as px

from dash_components import layout
from dash_components.layout import survey_df, meta_df, QUESTION_TEXTS, RESPONSE_STRINGS, parse_response_options


def register_callback(app):
    survey_df["PERIOD"] = pd.to_datetime(survey_df["PERIOD"], format="%b %Y", errors = "coerce")

    @app.callback(
        Output("survey-response-select", "options"),
        Input("question-selector", "value"),
    )
    def update_answer_choices(selected_question):
        if not selected_question or selected_question not in survey_df.columns:
            return []


        values = survey_df[selected_question].dropna().unique()
        values = sorted(values)
        return [{"label": str(val), "value": val} for val in values]
        #populate responses/answers dropdown

    @app.callback(
        Output("survey-line", "figure"),
        [Input("question-selector", "value"),
         Input("survey-response-select", "value")],
    )
    def update_line_graph(selected_questions, selected_answer):
        if not selected_questions or selected_answer is None:
            return px.line(
                title = "Select questions and a response value"
            )


        filtered = survey_df[survey_df[selected_questions] == selected_answer]

        weighted = (
            filtered.groupby(["PERIOD"])["PWEIGHT"]
            .sum()
            .reset_index()
            .rename(columns={"PWEIGHT": "selected_weight"})
        )

        total_weights = (survey_df.groupby("PERIOD")["PWEIGHT"]
            .sum()
            .reset_index()
            .rename(columns={"PWEIGHT": "total_weight"})
        )
        percent_merge = pd.merge(weighted, total_weights, on=["PERIOD"], how ="inner")
        percent_merge["percentage"] = 100 * percent_merge["selected_weight"] / percent_merge["total_weight"]
        fig = px.line(
            percent_merge,
            x="PERIOD",
            y="percentage",
            markers=True,
            title=f"Percentage of response '{selected_answer}' out of all options over time"
        )
        fig.update_layout(xaxis_title = "Survey Period", yaxis_title="Percentage Responses(%)")
        return fig

    @app.callback(
        Output("boxplot-graph", "figure"),
        [Input("category-selector", "value")]
    )
    def update_boxplot(selected_category):
        if not selected_category:
            return go.Figure()  # Return an empty figure if no selection is made

        # Choose the correct dataset based on user selection
        data = survey_df  # Use merged_census dataset

        # Calculate percentage values for the selected category
        filtered_data = data[[selected_category, "PERIOD", "PWEIGHT"]].dropna()
        grouped = filtered_data.groupby(["PERIOD", selected_category]).agg(
            selected_weight=("PWEIGHT", "sum")
        ).reset_index()

        # Calculate the percentage of responses per category out of the total for each period
        total_per_period = filtered_data.groupby("PERIOD")["PWEIGHT"].sum().reset_index()
        total_per_period = total_per_period.rename(columns={"PWEIGHT": "total_weight"})
        total_per_period = (
            filtered_data
            .groupby("PERIOD")["PWEIGHT"]
            .sum()
            .reset_index()
            .rename(columns={"PWEIGHT": "total_weight"})
        )
        merged = pd.merge(grouped, total_per_period, on="PERIOD")
        merged["percentage"] = 100 * merged["selected_weight"] / merged["total_weight"]
        pivot_df = merged.pivot(index="PERIOD", columns=selected_category, values="percentage").fillna(0)
        fig = go.Figure()
        for response_option in pivot_df.columns:
            fig.add_trace(go.Bar(
                x=pivot_df.index.astype(str),  # Convert datetime to string for better x-axis labels
                y=pivot_df[response_option],
                name=str(response_option)
            ))
        # Create the box plot
        fig.update_layout(
            barmode="stack",
            title=f"Stacked Bar Chart: {selected_category} Response Distribution Over Time",
            xaxis_title="Time Period",
            yaxis_title="Percentage of Responses",
            legend_title="Response Option",
        )
        return fig

    # @app.callback(
    #     Output("category-selector", "options"),
    #     Input("dataset-selector", "value")
    # )
    # def update_category_options(selected_dataset):
    #     if selected_dataset == "merged_census":
    #         columns = survey_df.columns
    #     else:
    #         columns = survey_df.columns
    #
    #     # Exclude non-category columns if needed (like PERIOD, PWEIGHT)
    #     exclude = {"PERIOD", "PWEIGHT"}
    #     category_columns = [col for col in columns if col not in exclude]
    #
    #     return [{"label": col, "value": col} for col in category_columns]

    @app.callback(
        Output("question-description", "children"),
        Input("question-selector", "value")
    )
    def display_question_info(var_code):
        if not var_code:
            return ""

        question = QUESTION_TEXTS.get(var_code, "No question text available.")
        raw_values = RESPONSE_STRINGS.get(var_code, "")
        response_lines = parse_response_options(raw_values)

        return html.Div([
            html.P(question, style={"fontWeight": "bold"}),
            html.Pre("\n".join(response_lines), style={"whiteSpace": "pre-wrap", "fontSize": "0.9rem"})
        ])

