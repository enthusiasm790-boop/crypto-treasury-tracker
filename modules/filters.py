import streamlit as st

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

        return df_filtered

