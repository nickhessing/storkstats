import logging
import pandas as pd
import datetime
import dash
from dash import (
    Dash,
    DiskcacheManager,
    Patch,
    CeleryManager,
    dcc,
    html,
    Input,
    Output,
    State,
    MATCH,
    ALL,
    ctx,
    clientside_callback,
    ClientsideFunction,
)
from flask_caching import Cache
from celery import Celery
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_trich_components as dtc
from dash.exceptions import PreventUpdate
import glob
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash_breakpoints import WindowBreakpoints
import json
from uuid import uuid4
import polars as pl
from dash_extensions.enrich import (
    DashProxy,
    RedisBackend,
    Output,
    Input,
    State,
    Serverside,
    html,
    dcc,
    ServersideOutputTransform,
)

# from flask_caching import Cache
import redis
import dash_loading_spinners as dls
import subprocess
import numpy as np

np.seterr(divide="ignore", invalid="ignore")
from flask import Flask

print("randomchange")
print(os.environ.values())
print("randomchange")


# Usage example:
def save_string_to_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)


def execute_batchie(walletaddress_str, json_data_string):
    try:
        # Call the Node.js runtime with the batchrequest.js script
        process = subprocess.run(
            ["node", "BatchRequestSimple.js", walletaddress_str, json_data_string],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return process.stdout
    except subprocess.CalledProcessError as e:
        # If an error occurs during the execution, you can handle it here
        print(f"Error executing batchie: {e}")


# execute_batchie(walletaddress_str, json_data_string)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/icon?family=Material+Icons",
        "rel": "stylesheet",
    },
]


# Connect to your internal Redis instance using the REDIS_URL environment variable
# The REDIS_URL is set to the internal Redis URL e.g. redis://red-343245ndffg023:6379
if "REDIS_URL" in os.environ.values():
    print("os.environ in environment")
    # Use Redis & Celery if REDIS_URL set as an env variable
    redis_url = os.environ["REDIS_URL"]
    from celery import Celery

    celery_app = Celery(__name__, broker=redis_url, backend="redis")
    background_callback_manager = CeleryManager(celery_app)
    one_backend = RedisBackend(host="redis", port=6379)

else:
    print("host = localhost")
    import diskcache

    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)
    one_backend = RedisBackend(host="redis", port=6379)

app = DashProxy(
    __name__
    # ,server=flask_server
    ,
    transforms=[
        ServersideOutputTransform(backends=[one_backend])
    ],  # ,]session_check=False, arg_check=False
    background_callback_manager=background_callback_manager
    # ,session_check=False, arg_check=False
    ,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
)
# server=app.server
# initial_callback_executed = False


server = app.server
callback_triggered = False

BeautifulSignalColor = "#f3f6d0"
ProjectOrange = "#f2730c"
Highlightcardcolor = "#f3f6d0"
graphcolor = "#243b55"
topcolor = "rgb(81 100 137)"  # 8EC5FC #tbv export
fontcolor = "rgb(247, 239, 213)"  # 141e30
buttoncolor = "#f3f6d0"
tabhover = "#4c7cb3"  # lichterblauw
buttonlogocolor = "#020b15"
rangeselected = "#1A2B3E"
slides_to_show_ifenough = 4
slides_to_scroll = 4
# to render in jupyterlab
pio.renderers.default = "plotly_mimetype"

# import MessageApp
gapminder = px.data.gapminder()
gapminder.head()

image_directory = "/Users/chriddyp/Desktop/"
list_of_images = [
    os.path.basename(x) for x in glob.glob("{}*.png".format(image_directory))
]
static_image_route = "/static/"

today = datetime.datetime.now()
thisYear = today.year
firstDay = datetime.datetime(thisYear, 1, 1)
lastDay = datetime.datetime(thisYear, 12, 31)
firstDayStr = firstDay.strftime("%Y-%m-%d")
lastDayStr = lastDay.strftime("%Y-%m-%d")

cookpi_attributestmp = pd.read_excel(
    open("assets/Attributes/dashboard_data/cookpi_per_pi.xlsx", "rb"),
    sheet_name="linktable",
)
filtered_df0 = cookpi_attributestmp[
    cookpi_attributestmp["Level_ID_present"] == "d_level0_id"
]
filtered_df1 = cookpi_attributestmp[
    cookpi_attributestmp["Level_ID_present"] == "d_level1_id"
]
filtered_df2 = cookpi_attributestmp[
    cookpi_attributestmp["Level_ID_present"] == "d_level2_id"
]
KPIName_listlevel0 = filtered_df0["KPIName"].tolist()
KPIName_listlevel1 = filtered_df1["KPIName"].tolist()
KPIName_listlevel2 = filtered_df2["KPIName"].tolist()

unique_dss_tab = cookpi_attributestmp["dss_tab"].unique()
d_kpi_tmp = pd.read_excel(
    open("assets/Attributes/dashboard_data/cookpi_per_pi.xlsx", "rb"),
    sheet_name="d_kpi",
)
attributeframetmp = []

Projects = pd.read_excel(
    open("assets/Attributes/dashboard_data/cookpi_per_pi.xlsx", "rb"),
    sheet_name="Project",
)

# Iterate through the sheets and read them into DataFrames
for sheet_name in unique_dss_tab:
    df = pd.DataFrame(
        pd.read_excel(
            "assets/Attributes/dashboard_data/cookpi_per_pi.xlsx", sheet_name=sheet_name
        )
    )
    attributeframetmp.append(df)

# you dont have to, so thats why we and frontera created seatless

# Concatenate the DataFrames
attributeframe = pd.concat(attributeframetmp)
attributeframe1 = attributeframe.filter(regex=r"^(?!.*_ID$)")
attributeframe1.fillna("Overig", inplace=True)
# Display the concatenated DataFrame

kpilevelcount = (
    cookpi_attributestmp.groupby(["d_kpi_id"])["d_kpi_id"]
    .count()
    .reset_index(name="kpilevelcount")
)

d_kpi = d_kpi_tmp[(d_kpi_tmp.live == 1)]  # & (df.carrier == "B6")
d_kpi = d_kpi.merge(kpilevelcount)

d_kpi.sort_values(by=["Sorting"])

KPINumAgg = dict(d_kpi.set_index("KPIName")["AggregateNum"].to_dict())
KPIDenomAgg = dict(d_kpi.set_index("KPIName")["AggregateDenom"].to_dict())

KPINumAggid = dict(d_kpi.set_index("d_kpi_id")["AggregateNum"].to_dict())
KPIDenomAggid = dict(d_kpi.set_index("d_kpi_id")["AggregateDenom"].to_dict())


def AggregateNumDenom(Calculation):
    if Calculation == 1:
        CalculationString = "'sum'"
        return CalculationString
    elif Calculation == 2:
        CalculationString = "'mean'"
        return CalculationString
    elif Calculation == 3:
        CalculationString = "'max'"
        return CalculationString


keysl0 = ["d_kpi_id", "d_level0_id"]
keysl1 = ["d_kpi_id", "d_level0_id", "d_level1_id"]
ListGrain = ["int_day", "int_month", "int_quarter", "int_year"]
dflmasterfrontpolars = pl.scan_parquet(
    "assets/Attributes/dashboard_data/dflmasterfront.parquet"
).collect()
dflmasterfrontpolars = dflmasterfrontpolars.with_columns(
    dflmasterfrontpolars["Period_int"].cast(pl.Utf8)
)
# dflmasterfrontpolars = dflmasterfrontpolars.filter(
#    (pl.col("Grain") == "M") & (pl.col("LevelName_0").is_in(["uniswap", "synthetix","lido","rocketpool","kwenta"]))
# )

GrainNameListtmp = pl.DataFrame(dflmasterfrontpolars["Grain"].unique())
tmp = GrainNameListtmp.rows(named=True)
GrainNameList = [i["Grain"] for i in tmp]

Level0NameListInitialShow = pl.DataFrame(
    dflmasterfrontpolars.filter(pl.col("InitialShow_0") == 1)["LevelName_0"].unique()
)
Level0NameListtmp = pl.DataFrame(dflmasterfrontpolars["LevelName_0"].unique())
tmp = Level0NameListtmp.rows(named=True)
Level0NameList = [i["LevelName_0"] for i in tmp]
tmpIS = Level0NameListInitialShow.rows(named=True)
Level0NameListIS = [i["LevelName_0"] for i in tmpIS]

Level1NameListInitialShow = pl.DataFrame(
    dflmasterfrontpolars.filter(pl.col("InitialShow_1") == 1)["LevelName_1"].unique()
)
Level1NameListtmp = pl.DataFrame(dflmasterfrontpolars["LevelName_1"].unique())
tmp = Level1NameListtmp.rows(named=True)
Level1NameList = [i["LevelName_1"] for i in tmp]
tmpIS = Level1NameListInitialShow.rows(named=True)
Level1NameListIS = [i["LevelName_1"] for i in tmpIS]

Level2NameListInitialShow = pl.DataFrame(
    dflmasterfrontpolars.filter(pl.col("InitialShow_2") == 1)["LevelName_2"].unique()
)
Level2NameListtmp = pl.DataFrame(dflmasterfrontpolars["LevelName_2"].unique())
tmp = Level2NameListtmp.rows(named=True)
Level2NameList = [i["LevelName_2"] for i in tmp]
tmpIS = Level2NameListInitialShow.rows(named=True)
Level2NameListIS = [i["LevelName_2"] for i in tmpIS]

print("Catergory0List boven")
Catergory0Listtmp = pl.DataFrame(dflmasterfrontpolars["Filter1_0"].unique())
tmp = Catergory0Listtmp.rows(named=True)
Catergory0List = [i["Filter1_0"] for i in tmp]
print("Catergory0List boven")

Level0Name = dflmasterfrontpolars.select(
    ["LevelEntitytype_0", "LevelName_0", "LevelColor_0", "KPIName", "Filter1_0"]
).unique()
Level1Name = dflmasterfrontpolars.select(
    ["LevelEntitytype_1", "LevelName_1", "LevelColor_1", "KPIName", "Filter1_1"]
).unique()
Level2Name = dflmasterfrontpolars.select(
    ["LevelEntitytype_2", "LevelName_2", "LevelColor_2", "KPIName", "Filter1_2"]
).unique()

dflmasterfrontpolars.drop_in_place("LevelColor_2")
dflmasterfrontpolars.drop_in_place("LevelEntitytype_2")
dflmasterfrontpolars.drop_in_place("LevelDescription_2")
dflmasterfrontpolars.drop_in_place("KPIType")
dflmasterfrontpolars.drop_in_place("Denominator_LP")
dflmasterfrontpolars.drop_in_place("Numerator_LP")


colorframe = attributeframe1[
    ~(
        (attributeframe1["LevelColor"] == "Overig")
        | (attributeframe1["Filter1Color"] == "Overig")
    )
]
LevelNameColor = dict(zip(attributeframe1["LevelName"], attributeframe1["LevelColor"]))
FilterColor = dict(zip(attributeframe1["Filter1"], attributeframe1["Filter1Color"]))
LevelNameColorFiltered = {
    key: value for key, value in LevelNameColor.items() if value != "Overig"
}
Level0attrtmp = Level0Name.select(["KPIName", "LevelEntitytype_0"])
Level0attr = Level0attrtmp.rows(named=True)
Level0attr = {level["KPIName"]: level["LevelEntitytype_0"] for level in Level0attr}

Level1attrtmp = Level1Name.select(["KPIName", "LevelEntitytype_1"])
Level1attr = Level1attrtmp.rows(named=True)
Level1attr = {level["KPIName"]: level["LevelEntitytype_1"] for level in Level1attr}

Level2attrtmp = Level2Name.select(["KPIName", "LevelEntitytype_2"])
Level2attr = Level2attrtmp.rows(named=True)
Level2attr = {level["KPIName"]: level["LevelEntitytype_2"] for level in Level2attr}

KPINameListCompare = d_kpi["KPIName"].unique()
KPINameToID = dict(d_kpi.set_index("KPIName")["d_kpi_id"].to_dict())
KPINameList = d_kpi["KPIName"].unique()
KPIGroupList = d_kpi["KPIGroup"].unique()
HigherIs = dict(d_kpi.set_index("KPIName")["HigherIs(1=positive)"].to_dict())
KPINotation = dict(d_kpi.set_index("KPIName")["Notation"].to_dict())
KPICalculation = dict(d_kpi.set_index("KPIName")["Calculation"].to_dict())
KPICum = dict(d_kpi.set_index("KPIName")["IsCum"].to_dict())
KPIColor = dict(d_kpi.set_index("KPIName")["kpicolor"].to_dict())
visual = dict(d_kpi.set_index("KPIName")["visual"].to_dict())
KPIGroupImage = dict(d_kpi.set_index("KPIGroup")["GroupImage"].to_dict())
KPIImage = dict(d_kpi.set_index("KPIName")["KPIImage"].to_dict())

GroupImage = d_kpi["GroupImage"].unique()
KPICountPerGroup = dict(d_kpi.groupby("KPIGroup")["KPIName"].count().to_dict())
KPILevelCountList = dict(d_kpi.set_index("KPIName")["kpilevelcount"].to_dict())

kpicountout = [len(KPINameList)]
kpigroupcountout = [len(KPIGroupList)]
KPIattributes = []

pd.set_option("display.expand_frame_repr", False)

template_theme1 = "stylesheet.css"
template_theme2 = "stylesheet2.css"

css_directory = os.getcwd()
stylesheets = ["stylesheet.css"]
static_css_route = "/static/"

bgcolor = "#f3f3f1"
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}
row_heights = [150, 500, 300]


def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


KPIdropdown = html.Div(
    [
        dbc.Select(
            id="KPISelect",
            options=[{"label": i, "value": i} for i in KPINameList],
            value=KPINameList[0],
        ),
    ],
    className="pretty_container",
    id="KPIContainer",
)

KPIGroupdropdown = html.Div(
    [
        dcc.Dropdown(
            id="KPIGroupSelect",
            value=KPIGroupList,
            multi=True,
            options=[{"label": i, "value": i} for i in KPIGroupList],
        ),
    ],
    className="pretty_container",
    id="KPIGroupContainer",
)

mainlogo = html.Div(
    html.Img(  # src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/attributes/Images/coa.png', 'rb').read()).decode())
        id="TopImage"
    ),
)

d_kpi_sorting = d_kpi

KPISorting = dict(d_kpi_sorting.set_index("Sorting")["KPIName"].to_dict())

Radiograin = html.Div(
    [
        dbc.RadioItems(
            id="GrainSelect",
            options=[{"label": i, "value": i} for i in GrainNameList],
            value="M",
            labelClassName="date-group-labels",
            labelCheckedClassName="date-group-labels-checked",
            inline=True,
        )
    ],
)

# @app.callback(
#    Output('Category1Select', 'value'),
#    [Input('sweepl0filter', 'n_clicks'),
#    ]
# )
#
# def reset_filter0(n_clicks):#,n_clicks2
#    print('removefilterl0')
#    filterl0 = [{'label': html.Span([i],style={'background-color': ProjectOrange}), 'value': i}  for i in Catergory0List]
#    print(filterl0)
#    return filterl0


Level0DD = html.Div(
    [
        html.Div(dcc.Textarea(id="dropdown0", className="h6")),
        dcc.Dropdown(
            id="Level0NameSelect",
            options=[
                {
                    "label": html.Span(
                        [i], style={"background-color": LevelNameColor[i]}
                    ),
                    "value": i,
                }
                for i in Level0NameList
            ],  # , 'style': {'backgroundColor': LevelNameColor[i]}
            multi=True,
            optionHeight=1,
            placeholder="Select a value",
            value=Level0NameListIS,
            persistence=True,
            persistence_type="local",
        ),
    ],
    id="Level0DD",
)


