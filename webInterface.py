import pandas as pd
import numpy as np
import json
from time import sleep

from random import randint, seed

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import no_update

import optimizer

# Variable used within the HTML:
requirements_df_columns = ["Total Number of Courses", "Req/Constraint 1"]
requirements_template_df = pd.DataFrame(
    np.zeros((13, len(requirements_df_columns))), columns=requirements_df_columns
)


# Just for Debugging NOTE: Remove Later
course_ratings_dict = {
    "CSCI 153 HM-02": 9,
    "CSCI 152 PO-01": 9,
    "ECON 197 PZ-01": 7,
    "MATH 189T HM-01": 4,
    "ART 002 HM-01": 6,
    "CSCI 153 HM-01": 9,
    "CSMT 183 HM-01": 8,
    "CSCI 105 HM-02": 6,
    "MATH 154 PO-01": 6,
    "MATH 103 PO-01": 8,
    "ENGR 190AW HM-01": 6,
    "MATH 156 CM-01": 6,
    "CSCI 105 HM-01": 6,
    "ENGR 205 HM-01": 0,
    "LIT 156 HM-01": 7,
    "CSCI 159 HM-01": 7,
    "SOSC 150 HM-01": 7,
}


# For the documentation to always render the same values
seed(0)


FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA, FONT_AWESOME])

app.layout = html.Div(
    [
        # Website Header and Sub Header
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Row(
                            [
                                html.H1(
                                    "Course Schedule Optimizer",
                                    style={"textAlign": "center", "fontSize": "400%"},
                                )
                            ]
                        ),
                        align="center",
                        width={"size": 10, "offset": 2},
                    )
                ],
                align="center",
            )
        ),
        # Input Text from HyperSchedule
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Textarea(
                                id="textarea-example",
                                placeholder="Paste HyperSchedule Json Data Here",
                                style={
                                    "height": 70,
                                    "width": "50%",
                                    "textAlign": "center",
                                    "fontSize": "200%",
                                },
                            ),
                        )
                    ],
                    style={
                        "textAlign": "center",
                        "marginTop": 50,
                    },
                    align="center",
                ),
                # Submit Text from Above
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                id="submit-button",
                                type="submit",
                                children="Submit",
                                style={"width": "50%", "height": 50},
                                color="secondary",
                                className="mr-2",
                            )
                        )
                    ],
                    style={
                        "textAlign": "center",
                    },
                    align="center",
                ),
            ],
            id="textarea-div",
        ),
        # Two DataTables - Ratings and Alternates
        html.Div(
            [
                dbc.Row(
                    id="datatables-row",
                    style={"marginLeft": 50, "marginTop": 35, "marginRight": 25},
                    justify="center",
                )
            ],
            id="datatables-div",
        ),
        # Final Optimized Course Selection
        html.Div(
            id="final-result",
            style={"marginTop": 20},
        ),
        html.Div(
            id="try-again-div",
            children=dbc.Row(
                dbc.Button(
                    id="try-again-button",
                    type="submit",
                    children="Try Again",
                    style={"width": "50%", "height": 50},
                    color="primary",
                    className="mr-2",
                ),
                align="center",
            ),
            style={"display": "none"},
        ),
    ]
)
# bgValues = [222, 236, 250]  # blueish
bgValues = [191, 245, 202]  # greenish
# bgValues = [0, 0, 0]
bgString = f"rgb{bgValues[0], bgValues[1], bgValues[2]}"


table1Height = "700px"
table1Width = "1000px"
table1FontSize = 30

table2Height = "auto"
table2Width = "1000px"
table2FontSize = 30


