import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
from modules.kpi_helpers import load_base64_image


logo_b64 = load_base64_image("assets/ctt-symbol.svg")


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

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=30, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
            center=dict(lat=20, lon=0),
            projection_scale=1  # optional zoom level
        ),
        uirevision="static-map",  # Prevents user interaction from updating layout
        margin=dict(l=0, r=0, t=10, b=0),
        height=500,
        coloraxis_colorbar=dict(title="Total USD"),
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

    # Step 1: Create custom hover info
    top["Custom Hover"] = top.apply(
        lambda row: f"<b>{row['Entity Name']}</b><br>" +
                    (f"Holdings: {row['Holdings']:,.0f}" if by == "units"
                     else f"USD Value: <b>${row['USD_Value']/1e9:.1f}B</b>"),
        axis=1
    )

    # Step 2: Updated figure with hovertemplate and customdata
    fig = go.Figure(go.Bar(
        x=values,
        y=top["Entity Name"],
        orientation='h',
        text=value_labels,
        textposition="auto",
        marker=dict(color="#f7931a" if asset == "BTC" else "#A9A9A9"),
        customdata=top["Custom Hover"],
        hovertemplate="%{customdata}<extra></extra>"
    ))

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=15, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
    )
    
    fig.update_layout(
        height=240,
        title=f"Top 5 {asset} Treasury Holders",
        yaxis=dict(autorange="reversed", tickfont=dict(size=12), title_standoff=25),
        margin=dict(l=140, r=10, t=40, b=20),  # Uniform left margin
        font=dict(size=12),
        hoverlabel=dict(align='left')
        )

    return fig


def historic_chart(df, by="USD"):
    # Ensure numeric
    df['USD Value'] = pd.to_numeric(df['USD Value'], errors='coerce')
    if 'Holdings (Unit)' in df.columns:
        df['Holdings (Unit)'] = pd.to_numeric(df['Holdings (Unit)'], errors='coerce')

    value_col = 'USD Value' if by == "USD" else 'Holdings (Unit)'

    # Aggregate monthly totals
    grouped = (
        df.groupby(['Date', 'Crypto Asset'])
        .agg({value_col: 'sum', 'USD Value': 'sum'})
        .reset_index()
    )

    # Build hover templates
    if by == "USD":
        breakdowns = (
            grouped.groupby('Date')
            .apply(lambda d: (
                f"<b>{d.name.strftime('%B %Y')}</b><br>" +
                "<br>".join([
                    f"{row['Crypto Asset']}: <b>{format_usd(row['USD Value'])}</b>"
                    for _, row in d.iterrows()
                ]) +
                f"<br>Total: <b>{format_usd(d['USD Value'].sum())}</b>"
            ))
            .to_dict()
        )
        grouped['Text'] = grouped[value_col].apply(format_usd)
    else:
        breakdowns = (
            grouped.groupby('Date')
            .apply(lambda d: (
                f"<b>{d.name.strftime('%B %Y')}</b><br>" +
                "<br>".join([
                    f"{row['Crypto Asset']}: <b>{int(row[value_col]):,}</b>"
                    for _, row in d.iterrows()
                ]) +
                f"<br>Total: <b>{int(d[value_col].sum()):,}</b>"
            ))
            .to_dict()
        )
        grouped['Text'] = grouped[value_col].apply(lambda x: f"{int(x):,}")

    grouped['Custom Hover'] = grouped['Date'].map(breakdowns)

    max_date = df['Date'].max()
    grouped = grouped[grouped['Date'] <= max_date]

    # Build figure
    fig = px.bar(
        grouped,
        x='Date',
        y=value_col,
        color='Crypto Asset',
        text='Text' if by != "USD" else None,
        custom_data=['Custom Hover'],
        barmode='stack',
        color_discrete_map={'BTC': '#f7931a', 'ETH': '#A9A9A9'}
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        textposition='outside'
    )

    # Add annotations only for USD
    if by == "USD":
        totals = grouped.groupby('Date')['USD Value'].sum()
        for date, total in totals.items():
            fig.add_annotation(
                x=date,
                y=total,
                text=(f"${total/1_000_000_000:.1f}B" if total >= 1_000_000_000
                      else f"${total/1_000_000:.1f}M"),
                showarrow=False,
                font=dict(size=14, color='white'),
                yanchor='bottom'
            )

    # Watermark
    fig.add_annotation(
        text="Crypto Treasury Tracker",
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=30, color="white"),
        opacity=0.3,
        xanchor="center",
        yanchor="middle",
    )

    fig.update_layout(
        margin=dict(t=50, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
        hoverlabel=dict(align='left'),
        xaxis_title="",
        yaxis_title="",
        legend_title_text=''
    )

    fig.update_xaxes(
        dtick="M1",
        tickformat="%b %Y",
     #   ticklabelmode="period"  # ensures labels like "Jul 2025" represent the period
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
        },
        category_orders={'Entity Type': sorted_types}  # ✅ This line is key
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

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=15, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
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
        legend_title_text=''
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

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=15, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
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

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=15, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
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

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=15, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
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
        showlegend=False,
    )

    return fig