@app.callback(
    [
        Output("Level0NameSelect", "value"),
    ],
    Input("graph-level0compare", "selectedData"),
    Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
    Input("Level0NameSelect", "value"),
    Input("WalletSwitch", "label"),
    Input("button_group", "value"),
    Input("button_group1", "value"),
    # Input('pieorbar','data'),
    Input({"type": "filter-dropdown-ex3-reset", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
    # background=True,
    # manager=background_callback_manager,
)
def Level0Update(
    selecteddatal0bar,
    n_clicks,
    Level0NameSelect,
    WalletSwitch,
    button_group,
    button_group1,
    reset,
):  # ,selecteddatal0,n_clicks,KPINameSelect,clickdatal0bar,clickdatal0
    print("Level0Update")
    print(selecteddatal0bar)
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    print(changed_id)
    try:
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        changed_id2 = [p["prop_id"] for p in dash.callback_context.triggered][0].split(
            "."
        )[0]
        selectedlistl0bar_list = []
        selectedlistl0bar_list.clear()
        # if not selecteddatal0bar:
        #    pieorbar='bar'
        # elif len(selecteddatal0bar['points'])==1:
        #    pieorbar='pie'
        # else:
        #    pieorbar='bar'
        try:
            if (
                '{"index":"LevelName_0","type":"sweepertje"}' in changed_id2
                and all(val is None for val in n_clicks) == False
            ):
                selectedlistl0bar_list.clear()
                print("sweepertje")
                for d in Level0NameList:
                    selectedlistl0bar_list.append(d)
            elif "WalletSwitch" in changed_id and WalletSwitch == "True":
                print("WalletSwitch")
                selectedlistl0bar_list.clear()
                for d in Level0NameList:
                    selectedlistl0bar_list.append(d)
            elif (
                not changed_id2 == "button_group"
                and selecteddatal0bar["points"]
                and button_group == "LevelName_0"
            ):
                print("selecteddatal0bar")
                selectedlistl0bar_list.clear()
                for p in selecteddatal0bar["points"]:
                    selectedlistl0bar_list.append(p["label"])
            elif "filter-dropdown-ex3-reset" in list(json.loads(changed_id2).values()):
                print("reset")
                selectedlistl0bar_list.clear()
                for j in Level0NameList:
                    selectedlistl0bar_list.append(j)
        except:
            print("nietgelukt")
        if len(selectedlistl0bar_list) > 0:
            print("returntje")
            return selectedlistl0bar_list
        else:
            print(PreventUpdate)
            raise dash.exceptions.PreventUpdate
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


Level1DD = html.Div(
    [
        html.Div(
            dcc.Textarea(value="Level one filters", id="dropdown1", className="h6")
        ),
        dcc.Dropdown(
            id="Level1NameSelect",
            # options=[{'label': html.Span([i],style={'background-color': LevelNameColor[i]}), 'value': i} for i in Level1NameList],
            multi=True,
            optionHeight=1,
            placeholder="Select a value",
            value=Level1NameListIS,
        ),
    ],
    id="Level1DD",
)


@app.callback(
    Output("graphoveralltime", "selectedData"),
    [
        Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
        # Input({'type': 'filter-dropdown-ex3-reset', 'index': ALL}, 'n_clicks'),
    ],
    session_check=False,
    prevent_initial_call=True,
)
def reset_clickDatal1(n_clicks):  # ,n_clicks2
    print("removefilterl1")
    return None


@app.callback(
    [
        Output("Level1NameSelect", "value"),
    ],
    Input("graph-level0compare", "selectedData"),
    Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
    Input("Level1NameSelect", "value"),
    Input("WalletSwitch", "label"),
    Input("button_group", "value"),
    Input({"type": "filter-dropdown-ex3-reset", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def Level1Update(
    selecteddatal1bar, n_clicks, Level1NameSelect, WalletSwitch, button_group, reset
):  # ,selecteddatal0,n_clicks,KPINameSelect,clickdatal0bar,clickdatal0
    print("Level1Update")
    try:
        selectedlistl1bar_list = []
        selectedlistl1bar_list.clear()
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        changed_id2 = [p["prop_id"] for p in dash.callback_context.triggered][0].split(
            "."
        )[0]
        try:
            if (
                '{"index":"LevelName_1","type":"sweepertje"}' in changed_id2
                and all(val is None for val in n_clicks) == False
            ):
                selectedlistl1bar_list.clear()
                print("sweepertje")
                for d in Level1NameList:
                    selectedlistl1bar_list.append(d)
            elif (
                not changed_id2 == "button_group"
                and selecteddatal1bar["points"]
                and button_group == "LevelName_1"
            ):
                selectedlistl1bar_list.clear()
                for p in selecteddatal1bar["points"]:
                    selectedlistl1bar_list.append(p["y"])
            elif "filter-dropdown-ex3-reset" in list(json.loads(changed_id2).values()):
                selectedlistl1bar_list.clear()
                for j in Level1NameList:
                    selectedlistl1bar_list.append(j)
        except:
            print()
        if len(selectedlistl1bar_list) > 0:
            return selectedlistl1bar_list
        else:
            raise dash.exceptions.PreventUpdate
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


Level2DD = html.Div(
    [
        html.Div(
            dcc.Textarea(value="Level two filters", id="dropdown2", className="h6")
        ),
        dcc.Dropdown(
            id="Level2NameSelect",
            #  options=[{'label': html.Span([i],style={'background-color': LevelNameColor[i]}), 'value': i} for i in Level2NameList],
            multi=True,
            placeholder="Select a value",
            value=Level2NameListIS,
        ),
    ],
    id="Level2DD",
)


@app.callback(
    Output("graph-with-slider", "selectedData"),
    [
        Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
        # Input({'type': 'filter-dropdown-ex3-reset', 'index': ALL}, 'n_clicks'),
    ],
    session_check=False,
    prevent_initial_call=True,
)
def reset_clickDatal2(n_clicks):  # ,n_clicks2
    print("removefilterl2")
    return None


@app.callback(
    [
        Output("Level2NameSelect", "value"),
    ],
    Input("graph-level0compare", "selectedData"),
    Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
    Input("Level2NameSelect", "value"),
    Input("WalletSwitch", "label"),
    Input("button_group", "value"),
    Input({"type": "filter-dropdown-ex3-reset", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def Level2Update(
    selecteddatal2bar, n_clicks, Level2NameSelect, WalletSwitch, button_group, reset
):  # ,selecteddatal0,n_clicks,KPINameSelect,clickdatal0bar,clickdatal0
    print("Level2Update")
    try:
        selectedlistl2bar_list = []
        selectedlistl2bar_list.clear()
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        changed_id2 = [p["prop_id"] for p in dash.callback_context.triggered][0].split(
            "."
        )[0]
        try:
            if (
                '{"index":"LevelName_2","type":"sweepertje"}' in changed_id2
                and all(val is None for val in n_clicks) == False
            ):
                selectedlistl2bar_list.clear()
                print("sweepertje")
                for d in Level2NameList:
                    selectedlistl2bar_list.append(d)
            elif selecteddatal2bar["points"]:
                selectedlistl2bar_list.clear()
                for p in selecteddatal2bar["points"] and button_group == "LevelName_2":
                    selectedlistl2bar_list.append(p["y"])
            elif "filter-dropdown-ex3-reset" in list(json.loads(changed_id2).values()):
                selectedlistl2bar_list.clear()
                for j in Level2NameList:
                    selectedlistl2bar_list.append(j)
        except:
            print()
        if len(selectedlistl2bar_list) > 0:
            return selectedlistl2bar_list
        else:
            raise dash.exceptions.PreventUpdate
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


Category1 = html.Div(
    [
        html.Div(dcc.Textarea(value="Category", id="Category1txt", className="h6")),
        dcc.Dropdown(
            id="Category1Select",
            options=[
                {
                    "label": html.Span([i], style={"background-color": buttoncolor}),
                    "value": i,
                }
                for i in Catergory0List
            ],  #
            multi=True,
            optionHeight=1,
            placeholder="Select a value",
            value=Catergory0List,  #'Derivatives',
        ),
    ],
    id="Category1",
)


@app.callback(
    [
        Output("Category1Select", "value"),
    ],
    Input("graph-level0compare", "selectedData"),
    Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
    Input("Category1Select", "value"),
    Input("WalletSwitch", "label"),
    Input("button_group", "value"),
    Input({"type": "filter-dropdown-ex3-reset", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def Category1Update(
    selecteddatal0bar, n_clicks, Category1Select, WalletSwitch, button_group, reset
):  # ,selecteddatal0,n_clicks,KPINameSelect,clickdatal0bar,clickdatal0
    print("Category1Selectupdate")
    try:
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        changed_id2 = [p["prop_id"] for p in dash.callback_context.triggered][0].split(
            "."
        )[0]
        selectedlistl0bar_list = []
        selectedlistl0bar_list.clear()
        try:
            if (
                '{"index":"SweepFilter1_0","type":"sweepertje"}' in changed_id2
                and all(val is None for val in n_clicks) == False
            ):
                selectedlistl0bar_list.clear()
                print("sweepertje")
                for d in Catergory0List:
                    selectedlistl0bar_list.append(d)
            elif "WalletSwitch" in changed_id and WalletSwitch == "True":
                print("WalletSwitch")
                selectedlistl0bar_list.clear()
                for d in Catergory0List:
                    selectedlistl0bar_list.append(d)
            elif (
                not changed_id2 == "button_group"
                and selecteddatal0bar["points"]
                and button_group == "Filter1_0"
            ):
                print("selecteddatal0bar")
                selectedlistl0bar_list.clear()
                for p in selecteddatal0bar["points"]:
                    selectedlistl0bar_list.append(p["y"])
            elif "filter-dropdown-ex3-reset" in list(json.loads(changed_id2).values()):
                print("reset")
                selectedlistl0bar_list.clear()
                for j in Catergory0List:
                    selectedlistl0bar_list.append(j)
        except:
            print("nietgelukt")
        if len(selectedlistl0bar_list) > 0:
            print("returntje")
            return selectedlistl0bar_list
        else:
            print(PreventUpdate)
            raise dash.exceptions.PreventUpdate
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


kpigrouplistinput = []
kpigrouplistinput3 = []

kpigroupstyleoutput = []
kpigroupstyleoutput3 = []

kpigrouplistinput.append(f"""Input('kpigroup0', 'n_clicks')""")

kpigroupstyleoutput.append(f"""Output('kpigroup0', 'style')""")

for i in range(len(KPIGroupList)):
    numbertmp = i
    numberidtmp = i + 1
    number = str(numbertmp)
    numberid = str(numberidtmp)
    kpigrouplistinput.append(f"""Input('kpigroup{numberidtmp}','n_clicks')""")
    kpigroupstyleoutput.append(f"""Output('kpigroup{numberidtmp}','style')""")

kpigrouplistinput2 = ",".join(kpigrouplistinput)
kpigrouplistinput3.append(kpigrouplistinput2)

kpigroupstyleoutput2 = ",".join(kpigroupstyleoutput)
kpigroupstyleoutput3.append(kpigroupstyleoutput2)


KPIdropdownCompare = html.Div(
    [
        dbc.Select(
            id="KPISelectCompare",
            options=[{"label": i, "value": i} for i in KPINameListCompare],
            value=KPINameListCompare[0],
        ),
    ],
    className="pretty_container",
    # style={"margin": "0px","padding-right":"0px","border-bottom-right-radius":"0px"},
    id="KPIContainerCompare",
)


Perioddropdown = html.Div(
    [
        dcc.Dropdown(
            id="Perioddropdown",
            # value="2019-05-01",
            multi=True,
        ),
    ],
    className="pretty_container",
)
Totaalaggregaatswitch = html.Div(
    [
        html.Div("Compare with total ", className="h6"),
        daq.BooleanSwitch(
            id="Totaalswitch",
            on=False,
            color=ProjectOrange,
            label="Dark",
            labelPosition="left",
        ),
    ]
)

CumulativeSwitch = html.Div(
    [
        html.Div("Cumulative ", className="h6"),
        daq.BooleanSwitch(
            id="CumulativeSwitch",
            on=False,
            color=ProjectOrange,
            label="Dark",
            labelPosition="left",
        ),
    ]
)

WalletSwitch = daq.BooleanSwitch(
    id="WalletSwitch",
    on=False,
    color=ProjectOrange,
    label="Dark",
    labelPosition="left",
)

CompetitorSwitch = daq.BooleanSwitch(
    id="CompetitorSwitch",
    on=False,
    color=ProjectOrange,
    label="Dark",
    labelPosition="left",
)


TargetSwitch = html.Div(
    [
        html.Div("Target ", className="h6"),
        daq.BooleanSwitch(
            id="TargetSwitch",
            on=False,
            color=ProjectOrange,
            label="Dark",
            labelPosition="left",
        ),
    ]
)

PercentageTotalSwitch = html.Div(
    [
        html.Div("Percentage of total ", className="h6"),
        daq.BooleanSwitch(
            id="PercentageTotalSwitch",
            on=True,
            color=ProjectOrange,
            label="Dark",
            labelPosition="left",
        ),
    ]
)

PercentageTotalSwitchNoTime = html.Div(
    [
        html.Div("Percentage of total no time", className="h6"),
        daq.BooleanSwitch(
            id="PercentageTotalSwitchNoTime",
            on=False,
            color=ProjectOrange,
            label="Dark",
            labelPosition="left",
        ),
    ]
)

ShowValueSwitch = html.Div(
    [
        html.Div("Show values", className="h6"),
        daq.BooleanSwitch(
            id="ShowValueSwitch",
            on=False,
            color=ProjectOrange,
            label="Dark",
            labelPosition="left",
        ),
    ]
)


fade = html.Div(
    [
        dbc.Button(
            children=[html.I("compare", className="material-icons md-48"), " Filters"],
            id="fade-transition-button",
            color="info",
        ),
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            KPIGroupdropdown, id="KPIGroup", style={"display": "none"}
                        ),
                        html.Div(KPIdropdown, id="KPI"),
                    ]
                ),
                className="pretty_bigtab",
            ),
            id="fade-transition",
            style={"transition": "opacity 100ms ease"},
        ),
    ],
)


@app.callback(
    Output("fade-transition", "is_open"),
    [Input("fade-transition-button", "n_clicks")],
    [State("fade-transition", "is_open")],
    prevent_initial_callback=True,
)
def toggle_collapse(n, is_open):
    if n:
        # Button has never been clicked
        return not is_open
    return is_open


def linesormarkers(Grain):
    if Grain == "D":
        return "lines"
    elif Grain == "M":
        return "lines"
    else:
        return "lines+markers"


def rangeselector(Grain):
    if Grain == "D":
        buttons = list(
            [
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=14, label="2w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
            ]
        )
    elif Grain == "M":
        buttons = list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=10, label="All", step="year", stepmode="backward"),
            ]
        )
    else:
        buttons = list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=10, label="All", step="year", stepmode="backward"),
            ]
        )
    return buttons


def CalculationLogic0Cum(Calculation):
    if Calculation == 2:
        CalculationString = (
            "df_by_Level0Name.NumeratorCum / df_by_Level0Name.DenominatorCum"
        )
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_by_Level0Name.NumeratorCum"
        return CalculationString


def CalculationLogic1Cum(Calculation):
    if Calculation == 2:
        CalculationString = (
            "df_by_Level1Name.NumeratorCum / df_by_Level1Name.DenominatorCum"
        )
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_by_Level1Name.NumeratorCum"
        return CalculationString


def CalculationLogic2Cum(Calculation):
    if Calculation == 2:
        CalculationString = (
            "df_by_Level2Name.NumeratorCum / df_by_Level2Name.DenominatorCum"
        )
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_by_Level2Name.NumeratorCum"
        return CalculationString


def CalculationLogic0(Calculation):
    if Calculation == 2:
        CalculationString = "df_by_Level0Name.Numerator / df_by_Level0Name.Denominator"
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_by_Level0Name.Numerator"
        return CalculationString


def CalculationLogic2(Calculation):
    if Calculation == 2:
        CalculationString = "df_by_Level2Name.Numerator / df_by_Level2Name.Denominator"
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_by_Level2Name.Numerator"
        return CalculationString


def CalculationLogic1(Calculation):
    if Calculation == 2:
        CalculationString = "df_by_Level1Name.Numerator / df_by_Level1Name.Denominator"
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_by_Level1Name.Numerator"  # "(df_by_Level1Name.Numerator - df_by_Level1Name.Numerator_LP) / df_by_Level1Name.Numerator"
        return CalculationString


def CalculationLogicTotal(Calculation):
    if Calculation == 2:
        CalculationString = "dff.Numerator / dff.Denominator"
        return CalculationString
    elif Calculation == 1:
        CalculationString = "dff.Numerator"
        return CalculationString


def CalculationLogicCompKPI(Calculation):
    if Calculation == 2:
        CalculationString = "df_filtered_kpi.Numerator / df_filtered_kpi.Denominator"
        return CalculationString
    elif Calculation == 1:
        CalculationString = "df_filtered_kpi.Numerator"
        return CalculationString


def CalculationLogicTotalCompare(Calculation):
    if Calculation == 2:
        CalculationString = "dffcomp.Numerator / dffcomp.Denominator"
        return CalculationString
    elif Calculation == 1:
        CalculationString = "dffcomp.Numerator"
        return CalculationString


def PercentageTotalSwitchDEF(PercentageSwitchie):
    if PercentageSwitchie == "True":
        list2 = "'percent'"
        return list2
    elif PercentageSwitchie == "False":
        list2 = "''"
        return list2


def Totaalloop(Totaalloop):
    if Totaalloop == "True":
        list = "[tracestotal,traces2]"
        return list
    elif Totaalloop == "False":
        list = "[traces2]"
        return list


def Cumloop0(Cumloop):
    if Cumloop == "False":
        list = ["df_by_Level0Name", "CalculationLogic0(Calculation)"]
        return list
    elif Cumloop == "True":
        list = ["df_by_Level0Name", "CalculationLogic0Cum(Calculation)"]
        return list


def Cumloop1(Cumloop):
    if Cumloop == "False":
        list = ["df_by_Level1Name", "CalculationLogic1(Calculation)"]
        return list
    elif Cumloop == "True":
        list = ["df_by_Level1Name", "CalculationLogic1Cum(Calculation)"]
        return list


def Cumloop2(Cumloop):
    if Cumloop == "False":
        list = ["df_by_Level2Name", "CalculationLogic2(Calculation)"]
        return list
    elif Cumloop == "True":
        list = ["df_by_Level2Name", "CalculationLogic2Cum(Calculation)"]
        return list


def KPISelectedStyle(kpi):
    Notation = KPINotation[kpi]
    if Notation == "%":
        Notation = ['".1%"']
        return Notation
    elif Notation == "#":
        Notation = ['".2s"']
        return Notation
    elif Notation == "$":
        Notation = ['"$.2s"']
        return Notation


def KPISelectedStylePython(kpi):
    Notation = KPINotation[kpi]
    if Notation == "%":
        Notation = ["'{:2.2%}'"]
        return Notation
    elif Notation == "#":
        Notation = ["'{:.0f}'"]
        return Notation
    elif Notation == "$":
        Notation = ["'${:,.2f}'"]
        return Notation


def KPISelectedStyleFloat(kpi):
    Notation = KPINotation[kpi]
    if Notation == "%":
        Notation = ['"{:.2%}"']
        return Notation
    elif Notation == "#":
        Notation = ['".2s"']
        return Notation
    elif Notation == "$":
        Notation = ['"$.2s"']
        return Notation


def CalculationDEF(kpi):
    Calculation = KPICalculation[kpi]
    return Calculation


