import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def render_world_map(df, asset_filter, type_filter, value_range_filter):
    # Apply filters to raw data
    filtered = df.copy()
    if asset_filter != "All":
        filtered = filtered[filtered["Crypto Asset"] == asset_filter]
    if type_filter != "All":
        filtered = filtered[filtered["Entity Type"] == type_filter]

    # Group first
    grouped = filtered.groupby("Country").agg(
        Total_USD=("USD Value", "sum"),
        Entity_Count=("Entity Name", "nunique"),
        Avg_Holdings=("USD Value", "mean")
    ).reset_index()

    # Value range filter (now on grouped data)
    if value_range_filter == "0–100M":
        grouped = grouped[grouped["Total_USD"] < 100_000_000]
    elif value_range_filter == "100M–1B":
        grouped = grouped[(grouped["Total_USD"] >= 100_000_000) & (grouped["Total_USD"] < 1_000_000_000)]
    elif value_range_filter == ">1B":
        grouped = grouped[grouped["Total_USD"] >= 1_000_000_000]

    # Create choropleth
    fig = px.choropleth(
        grouped,
        locations="Country",
        locationmode="country names",
        color="Total_USD",
        hover_name="Country",
        hover_data={
            "Total_USD": ":,.0f",
            "Entity_Count": True,
            "Avg_Holdings": ":,.0f"
        },
        color_continuous_scale=px.colors.sequential.Sunset,
        projection="natural earth",
        template="plotly_dark"
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=500,
        coloraxis_colorbar=dict(title="Total USD"),
        geo=dict(showframe=False, showcoastlines=True),
        font=dict(size=12),
    )

    return fig


def render_rankings(df, asset="BTC", by="units"):
    d = df[df["Crypto Asset"] == asset]

    top = (
        d.groupby("Entity Name")
        .agg(
            Holdings=("Holdings (Unit)", "sum"),
            USD_Value=("USD Value", "sum")
        )
        .sort_values("Holdings" if by == "units" else "USD_Value", ascending=False)
        .head(5)
        .reset_index()
    )

    values = top["Holdings"] if by == "units" else top["USD_Value"]
    value_labels = (
        top["Holdings"].apply(lambda x: f"{x:,.0f}")
        if by == "units"
        else top["USD_Value"].apply(lambda x: f"${x/1e9:.1f}B")
    )

    fig = go.Figure(go.Bar(
        x=values,
        y=top["Entity Name"],
        orientation='h',
        text=value_labels,
        textposition="auto",
        marker=dict(color="darkorange" if asset == "BTC" else "steelblue")
    ))

    fig.update_layout(
        height=240,
        title=f"Top 5 {asset} Treasury Holders",
        yaxis=dict(autorange="reversed", tickfont=dict(size=12), title_standoff=25),
        margin=dict(l=140, r=10, t=40, b=20),  # Uniform left margin
        font=dict(size=12),
    )

    return fig