@app.callback(
    [Output("textarea-div", "style"), Output("datatables-div", "children")],
    [Input("submit-button", "n_clicks")],
    [State("textarea-example", "value")],
)
def update_output(clicks, input_value):
    if clicks is not None:
        # print("Hello")
        # print(clicks)
        hyperschedule_input = json.loads(input_value)
        data = []

        for course in hyperschedule_input:
            courses_costs = {}
            courseCode = course["courseCode"]
            courses_costs["Course Code"] = courseCode
            courses_costs["Course Name"] = course["courseName"]
            if False:  # courseCode in course_ratings_dict: # TODO: Change this
                courses_costs["Rating"] = course_ratings_dict[courseCode]
            else:
                courses_costs["Rating"] = 0

            data.append(courses_costs)

        selectable_columns = [i for i in range(len(data))]

        courses_datatable = dash_table.DataTable(
            id="courses-table",
            columns=[
                {"name": i, "id": i, "editable": j}
                for i, j in [
                    ("Course Code", False),
                    ("Course Name", False),
                    ("Rating", True),
                ]
            ],
            data=data,
            sort_action="native",
            sort_mode="single",
            column_selectable="multi",
            row_selectable="multi",
            selected_rows=selectable_columns,
            page_action="native",
            style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
            style_table={
                "height": table1Height,
                "width": table1Width,
                "overflowY": "auto",
            },
            style_cell={
                "backgroundColor": bgString,
                "color": "black",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "textAlign": "left",
                "fontSize": table1FontSize,
            },
            style_data_conditional=[
                {
                    "if": {"column_id": "Rating"},
                    "backgroundColor": "#32a893",
                    "color": "white",
                    "text-align": "center",
                },
                {
                    "if": {"state": "active"},
                    "backgroundColor": "rgb(200, 200, 200)",
                    "border": "1px solid rgb(0, 116, 217)",
                },
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "rgb(200, 200, 200)",
                    "border": "1px solid rgb(0, 116, 217)",
                },
            ],
        )

        requirements_table = dash_table.DataTable(
            id="requirements-table",
            columns=[
                {"name": i, "id": i, "deletable": True}
                for i in requirements_template_df.columns
            ],
            data=requirements_template_df.to_dict("records"),
            editable=True,
            page_action="none",
            style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
            # style_data={
            #     'height': 'auto'
            # },
            style_cell={
                "backgroundColor": bgString,
                "color": "black",
                "whiteSpace": "normal",
                "minWidth": "250px",
                # 'maxWidth': '200px',
                "width": "250px",
                "height": "auto",
                "textAlign": "center",
                "fontSize": table2FontSize,
            },
            style_table={
                "height": table2Height,
                "width": table2Width,
                "overflowY": "auto",
                "overflowX": "auto",
            },
        )

        final_button = dbc.Button(
            id="submit-button-2",
            type="submit",
            children="Calculate the Optimal Course Schedule!",
            size="lg",
            color="primary",
            className="mr-1"
            # style={"width": "600px", "height": "100px"}
        )

        add_col_button = dbc.Button(
            "Add Requirement",
            id="adding-cols-button",
            color="success",
            className="mr-1",
            size="rg",
            style={"marginLeft": 75, "fontSize": 25},
        )

        rating_instructions_modal = html.Div(
            [
                dbc.Button("Open", id="open-centered"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Header"),
                        dbc.ModalBody("This modal is vertically centered"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="close-centered", className="ml-auto"
                            )
                        ),
                    ],
                    id="modal-centered",
                    centered=True,
                ),
            ]
        )

        requirement_instructions_modal = html.Div(
            [
                dbc.Button("Open", id="open-centered-2"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Header"),
                        dbc.ModalBody("This modal is vertically centered"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="close-centered", className="ml-auto"
                            )
                        ),
                    ],
                    id="modal-centered-2",
                    centered=True,
                ),
            ]
        )

        return [
            {"display": "none"},
            [
                dbc.Row(
                    [
                        html.H2(
                            "Enter Your Course Ratings:     ",
                            style={
                                "textAlign": "center",
                            },
                        ),
                        dbc.Button(
                            [html.I(className="fa fa-question-circle"), ""],
                            color="info",
                            style={"marginLeft": 75},
                        ),
                    ],
                    justify="center",
                    align="center",
                    style={"marginTop": 50},
                ),
                dbc.Row([courses_datatable], align="center", justify="center"),
                dbc.Row(
                    [
                        html.H2("Requirements: ", style={"fontSize": 45}),
                        add_col_button,
                        dbc.Button(
                            [html.I(className="fa fa-question-circle"), ""],
                            color="info",
                            style={"marginLeft": 150},
                        ),
                    ],
                    justify="center",
                    align="center",
                    style={"marginTop": 50},
                ),
                dbc.Row(
                    [requirements_table],
                    justify="center",
                    align="center",
                ),
                dbc.Row(
                    dbc.Col(
                        [final_button],
                        width={"size": 6, "offset": 2},
                        style={"marginTop": 50},
                    ),
                    justify="center",
                ),
            ],
        ]

    else:
        return (no_update, no_update)