def NumaggregateDEF(kpi):
    Calculation = KPINumAgg[kpi]
    return Calculation


def DenomaggregateDEF(kpi):
    Calculation = KPIDenomAgg[kpi]
    return Calculation


def IsCum(kpi):
    IsCum = KPICum[kpi]
    return IsCum


def kpicolorDEF(kpi):
    Calculation = KPIColor[kpi]
    return Calculation


def visualDEF(kpi):
    visuall = visual[kpi]
    return visuall


def kpilevel0attrDEF(kpi):
    kpilevel0attr = Level0attr[kpi]
    return kpilevel0attr


def kpilevel1attrDEF(kpi):
    kpilevel1attr = Level1attr[kpi]
    return kpilevel1attr


def kpilevel2attrDEF(kpi):
    kpilevel2attr = Level2attr[kpi]
    return kpilevel2attr


def update_filter_compare_l2(
    dfl2Compare, GrainSelect, KPISelectCompare, Level1NameSelect, Level2NameSelect
):
    dffcomp = dfl2Compare[
        (dfl2Compare["Grain"] == GrainSelect)
        & (dfl2Compare["KPIName"] == KPISelectCompare)
        & (dfl2Compare["LevelName_1"].isin(Level1NameSelect))
        & dfl2Compare["LevelName_2"].isin(Level2NameSelect)
    ]
    return dffcomp


def update_filter_compare_l1(
    dfl1Compare, GrainSelect, KPISelectCompare, Level1NameSelect
):
    dffcomp = dfl1Compare[
        (dfl1Compare["Grain"] == GrainSelect)
        & (dfl1Compare["KPIName"] == KPISelectCompare)
        & (dfl1Compare["LevelName_1"].isin(Level1NameSelect))
    ]
    return dffcomp


def update_filter_compare_l0(dfl0Compare, GrainSelect, KPISelectCompare):
    dffcomp = dfl0Compare[
        (dfl0Compare["Grain"] == GrainSelect)
        & (dfl0Compare["KPIName"] == KPISelectCompare)
    ]
    return dffcomp


def update_filter_l0(dfl0, GrainSelect, KPISelect, Level0NameSelect):
    dff = dfl0[
        (dfl0["Grain"] == GrainSelect)
        & (dfl0["KPIName"] == KPISelect)
        & (dfl0["LevelName_0"].isin(Level0NameSelect))
    ]
    return dff


def update_filter_l1(dfl1, GrainSelect, KPISelect, Level0NameSelect, Level1NameSelect):
    dff = dfl1[
        (dfl1["Grain"] == GrainSelect)
        & (dfl1["KPIName"] == KPISelect)
        & (dfl1["LevelName_0"].isin(Level0NameSelect))
        & (dfl1["LevelName_1"].isin(Level1NameSelect))
    ]
    return dff


def update_filter_l2(
    dfl2,
    GrainSelect,
    KPISelect,
    Level0NameSelect,
    Level1NameSelect,
    Level2NameSelect,
    Category1,
):
    dff = dfl2[
        (dfl2["Grain"] == GrainSelect)
        & (dfl2["KPIName"] == KPISelect)
        & (dfl2["LevelName_0"].isin(Level0NameSelect))
        & (dfl2["LevelName_1"].isin(Level1NameSelect))
        & (dfl2["LevelName_2"].isin(Level2NameSelect))
        & (dfl2["Filter1_0"].isin(Category1))
    ]
    return dff


def update_KPIDescription(KPISelect):

    KPIValue = KPISelectedStyle(KPISelect)
    return KPIValue


@app.callback(
    dash.dependencies.Output("Totaalswitch", "label"),
    [dash.dependencies.Input("Totaalswitch", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("CumulativeSwitch", "label"),
    [dash.dependencies.Input("CumulativeSwitch", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("TargetSwitch", "label"),
    [dash.dependencies.Input("TargetSwitch", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("CompetitorSwitch", "label"),
    [dash.dependencies.Input("CompetitorSwitch", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("WalletSwitch", "label"),
    [dash.dependencies.Input("WalletSwitch", "on")],
    prevent_initial_call=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("PercentageTotalSwitch", "label"),
    [dash.dependencies.Input("PercentageTotalSwitch", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("PercentageTotalSwitchNoTime", "label"),
    [dash.dependencies.Input("PercentageTotalSwitchNoTime", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


@app.callback(
    dash.dependencies.Output("ShowValueSwitch", "label"),
    [dash.dependencies.Input("ShowValueSwitch", "on")],
    prevent_initial_callback=True,
)
def update_output(on):
    return format(on)


######################################################################################################################
######################################################################################################################
################################################----tabs aanmaken----###############################################
######################################################################################################################
######################################################################################################################
button_group = html.Div(
    [
        dbc.RadioItems(
            id="button_group",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn-tab-top btn-outline-primary-tabs-top",
            labelCheckedClassName="active",
            options=[
                {"label": "LevelName_0", "value": "LevelName_0"},
                {"label": "LevelName_1", "value": "LevelName_1"},
                {"label": "LevelName_2", "value": "LevelName_2"},
                {"label": "Filter1_0", "value": "Filter1_0"},
            ],
            value="LevelName_0",
        ),
        html.Div(id="output"),
    ],
    className="radio-group",
)


button_group1 = html.Div(
    [
        dbc.RadioItems(
            id="button_group1",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn-tab-bottom btn-outline-primary-tabs-top",
            labelCheckedClassName="active",
            # options=[
            #    {"label": "LevelName_0", "value": 'LevelName_0'},
            #    {"label": "LevelName_1", "value": 'LevelName_1'},
            #    {"label": "LevelName_2", "value": 'LevelName_2'},
            #    {"label": "Filter1_1", "value": "Filter1_1"},
            # ],
            value="LevelName_0",
            style={"right": "0px", "margin-bottom": "2px"},
        ),
        html.Div(id="outputattributecolor"),
    ],
    className="radio-group",
)

tabs = html.Div(
    [
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        dls.Hash(  # ,spinner_class_name='loading'
                            dcc.Graph(
                                id="graphlevel0",
                                config=dict(
                                    modeBarButtonsToAdd=["customButton"],
                                    modeBarButtonsToRemove=[
                                        "pan",
                                        "lasso2d",
                                        "select",
                                        "zoom2d",
                                        "zoomIn",
                                        "zoomOut",
                                        "toImage",
                                        "resetScale",
                                        "hoverCompareCartesian",
                                        "logo",
                                        "autoScale",
                                    ],
                                    displaylogo=False,
                                    # scrollZoom = True,
                                    toImageButtonOptions=dict(
                                        width=550,
                                        height=300,
                                        format="png",
                                        scale=10,
                                        filename="Plotlygraph",
                                    ),
                                ),
                                className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12 pretty_graph",
                            ),
                            color=ProjectOrange,
                            speed_multiplier=2,
                            size=100,
                            # debounce=1000
                        ),
                        className="col-12 col-sm-12 col-md-12 col-lg-7 col-xl-7 empty_tab",
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                dls.Hash(
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                id="graph-level0compare",
                                                clear_on_unhover=True,
                                                config=dict(
                                                    modeBarButtonsToAdd=[
                                                        "customButton"
                                                    ],
                                                    modeBarButtonsToRemove=[
                                                        "pan",
                                                        "zoom2d",
                                                        "select2d",
                                                        "lasso2d",
                                                        "zoomIn",
                                                        "zoomOut",
                                                        "toImage",
                                                        "resetScale",
                                                        "hoverCompareCartesian",
                                                        "logo",
                                                        "autoScale",
                                                    ],
                                                    displaylogo=False,
                                                    # scrollZoom=True,
                                                    toImageButtonOptions=dict(
                                                        width=500,
                                                        height=300,
                                                        format="png",
                                                        scale=10,
                                                        filename="Plotlygraph",
                                                    ),
                                                ),
                                                style={"overflow": "auto"},
                                            ),
                                        ]
                                    ),
                                    color=ProjectOrange,
                                    speed_multiplier=2,
                                    size=100,
                                    # debounce=1000
                                ),
                                # daq.BooleanSwitch(
                                #     id='AnimationSwitch',
                                #     on=False,
                                #     color=ProjectOrange,
                                #     label="Create nimation",
                                # labelPosition="right",
                                # )
                                html.Div(
                                    [
                                        html.I(
                                            "play_circle",
                                            className="material-icons",
                                            n_clicks=0,
                                        ),
                                        html.Span(
                                            "Create animation",
                                            className="text nav-text",
                                        ),
                                    ],
                                    id="animation",
                                    style={"position": "relative", "z-index": "1"},
                                ),
                            ],
                            className="col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 pretty_graph2",
                        ),
                        className="col-12 col-sm-12 col-md-12 col-lg-5 col-xl-5 empty_tab2",
                    ),
                ],
                className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12",
            ),
            className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12 pretty_tab",
            id="Tab0drilldown",
        )
    ],
    id="tabsdrilldown",
)

tabscompare = dbc.Tabs(
    [
        dbc.Tab(
            label="Compare two",
            children=[
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(KPIdropdownCompare, id="KPICompare"),
                            dbc.Col(
                                dbc.Spinner(
                                    children=[
                                        dcc.Graph(
                                            id="graph-compare-kpi",
                                            config={
                                                "modeBarButtonsToRemove": [
                                                    "pan",
                                                    "lasso2d",
                                                    "select",
                                                    "zoom2d",
                                                    "zoomIn",
                                                    "zoomOut",
                                                    "toImage",
                                                    "resetScale",
                                                    "hoverCompareCartesian",
                                                    "logo",
                                                    "autoScale",
                                                ],
                                                "displaylogo": False,
                                                # 'scrollZoom': True,
                                            },
                                            className="col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 pretty_graph",
                                        )
                                    ]
                                ),
                                className="col-12 col-sm-11 col-md-11 col-lg-12 col-xl-12 empty_tab2",
                            ),
                        ],
                        className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12",
                    ),
                    className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12 pretty_tab",
                )
            ],
            id="Tabcompare",
        ),
        dbc.Tab(
            label="Compare change",
            children=[
                dbc.CardBody(
                    dbc.Row(
                        [
                            # dbc.Col(KPIdropdownCompare,
                            #        id='KPICompare'),
                            dbc.Col(
                                dbc.Spinner(
                                    children=[
                                        dcc.Graph(
                                            id="graph-compare-kpi2",
                                            config={
                                                "modeBarButtonsToRemove": [
                                                    "pan",
                                                    "lasso2d",
                                                    "select",
                                                    "zoom2d",
                                                    "zoomIn",
                                                    "zoomOut",
                                                    "toImage",
                                                    "resetScale",
                                                    "hoverCompareCartesian",
                                                    "logo",
                                                    "autoScale",
                                                ],
                                                "displaylogo": False,
                                                #'scrollZoom': True,
                                            },
                                            className="col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 pretty_graph",
                                        )
                                    ]
                                ),
                                className="col-12 col-sm-11 col-md-11 col-lg-12 col-xl-12 empty_tab2",
                            ),
                        ],
                        className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12",
                    ),
                    className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12 pretty_tab",
                )
            ],
            id="Tabcompare2",
        ),
        #  dbc.Tab(label="Tab compare 2", children=[tab1_compare]),
    ]
)

tabscontainer = html.Div(
    dbc.Tabs(
        children=[
            dbc.Tab(label="Tab 1", children=[tabs]),
            dbc.Tab(label="Tab 2", children=[tabscompare]),
        ]
    )
    #  )
    ,
    style={"min-height": "auto"},
)


######################################################################################################################
################################################----layout aanmaken----###############################################
######################################################################################################################
######################################################################################################################

app.layout = html.Div(
    [
        html.Div(
            [
                dbc.Col(
                    [WalletSwitch], className="col-sm-12 col-md-12 col-lg-12 col-xl-12"
                ),
                dbc.Button(
                    "Connect wallet",
                    id="toggle-buttonn",
                    className="mb-3 form-check-label btn btn-outline-primary active",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Modal Title"),
                        dbc.ModalBody(
                            html.Div(
                                [
                                    dcc.Input(
                                        id="input-field",
                                        type="text",
                                        placeholder="Enter value...",
                                    ),
                                    dbc.Col(
                                        [CompetitorSwitch],
                                        className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    ),
                                ]
                            )
                        ),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="close-buttonn", className="ml-auto")
                        ),
                    ],
                    id="modalwallet",
                    is_open=False,
                ),
            ],
            style={
                "position": "fixed",
                "top": "2%",
                "right": "12px",
                "z-index": "1",
                "display": "flex",
                "flex-direction": "column",
            },
        ),
        html.I(
            "chevron_right",
            className="material-icons toggle-right",
            id="Opennavbar-right",
        ),  # html.I("filter_alt", id='dropdowncontrol', className="material-icons filtericon", n_clicks=0),
        html.Div(
            [
                html.I(
                    "filter_alt", id="sweepl0filter", className="material-icons md-48"
                ),
            ],
            style={
                "position": "fixed",
                "top": "44%",
                "right": "12px",
                "z-index": "1",
                "display": "flex",
                "flex-direction": "column",
            },
        ),
        html.Div(
            [],
            id="sweepers",
            style={
                "position": "fixed",
                "top": "52%",
                "right": "12px",
                "z-index": "1",
                "display": "flex",
                "flex-direction": "column",
            },
        ),
        # dcc.Graph(id='animatedbar'),
        dbc.Row(
            [
                html.Div(
                    id="output-container-date-picker-range",
                    style={"margin-top": "12px", "display": "none"},
                    className="h7",
                ),
                dbc.Modal(
                    [
                        dbc.ModalBody(
                            children=[
                                dbc.Col(
                                    [mainlogo],
                                    className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    style={"margin-bottom": "2px"},
                                ),
                                dbc.Col(
                                    [Category1],
                                    className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    style={"margin-bottom": "2px"},
                                ),
                                dbc.Col(
                                    [Level0DD],
                                    className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    style={"margin-bottom": "2px"},
                                ),
                                dbc.Col(
                                    [Level1DD],
                                    className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    style={"margin-bottom": "2px"},
                                ),
                                dbc.Col(
                                    [Level2DD],
                                    className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    style={"margin-bottom": "2px"},
                                ),
                            ],
                            id="dropdowns",
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close",
                                id="close-filter",
                                className="ms-auto",
                                n_clicks=0,
                            ),
                            style={"border-top": "0px"},
                        ),
                    ],
                    id="modalfilter",
                    className="modalfilter",
                    is_open=False,
                ),
                dbc.Col(
                    fade,
                    className="col-sm-12 col-md-12 col-lg-2 col-xl-2",
                    style={"display": "none"},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            Perioddropdown,
                            className="col-sm-2 col-md-2 col-lg-2 col-xl-2",
                            style={"display": "none"},
                        ),
                        dls.Hash(
                            html.Div(
                                className="col-sm-9 col-md-9 col-lg-9 col-xl-9",
                                style={"margin": "0 auto"},
                                id="cardsid",
                            ),
                            color=ProjectOrange,
                            speed_multiplier=2,
                            size=100,
                        ),
                        html.Div(id="container-ex3", children=[]),
                        # html.Div(className="col-sm-9 col-md-9 col-lg-9 col-xl-9"
                        #    ,style={"margin": '0 auto'},id='cardsid')
                    ]
                ),
            ]
        ),
        dbc.Row(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.I(
                                    "settings_suggest",
                                    id="open-settings",
                                    className="material-icons",
                                    n_clicks=0,
                                ),
                            ],
                            style={"position": "relative", "z-index": "1"},
                        ),
                        dbc.Row(
                            [
                                html.Div(
                                    [button_group],
                                    id="button_group00",
                                    style={"position": "relative"},
                                )
                            ],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                        tabs,
                        dbc.Row(
                            [
                                html.Div(
                                    [button_group1],
                                    id="button_group11",
                                    style={"right": "0px", "position": "absolute"},
                                )
                            ],
                            style={"margin-bottom": "20px"},
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                    ],
                    id="tabscontainer",
                    style={"min-height": "auto"},
                ),
                html.Div("test", id="graphcontainer", style={"display": "none"}),
                html.Div(
                    [
                        dbc.Button(
                            children=[
                                html.I(
                                    "keyboard_double_arrow_down",
                                    className="material-icons md-48",
                                )
                            ],
                            id="collapse-button",
                            className="mb-3",
                            n_clicks=0,
                            style={"right": "50%", "bottom": "2%", "position": "fixed"},
                        ),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    html.Div(
                                        id="graphcontainerOutput",
                                        style={"min-height": "auto"},
                                    )
                                ),
                                style={"background-color": "transparent"},
                            ),
                            id="collapse",
                            is_open=False,
                        ),
                    ]
                ),
            ],
            className="col-sm-11 col-md-11 col-lg-10 col-xl-10 pretty_bigtab",
            style={
                "margin": "0 auto",
                "margin-top": "20px",
                "min-height": "auto",
                "display": "block",
            },
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Graph settings", className="h5"),
                    style={"border-bottom": "0px"},
                ),
                dbc.ModalBody(
                    children=[
                        dbc.Col(
                            [Radiograin],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                            style={"margin-bottom": "46px"},
                        ),
                        dbc.Col(
                            [Totaalaggregaatswitch],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                        dbc.Col(
                            [CumulativeSwitch],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                        dbc.Col(
                            [TargetSwitch],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                        dbc.Col(
                            [PercentageTotalSwitch],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                        dbc.Col(
                            [PercentageTotalSwitchNoTime],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                        dbc.Col(
                            [ShowValueSwitch],
                            className="col-sm-12 col-md-12 col-lg-12 col-xl-12",
                        ),
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-settings",
                        className="form-check-label btn btn-outline-primary active",
                        n_clicks=0,
                    ),
                    style={"border-top": "0px"},
                ),
            ],
            id="modal",
            is_open=False,
        ),
        html.Div(html.Nav(id="navbar")),
        html.Span(html.I(""), style={"margin-top": "5em", "display": "block"}),
        dcc.Store(id="dflmasterfrontpolarsRedis"),
        dcc.Store(id="mastersetkpifiltered"),
        dcc.Store(id="mastersetkpifilterednotime"),
        dcc.Store(id="dfl0"),
        dcc.Store(id="dfl1"),
        dcc.Store(id="dfl2"),
        dcc.Store(id="dffcomparefilter"),
        dcc.Store(id="dflcomparekpi"),
        dcc.Store(id="selectedkpigroup"),
        dcc.Store(id="dfgroups"),
        dcc.Store(id="coinsinwallet"),
        dcc.Store(id="coinsinwalletComp"),
        dcc.Store(id="contract_addresses_internal_toproject"),
        dcc.Store(id="daterange"),
        # dcc.Store(id='pieorbar'),
        dcc.Store(id="graph-level0compare-dataset"),
        dcc.Store(id="graphlevel0data"),
        # graphlevel0data
        WindowBreakpoints(
            id="breakpoints",
            # Define the breakpoint thresholds
            widthBreakpointThresholdsPx=[800, 1200],
            # And their name, note that there is one more name than breakpoint thresholds
            widthBreakpointNames=["sm", "md", "lg"],
        ),
        dbc.Row(
            [
                # html.Div([dcc.DatePickerRange(
                #            id='my-date-picker-range',
                #            min_date_allowed=date(2010, 1, 1),
                #            max_date_allowed=date(2030, 12, 31),
                #            initial_visible_month=date(2020, 1, 1),
                #            end_date=date(2022, 10, 31),
                #            style={"color": "red"}
                #         ),
            ]
        ),
    ],
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output("daterange", "data")],
    Input("GrainSelect", "value"),
    Input("graphlevel0", "relayoutData"),
    [State("daterange", "data")],
    #  prevent_initial_callback=True
)
def updatestartdt(GrainSelect, relayoutdata1, daterangestate):
    print("execute updatestartdt")
    try:
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        # datefromtmp.clear()
        # datetotmp.clear()
        daterange = []
        daterange.append("2023-01-01")
        daterange.append("2023-09-01")
        if not daterangestate:
            print("notdaterange")
            return daterange
        else:
            if changed_id == "GrainSelect.value":
                daterange.clear()
                if GrainSelect == "D":
                    daterange.append("2023-06-01")
                    daterange.append("2023-09-01")
                    return daterange
                elif GrainSelect == "M":
                    daterange.append("2023-01-01")
                    daterange.append("2023-09-01")
                    return daterange
                elif GrainSelect == "Q":
                    daterange.append("2022-01-01")
                    daterange.append("2023-09-01")
                    return daterange
                elif GrainSelect == "Y":
                    daterange.append("2020-01-01")
                    daterange.append("2023-12-31")
                    return daterange
            elif changed_id == "graphlevel0.relayoutData":
                if relayoutdata1 == {"autosize": True} or relayoutdata1 is None:
                    print("prventer")
                    raise PreventUpdate
                elif "yaxis.range" in relayoutdata1:
                    raise PreventUpdate
                else:
                    print("xaxisss")
                    daterange.clear()
                    if "xaxis.range[0]" in relayoutdata1:
                        daterange.append(relayoutdata1["xaxis.range[0]"][0:10])
                        daterange.append(relayoutdata1["xaxis.range[1]"][0:10])
                        return daterange
                    elif "xaxis.range" in relayoutdata1:
                        daterange.append(relayoutdata1["xaxis.range"][0])
                        daterange.append(relayoutdata1["xaxis.range"][1])
                        return daterange
                    else:
                        return daterange
            else:
                return daterange
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


