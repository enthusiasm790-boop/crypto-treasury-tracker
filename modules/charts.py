import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative

def format_usd(value):
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.0f}"


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

    # Format values for display
    grouped["Formatted_Total_USD"] = grouped["Total_USD"].apply(format_usd)
    grouped["Formatted_Avg_Holdings"] = grouped["Avg_Holdings"].apply(format_usd)

    # Prepare custom hover data columns
    grouped["Custom_Hover"] = (
        "Total Reserves: " + grouped["Formatted_Total_USD"] +
        "<br>Entities Reporting: " + grouped["Entity_Count"].astype(str) +
        "<br>Average Reserve per Entity: " + grouped["Formatted_Avg_Holdings"]
    )

    # Create choropleth
    fig = px.choropleth(
        grouped,
        locations="Country",
        locationmode="country names",
        color="Total_USD",
        hover_name="Country",
        custom_data=["Custom_Hover"],
        color_continuous_scale=px.colors.sequential.Sunset,
        projection="natural earth",
        template="plotly_dark"
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<extra></extra>"
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
        marker=dict(color="#f7931a" if asset == "BTC" else "#A9A9A9")
    ))

    fig.update_layout(
        height=240,
        title=f"Top 5 {asset} Treasury Holders",
        yaxis=dict(autorange="reversed", tickfont=dict(size=12), title_standoff=25),
        margin=dict(l=140, r=10, t=40, b=20),  # Uniform left margin
        font=dict(size=12),
        hoverlabel=dict(align='left') 
    )

    return fig


def holdings_by_entity_type_bar(df):
    # Step 1: Group by Entity Type and Crypto Asset
    grouped = (
        df.groupby(['Entity Type', 'Crypto Asset'])['USD Value']
        .sum()
        .reset_index()
    )

    # Step 2: Build custom hover text per Entity Type
    breakdowns = (
        grouped.groupby('Entity Type')
        .apply(lambda d: f"<b>{d.name}</b><br>" + "<br>".join(
            [f"{row['Crypto Asset']}: <b>{format_usd(row['USD Value'])}</b>" for _, row in d.sort_values('USD Value', ascending=False).iterrows()])
        ).to_dict()
    )
    grouped['Custom Hover'] = grouped['Entity Type'].map(breakdowns)

    # Step 3: Sort Entity Types by total USD Value descending
    totals = grouped.groupby('Entity Type')['USD Value'].sum().sort_values(ascending=False)
    sorted_types = totals.index.tolist()
    grouped['Entity Type'] = pd.Categorical(grouped['Entity Type'], categories=sorted_types, ordered=True)
    grouped = grouped.sort_values(['Entity Type', 'Crypto Asset'])

    # Step 4: Create chart with formatted labels
    fig = px.bar(
        grouped,
        x='Entity Type',
        y='USD Value',
        color='Crypto Asset',
        barmode='stack',
        custom_data=['Custom Hover'],
        color_discrete_map={
            'BTC': '#f7931a',
            'ETH': '#A9A9A9'
        }
    )

    # Add total USD value as annotation above each full bar
    totals = grouped.groupby('Entity Type')['USD Value'].sum()
    for i, entity_type in enumerate(totals.index):
        fig.add_annotation(
            x=entity_type,
            y=totals[entity_type],
            text=(
                f"${totals[entity_type]/1_000_000_000:.1f}B" if totals[entity_type] >= 1_000_000_000
                else f"${totals[entity_type]/1_000_000:.1f}M"
            ),
            showarrow=False,
            font=dict(size=14, color='white'),
            yanchor='bottom'
        )

    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )


    # Step 5: Layout updates
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        textposition='outside',
        textfont=dict(size=14)
    )

    fig.update_layout(
        margin=dict(t=50, b=20),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.1,
            xanchor='center',
            x=0.5
        ),
        hoverlabel=dict(align='left'),
        xaxis_title="",
        yaxis_title="",
        legend_title_text='',
    )

    return fig


def entity_type_distribution_pie(df):
    # Drop duplicates to count entities uniquely per type
    entity_type_counts = df[['Entity Name', 'Entity Type']].drop_duplicates()
    type_counts = entity_type_counts['Entity Type'].value_counts().reset_index()
    type_counts.columns = ['Entity Type', 'Count']

    fig = px.pie(
        type_counts,
        values='Count',
        names='Entity Type',
        hole=0.65
    )

    # Force all percentages to show with 1 decimal (even <1%)
    fig.update_traces(
        texttemplate='%{percent:.1%}',
        textfont=dict(size=16),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    )

    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.1,
            xanchor='center',
            x=0.5
        ),
        hoverlabel=dict(align='left') 
    )

    return fig


