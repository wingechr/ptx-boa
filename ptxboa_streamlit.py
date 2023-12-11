# -*- coding: utf-8 -*-
"""Mockup streamlit app."""
# TODO how do I use the treamlit logger?
import logging

import pandas as pd
import streamlit as st
import streamlit_antd_components as sac

import app.ptxboa_functions as pf
from app.context_data import load_context_data
from app.sidebar import make_sidebar
from app.tab_certification_schemes import content_certification_schemes
from app.tab_country_fact_sheets import content_country_fact_sheets
from app.tab_dashboard import content_dashboard
from app.tab_deep_dive_countries import content_deep_dive_countries
from app.tab_info import content_info
from app.tab_input_data import content_input_data
from app.tab_literature import content_literature
from app.tab_market_scanning import content_market_scanning
from app.tab_sustainability import content_sustainability
from app.user_data_from_file import download_user_data, upload_user_data
from ptxboa.api import PtxboaAPI

# setup logging
# level can be changed on strartup with: --logger.level=LEVEL
loglevel = st.logger.get_logger(__name__).level


logger = logging.getLogger()  # do not ude __name__ so we can resue it in submodules
logger.setLevel(loglevel)
log_handler = logging.StreamHandler()
log_handler.setFormatter(
    logging.Formatter(
        "[%(asctime)s %(levelname)7s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
logger.addHandler(log_handler)


logger.info("Updating app...")

# app layout:

# Set the pandas display option to format floats with 2 decimal places
pd.set_option("display.float_format", "{:.2f}".format)

if "user_changes_df" not in st.session_state:
    st.session_state["user_changes_df"] = None

if "edit_input_data" not in st.session_state:
    st.session_state["edit_input_data"] = False

# https://discuss.streamlit.io/t/can-not-set-page-width-in-streamlit-1-5-0/21522/5
css = """
<style>
    section.main > div {max-width:80rem}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

api = st.cache_resource(PtxboaAPI)()
st.title("PtX Business Opportunity Analyzer :red[draft version, please do not quote!]")

with st.container():
    if st.session_state["edit_input_data"]:
        st.info("Data editing mode **ON**")
        with st.expander("Modified data"):
            if st.session_state["user_changes_df"] is not None:
                download_user_data()
            pf.display_user_changes(api)

            with st.container():
                st.divider()
                st.markdown("##### Upload your data from a previous session")
                upload_user_data(api)
    else:
        placeholder = st.empty()

tabs = (
    "Dashboard",
    "Market scanning",
    "Input data",
    "Deep-dive countries",
    "Country fact sheets",
    "Certification schemes",
    "Sustainability",
    "Literature",
    "Info",
)

tabs_icons = {
    "Dashboard": "house-fill",
    "Info": "question-circle-fill",
}

# the "tab_key" is used to identify the sac.tabs element. Whenever a tab is switched
# programatically (e.g. via app.ptxboa.functions.move_to_tab), the "tab_key" entry is
# incremented by 1. This allows us to set the programatically set tab as the default
# `index` in `sac.tabs()`.
if "tab_key" not in st.session_state:
    st.session_state["tab_key"] = "tab_key_0"

# initializing "tab at first round
if st.session_state["tab_key"] not in st.session_state:
    st.session_state[st.session_state["tab_key"]] = "Dashboard"

sac.tabs(
    [
        sac.TabsItem(label=i, icon=tabs_icons[i] if i in tabs_icons.keys() else None)
        for i in tabs
    ],
    index=tabs.index(st.session_state[st.session_state["tab_key"]]),
    format_func="title",
    align="center",
    key=st.session_state["tab_key"],
)

# create sidebar:
make_sidebar(api)

# import agora color scale:
if "colors" not in st.session_state:
    colors = pd.read_csv("data/Agora_Industry_Colours.csv")
    st.session_state["colors"] = colors["Hex Code"].to_list()

# calculate results over different data dimensions:
costs_per_region = pf.calculate_results_list(
    api,
    parameter_to_change="region",
    parameter_list=None,
)
costs_per_scenario = pf.calculate_results_list(
    api,
    parameter_to_change="scenario",
    parameter_list=None,
)
costs_per_res_gen = pf.calculate_results_list(
    api,
    parameter_to_change="res_gen",
    # TODO: here we remove PV tracking manually, this needs to be fixed in data
    parameter_list=[
        x for x in api.get_dimension("res_gen").index.to_list() if x != "PV tracking"
    ],
)
costs_per_chain = pf.calculate_results_list(
    api,
    parameter_to_change="chain",
    parameter_list=None,
    override_session_state={"output_unit": "USD/MWh"},
)

# import context data:
cd = load_context_data()

# dashboard:
if st.session_state[st.session_state["tab_key"]] == "Dashboard":
    content_dashboard(
        api,
        costs_per_region=costs_per_region,
        costs_per_scenario=costs_per_scenario,
        costs_per_res_gen=costs_per_res_gen,
        costs_per_chain=costs_per_chain,
    )

if st.session_state[st.session_state["tab_key"]] == "Market scanning":
    content_market_scanning(api, costs_per_region)

if st.session_state[st.session_state["tab_key"]] == "Input data":
    content_input_data(api)

if st.session_state[st.session_state["tab_key"]] == "Deep-dive countries":
    content_deep_dive_countries(api, costs_per_region)

if st.session_state[st.session_state["tab_key"]] == "Country fact sheets":
    content_country_fact_sheets(cd)

if st.session_state[st.session_state["tab_key"]] == "Certification schemes":
    content_certification_schemes(cd)

if st.session_state[st.session_state["tab_key"]] == "Sustainability":
    content_sustainability(cd)

if st.session_state[st.session_state["tab_key"]] == "Literature":
    content_literature(cd)

if st.session_state[st.session_state["tab_key"]] == "Info":
    content_info()