@app.callback(
    Output("modalwallet", "is_open"),
    [Input("toggle-buttonn", "n_clicks"), Input("close-buttonn", "n_clicks")],
    [State("modalwallet", "is_open")],
    prevent_initial_callback=True,
)
def toggle_modal(toggle_clicks, close_clicks, is_open):
    print("modalwallet")
    if toggle_clicks or close_clicks:
        return not is_open
    return is_open


KPIGroup = []


@app.callback(
    [
        Output("KPIGroupSelect", "value"),
    ],
    [Input({"type": "kpigroup-ex3", "index": ALL}, "n_clicks")],
    # prevent_initial_call=True
    # eval(kpigrouplistinput3[0])
    prevent_initial_call=True,
)
def KPIgrouplighter(n_clicks):  # *args
    print("execute KPIgrouplighter")
    try:
        if all(val is None for val in n_clicks) == True:
            PreventUpdate
        KPIGroupList = d_kpi["KPIGroup"].unique().tolist()
        if 1 in n_clicks:
            changed_id = [p["prop_id"] for p in dash.callback_context.triggered][
                0
            ].split(".")[0]
            valuelist = []
            try:
                valuelisttmp = list(json.loads(changed_id).values())
                valuelist.clear()
                valuelist.append(valuelisttmp[0])
            except json.decoder.JSONDecodeError as e:
                print("Unable to decode JSON: ", e)

            if changed_id == '{"index":"kpigroup0","type":"kpigroup-ex3"}':
                KPIGrouptmp1 = []
                for i in range(len(KPIGroupList)):
                    KPIGrouptmp1.append(KPIGroupList[i])
                KPIGroup.append(KPIGrouptmp1)
                kpicountout.clear()
                kpicountout.append(len(KPINameList))
            elif valuelist:
                KPIGroup.append([valuelist[0]])
        if not KPIGroup:
            KPIGrouptmp3 = []
            for i in range(len(KPIGroupList)):
                KPIGrouptmp3.append(KPIGroupList[i])
            KPIGroup.append(KPIGrouptmp3)
            kpicountout.clear()
            kpicountout.append(len(KPINameList))
        KPIGroup2 = KPIGroup[-1]
        return KPIGroup2
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


kpi = []


# print(eval(carddivnclicks3new[0]+','+kpigrouplistinput3[0]) if carddivnclicks3new else eval(carddivnclicks3[0]+','+kpigrouplistinput3[0]))
@app.callback(
    [
        Output("KPISelect", "value"),
        #  Output({'type': 'output-ex3', 'index': MATCH}, 'children'),
    ],
    [
        Input({"type": "filter-dropdown-ex3", "index": ALL}, "n_clicks"),
        Input({"type": "filter-dropdown-ex3-reset", "index": ALL}, "n_clicks"),
        Input("KPIGroupSelect", "value"),
        # Input({'type': 'kpigroup-ex3', 'index': ALL}, 'n_clicks'),
        # eval(kpigrouplistinput3[0])
    ],
    prevent_initial_call=True,
)
def update_df_KPIGroup(n_clicks, n_clicks2, KPIGroupSelect):  # ,*args,KPIGroupSelect
    print("execute update_df_KPISelect")
    try:
        ctx = dash.callback_context
        merged_clicks = n_clicks + n_clicks2
        if all(val is None for val in n_clicks) == True:
            print("weird")
            raise PreventUpdate
        else:
            dffKPISelect = d_kpi[(d_kpi["KPIGroup"].isin(KPIGroupSelect))]
            dffKPISelect.sort_values(by=["Sorting"])
            KPINameListi = dffKPISelect["KPIName"].unique()
            try:
                changed_id = [p["prop_id"] for p in dash.callback_context.triggered][
                    0
                ].split(".")[0]
                valuelist = list(json.loads(changed_id).values())
            except json.decoder.JSONDecodeError as e:
                print("Unable to decode JSON: ", e)
            try:
                changed_id = [p["prop_id"] for p in dash.callback_context.triggered][
                    0
                ].split(".")[0]
                if len(dash.callback_context.triggered) != 1:
                    print("nothingtoseehere")
                elif "filter-dropdown-ex3-reset" in valuelist:
                    kpi.append(valuelist[0])
                elif "filter-dropdown-ex3" in valuelist:
                    kpi.append(valuelist[0])
                elif "kpigroup" in changed_id[0:8]:
                    kpi.append(KPINameListi[0])
            except:
                print("bs!")
            return KPINameListi[0] if not kpi else kpi[-1]
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


######################################################################################################################
######################################################################################################################
################################################----tab 0 aanmaken----###############################################
######################################################################################################################
######################################################################################################################


@app.callback(
    Output("graph-level0compare", "selectedData"),
    [
        Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
    ],
    session_check=False,
    prevent_initial_call=True,
)
def reset_clickDatal0(n_clicks):  # ,n_clicks2
    print("removefilterl0")
    print(n_clicks)
    return None


# @app.callback([
#    Output("Category1Select", "value"),
#    ],
#    Input('sweepl0filter', 'n_clicks'),
#    State("KPISelect", "value"),
# )
#
# def dropdown1_reset(n_clicks,KPISelect):  #,*args ,Level2NameSelect,toggle, relayoutData
#   print('execute dropdown1_reset')
#   print(KPISelect)
#   Category1filtered = dfl0[(dfl0["KPIName"] == KPISelect)]
#   output=[]
#   Category1Select =  [i for i in Category1filtered["Filter1_0"].unique()]
#   for i in Category1Select:
#       output.append(i)
#   print(Category1Select)
#   return [Category1Select]


# datefromtmp = []
# datetotmp = []
# datefromtmp.append(str(dfl0['Period_int'].min())[0:10])
# datetotmp.append(str(dfl0['Period_int'].max())[0:10])