def top_countries_by_entity_count(df):
    # Step 1: Group by Country and Entity Type to count unique entities
    grouped = (
        df.groupby(['Country', 'Entity Type'])['Entity Name']
        .nunique()
        .reset_index(name='Entity Count')
    )

    # Step 2: Get top 5 countries by total entity count
    top_countries = (
        grouped.groupby('Country')['Entity Count']
        .sum()
        .nlargest(5)
        .index.tolist()
    )

    filtered = grouped[grouped['Country'].isin(top_countries)]

    # Step 3: Prepare custom hover text with aggregated breakdown per country
    country_breakdowns = (
        filtered.groupby('Country')
        .apply(lambda d: f"<b>{d.name}</b><br>" + "<br>".join(
            [f"{row['Entity Type']}: <b>{int(row['Entity Count'])}</b>" for _, row in d.sort_values('Entity Count', ascending=False).iterrows()])
        ).to_dict()
    )

    filtered['Custom Hover'] = filtered['Country'].map(country_breakdowns)

    # Step 4: Create stacked bar chart
    fig = px.bar(
        filtered,
        x='Entity Count',
        y='Country',
        color='Entity Type',
        orientation='h',
        labels={'Entity Count': 'Entities'},
        custom_data=['Custom Hover'],
        text=None  # Remove individual labels
    )

    # Step 5: Add total text at end of each full bar (sum by country)
    totals = (
        filtered.groupby('Country')['Entity Count']
        .sum()
        .sort_values(ascending=True)  # Match y-axis order
    )

    for country, total in totals.items():
        fig.add_annotation(
            x=total,
            y=country,
            text=str(int(total)),
            showarrow=False,
            font=dict(size=16, color="white"),
            xanchor='left',
            yanchor='middle'
        )


    # Step 6: Final layout adjustments
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        textfont=dict(size=12),
        hoverlabel=dict(align="left")
    )

    fig.update_layout(
        height=365,
        margin=dict(t=10, b=20),  # ↓ reduce top and bottom margin
        yaxis=dict(categoryorder='total ascending', title="", tickfont=dict(size=14)),
        xaxis=dict(tickformat=',d', title=""),
        showlegend=False
    )

    return fig


def top_countries_by_usd_value(df):
    # Step 1: Group by Country and Entity Type to get USD sums
    grouped = (
        df.groupby(['Country', 'Entity Type'])['USD Value']
        .sum()
        .reset_index()
    )

    # Step 2: Get top 5 countries by total USD value
    top_countries = (
        grouped.groupby('Country')['USD Value']
        .sum()
        .nlargest(5)
        .index.tolist()
    )

    filtered = grouped[grouped['Country'].isin(top_countries)]

    # Step 3: Prepare custom hover text with aggregated breakdown per country
    country_breakdowns = (
        filtered.groupby('Country')
        .apply(lambda d: f"<b>{d.name}</b><br>" + "<br>".join(
            [f"{row['Entity Type']}: <b>{format_usd(row['USD Value'])}</b>" for _, row in d.sort_values('USD Value', ascending=False).iterrows()])
        ).to_dict()
    )

    filtered['Custom Hover'] = filtered['Country'].map(country_breakdowns)

    # Step 4: Create stacked bar chart
    fig = px.bar(
        filtered,
        x='USD Value',
        y='Country',
        color='Entity Type',
        orientation='h',
        labels={'USD Value': 'USD'},
        custom_data=['Custom Hover'],
        text=None  # Remove partial bar labels
    )

    # Step 5: Add total value at end of bar
    totals = (
        filtered.groupby('Country')['USD Value']
        .sum()
        .sort_values(ascending=True)
    )

    for country, total in totals.items():
        fig.add_annotation(
            x=total,
            y=country,
            text=format_usd(total),
            showarrow=False,
            font=dict(size=16, color='white'),
            xanchor='left',
            yanchor='middle'
        )

    # Step 6: Final layout adjustments
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        textfont=dict(size=12),
        hoverlabel=dict(align="left")
    )

    fig.update_layout(
        height=365,
        margin=dict(t=10, b=20),  # ↓ reduce top and bottom margin
        yaxis=dict(categoryorder='total ascending', title=""),
        xaxis=dict(title=""),
        showlegend=False
    )

    return fig



