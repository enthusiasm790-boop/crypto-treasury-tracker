import streamlit as st
import pandas as pd


def apply_filters(df):
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        asset_options = df['Crypto Asset'].dropna().unique().tolist()
        selected_assets = col1.multiselect("Select Crypto Asset(s)", asset_options, default=asset_options)

        type_options = ["All"] + df['Entity Type'].dropna().unique().tolist()
        selected_type = col2.selectbox("Select Entity Type", type_options, index=0)

        country_options = ["All"] + sorted(df['Country'].dropna().unique())
        selected_country = col3.selectbox("Select Country/Region", country_options, index=0)

        # Apply filters
        df_filtered = df[df['Crypto Asset'].isin(selected_assets)]

        if selected_type != "All":
            df_filtered = df_filtered[df_filtered['Entity Type'] == selected_type]

        if selected_country != "All":
            df_filtered = df_filtered[df_filtered['Country'] == selected_country]

        # Filter out zero USD value holdings
        df_filtered = df_filtered[df_filtered['USD Value'] > 0]

        return df_filtered

def apply_filters_historic(df):
    with st.container(border=True):
        col1, col2 = st.columns(2)

        asset_options = df['Crypto Asset'].dropna().unique().tolist()
        selected_assets = col1.multiselect("Select Crypto Asset(s)", asset_options, default=asset_options)

        # Time range filter
        time_options = ["3M", "YTD", "12M", "All"]
        selected_range = col2.selectbox("Select Time Range", time_options, index=3)  # Default = "All"

        # Apply asset filter
        df_filtered = df[df['Crypto Asset'].isin(selected_assets)]
        latest_date = df_filtered['Date'].max()

        if selected_range != "All":
            if selected_range == "3M":
                cutoff_date = latest_date - pd.DateOffset(months=3)
            elif selected_range == "12M":
                cutoff_date = latest_date - pd.DateOffset(months=12)
            elif selected_range == "YTD":
                cutoff_date = (pd.Timestamp(year=latest_date.year - 1, month=12, day=31))
            df_filtered = df_filtered[df_filtered['Date'] >= cutoff_date]

        # Filter out zero USD value holdings
        df_filtered = df_filtered[df_filtered['USD Value'] > 0]

        return df_filtered