@app.callback(
    [
        Output("coinsinwallet", "data"),  # dit is een random gekozen output
    ],
    Input("input-field", "value"),
    prevent_initial_callback=True,
)
def wegschrijvendiehap(inputfield):
    print("wegschrijvendiehappert")
    # print(os.environ.values())
    try:
        if inputfield:
            with open(
                "assets/Attributes/dashboard_data/contract_addresses_internal_toproject.json",
                "r",
            ) as f:
                # Load JSON data from file
                data = json.load(f)
                data_str = json.dumps(data)
            result = subprocess.run(
                ["node", "BatchRequestSimple.js", inputfield, data_str],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            answer = result.stdout
            tmpaswer = [
                {"id": "12.0", "value": "2.891323835569685308"},
                {"id": "55.0", "value": "28.091493"},
                {"id": "8.0", "value": "1.918714491283379120"},
                {"id": "6.0", "value": "158.502814222575437952"},
                {"id": "9.0", "value": "38362.771085839216539171"},
            ]
            idlist = [int(float(item["id"])) for item in json.loads(answer)]
            return idlist
        else:
            PreventUpdate
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


# @app.callback([Output('coinsinwallet', 'data'), # dit is een random gekozen output
#                ],
#                Input("contract_addresses_internal_toproject", "data")
#            )
# def coinsinwallet(contract_addresses_internal_toproject):
#    print('coinsinwallet')
#    if contract_addresses_internal_toproject:
#        idlist = [int(item['id']) for item in contract_addresses_internal_toproject]
#        print(idlist)
#        return idlist


@app.callback(
    [
        Output("coinsinwalletComp", "data"),  # dit is een random gekozen output
    ],
    Input("coinsinwallet", "data"),
    Input("CompetitorSwitch", "value"),
    prevent_initial_callback=True,
    #   Input("contract_addresses_internal_toproject", "data"),
)
def coinsinwallet(coinsinwallet, CompetitorSwitch):
    print("jodeliee")
    try:
        if not coinsinwallet:
            return ""
        else:
            print("startcoinsinwallet")
            if CompetitorSwitch == "False":
                return ""
            else:
                comp_values = Projects.loc[
                    Projects["Project_ID"].isin(coinsinwallet), "MainCompetitors_NoJoin"
                ].values
                result_list = []
                for item in comp_values:
                    if isinstance(item, str):
                        values = item.split("&")
                        result_list.extend(values)
                    elif not np.isnan(item):
                        result_list.append(item)

                result_list = [int(value) for value in result_list]
                endresult = list(coinsinwallet) + list(result_list)
                return endresult if endresult else ""
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


@app.callback(
    Output("dflmasterfrontpolarsRedis", "data"),
    [Input("daterange", "data"), Input("GrainSelect", "value")],
)
def polarsdataframeinitial(daterange, GrainSelect):
    print("execute polarsdataframeinitial")
    datefromtmp = []
    datetotmp = []
    datefromtmp.append(daterange[0])
    datetotmp.append(daterange[1])
    dff = dflmasterfrontpolars.filter(
        (pl.col("Grain") == GrainSelect)
        & (pl.col("Period_int") >= datefromtmp[-1])
        & (pl.col("Period_int") <= datetotmp[-1])
    )
    return Serverside(dff)


@app.callback(
    [
        Output("mastersetkpifiltered", "data"),
        Output("dropdown0", "value"),
        Output("dropdown1", "value"),
        Output("dropdown2", "value"),
        Output("button_group", "options"),
        Output("button_group1", "options"),
        # Output("button_group", "value"),
        # Output('output-container-date-picker-range', 'children'),
    ],
    Input("dflmasterfrontpolarsRedis", "data"),
    Input("KPISelect", "value"),
    Input("Level0NameSelect", "value"),
    Input("Level1NameSelect", "value"),
    Input("Level2NameSelect", "value"),
    Input("Category1Select", "value"),
    Input("CompetitorSwitch", "label"),
    Input("coinsinwallet", "data"),
    Input("coinsinwalletComp", "data"),
)
def change_KPI(
    dflmasterfrontpolarsRedis,
    KPISelect,
    Level0NameSelect,
    Level1NameSelect,
    Level2NameSelect,
    Category1Select,
    CompetitorSwitch,
    coinsinwallet,
    coinsinwalletComp,
):
    # changes buttons
    # changes Levels
    if coinsinwallet and WalletSwitch == "True" and CompetitorSwitch == "True":
        dflmasterfrontpolarswallet = dflmasterfrontpolarsRedis.filter(
            pl.col("d_level0_id").is_in(coinsinwalletComp)
        )
    elif coinsinwallet and WalletSwitch == "True":
        dflmasterfrontpolarswallet = dflmasterfrontpolarsRedis.filter(
            pl.col("d_level0_id").is_in(coinsinwallet)
        )
    else:
        dflmasterfrontpolarswallet = dflmasterfrontpolarsRedis
    if KPISelect in KPIName_listlevel2:
        print("KPIName_listlevel2")
        dff = dflmasterfrontpolarswallet.filter(
            (
                (pl.col("KPIName") == KPISelect)
                & (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("LevelName_1").is_in(Level1NameSelect))
                & (pl.col("LevelName_2").is_in(Level2NameSelect))
                & (pl.col("Filter1_0").is_in(Category1Select))
                # & (pl.col("Filter1_1").is_in(Category1))
                # & (pl.col("Filter1_2").is_in(Category1))
            )
        )

    elif KPISelect in KPIName_listlevel1:
        print("KPIName_listlevel1")
        dff = dflmasterfrontpolarswallet.filter(
            (
                (pl.col("KPIName") == KPISelect)
                & (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("LevelName_1").is_in(Level1NameSelect))
                & (pl.col("Filter1_0").is_in(Category1Select))
                # & (pl.col("Filter1_1").is_in(Category1))
            )
        )

    elif KPISelect in KPIName_listlevel0:
        print("KPIName_listlevel0")
        dff = dflmasterfrontpolarswallet.filter(
            (
                (pl.col("KPIName") == KPISelect)
                & (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        )
    dff_sorted = dff.sort(pl.col("Period_int"))
    cookpi_attributes = cookpi_attributestmp[
        (cookpi_attributestmp.d_kpi_id == KPINameToID[KPISelect])
    ]
    result = {}
    level0 = []
    level1 = []
    level2 = []
    button_sweeps_count = []
    button_names = []
    for index, row in cookpi_attributes.iterrows():
        if row["Level_ID_present"] == "d_level0_id":
            result[row["Level_ID_present"]] = row["dds_name"]
            level0.append(result["d_level0_id"])
            button_sweeps_count.append(f"LevelName_{row['Level_ID_present'][7]}")
            button_names.append(result["d_level0_id"])
        elif row["Level_ID_present"] == "d_level1_id":
            result[row["Level_ID_present"]] = row["dds_name"]
            level1.append(result["d_level1_id"])
            button_sweeps_count.append(f"LevelName_{row['Level_ID_present'][7]}")
            button_names.append(result["d_level1_id"])
        elif row["Level_ID_present"] == "d_level2_id":
            result[row["Level_ID_present"]] = row["dds_name"]
            level2.append(
                result["d_level2_id"]
            )  # used to fill the name of the dropdownlist
            button_sweeps_count.append(f"LevelName_{row['Level_ID_present'][7]}")
            button_names.append(result["d_level2_id"])
    button_grouptmp = [
        # {"label": row['dss_tab'], "value": f"LevelName_{row['Level_ID_present'][7]}"}
        # for _, row in cookpi_attributes.iterrows()
    ]
    button_grouptmp.clear()
    cnt = 0
    for f, b in zip(button_sweeps_count, button_names):
        print(f)
        print("printttie")
        Level = eval(f[-1])
        print(eval(f"Level{Level}NameSelect"))
        print(eval(f"list(Level{Level}NameList)"))
        if eval(f"Level{Level}NameSelect") == eval(f"list(Level{Level}NameList)"):
            sweepstyle = {"display": "none", "font-size": "14px"}
        else:
            sweepstyle = {"opacity": "1", "font-size": "14px"}  # ,'color':ProjectOrange
        testlogo = {
            "label": html.Div(
                [
                    f"{b}  ",
                    eval(
                        f"""html.Div(html.I('filter_list_off',id='sweepl{Level}',className='material-icons',style={sweepstyle}),style={{'display': 'inline-block','padding':'0px','text-size':'14px'}},id=dict(type='sweepertje',index='{f}'))"""
                    ),
                ]
            ),
            "value": f"{f}",
        }
        button_grouptmp.append(testlogo)
        cnt += 1
    tmp = dff_sorted.unique(subset=["FilterName_0"], maintain_order=True)
    FilterName_0_list = [row["FilterName_0"] for row in tmp.iter_rows(named=True)]
    for d in FilterName_0_list:
        if eval(f"Category1Select") == eval(f"list(Catergory0List)"):
            filter1 = {"label": d, "value": "Filter1_0"}
        else:
            filter1 = {
                "label": html.Div(
                    [
                        f"{d}  ",
                        eval(
                            f"""html.Div(html.I('filter_list_off',id='SweepFiltertje1_0',className='material-icons',style={sweepstyle}),style={{'display': 'inline-block','padding':'0px','text-size':'14px'}},id=dict(type='sweepertje',index='SweepFilter1_0'))"""
                        ),
                    ]
                ),
                "value": "Filter1_0",
            }
        button_grouptmp.append(filter1)
    button_groups = sorted(button_grouptmp, key=lambda x: x["value"])
    return (
        Serverside(dff_sorted),
        "bs" if not level0 else level0[0],
        "bs" if not level1 else level1[0],
        "bs" if not level2 else level2[0],
        button_groups,
        button_groups,
    )


"""
@app.callback([
               Output("button_group", "value",allow_duplicate=True),
               ],
              Input("button_group", "value"),
              Input("button_group", "options"),
              Input("button_group1", "options"),
)

def change_button_groups(button_group,button_groupoptions,button_group1options):
    is_in_list = any(item['value'] == button_group for item in button_groupoptions)
    if is_in_list:
        print("'button_group' is in the list.")
        selectedbutton = button_group
    else:
        selectedbutton = button_group[0]['value']
        print("'button_group' is not in the list.")

    return selectedbutton
"""


@app.callback(
    [
        Output("dflcomparekpi", "data"),
        Output("dfgroups", "data"),
        # Output('output-container-date-picker-range', 'children'),
    ],
    Input("dflmasterfrontpolarsRedis", "data"),
    Input("KPIGroupSelect", "value"),
    Input("Level0NameSelect", "value"),
    Input("Level1NameSelect", "value"),
    Input("Level2NameSelect", "value"),
    Input("Category1Select", "value"),
)
def All_KPIs(
    dflmasterfrontpolarsRedis,
    KPIGroupSelect,
    Level0NameSelect,
    Level1NameSelect,
    Level2NameSelect,
    Category1Select,
):
    # changes buttons
    # changes Levels
    dflpolarsfilterlist = []
    ###################################
    # calculate for divs with multiple KPIs
    ###################################
    for i in KPIName_listlevel2:
        tmppolars2 = dflmasterfrontpolarsRedis.filter(
            (
                (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("LevelName_1").is_in(Level1NameSelect))
                & (pl.col("LevelName_2").is_in(Level2NameSelect))
                & (pl.col("KPIGroup").is_in(KPIGroupSelect))
                & (pl.col("KPIName") == i)
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        )
        dflpolarsfilterlist.append(tmppolars2)
    for d in KPIName_listlevel1:
        tmppolars1 = dflmasterfrontpolarsRedis.filter(
            (
                (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("LevelName_1").is_in(Level1NameSelect))
                & (pl.col("KPIGroup").is_in(KPIGroupSelect))
                & (pl.col("KPIName") == d)
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        )
        dflpolarsfilterlist.append(tmppolars1)
    for v in KPIName_listlevel0:
        tmppolars0 = dflmasterfrontpolarsRedis.filter(
            (
                (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("KPIGroup").is_in(KPIGroupSelect))
                & (pl.col("KPIName") == v)
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        )
        dflpolarsfilterlist.append(tmppolars0)
    dff = pl.concat(dflpolarsfilterlist, how="diagonal")
    dflpolarsgroup = dff.select("KPIGroup").unique()
    dffgroups = dflpolarsgroup.sort("KPIGroup")
    return Serverside(dff), Serverside(dffgroups)


"""
def change_Level()
    #changes KPI's
    #changes buttons

def change_Button()
    #changes KPI's

"""


@app.callback(
    [  # Output('mastersetkpifiltered', 'data'),
        Output("mastersetkpifilterednotime", "data"),
        # Output('dfgroups', 'data'),
        Output("output-container-date-picker-range", "children"),
        # Output('dropdown0', 'value'),
        # Output('dropdown1', 'value'),
        # Output('dropdown2', 'value'),
        # Output("button_group", "options"),
        # Output("button_group1", "options"),
        # Output("pieorbar", "data"),
        #  Output('sweepers', 'children'),
    ],
    Input("mastersetkpifiltered", "data"),
    Input("KPISelect", "value"),
    #  Input('graphlevel0', 'relayoutData'),
    Input("button_group", "value"),
    Input("daterange", "data"),
    State("dropdown0", "value"),
    memoize=True,
    # ,background=True
    # ,manager=background_callback_manager
)  # ,prevent_initial_callback=True
def clean_data(
    mastersetkpifiltered, KPISelect, button_group, daterange, dropdown0State
):  # ,*args,sweepl1 relayoutl1barclickdatal2bar,clickdatal0,clickdatal1,clickdatal2,relayoutDatal0
    print("bigboi")
    try:
        datefromtmp = []
        datetotmp = []
        datefromtmp.append(daterange[0])
        datetotmp.append(daterange[1])

        mastersetkpifiltered.fill_null(0)

        columnsmastersetkpifiltered = mastersetkpifiltered.columns
        columnsmastersetkpifiltered.remove("Numerator")
        columnsmastersetkpifiltered.remove("Denominator")

        mastersetkpifiltered2 = mastersetkpifiltered
        noemer = (
            f'pl.col("Denominator").{eval(AggregateNumDenom(KPIDenomAgg[KPISelect]))}()'
        )
        teller = (
            f'pl.col("Numerator").{eval(AggregateNumDenom(KPINumAgg[KPISelect]))}()'
        )

        mastersetkpifiltered2.select(pl.exclude(["Period_int", "PeriodName"]))
        columnsmastersetkpifiltered.remove("Period_int")
        columnsmastersetkpifiltered.remove("PeriodName")

        mastersetkpifilterednotime = (
            mastersetkpifiltered2.lazy()
            .groupby(columnsmastersetkpifiltered)
            .agg(
                [
                    eval(noemer),
                    eval(teller),
                ]
            )
            .sort(["LevelName_0"])
            #     .limit(5)
        )
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        mastersetkpifilteredjsonnotime = mastersetkpifilterednotime.collect()
        # dffgroups = dflpolarsgroup.sort("KPIGroup")
        string_prefix = "You have selected: "
        if datefromtmp is not None:
            start_date_string = str(
                mastersetkpifiltered.lazy().select(pl.col("Period_int")).min().collect()
            )[0:10]
            string_prefix = string_prefix + "Start Date: " + start_date_string + " | "
        if datetotmp is not None:
            end_date_string = str(
                mastersetkpifiltered.lazy().select(pl.col("Period_int")).max().collect()
            )[0:10]
            string_prefix = string_prefix + "End Date: " + end_date_string
        if len(string_prefix) == len("You have selected: "):
            string_prefix = "Select a date to see it displayed here"
        # pieorbarcountlist = mastersetkpifiltered.select(button_group).unique()
        # pieorbarcount = pieorbarcountlist.select(pl.count()).item()
        # pieorbar = 'pie' if pieorbarcount==1 else 'bar'
        return (
            Serverside(mastersetkpifilteredjsonnotime),
            string_prefix,
        )  # ,eval(button_sweeps_3[0]) #sweep0style,sweep1style,sweep2style,
    # pickle.dumps(
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


# datefromtmp.clear()
# datetotmp.clear()


@app.callback(
    [
        Output("cardsid", "children"),
        Output("navbar", "children"),
        Output("graphcontainer", "children", allow_duplicate=True),
    ],
    Input("dfgroups", "data"),
    Input("dflcomparekpi", "data"),
    Input("KPISelect", "value"),
    Input("KPIGroupSelect", "value"),
    Input("breakpoints", "widthBreakpoint"),
    # Input("WalletSwitch", "label"),
    # Input("CompetitorSwitch", "label")
    # ,
    State("cardsid", "children"),
    # ,background=True
    # ,manager=background_callback_manager
    # ,running=[
    #    (Output("dflcomparekpi", "disabled"), True, False),
    # ],
    # ,session_check=False, prevent_initial_call=True
)
def updatekpiindicator(
    dfgroups, dffcompare, KPISelect, KPIGroupSelect, widthBreakpoint, cardsidState
):
    print("execute updatekpiindicator")
    try:
        # if not str(cardsidState)=='None' and len([item for item in ctx.triggered if 'prop_id' in item]) >1:
        #    print('dash.exceptions.PreventUpdate')
        #    raise dash.exceptions.PreventUpdate
        # else:
        sidemenulist = []
        sidemenulist3 = []
        sidemenulist.clear()
        sidemenulist3.clear()
        accordionlist = []
        accordionlist3 = []
        accordionlist.clear()
        accordionlist3.clear()
        carousellistnew = []
        carousellist3new = []
        carousellist3new.clear()
        carousellistnew.clear()
        graphscontainer = []
        graphscontainer3 = []
        print("coparegraph")
        dftouse = dffcompare.to_pandas()  # pd.DataFrame(dffcompare)
        dfgroups = dfgroups.sort("KPIGroup")  # pd.DataFrame(dfgroups)
        if kpicountout[0] < slides_to_show_ifenough:
            slides_to_show = kpicountout[0]
        else:
            slides_to_show = slides_to_show_ifenough

        dftouse.sort_values(by=["Sorting"])
        # create list with all kpi group names that exist for the selected level 1, 2 or 3
        KPIGroupListmodelfilter = dfgroups["KPIGroup"]
        # create list with all kpi group names that exist in the selected group without select
        KPIGroupListFiltered = d_kpi["KPIGroup"].unique()
        # create list with all kpi names that exist for the selected level 1, 2 or 3
        KPINameListmodelfilter = dftouse["KPIName"].unique()
        # create list with all kpi names that exist in the selected group without select
        KPIListFiltered = d_kpi[(d_kpi["KPIGroup"].isin(KPIGroupSelect))]
        KPIListFiltered.sort_values(by=["Sorting"])
        KPINameListFilter = KPIListFiltered["KPIName"].unique()

        KPINameListIterate = []
        # enter all values that exist for the selected level 1 2 and 3
        for i in KPINameListmodelfilter:
            KPINameListIterate.append(i)
        # enter all values that exist in the whole project but not for the selected level 1 2 and 3
        for p in KPINameListFilter:
            if p not in KPINameListmodelfilter:
                KPINameListIterate.append(p)

        KPIGroupListIterate = []
        # enter all values that exist for the selected level 1 2 and 3
        for j in KPIGroupListmodelfilter:
            KPIGroupListIterate.append(j)
        # enter all values that exist in the whole project but not for the selected level 1 2 and 3
        for l in KPIGroupListFiltered:
            if l not in KPIGroupListmodelfilter:
                KPIGroupListIterate.append(l)
        outputactual = []
        outputactualtxt = []
        #     outputlasttxt =[]
        #     outputlast = []
        Card = []
        Cardstyle = []
        popbody = []
        carddivstyle = []
        #     outputlasttxtlogo = []
        arrow = []
        outputactual.clear()
        outputactualtxt.clear()
        Card.clear()
        Cardstyle.clear()
        carddivstyle.clear()
        arrow.clear()
        popbody.clear()
        #      outputlasttxtlogo.clear()
        code_executed = False
        stylegroup = {"color": buttonlogocolor, "background-color": buttoncolor}
        sidemenulist.append(
            f"""html.Li(html.A([
                     html.I('category',className='material-icons icon'),
                     html.Span('All categories',className='text nav-text')],style={stylegroup if len(KPIGroupSelect)>1 else {}},href='#',id=dict(type='kpigroup-ex3',index ='kpigroup0'))
                    ,className='nav-link')"""
        )
        for i, kpigroup in enumerate(KPIGroupListIterate):
            numbertmp = i
            numberidtmp = i + 1
            number = str(numberidtmp)
            numberid = str(numberidtmp)
            GroupImage2 = KPIGroupImage[kpigroup]
            if KPIGroupSelect[0] == kpigroup:
                stylegroup1 = {
                    "color": buttonlogocolor,
                    "background-color": buttoncolor,
                }
            else:
                stylegroup1 = {}
            KPIGroupList2 = KPIGroupList[numbertmp]
            if kpigroup in KPIGroupListmodelfilter:
                sidemenulist.append(
                    f"""html.Li(html.A([
                            html.I('{GroupImage2}',className='material-icons icon'),
                            html.Span('{kpigroup}',className='text nav-text')],href='#',id=dict(type='kpigroup-ex3',index ='{kpigroup}'),style={stylegroup1 if len(KPIGroupSelect)==1 else {}})
                            ,className='nav-link')"""
                )
            else:
                sidemenulist.append(
                    f"""html.Li(html.A([
                                html.I('{GroupImage2}',className='material-icons icon'),
                                html.Span('{kpigroup}',className='text nav-text')],href='#',id=dict(type='kpigroup-ex3-reset',index ='{kpigroup}'))
                                ,style = {{'opacity':'25%'}},className='nav-link')"""
                )
        sidemenulist2 = ",".join(sidemenulist)
        sidemenulist3.append(sidemenulist2)
        for i, kpi in enumerate(KPINameListIterate):
            if kpi in KPINameListmodelfilter:
                enum = str(i + 1)
                dataCompare1 = dftouse[(dftouse["KPIName"] == kpi)]
                df_by_LevelName = dataCompare1[
                    ["Denominator", "Numerator"]
                ]  # "Denominator_LP","Numerator_LP"

                clickdatasend = dataCompare1["PeriodName"].unique()
                Periodchosencount = []
                Periodchosencount.clear()
                Periodchosencount.append(len(clickdatasend.tolist()))
                Displayprevious = []
                if Periodchosencount[0] > 1:
                    Displayprevious.append("none")
                else:
                    Displayprevious.append("block")
                logopositive = "green"
                logonegative = "red"
                logoneutral = "grey"
                value = []
                # value_lp = []
                valueNum = []
                valueDenom = []
                valueNumLP = []
                valueDenomLP = []
                notation = []
                valueNum.clear()
                valueDenom.clear()
                valueNumLP.clear()
                valueDenomLP.clear()
                df_by_LevelName.reset_index(drop=True, inplace=True)
                Notationtmp = KPISelectedStylePython(kpi)
                Notation = KPISelectedStyle(kpi)
                Notationlist = Notationtmp[0]
                Calculation = CalculationDEF(kpi)
                AggregateNum = AggregateNumDenom(Calculation)
                AggregateDenom = AggregateNumDenom(Calculation)
                meannum = []
                if str(eval(AggregateNum)) == "mean":
                    meannum.append("axis = 0")
                else:
                    meannum.append("")
                meandenom = []
                if str(eval(AggregateDenom)) == "mean":
                    meandenom.append("axis = 0")
                else:
                    meandenom.append("")
                agnum = (
                    "df_by_LevelName['Numerator']."
                    + str(eval(AggregateNum))
                    + "("
                    + meannum[0]
                    + ")"
                )
                agdenom = (
                    "df_by_LevelName['Denominator']."
                    + str(eval(AggregateDenom))
                    + "("
                    + meandenom[0]
                    + ")"
                )
                # agnumlp = "df_by_LevelName['Numerator_LP']." + str(eval(AggregateNum)) +"("+meannum[0]+")"
                # agdenomlp = "df_by_LevelName['Denominator_LP']." + str(eval(AggregateDenom)) +"("+meandenom[0]+")"
                df_by_LevelName = df_by_LevelName.assign(Aggnum=eval(agnum))
                valueNum.append(df_by_LevelName["Aggnum"].iloc[0])
                df_by_LevelName = df_by_LevelName.assign(Aggdenom=eval(agdenom))
                valueDenom.append(df_by_LevelName["Aggdenom"].iloc[0])
                # df_by_LevelName = df_by_LevelName.assign(Aggnum_LP=eval(agnumlp))
                # valueNumLP.append(df_by_LevelName['Aggnum_LP'].iloc[0])
                # df_by_LevelName = df_by_LevelName.assign(Aggdenom_LP=eval(agdenomlp))
                # valueDenomLP.append(df_by_LevelName['Aggdenom_LP'].iloc[0])
                twee = [i / j for i, j in zip(valueNum, valueDenom)]
                # twee_lp = [i / j for i, j in zip(valueNumLP, valueDenomLP)]
                if Calculation == 2:
                    CalculationString = twee[0]
                    # CalculationStringlp = twee_lp[0]
                    value.append(CalculationString)
                # value_lp.append(CalculationStringlp)
                elif Calculation == 1:
                    CalculationString = sum(valueNum)
                    # CalculationStringlp = sum(valueNumLP)
                    value.append(CalculationString)
                # value_lp.append(CalculationStringlp)
                # if value_lp[0]==value[0]:
                #    arrow = "'arrow_right'"
                # elif value_lp[0]<value[0]:
                #    arrow = "'arrow_drop_up'"
                # else:
                #    arrow = "'arrow_drop_down'"
                arrow = "'arrow_drop_down'"
                valueNum.clear()
                valueDenom.clear()
                valueNumLP.clear()
                valueDenomLP.clear()
                meannum.clear()
                meandenom.clear()
                notation.append(Notationlist)
                if kpi == KPISelect:
                    colorcardtext = graphcolor
                    style111 = {
                        "box-shadow": f"0px -0px 5px 2px {Highlightcardcolor}"
                    }  #'background': f'{tabhover}'}#
                else:
                    colorcardtext = Highlightcardcolor
                    style111 = {}
                outputactualtxt = str(eval(Notationlist).format(value[0]))
                # outputlasttxt = str(eval(Notationlist).format(value_lp[0]))
                Card.append(kpi)
                style = {
                    "display": Displayprevious[0],
                    "color": (
                        logopositive
                        if HigherIs[kpi] == 1
                        else logonegative if HigherIs[kpi] == 2 else logoneutral
                    ),
                }
                popbody.append(kpi)
                value.clear()
                #  value_lp.clear()
                notation.clear()
                numbertmp = i + 1
                number = str(numbertmp)
                numberi = str(numbertmp)
                KPIImageLogo = str(KPIImage[kpi])
                if widthBreakpoint == "sm":
                    logoclass = "col-2"
                    valueclass = "col-10"
                else:
                    logoclass = "col-4"
                    valueclass = "col-8"
                graphscontainer.append(
                    f"""dcc.Textarea(value='{kpi}',id=dict(type='graphsloop',index ='{kpi}'))"""
                )
                carousellistnew.append(
                    f"""html.Div(
                        dbc.Row([
                            dbc.Col([html.Div([html.I('{KPIImageLogo}', className='material-icons md-48',style={{'position':'absolute','top':'33%','text-align': 'center','padding':'0px','font-size': '54px'}},
                                       id='iconid{number}', n_clicks=0),
                                       ])],style={{'position':'relative','padding':'0px'}},className='{logoclass}'),
                            #html.I('info', className='material-icons md-18',style={{'text-align':'right','right':'4%','top':'4%','position':'absolute'}},
                            #           id='open-box{number}', n_clicks=0),
                            dbc.Col([html.Div([
                                dbc.Popover(
                                    [
                                        dbc.PopoverBody('And heres some amazing content. Cool!',id='popbody{number}',className='h6'),
                                    ],
                                    target='open-box{number}',
                                    trigger='legacy',
                                    className='popupper',
                                    hide_arrow=False
                                    ),
                                html.Div(id=dict(type='output-ex3',index = '{kpi}')),
                                dcc.Textarea(value=f'{kpi}',
                                             disabled=True,
                                             draggable=False,
                                             contentEditable=False,
                                             id='Card{number}',
                                             className='col-12 h6',
                                             style={{'margin-top':'25px'}}),
                                html.Div(children=[
                                    dcc.Textarea(value=f'{outputactualtxt}',
                                        id='indicator-graph{number}TXT',
                                        contentEditable=False,
                                        disabled=True,
                                        readOnly=True,
                                        draggable=False,
                                        className='col-12 h6'
                                    ),
                                    #html.Div([
                                    #     dcc.Textarea(value=f'',
                                    #         id="indicatorlast-graph{number}TXT",
                                    #         contentEditable =False,
                                    #         disabled=True,
                                    #         readOnly=True,
                                    #         draggable=False,
                                    #         className='col-8 h7',
                                    #     ),
                                    #     html.I({arrow},className="material-icons icon",id="arrow{number}")
                                    #    ],id="indicatorlast-graph{number}TXTLogo",style={style})
                                ]),
                            ],id='CardContent{number}')],className='{valueclass}'),
                        	])
                        ,id=dict(type='filter-dropdown-ex3',index = '{kpi}'),style={style111},className='carddiv')"""
                )
            else:
                accordionlist.append(
                    f"""html.Div('{kpi}',id=dict(type='filter-dropdown-ex3-reset',index='{kpi}'),className ='KPIRemainingbox h7')"""
                )
                if i == len(KPINameListmodelfilter) - 1:
                    accordionliststring = str(accordionlist)
                    accordionliststring2 = accordionliststring.replace('"', "")
                    accordionlist2 = ",".join(accordionlist)
                    accordionlist3.append(accordionlist2)
                    lastlistaccordionstring = []
                    lastlistaccordionstring.append(eval(accordionlist3[0]))
                    carousellistnew.append(
                        "html.Div(className='KPIRemainingcontainer',children="
                        + accordionliststring2
                        + ")"
                    )
                # carousellistnew.append(
                # f"""html.Div(
                #   ,id=dict(type='filter-dropdown-ex3',index = '{kpi}'),style={style111},className='carddiv')"""
                # )
        if accordionlist:
            slides_to_show_if_little = len(KPINameListmodelfilter) + 1
        else:
            slides_to_show_if_little = len(KPINameListmodelfilter)
        accordionlist.clear()
        accordionlist3.clear()
        carousellist2new = ",".join(carousellistnew)
        carousellist3new.append(carousellist2new)
        graphscontainer2 = ",".join(graphscontainer)
        graphscontainer3.append(graphscontainer2)
        # print(carousellist3new)
        # print(carousellist3new[0])
        if widthBreakpoint == "sm":
            slides_to_showfinal = 1
            slides_to_scrollfinal = 1
        else:
            slides_to_showfinal = (
                slides_to_show
                if slides_to_show_if_little >= slides_to_show
                else slides_to_show_if_little
            )
            slides_to_scrollfinal = slides_to_scroll
        divlist = [
            [
                html.Div(
                    [
                        dbc.Spinner(
                            size="md",
                            delay_hide=1500,
                            children=[
                                dtc.Carousel(
                                    eval(carousellist3new[0]),
                                    infinite=False,
                                    slides_to_scroll=slides_to_scrollfinal,
                                    slides_to_show=slides_to_showfinal,
                                    center_padding="10px",
                                    swipe_to_slide=True,
                                    autoplay=False,
                                    dots=True,
                                    speed=120,
                                    # variable_width=True,
                                    center_mode=False,
                                    id="slickthinky",
                                    className="col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12",
                                    responsive=[],
                                )
                            ],
                        )
                    ]
                )
            ],
            [
                html.Nav(
                    [
                        html.Header(
                            [
                                html.Div(
                                    [
                                        #    html.Div(Radiograin,className="col-sm-12 col-md-12 col-lg-12 col-xl-12 text logo-text")
                                    ],
                                    className="image-text",
                                ),
                                html.I(
                                    "chevron_right",
                                    className="material-icons toggle",
                                    id="Opennavbar",
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            html.Span(
                                                "Performace category",
                                                className="text nav-text",
                                            )
                                        ),
                                        html.Ul(
                                            eval(sidemenulist2), className="menu-links"
                                        ),
                                    ],
                                    className="menu",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Span(
                                                        "Performace view",
                                                        className="text nav-text",
                                                    )
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            html.A(
                                                                [
                                                                    html.I(
                                                                        "lan",
                                                                        className="material-icons icon",
                                                                    ),
                                                                    html.Span(
                                                                        "Drill down",
                                                                        className="text nav-text",
                                                                    ),
                                                                ],
                                                                href="/drilldown",
                                                                id="NavItem1",
                                                            ),
                                                            className="nav-link",
                                                        ),
                                                        html.Li(
                                                            html.A(
                                                                [
                                                                    html.I(
                                                                        "balance",
                                                                        className="material-icons icon",
                                                                    ),
                                                                    html.Span(
                                                                        "Compare",
                                                                        className="text nav-text",
                                                                    ),
                                                                ],
                                                                href="/compare",
                                                                id="NavItem2",
                                                            ),
                                                            className="nav-link",
                                                        ),
                                                        html.Li(
                                                            html.A(
                                                                [
                                                                    html.I(
                                                                        "bolt",
                                                                        className="material-icons icon",
                                                                    ),
                                                                    html.Span(
                                                                        "Predict",
                                                                        className="text nav-text",
                                                                    ),
                                                                ],
                                                                href="/predict",
                                                                id="NavItem3",
                                                            ),
                                                            className="nav-link",
                                                        ),
                                                    ],
                                                    className="menu-links",
                                                ),
                                            ],
                                            className="menu",
                                        ),
                                    ]
                                ),
                            ],
                            className="menu-bar",
                        ),
                    ],
                    className="sidebar close",
                    id="nav",
                )
            ],
        ]
        return divlist[0], divlist[1], html.Div(eval(graphscontainer3[0]))
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