@app.callback(
    [Output("datatables-div", "style"), Output("final-result", "children")],
    [Input("submit-button-2", "n_clicks")],
    [State("courses-table", "derived_virtual_data")],
    [State("courses-table", "derived_virtual_selected_rows")],
    [State("requirements-table", "derived_virtual_data")],
)
def update_output_2(clicks, courses_table, selected_course_row_ids, requirements_table):
    if clicks is not None:
        courses_df = pd.DataFrame(courses_table)
        courses_df = courses_df.iloc[selected_course_row_ids]
        courses_df.set_index("Course Code", inplace=True)
        requirements_df = pd.DataFrame.from_records(requirements_table)

        requirements_df = requirements_df.loc[(requirements_df != 0).any(axis=1)]

        courses = courses_df.index.tolist()
        set_courses = set(courses)

        courses_cost = {}
        for course in courses:
            courses_cost[course] = float(courses_df.loc[course, "Rating"])

        # Alternates
        set_alternates = set()
        alternates_dict = {}
        lower_bounds = {}
        upper_bounds = {}

        for i in range(len(requirements_df.columns.tolist())):

            # set alternates
            curr_alt_id = "alternates" + str(i)
            set_alternates.add(curr_alt_id)

            # lower and upper bounds
            curr_alt = requirements_df.iloc[:, i]
            lower_bounds[curr_alt_id] = int(curr_alt[0])
            upper_bounds[curr_alt_id] = int(curr_alt[1])

            # alternates dict
            if i == 0:
                curr_alternates = [" "]

            else:
                curr_alternates = curr_alt[2:]
                curr_alternates = [
                    x for x in curr_alternates if (str(x) != "nan") and (str(x) != "0")
                ]  # Note- will need to change later

            alternates_dict[curr_alt_id] = curr_alternates

        inputToOptimizer = (
            set_courses,
            courses_cost,
            set_alternates,
            alternates_dict,
            lower_bounds,
            upper_bounds,
        )

        total_value, coursesChosenByOptimizer = optimizer.optimizer(inputToOptimizer)

        # Helpful for Debugging:
        # print(coursesChosenByOptimizer)
        # print("Total Value: ", total_value)

        hyperScheduleOutput = optimizer.courseToHyperScheduleFormat(
            coursesChosenByOptimizer
        )

        jsonOutput = json.dumps(hyperScheduleOutput)

        modal = html.Div(
            [
                dbc.Button(
                    "Input for HyperSchedule",
                    id="open-scroll",
                    className="mr-1",
                    style={"fontSize": 30},
                ),
                # dbc.Button("Modal with scrollable body",
                #            id="open-body-scroll"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Copy this and enter it into HyperSchedule"),
                        dbc.ModalBody(jsonOutput),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close",
                                id="close-scroll",
                                className="ml-auto",
                                style={"fontSize": 30},
                            )
                        ),
                    ],
                    id="modal-scroll",
                    # size="sm"
                ),
            ]
        )

        with open(r"rawData/test.json", "w") as f:
            json.dump(hyperScheduleOutput, f, indent=4)

        colors = ["primary", "secondary", "success", "warning", "danger", "info"]

        list_group = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    f"{coursesChosenByOptimizer[i][0]}: {coursesChosenByOptimizer[i][1]}",
                    color=colors[i % len(colors)],
                )
                for i in range(len(coursesChosenByOptimizer))
            ],
            style={"fontSize": 30},
        )

        return [
            {"display": "none"},
            [
                dbc.Row(
                    html.H2("An Optimal Combination of Courses!"), justify="center"
                ),
                dbc.Row(list_group, justify="center"),
                dbc.Row(
                    modal,
                    justify="center",
                    style={
                        "marginTop": 25,
                    },
                ),
            ],
        ]

    else:
        return (no_update, no_update)


def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


app.callback(
    Output("modal-scroll", "is_open"),
    [Input("open-scroll", "n_clicks")],
    [State("modal-scroll", "is_open")],
)(toggle_modal)

app.callback(
    Output("modal-body-scroll", "is_open"),
    [Input("open-body-scroll", "n_clicks")],
    [State("modal-body-scroll", "is_open")],
)(toggle_modal)


@app.callback(
    Output("requirements-table", "columns"),
    Input("adding-cols-button", "n_clicks"),
    State("requirements-table", "columns"),
)
def update_columns(n_clicks, existing_columns):
    if n_clicks is None:
        raise PreventUpdate

    if n_clicks > 0:
        i = len(existing_columns) - 1
        existing_columns.append(
            {
                "id": f"Req/Constraint {i+1}",
                "name": f"Req {i}",
                "renamable": True,
                "deletable": True,
            }
        )
    return existing_columns


if __name__ == "__main__":
    app.run_server(debug=True)