def entity_ranking(df, by="USD", top_n=10):
    value_col = 'USD Value' if by == "USD" else 'Holdings (Unit)'

    # Step 1: Aggregate values for plotting
    grouped = (
        df.groupby(['Entity Name', 'Crypto Asset'])[value_col]
        .sum()
        .reset_index()
    )

    # Step 2: USD total ranking
    usd_totals = (
        df.groupby('Entity Name')['USD Value']
        .sum()
        .sort_values(ascending=False)
    )

    # Limit to top N by USD value
    top_entities = usd_totals.head(top_n).index.tolist()
    grouped = grouped[grouped['Entity Name'].isin(top_entities)]
    grouped["USD Total"] = grouped["Entity Name"].map(usd_totals)

    # Step 3: Hover & label formatting
    if by == "USD":
        grouped["Text"] = grouped[value_col].apply(format_usd)
        hover = grouped.groupby('Entity Name').apply(
            lambda d: f"<b>{d.name}</b><br>" + "<br>".join(
                [f"{row['Crypto Asset']}: <b>{format_usd(row[value_col])}</b>" for _, row in d.iterrows()])
        ).to_dict()
    else:
        grouped["Text"] = grouped[value_col].apply(lambda x: f"{int(x):,}")
        hover = grouped.groupby('Entity Name').apply(
            lambda d: f"<b>{d.name}</b><br>" + "<br>".join(
                [f"{row['Crypto Asset']}: <b>{int(row[value_col]):,}</b>" for _, row in d.iterrows()])
        ).to_dict()

    grouped['Custom Hover'] = grouped['Entity Name'].map(hover)

    # Step 4: Enforce x-axis sort
    sorted_entities = (
        grouped.groupby('Entity Name')['USD Total']
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )

    grouped['Entity Name'] = pd.Categorical(grouped['Entity Name'], categories=sorted_entities, ordered=True)
    grouped = grouped.sort_values(['Entity Name', 'Crypto Asset'])

    # Step 5: Plot
    fig = px.bar(
        grouped,
        x='Entity Name',
        y=value_col,
        color='Crypto Asset',
        barmode='stack',
        custom_data=['Custom Hover'],
        color_discrete_map={'BTC': '#f7931a', 'ETH': '#A9A9A9'},
        category_orders={'Entity Name': sorted_entities}
    )

    totals = grouped.groupby('Entity Name')[value_col].sum()
    for entity in totals.index:
        label = format_usd(totals[entity]) if by == "USD" else f"{int(totals[entity]):,}"
        fig.add_annotation(
            x=entity,
            y=totals[entity],
            text=label,
            showarrow=False,
            font=dict(size=14, color='white'),
            xanchor='center',
            yanchor='bottom'
        )

    fig.add_annotation(
        text="Crypto Treasury Tracker",  # or "Crypto Treasury Tracker"
        x=0.5, y=0.5,                      # Center of chart
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=30, color="white"),
        opacity=0.3,                       # Adjust for subtlety
        xanchor="center",
        yanchor="middle",
    )

    fig.update_traces(
        textposition="none",
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        height=500,
        xaxis=dict(title=None, tickfont=dict(size=12)),
        yaxis=dict(title="" if by == "USD" else ""),
        margin=dict(l=40, r=40, t=50, b=60),
        font=dict(size=12),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.1,
            xanchor='center',
            x=0.5
        ),
        legend_title_text='',
        hoverlabel=dict(align='left')
    )

    return fig