##graphlevel0
@app.callback(
    Output("graphcontainerOutput", "children", allow_duplicate=True),
    [
        Input({"type": "graphsloop", "index": ALL}, "value"),
    ],
    prevent_initial_call=True,
)
def allgraphsindiv(values):
    print("execute allgraphsindiv")
    allreturns = html.Div([html.Div(value) for (i, value) in enumerate(values)])
    return allreturns


@app.callback(
    Output("graphcontainerOutput", "children", allow_duplicate=True),
    # Output("Category1Select", "value"),
    #  Output("Level0NameSelect", "options"),
    # Output('animatedbar', 'figure'),
    [
        Input({"type": "graphsloop", "index": ALL}, "value"),
        Input("GrainSelect", "value"),
        Input("dflcomparekpi", "data"),
        Input("CumulativeSwitch", "label"),
        Input("PercentageTotalSwitch", "label"),
        Input("ShowValueSwitch", "label"),
        Input("breakpoints", "widthBreakpoint"),
        Input("button_group", "value"),
        Input("button_group1", "value"),
        Input("Totaalswitch", "label"),
        Input("collapse", "is_open"),
        # State('graphlevel0', 'figure'),
    ],
    prevent_initial_call=True,
)
def update_kpiaggcontainer(
    graphsloop,
    GrainSelect,
    dflcomparekpi,
    CumulativeSwitch,
    PercentageTotalSwitch,
    ShowValueSwitch,
    widthBreakpoint,
    button_group,
    button_group1,
    Totaalswitch,
    collapse,
):  # ,*args ,Level2NameSelect,toggle, relayoutData
    print("execute update_kpiaggcontainer")
    print("collapse")
    try:
        # mastersetkpifiltered=dflcomparekpi
        graphs = []
        if collapse == False:
            raise PreventUpdate
        else:
            for i, value in enumerate(graphsloop):
                KPISelect = value
                mastersetkpifiltered = dflcomparekpi.filter(
                    (pl.col("KPIName") == KPISelect)
                )
                columns_to_removemasterset = mastersetkpifiltered.columns
                noemer = f'pl.col("Denominator").{eval(AggregateNumDenom(KPIDenomAgg[KPISelect]))}()'
                teller = f'pl.col("Numerator").{eval(AggregateNumDenom(KPINumAgg[KPISelect]))}()'
                dataframe = Cumloop0(CumulativeSwitch)
                dataframe1 = Cumloop1(CumulativeSwitch)
                dataframe2 = Cumloop2(CumulativeSwitch)
                Notation = KPISelectedStyle(KPISelect)
                Calculation = CalculationDEF(KPISelect)
                Notation = KPISelectedStyle(KPISelect)
                Calculation = CalculationDEF(KPISelect)
                if widthBreakpoint == "sm":
                    title = ""
                else:
                    title = dict(
                        text=str(KPISelect),  # + ' per ' + Level2Entitytype,
                        # +' -     selected: '+str(Level2NameSelect),
                        font=dict(  # family='Montserrat',
                            size=22,
                            color=fontcolor,
                        ),
                    )
                if widthBreakpoint == "sm":
                    legend = dict(
                        font=dict(
                            size=15,
                            color=fontcolor,
                        ),
                        orientation="h",
                    )
                else:
                    legend = dict(
                        font=dict(
                            size=15,
                            color=fontcolor,
                        ),
                        yanchor="top",
                        y=1,
                        x=1.01,
                        xanchor="left",
                    )
                if button_group == "LevelName_0":
                    # data0 = mastersetkpifiltered.to_pandas() # pd.DataFrame(data00)
                    traces3 = []
                    mastersetkpifilterednewcol = [
                        column
                        for column in columns_to_removemasterset
                        if "_1" not in column
                        and "_2" not in column
                        and column not in ["d_level1_id", "d_level2_id"]
                    ]
                    # Select only the filtered columns
                    mastersetkpifilterednew = mastersetkpifiltered.select(
                        mastersetkpifilterednewcol
                    )
                    mastersetkpifilterednewcol.remove("Numerator")
                    mastersetkpifilterednewcol.remove("Denominator")
                    mastersetkpifilterednotime = (
                        mastersetkpifilterednew.lazy()
                        .groupby(mastersetkpifilterednewcol)
                        .agg(
                            [
                                eval(noemer),
                                eval(teller),
                            ]
                        )
                        # .sort(["LevelName_0"])
                    )
                    data000collect = mastersetkpifilterednotime.collect()
                    data000 = data000collect.to_pandas()
                    data000["Period_int"] = pd.to_datetime(data000["Period_int"])
                    data000 = data000.sort_values(by="Period_int")
                    for i in data000["LevelName_0"].unique():
                        df_by_Level0Name = data000[data000["LevelName_0"] == i]
                        df_by_Level0Name = df_by_Level0Name.assign(
                            NumeratorCum=lambda df_by_Level0Name: df_by_Level0Name.Numerator.cumsum()
                        )
                        df_by_Level0Name = df_by_Level0Name.assign(
                            DenominatorCum=lambda df_by_Level0Name: df_by_Level0Name.Denominator.cumsum()
                        )
                        y = eval(eval(dataframe[1]))
                        default_color = "red"
                        colors = {"2021-05-31T00:00:00.000Z": "red"}
                        color_discrete_map = {
                            c: colors.get(c, default_color)
                            for c in eval(dataframe[0]).Period_int.unique()
                        }
                        traces3.append(
                            dict(
                                eval(dataframe[0]),
                                x=eval(
                                    dataframe[0]
                                ).Period_int,  # df_by_Level1Name['Period_int'],
                                cumulative_enabled=True,
                                color=eval(dataframe[0]).Period_int,
                                y=y,
                                text=y if ShowValueSwitch == "True" else "",
                                mode=linesormarkers(GrainSelect),
                                opacity=1,
                                customdata=eval(dataframe[0]).LevelName_0,
                                line=dict(
                                    width=3,
                                    shape="spline",
                                ),
                                marker=dict(
                                    size=5,
                                    opacity=1,
                                    line=dict(width=0.1),
                                    color=LevelNameColor[i],  #
                                ),
                                type=visualDEF(KPISelect),
                                name=i,
                                transforms=dict(
                                    type="aggregate",
                                    groups="Period_int",
                                    aggregations=[
                                        dict(
                                            target="Numerator",
                                            func=AggregateNumDenom(Calculation),
                                        ),  # , enabled=True
                                        dict(
                                            target="Denominator",
                                            func=AggregateNumDenom(Calculation),
                                        ),  # , enabled=True
                                    ],
                                ),
                            )
                        )
                    if not traces3:
                        return {
                            "layout": dict(
                                xaxis=dict(visible=False),
                                yaxis=dict(visible=False),
                                style={"background-color": "red", "color": "white"},
                                annotations=[
                                    dict(
                                        xref="paper",
                                        yref="paper",
                                        x=0.5,
                                        y=0.5,
                                        text="No data available",
                                        showarrow=False,
                                        font=dict(size=26, color=fontcolor),
                                    )
                                ],
                                plot_bgcolor="transparent",
                                paper_bgcolor="transparent",
                            )
                        }
                    else:
                        figure = {
                            "data": traces3,
                            "layout": dict(
                                clickmode="event+select",
                                barmode="stack",
                                showlegend=True,  # False if button_group1 == 'LevelName_0' else True,
                                barnorm=eval(
                                    PercentageTotalSwitchDEF(PercentageTotalSwitch)
                                ),
                                xaxis=dict(
                                    type="string",
                                    title="",
                                    showgrid=False,
                                    gridwidth=0,
                                    # showspikes=True,
                                    showline=False,
                                    color=fontcolor,
                                    rangeselector=dict(
                                        buttons=rangeselector(GrainSelect),
                                        bgcolor=tabhover,  # Background color of the range selector
                                        activecolor=rangeselected,
                                        activebordercolor="white",
                                        font=dict(color=fontcolor, size=16),
                                    ),
                                    rangeslider=dict(visible=False),
                                    linewidth=2,
                                    font=dict(
                                        size=14,
                                    ),
                                ),
                                yaxis=dict(
                                    title="",
                                    linewidth=2,
                                    tickformat=eval(Notation[0]),
                                    showgrid=False,
                                    showline=False,
                                    autorange=True,
                                    fixedrange=True,
                                    # showspikes=True,
                                    color=fontcolor,
                                    gridwidth=0.5,
                                    font=dict(
                                        size=14,
                                    ),
                                ),
                                margin={"l": 60, "b": 45, "t": 37, "r": 40},
                                modebar=dict(
                                    bgcolor="transparent",
                                    color=BeautifulSignalColor,
                                ),
                                autosize=True,
                                plot_bgcolor=graphcolor,
                                paper_bgcolor=graphcolor,
                                legend=legend,
                                title=title,
                                font=dict(),
                                images=dict(
                                    x=0,
                                    y=1,
                                    sizex=0.2,
                                    sizey=0.2,
                                ),
                                hovermode="x-unified",
                                transition={"duration": 50},
                            ),
                        }
                        graphs.append(
                            dcc.Graph(
                                figure=figure,
                                config=dict(
                                    modeBarButtonsToAdd=["customButton"],
                                    modeBarButtonsToRemove=[
                                        "pan",
                                        "lasso2d",
                                        "select",
                                        "zoom2d",
                                        "zoomIn",
                                        "zoomOut",
                                        "toImage",
                                        "resetScale",
                                        "hoverCompareCartesian",
                                        "logo",
                                        "autoScale",
                                    ],
                                    displaylogo=False,
                                    # scrollZoom = True,
                                    toImageButtonOptions=dict(
                                        width=550,
                                        height=300,
                                        format="png",
                                        scale=10,
                                        filename="Plotlygraph",
                                    ),
                                ),
                                className="row-cols-sm-12 row-cols-md-12 row-cols-lg-12 row-cols-xl-12 pretty_graph",
                            )
                        )
            # print(traces3)
        return graphs
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


@app.callback(
    Output("graphlevel0data", "data"),
    Output("graph-level0compare-dataset", "data"),
    [
        Input("GrainSelect", "value"),
        Input("KPISelect", "value"),
        Input("mastersetkpifiltered", "data"),
        Input("CumulativeSwitch", "label"),
        Input("PercentageTotalSwitch", "label"),
        Input("ShowValueSwitch", "label"),
        Input("breakpoints", "widthBreakpoint"),
        Input("button_group", "value"),
        Input("button_group1", "value"),
        Input("Totaalswitch", "label"),
        # State('graphlevel0', 'figure'),
    ],
    prevent_initial_call=True,
    # ,background=True
    # ,manager=background_callback_manager
)
def update_kpiagg_data(
    GrainSelect,
    KPISelect,
    mastersetkpifilteredstore,
    CumulativeSwitch,
    PercentageTotalSwitch,
    ShowValueSwitch,
    widthBreakpoint,
    button_group,
    button_group1,
    Totaalswitch,
):  # ,*args ,Level2NameSelect,toggle, relayoutData
    print("execute update_kpiagg data")
    try:
        columns_to_removemasterset = mastersetkpifilteredstore.columns
        print(columns_to_removemasterset)
        noemer = (
            f'pl.col("Denominator").{eval(AggregateNumDenom(KPIDenomAgg[KPISelect]))}()'
        )
        teller = (
            f'pl.col("Numerator").{eval(AggregateNumDenom(KPINumAgg[KPISelect]))}()'
        )
        LevelOrFilter = button_group.split("_")[0]
        LevelOrFilterNumber = button_group.split("_")[1]
        columns_to_remove_dict = {
            "LevelName_0": [
                column
                for column in columns_to_removemasterset
                if "_1" not in column
                and "_2" not in column
                and column not in ["d_level1_id", "d_level2_id"]
            ],
            "LevelName_1": [
                column
                for column in columns_to_removemasterset
                if "_0" not in column
                and "_2" not in column
                and column not in ["d_level0_id", "d_level2_id"]
            ],
            "LevelName_2": [
                column
                for column in columns_to_removemasterset
                if "_0" not in column
                and "_1" not in column
                and column not in ["d_level0_id", "d_level1_id"]
            ],
            "Filter1_0": [
                column
                for column in columns_to_removemasterset
                if "_0" not in column
                and "_1" not in column
                and "_2" not in column
                and column not in ["d_level0_id", "d_level1_id", "d_level2_id"]
            ],
        }
        # Check the value of LevelOrFilterNumber and select the appropriate list
        if button_group in columns_to_remove_dict:
            columns_to_remove = columns_to_remove_dict[button_group]
            if LevelOrFilter == "Filter1":
                columns_to_remove.append("Filter1_0")
        else:
            print(
                f"LevelOrFilterNumber '{LevelOrFilterNumber}' not found in the dictionary."
            )
        traces3 = []
        mastersetkpifilterednewcol = columns_to_remove  # [column for column in columns_to_removemasterset if '_1' not in column and '_2' not in column and column not in ['d_level1_id', 'd_level2_id']]
        # Select only the filtered columns
        mastersetkpifilterednew = mastersetkpifilteredstore.select(columns_to_remove)
        mastersetkpifilterednewcol.remove("Numerator")
        mastersetkpifilterednewcol.remove("Denominator")
        mastersetkpifilterednotimee = (
            mastersetkpifilterednew.lazy()
            .groupby(mastersetkpifilterednewcol)
            .agg(
                [
                    eval(noemer),
                    eval(teller),
                ]
            )
            # .sort(["LevelName_0"])
        )
        mastersetkpifilterednotimee.fill_null(0)
        mastersetkpifilterednotimeecollect = mastersetkpifilterednotimee.collect()
        print("before update_kpiagg data")
        print("before update_kpiagg data")

        ####################################
        ####################################
        columns_to_removemasterset = mastersetkpifilteredstore.columns
        if button_group1 == "LevelName_0":
            columns_to_remove_dict = {
                "LevelName_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_1" not in column
                    and "_2" not in column
                    and column not in ["d_level1_id", "d_level2_id"]
                ],
                "LevelName_1": [
                    column
                    for column in columns_to_removemasterset
                    if "_2" not in column and column not in ["d_level2_id"]
                ],
                "LevelName_2": [
                    column
                    for column in columns_to_removemasterset
                    if "_1" not in column and column not in ["d_level1_id"]
                ],
                "Filter1_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_2" not in column
                    and "_1" not in column
                    and column not in ["d_level2_id", "d_level1_id"]
                ],
            }
        elif button_group1 == "LevelName_1":
            columns_to_remove_dict = {
                "LevelName_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_2" not in column and column not in ["d_level2_id"]
                ],
                "LevelName_1": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_2" not in column
                    and column not in ["d_level0_id", "d_level2_id"]
                ],
                "LevelName_2": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column and column not in ["d_level0_id"]
                ],
                "Filter1_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_2" not in column
                    and column not in ["d_level0_id", "d_level2_id"]
                ],
            }
        elif button_group1 == "LevelName_2":
            columns_to_remove_dict = {
                "LevelName_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_1" not in column and column not in ["d_level1_id"]
                ],
                "LevelName_1": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column and column not in ["d_level0_id"]
                ],
                "LevelName_2": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_1" not in column
                    and column not in ["d_level0_id", "d_level1_id"]
                ],
                "Filter1_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_1" not in column
                    and column not in ["d_level0_id", "d_level1_id"]
                ],
            }
        elif button_group1 == "Filter1_0":
            columns_to_remove_dict = {
                "LevelName_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_1" not in column
                    and "_2" not in column
                    and column not in ["d_level1_id", "d_level2_id"]
                ],
                "LevelName_1": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_2" not in column
                    and column not in ["d_level0_id", "d_level2_id"]
                ],
                "LevelName_2": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_1" not in column
                    and column not in ["d_level0_id", "d_level1_id"]
                ],
                "Filter1_0": [
                    column
                    for column in columns_to_removemasterset
                    if "_0" not in column
                    and "_1" not in column
                    and "_2" not in column
                    and column not in ["d_level0_id", "d_level1_id", "d_level2_id"]
                ],
            }
        columns_to_remove = columns_to_remove_dict[button_group]
        if "Filter1_0" not in columns_to_remove and (
            button_group == "Filter1_0" or button_group1 == "Filter1_0"
        ):
            columns_to_remove.append("Filter1_0")
        mastersetkpifilterednew = mastersetkpifilteredstore.select(columns_to_remove)
        columns_to_remove.remove("Numerator")
        columns_to_remove.remove("Denominator")

        mastersetkpifilterednotimeee = (
            mastersetkpifilterednew.lazy()
            .groupby(columns_to_remove)
            .agg(
                [
                    eval(noemer),
                    eval(teller),
                ]
            )
        )
        mastersetkpifilterednotimeee.fill_null(0)
        export = mastersetkpifilterednotimeee.collect()
        print("before graph-level0compare-dataset")
        print("before graph-level0compare-dataset")
        ####################################33
        ##############################3####
        return Serverside(mastersetkpifilterednotimeecollect), Serverside(export)
    except Exception as e:
        logging.error(f"Exception in callback update_kpiagg_data: {str(e)}")
        raise


@app.callback(
    [
        Output("Category1Select", "options"),
        Output("Level0NameSelect", "options"),
        Output("Level1NameSelect", "options"),
        Output("Level2NameSelect", "options"),
    ],
    # Output('animatedbar', 'figure'),
    Input("Category1Select", "value"),
    Input("Level0NameSelect", "value"),
    Input("Level1NameSelect", "value"),
    Input("Level2NameSelect", "value"),
    Input("KPISelect", "value"),
    Input("dflcomparekpi", "data"),
    prevent_initial_call=True,
)
def DropdownOptions(
    Category1Select,
    Level0NameSelect,
    Level1NameSelect,
    Level2NameSelect,
    KPISelect,
    dflmasterfrontpolarsRedis,
):  # ,*args ,Level2NameSelect,toggle, relayoutData
    print("execute DropdownOptions")
    try:
        if KPISelect in KPIName_listlevel0:
            dffonlykpifiltered = dflmasterfrontpolarsRedis.filter(
                (pl.col("KPIName") == KPISelect)
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        elif KPISelect in KPIName_listlevel1:
            dffonlykpifiltered = dflmasterfrontpolarsRedis.filter(
                (pl.col("KPIName") == KPISelect)
                & (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        elif KPISelect in KPIName_listlevel2:
            dffonlykpifiltered = dflmasterfrontpolarsRedis.filter(
                (pl.col("KPIName") == KPISelect)
                & (pl.col("LevelName_0").is_in(Level0NameSelect))
                & (pl.col("LevelName_1").is_in(Level1NameSelect))
                & (pl.col("Filter1_0").is_in(Category1Select))
            )
        Category1Select = [
            {
                "label": html.Span([i], style={"background-color": FilterColor[i]}),
                "value": i,
            }
            for i in dffonlykpifiltered["Filter1_0"].unique()
        ]
        Level0NameSelect = [
            {
                "label": html.Span([i], style={"background-color": LevelNameColor[i]}),
                "value": i,
            }
            for i in dffonlykpifiltered["LevelName_0"].unique()
        ]
        Level1NameSelect = [
            {
                "label": html.Span([i], style={"background-color": LevelNameColor[i]}),
                "value": i,
            }
            for i in dffonlykpifiltered["LevelName_1"].unique()
        ]
        Level2NameSelect = [
            {
                "label": html.Span([i], style={"background-color": LevelNameColor[i]}),
                "value": i,
            }
            for i in dffonlykpifiltered["LevelName_2"].unique()
        ]
        #      button_group = [{'label': html.Span([i],style={'background-color': buttoncolor}), 'value': i}  for i in Category1filtered["Filter1_0"].unique()]
        # print(Category1Select)
        # print(Level0NameSelect)
        # print(Level1NameSelect)
        # print(Level2NameSelect)
        return Category1Select, Level0NameSelect, Level1NameSelect, Level2NameSelect
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


@app.callback(
    Output("graphlevel0", "figure"),
    # Output("Category1Select", "value"),
    #  Output("Level0NameSelect", "options"),
    # Output('animatedbar', 'figure'),
    [
        Input("graphlevel0data", "data"),
        Input("GrainSelect", "value"),
        Input("KPISelect", "value"),
        Input("CumulativeSwitch", "label"),
        Input("PercentageTotalSwitch", "label"),
        Input("ShowValueSwitch", "label"),
        Input("breakpoints", "widthBreakpoint"),
        Input("button_group", "value"),
        Input("button_group1", "value"),
        Input("Totaalswitch", "label"),
        # State('graphlevel0', 'figure'),
    ],
    prevent_initial_call=True,
)
def update_kpiagg(
    graphlevel0datasetje,
    GrainSelect,
    KPISelect,
    CumulativeSwitch,
    PercentageTotalSwitch,
    ShowValueSwitch,
    widthBreakpoint,
    button_group,
    button_group1,
    Totaalswitch,
):  # ,*args ,Level2NameSelect,toggle, relayoutData
    print("execute update_kpiagg")
    try:
        dataframe = Cumloop0(CumulativeSwitch)
        dataframe1 = Cumloop1(CumulativeSwitch)
        Calculation = CalculationDEF(KPISelect)
        Notation = KPISelectedStyle(KPISelect)
        Calculation = CalculationDEF(KPISelect)
        if widthBreakpoint == "sm":
            title = ""
        else:
            title = dict(
                text=str(KPISelect),  # + ' per ' + Level2Entitytype,
                # +' -     selected: '+str(Level2NameSelect),
                font=dict(  # family='Montserrat',
                    size=22,
                    color=fontcolor,
                ),
            )
        if widthBreakpoint == "sm":
            legend = dict(
                font=dict(
                    size=15,
                    color=fontcolor,
                ),
                orientation="h",
            )
        else:
            legend = dict(
                font=dict(
                    size=15,
                    color=fontcolor,
                ),
                yanchor="top",
                y=1,
                x=1.01,
                xanchor="left",
            )

        # data0 = graphlevel0datasetje.to_pandas()
        LevelOrFilter = button_group.split("_")[0]
        LevelOrFilterNumber = button_group.split("_")[1]
        traces3 = []
        print("after update_kpiagg data")
        print("gimme OS ENVIRON VALUES")
        print(os.environ.values())
        print("gimme OS ENVIRON VALUES")
        print("gimme OS ENVIRON")
        print(os.environ)
        print("gimme OS ENVIRON")
        data000 = graphlevel0datasetje.to_pandas()
        data000["Period_int"] = pd.to_datetime(data000["Period_int"])
        data000 = data000.sort_values(by="Period_int")
        """
        columns_to_remove = data0.columns[data0.columns.str.contains('_1|_2|d_level1_id|d_level2_id')]
        data00 = data0.drop(columns=columns_to_remove)
        columnsdffpol = data00.columns.tolist()
        columnsdffpol.remove('Numerator')
        columnsdffpol.remove('Denominator')
        data000 = data00.groupby(columnsdffpol, as_index=False, sort=False).agg(
            {'Denominator': [eval(AggregateNumDenom(KPIDenomAgg[KPISelect]))], 'Numerator': [eval(AggregateNumDenom(KPINumAgg[KPISelect]))]},dtype=object)
        data000.reset_index()
        data000.columns = data000.columns.droplevel(1)
        for v in polarsdata.select(['LevelName_0']).unique().to_series().to_list():
            print(polarsdata.select(['LevelName_0']).unique().to_series().to_list())
            print(v)
            print(LevelNameColor[v])
            df_by_Level0Name = polarsdata.filter(pl.col("LevelName_0") == v)
            y = df_by_Level0Name.select(['Numerator']).to_series()
            traces3.append(dict(
                x=df_by_Level0Name.select(['Period_int']).to_series(),
                cumulative_enabled=True,
                color=df_by_Level0Name.select(['Period_int']).to_series(),
                y=y,
                text=y if ShowValueSwitch == 'True' else '',
                mode=linesormarkers(GrainSelect),
                opacity=1,
                customdata=df_by_Level0Name.select(['LevelName_0']).to_series(),
                line=dict(
                    width=3,
                    shape="spline",
                ),
                marker=dict(
                    size=5,
                    opacity=1,
                    line=dict(width=0.1
                              ),
                    color=LevelNameColor[v] #
                ),
                type=visualDEF(KPISelect),
                name=v,
                transforms=dict(
                    type='aggregate',
                    groups="Period_int",
                    aggregations=[
                        dict(target='Numerator', func=AggregateNumDenom(Calculation)),  # , enabled=True
                        dict(target='Denominator', func=AggregateNumDenom(Calculation))  # , enabled=True
                    ]
                ),
                )
            )
        """
        for i in data000[button_group].unique():
            df_by_Level0Name = data000[data000[button_group] == i]
            ##df_by_Level0NameCum = dff[dff['Level0Name'] == i]
            ##df_by_Level0NameCum['Numerator'] = df_by_Level0NameCum['Numerator'].cumsum()
            ##df_by_Level0NameCum['Denominator'] = df_by_Level0NameCum['Denominator'].cumsum()
            df_by_Level0Name = df_by_Level0Name.assign(
                NumeratorCum=lambda df_by_Level0Name: df_by_Level0Name.Numerator.cumsum()
            )
            df_by_Level0Name = df_by_Level0Name.assign(
                DenominatorCum=lambda df_by_Level0Name: df_by_Level0Name.Denominator.cumsum()
            )
            y = eval(eval(dataframe[1]))
            default_color = "red"
            colors = {"2021-05-31T00:00:00.000Z": "red"}
            traces3.append(
                dict(
                    eval(dataframe[0]),
                    x=eval(dataframe[0]).Period_int,  # df_by_Level1Name['Period_int'],
                    cumulative_enabled=True,
                    color=eval(dataframe[0]).Period_int,
                    y=y,
                    text=y if ShowValueSwitch == "True" else "",
                    mode=linesormarkers(GrainSelect),
                    opacity=1,
                    customdata=eval(dataframe[0]).eval(button_group),
                    line=dict(
                        width=3,
                        shape="spline",
                    ),
                    marker=dict(
                        size=5,
                        opacity=1,
                        line=dict(width=0.1),
                        color=(
                            LevelNameColor[i]
                            if LevelOrFilter == "LevelName"
                            else FilterColor[i]
                        ),  #
                    ),
                    type=visualDEF(KPISelect),
                    name=i,
                    transforms=dict(
                        type="aggregate",
                        groups="Period_int",
                        aggregations=[
                            dict(
                                target="Numerator", func=AggregateNumDenom(Calculation)
                            ),  # , enabled=True
                            dict(
                                target="Denominator",
                                func=AggregateNumDenom(Calculation),
                            ),  # , enabled=True
                        ],
                    ),
                )
            )
        if Totaalswitch == "True":
            for d in appendList2:
                columns_to_remove0 = data0.columns[
                    data0.columns.str.contains("_1|_2|d_level1_id|d_level2_id")
                ]
                data00 = data0.drop(columns=columns_to_remove0)
                columnsdffpol0 = data00.columns.tolist()
                columnsdffpol0.remove("Numerator")
                columnsdffpol0.remove("Denominator")
                data000 = data00.groupby(
                    columnsdffpol0, as_index=False, sort=False
                ).agg(
                    {
                        "Denominator": [
                            eval(AggregateNumDenom(KPIDenomAgg[KPISelect]))
                        ],
                        "Numerator": [eval(AggregateNumDenom(KPINumAgg[KPISelect]))],
                    },
                    dtype=object,
                )
                data000.reset_index()
                data000.columns = data000.columns.droplevel(1)
                for v in data000.LevelName_0.unique():
                    df_by_Level0Name = data000[data000["LevelName_0"] == v]
                    df_by_Level0Name = df_by_Level0Name.assign(
                        NumeratorCum=lambda df_by_Level0Name: df_by_Level0Name.Numerator.cumsum()
                    )
                    df_by_Level0Name = df_by_Level0Name.assign(
                        DenominatorCum=lambda df_by_Level0Name: df_by_Level0Name.Denominator.cumsum()
                    )
                    y2 = eval(eval(dataframe0[1]))
                    d.append(
                        dict(
                            eval(dataframe0[0]),
                            x=eval(dataframe0[0]).Period_int,
                            cumulative_enabled=True,
                            y=y2,
                            text=y2,
                            text_auto=True,
                            customdata=eval(dataframe0[0]).LevelName_0,
                            mode=linesormarkers(GrainSelect),
                            opacity=1,
                            marker=dict(
                                size=5,
                                color=LevelNameColor[v],
                                color_discrete_map="identity",
                                line=dict(width=0.1, color="white"),
                            ),
                            type="line",
                            name=v,
                            line=dict(
                                width=5,
                                shape="spline",
                                color=(
                                    LevelNameColor[i]
                                    if LevelOrFilter == "LevelName"
                                    else FilterColor[i]
                                ),
                            ),
                            #  fill='tozeroy',
                            transforms=[
                                dict(
                                    type="aggregate",
                                    groups=eval(dataframe0[0]).Period_int,
                                    aggregations=[
                                        dict(
                                            target="Numerator",
                                            func=AggregateNumDenom(Calculation),
                                        ),  # , enabled=True
                                        dict(
                                            target="Denominator",
                                            func=AggregateNumDenom(Calculation),
                                        ),  # , enabled=True
                                    ],
                                ),
                            ],
                        )
                    )
        if not traces3:
            return {
                "layout": dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    style={"background-color": "red", "color": "white"},
                    annotations=[
                        dict(
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.5,
                            text="No data available",
                            showarrow=False,
                            font=dict(size=26, color=fontcolor),
                        )
                    ],
                    plot_bgcolor="transparent",
                    paper_bgcolor="transparent",
                )
            }
        else:
            return {
                "data": traces3,
                "layout": dict(
                    clickmode="event+select",
                    barmode="stack",
                    showlegend=False if button_group1 == button_group else True,
                    barnorm=eval(PercentageTotalSwitchDEF(PercentageTotalSwitch)),
                    xaxis=dict(
                        type="string",
                        title="",
                        showgrid=False,
                        gridwidth=0,
                        # showspikes=True,
                        showline=False,
                        color=fontcolor,
                        rangeselector=dict(
                            buttons=rangeselector(GrainSelect),
                            bgcolor="transparent",  # Background color of the range selector
                            activecolor=ProjectOrange,  # tabhover
                            font=dict(color=fontcolor, size=16),
                        ),
                        rangeslider=dict(visible=False),
                        linewidth=2,
                        font=dict(
                            size=14,
                        ),
                    ),
                    yaxis=dict(
                        title="",
                        linewidth=2,
                        tickformat=eval(Notation[0]),
                        showgrid=False,
                        showline=False,
                        autorange=True,
                        fixedrange=True,
                        # showspikes=True,
                        color=fontcolor,
                        gridwidth=0.5,
                        font=dict(
                            size=14,
                        ),
                    ),
                    margin={"l": 60, "b": 45, "t": 37, "r": 40},
                    modebar=dict(
                        bgcolor="transparent",
                        color=BeautifulSignalColor,
                    ),
                    autosize=True,
                    plot_bgcolor=graphcolor,
                    paper_bgcolor=graphcolor,
                    legend=legend,
                    title=title,
                    font=dict(),
                    images=dict(
                        x=0,
                        y=1,
                        sizex=0.2,
                        sizey=0.2,
                    ),
                    hovermode="x-unified",
                    transition={"duration": 50},
                ),
            }  # ,level0filteroptions,level0options#,animatedreturn
    except Exception as e:
        logging.error(f"Exception in callback: {str(e)}")
        raise


# """
# @app.callback(
#     Output("animation", "is_open"),
#     [Input("animation", "n_clicks"),
#      ],prevent_initial_callback=True
# )
# def toggle_modal(n1, n2, n3, is_open):
#     if n1 or n2 or n3:
#         return not is_open
#     return is_open
# """


# @app.callback(
#     Output("graph-level0compare", "figure", allow_duplicate=True),
#     [
#         Input("graph-level0compare-dataset", "data"),
#         Input("button_group", "value"),
#         Input("button_group1", "value"),
#         Input("PercentageTotalSwitchNoTime", "label"),
#         Input("animation", "n_clicks"),
#         Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
#         State("KPISelect", "value"),
#         Input("Totaalswitch", "label"),
#         State("breakpoints", "widthBreakpoint"),
#     ],
#     prevent_initial_call=True,
# )
# def update_level0Graph(
#     graphlevel0comparedataset,
#     button_group,
#     button_group1,
#     PercentageTotalSwitchNoTime,
#     animation,
#     sweepertje,
#     KPISelect,
#     Totaalswitch,
#     widthBreakpoint,
# ):  # ,hoverData,*args
#     print("update_level0Graph cfpandacompare")
#     print("update_level0Graph cfpandacompare")
#     print("update_level0Graph cfpandacompare")
#     print("update_level0Graph cfpandacompare")
#     if not animation or animation % 2 == 0:
#         try:
#             # changed_id2 = [p['prop_id'] for p in dash.callback_context.triggered][0].split('.')[0]
#             LevelOrFilterAttribuut = button_group.split("_")[0]
#             LevelOrFilterLegend = button_group1.split("_")[0]
#             # noemer = f'pl.col("Denominator").{eval(AggregateNumDenom(KPIDenomAgg[KPISelect]))}()'
#             # teller = f'pl.col("Numerator").{eval(AggregateNumDenom(KPINumAgg[KPISelect]))}()'
#             Notation = KPISelectedStyle(KPISelect)
#             Calculation = CalculationDEF(KPISelect)
#             AggregateNum = NumaggregateDEF(KPISelect)
#             AggregateDenom = DenomaggregateDEF(KPISelect)
#             # totaaljanee = Totaalloop(Totaalswitch)
#             if widthBreakpoint == "sm":
#                 title = ""
#             else:
#                 title = dict(
#                     text=str(KPISelect),  # + Level2Entitytype,
#                     # +' -     selected: '+str(Level2NameSelect),
#                     font=dict(  # family='Montserrat',
#                         size=22,
#                         color=fontcolor,
#                     ),
#                 )
#             data000 = graphlevel0comparedataset.to_pandas()
#             traces = []
#             countiterations = data000.eval(button_group).nunique()
#             # countiterations = iterationslist.shape[0]
#             df_by_Level0Name = data000
#             x2 = eval(CalculationLogic0(Calculation))
#             if countiterations == 1:
#                 print("countiterations==1 traces")
#                 traces.append(
#                     dict(
#                         values=x2[0],
#                         labels=df_by_Level0Name.eval(button_group1),
#                         type="pie",
#                         hole=0.7,
#                         margin=dict(t=50, b=30, l=0, r=0),
#                         showlegend=False,
#                         font=dict(size=17, color="white"),
#                         textposition="outside",
#                         textinfo="percent+label",
#                         rotation=50,
#                         marker=dict(
#                             # colors= FilterColor
#                         ),
#                     )
#                 )
#             elif countiterations != 1:
#                 print("countiterations>1 traces")
#                 for j in data000.eval(button_group1).unique():
#                     opacity = "1"
#                     df_by_Level0Name = data000[data000[button_group1] == j]
#                     x3 = eval(CalculationLogic0(Calculation))
#                     traces.append(
#                         dict(
#                             # df_by_Level0Name,
#                             y=df_by_Level0Name.eval(button_group),  # Filter1_0,
#                             x=x3,
#                             # animation_group = df_by_Level0Name.eval(button_group),
#                             # animation_frame= df_by_Level0Name.Period_int,
#                             text=x3,
#                             text_auto=True,
#                             texttemplate="%{value:"
#                             + eval(Notation[0])
#                             + "}",  # "%{value:.01%}",
#                             textformat=eval(Notation[0]),
#                             type="bar",
#                             marker=dict(
#                                 opacity=opacity,
#                                 color=(
#                                     LevelNameColor[j]
#                                     if LevelOrFilterLegend == "LevelName"
#                                     else FilterColor[j]
#                                 ),
#                                 color_discrete_map="identity",
#                                 line=dict(
#                                     width=0.1,
#                                     color=(
#                                         LevelNameColor[j]
#                                         if LevelOrFilterLegend == "LevelName"
#                                         else FilterColor[j]
#                                     ),
#                                     color_discrete_map="identity",
#                                     opacity=1,
#                                 ),
#                             ),
#                             # orientation="v",
#                             # orientation="h",
#                             orientation="h",
#                             name=j,
#                             transforms=[
#                                 dict(
#                                     type="aggregate",
#                                     groups=df_by_Level0Name.eval(button_group),
#                                     aggregations=[
#                                         dict(
#                                             target="Numerator",
#                                             func=AggregateNumDenom(AggregateNum),
#                                         ),
#                                         dict(
#                                             target="Denominator",
#                                             func=AggregateNumDenom(AggregateDenom),
#                                         ),
#                                     ],
#                                 ),
#                             ],
#                         )
#                     )
#             if countiterations == 1:
#                 print("countiterations==1 layout")
#                 returndit = {
#                     "data": traces,
#                     "layout": dict(
#                         font=dict(
#                             size=15,
#                         ),
#                         margin={"l": 140, "b": 25, "t": 37, "r": 40},
#                         annotations=[
#                             dict(
#                                 align="center",
#                                 xref="paper",
#                                 yref="paper",
#                                 showarrow=False,
#                                 font=dict(
#                                     family="Courier New, monospace",
#                                     size=26,
#                                     color="#ffffff",
#                                 ),
#                                 text=str(x2[0]),  # <i class='material-icons'>gender</i>
#                             )
#                         ],
#                         plot_bgcolor=graphcolor,
#                         paper_bgcolor=graphcolor,
#                     ),
#                 }
#             elif countiterations != 1:
#                 print("countiterations>1 layout")
#                 returndit = {
#                     "data": traces,
#                     "layout": dict(
#                         dragmode="select",
#                         clickmode="event+select",
#                         barnorm=eval(
#                             PercentageTotalSwitchDEF(PercentageTotalSwitchNoTime)
#                         ),
#                         barmode="stack",  # aanzetten indien tweede per
#                         clear_on_unhover=True,
#                         type="bar",
#                         xaxis=dict(
#                             type="string",
#                             title="",
#                             showgrid=False,
#                             gridwidth=0,
#                             fixedrange=True,
#                             showline=False,
#                             tickformat=eval(Notation[0]),
#                             visible=False,
#                             color=fontcolor,
#                             font=dict(
#                                 size=14,
#                             ),
#                         ),
#                         yaxis=dict(
#                             title="",
#                             showline=False,
#                             showgrid=False,
#                             categoryorder="total ascending",
#                             gridwidth=0,
#                             color=fontcolor,
#                         ),
#                         margin={"l": 140, "b": 25, "t": 37, "r": 40},
#                         showlegend=False if button_group1 == button_group else True,
#                         legend=dict(
#                             font=dict(color=fontcolor)  # Change the font color here
#                         ),
#                         autosize=True,
#                         plot_bgcolor=graphcolor,
#                         paper_bgcolor=graphcolor,
#                         modebar=dict(
#                             bgcolor="transparent",
#                             color=BeautifulSignalColor,
#                         ),
#                         font=dict(
#                             size=15,
#                         ),
#                         title=title,
#                         hovermode="x-unified",
#                         transition={"duration": 500},
#                         style={"overflow": "auto"},
#                     ),
#                 }
#             elif data000.empty:
#                 print("returnemptybar")
#                 returndit = {
#                     "layout": dict(
#                         xaxis=dict(visible=False),
#                         yaxis=dict(visible=False),
#                         annotations=[
#                             dict(
#                                 xref="paper",
#                                 yref="paper",
#                                 x=0.5,
#                                 y=0.5,
#                                 text="No data available",
#                                 showarrow=False,
#                                 font=dict(size=26, color=fontcolor),
#                             )
#                         ],
#                         plot_bgcolor=graphcolor,
#                         paper_bgcolor=graphcolor,
#                     )
#                 }
#             return returndit
#         except Exception as e:
#             logging.error(f"Exception in callback: {str(e)}")
#             raise
#     else:
#         raise PreventUpdate


# app.config['suppress_callback_exceptions'] = True


@app.callback(
    Output("graph-level0compare", "figure", allow_duplicate=True),
    [
        Input("mastersetkpifiltered", "data"),
        Input("button_group", "value"),
        Input("button_group1", "value"),
        Input("PercentageTotalSwitchNoTime", "label"),
        Input({"type": "sweepertje", "index": ALL}, "n_clicks"),
        State("KPISelect", "value"),
        Input("Totaalswitch", "label"),
        Input("animation", "n_clicks"),
        State("breakpoints", "widthBreakpoint"),
    ],
    prevent_initial_call=True,
)
def update_animation(
    mastersetkpifiltered,
    button_group,
    button_group1,
    PercentageTotalSwitchNoTime,
    sweepertje,
    KPISelect,
    Totaalswitch,
    animation,
    widthBreakpoint,
):  # ,hoverData,*args
    # changed_id2 = [p['prop_id'] for p in dash.callback_context.triggered][0].split('.')[0]
    # print(changed_id2)
    if not animation or animation % 2 == 0:
        raise PreventUpdate
    else:
        print("update_animation executed")
        try:
            data000 = mastersetkpifiltered.to_pandas()
            pxbar = px.bar(
                data000,
                y=button_group,
                x="Numerator",
                color=button_group1,
                color_discrete_map=LevelNameColorFiltered,
                animation_group=button_group,
                animation_frame="Period_int",
            )
            pxbar.update_layout(
                dict(
                    dragmode="select",
                    clickmode="event+select",
                    barnorm=eval(PercentageTotalSwitchDEF(PercentageTotalSwitchNoTime)),
                    barmode="stack",  # aanzetten indien tweede per
                    xaxis=dict(  # type='string',
                        title="",
                        showgrid=False,
                        gridwidth=0,
                        fixedrange=True,
                        showline=False,
                        # tickformat=eval(Notation[0]),
                        visible=False,
                        color=fontcolor,
                    ),
                    yaxis=dict(
                        title="",
                        showline=False,
                        showgrid=False,
                        categoryorder="total ascending",
                        gridwidth=0,
                        color=fontcolor,
                    ),
                    legend=dict(
                        #  color=fontcolor  # Change the font color here
                    ),
                    margin={"l": 140, "b": 25, "t": 37, "r": 40},
                    showlegend=False if button_group1 == button_group else True,
                    autosize=True,
                    plot_bgcolor=graphcolor,
                    paper_bgcolor=graphcolor,
                    updatemenus=[
                        dict(
                            type="buttons",
                            showactive=False,
                            y=-0.10,
                            x=-0.05,
                            xanchor="left",
                            yanchor="bottom",
                        )
                    ],
                )
            )
            pxbar["layout"]["sliders"][0]["pad"] = dict(r=70, t=5)
            return pxbar
        except Exception as e:
            logging.error(f"Exception in callback: {str(e)}")
            raise


@app.callback(
    Output("modal", "is_open"),
    [Input("open-settings", "n_clicks"), Input("close-settings", "n_clicks")],
    [State("modal", "is_open")],
    prevent_initial_callback=True,
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modalfilter", "is_open"),
    [
        Input("Opennavbar-right", "n_clicks"),
        Input("close-filter", "n_clicks"),
        Input("sweepl0filter", "n_clicks"),
    ],
    [State("modalfilter", "is_open")],
    prevent_initial_callback=True,
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open


"""
@app.callback(
    Output("animation", "is_open"),
    [Input("animation", "n_clicks"),
     ],prevent_initial_callback=True
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open
"""


# app.clientside_callback(
#    """
#    function(className) {
#        var selectValue = document.querySelector('.' + className);
#        selectValue.addEventListener('click', function(e) {
#            if (e.target.classList.contains('Select-value')) {
#                e.target.remove();
#            }
#        });
#    }
#    """,
#    Output("Level0DD", "children"),
#    Input("Level0DD", "id"),
# )
@app.callback(
    Output("graphlevel0", "figure", allow_duplicate=True),
    [
        Input("graph-level0compare", "hoverData"),
        Input("button_group", "value"),
        # Input('pieorbar', 'data'),
        State("graphlevel0", "figure"),
    ],
    prevent_initial_call=True,
)
def opacity_level0Graph(hoverData, button_group, figure):
    print("update opacity")
    if hoverData is None or hoverData.get("clear_data"):
        for item in figure["data"]:
            item["marker"].update({"opacity": 1})
    else:
        for item in figure["data"]:
            if hoverData["points"][0]["label"] in item[f"{button_group}"]:
                item["marker"].update({"opacity": 1})
            else:
                item["marker"].update({"opacity": 0.2})
    # print(figure)
    updated_marker_opacity = figure["data"]
    patched_figure = Patch()
    patched_figure["data"] = updated_marker_opacity
    return patched_figure


app.clientside_callback(
    """window.onload=function () {
        addListeners()
        return 0
    }""",
    Output("nav", "n_clicks"),
    Input("nav", "children"),
)

if __name__ == "__main__":
    print("application loaded")
    app.run_server(host="0.0.0.0")
    # app.run_server()
