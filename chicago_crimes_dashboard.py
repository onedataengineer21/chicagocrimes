import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Chicago Crimes Analytics",
    page_icon="🚔",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'chicagocrimes.csv')
    df = pd.read_csv(csv_path)

    # Clean column names (remove leading/trailing spaces and normalize internal spaces)
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    # Parse date - handle the date column which might have different spacing
    date_col = 'DATE OF OCCURRENCE'
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    # Remove rows with invalid dates
    df = df.dropna(subset=[date_col])

    df['date'] = df[date_col].dt.date
    df['hour'] = df[date_col].dt.hour
    df['day_of_week'] = df[date_col].dt.day_name()
    df['month'] = df[date_col].dt.to_period('M').astype(str)

    return df

# Load the data
try:
    df = load_data()

    # Sidebar - View Mode Selection
    st.sidebar.title("🚔 Chicago Crimes")
    st.sidebar.markdown("---")

    view_mode = st.sidebar.radio(
        "Select View Mode:",
        ["Daily", "Weekly", "Monthly"],
        index=0
    )

    st.sidebar.markdown("---")

    # Date selection based on view mode
    if view_mode == "Daily":
        max_date = df['date'].max()
        min_date = df['date'].min()
        selected_date = st.sidebar.date_input(
            "Select Date:",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        # Filter data for selected day
        filtered_df = df[df['date'] == selected_date]
        period_label = f"{selected_date.strftime('%B %d, %Y')}"
        time_grouping = 'hour'

    elif view_mode == "Weekly":
        max_date = df['date'].max()
        min_date = df['date'].min()
        selected_date = st.sidebar.date_input(
            "Select Week Starting:",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        # Calculate week range
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)

        # Filter data for selected week
        filtered_df = df[(df['date'] >= week_start) & (df['date'] <= week_end)]
        period_label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        time_grouping = 'day_of_week'

    else:  # Monthly
        # Get unique months
        months = sorted(df['month'].unique(), reverse=True)
        selected_month = st.sidebar.selectbox(
            "Select Month:",
            months
        )

        # Filter data for selected month
        filtered_df = df[df['month'] == selected_month]
        period_label = selected_month
        time_grouping = 'date'

    # Title with period
    st.header(f"🚔 Chicago Crimes Analytics - {view_mode} View")
    st.markdown(f"**📅 Period:** {period_label}")
    st.markdown("---")

    # KPI Metrics
    total_crimes = len(filtered_df)
    arrests_made = len(filtered_df[filtered_df['ARREST'] == 'Y'])
    arrest_rate = (arrests_made / total_crimes * 100) if total_crimes > 0 else 0
    domestic_crimes = len(filtered_df[filtered_df['DOMESTIC'] == 'Y'])
    domestic_rate = (domestic_crimes / total_crimes * 100) if total_crimes > 0 else 0

    # Most common crime type
    if total_crimes > 0:
        most_common_crime = filtered_df['PRIMARY DESCRIPTION'].value_counts().index[0]
    else:
        most_common_crime = "N/A"

    # Display KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="📊 Total Crimes",
            value=f"{total_crimes:,}"
        )

    with col2:
        st.metric(
            label="👮 Arrests Made",
            value=f"{arrests_made:,}",
            delta=f"{arrest_rate:.1f}% arrest rate"
        )

    with col3:
        st.metric(
            label="🏠 Domestic Crimes",
            value=f"{domestic_crimes:,}",
            delta=f"{domestic_rate:.1f}% of total"
        )

    with col4:
        st.metric(
            label="🔝 Top Crime Type",
            value=most_common_crime if len(most_common_crime) < 15 else most_common_crime[:12] + "..."
        )

    with col5:
        unique_locations = filtered_df['LOCATION DESCRIPTION'].nunique()
        st.metric(
            label="📍 Location Types",
            value=f"{unique_locations:,}"
        )

    st.markdown("---")

    # Row 1: Time Series and Map
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📈 Crimes Over Time")

        if total_crimes > 0:
            if time_grouping == 'hour':
                # Hourly trend
                hourly_data = filtered_df.groupby('hour').size().reset_index(name='count')
                hourly_data['hour_label'] = hourly_data['hour'].apply(lambda x: f"{x:02d}:00")

                fig_time = px.line(
                    hourly_data,
                    x='hour_label',
                    y='count',
                    title=f'Crimes by Hour',
                    labels={'hour_label': 'Hour', 'count': 'Number of Crimes'},
                    markers=True
                )
                fig_time.update_traces(line_color='#002147', marker=dict(size=8, color='#FFBA00'))

            elif time_grouping == 'day_of_week':
                # Day of week trend
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_data = filtered_df.groupby('day_of_week').size().reset_index(name='count')
                day_data['day_of_week'] = pd.Categorical(day_data['day_of_week'], categories=day_order, ordered=True)
                day_data = day_data.sort_values('day_of_week')

                fig_time = px.bar(
                    day_data,
                    x='day_of_week',
                    y='count',
                    title=f'Crimes by Day of Week',
                    labels={'day_of_week': 'Day', 'count': 'Number of Crimes'},
                    color_discrete_sequence=['#002147']
                )

            else:  # date
                # Daily trend for the month
                daily_data = filtered_df.groupby('date').size().reset_index(name='count')

                fig_time = px.line(
                    daily_data,
                    x='date',
                    y='count',
                    title=f'Daily Crimes Trend',
                    labels={'date': 'Date', 'count': 'Number of Crimes'},
                    markers=True
                )
                fig_time.update_traces(line_color='#002147', marker=dict(size=8, color='#FFBA00'))

            fig_time.update_layout(
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No crime data available for the selected period.")

    with col2:
        st.subheader("🗺️ Crime Density Map")

        if total_crimes > 0:
            # Filter out rows with missing coordinates
            map_df = filtered_df.dropna(subset=['LATITUDE', 'LONGITUDE'])

            if len(map_df) > 0:
                # Sample if too many points (for performance)
                if len(map_df) > 5000:
                    map_df = map_df.sample(5000, random_state=42)

                fig_map = px.density_mapbox(
                    map_df,
                    lat='LATITUDE',
                    lon='LONGITUDE',
                    radius=8,
                    center=dict(lat=41.8781, lon=-87.6298),
                    zoom=10,
                    mapbox_style="carto-positron",
                    title=f"Crime Density Heatmap ({len(map_df):,} incidents)",
                    color_continuous_scale=["#FFBA00", "#FF6B00", "#002147"]
                )

                fig_map.update_layout(
                    height=400,
                    margin={"r": 0, "t": 30, "l": 0, "b": 0}
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No location data available for mapping.")
        else:
            st.info("No crime data available for mapping.")

    st.markdown("---")

    # Row 2: Crime Types Distribution and Location Analysis
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Crime Types Distribution")

        if total_crimes > 0:
            # Top 10 crime types
            crime_types = filtered_df['PRIMARY DESCRIPTION'].value_counts().head(10).reset_index()
            crime_types.columns = ['Crime Type', 'Count']

            fig_crimes = px.bar(
                crime_types,
                y='Crime Type',
                x='Count',
                orientation='h',
                title='Top 10 Crime Types',
                labels={'Crime Type': 'Crime Type', 'Count': 'Number of Incidents'},
                color='Count',
                color_continuous_scale=['#FFBA00', '#002147']
            )

            fig_crimes.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_crimes, use_container_width=True)
        else:
            st.info("No crime type data available.")

    with col2:
        st.subheader("📍 Top Crime Locations")

        if total_crimes > 0:
            # Top 10 location types
            location_types = filtered_df['LOCATION DESCRIPTION'].value_counts().head(10).reset_index()
            location_types.columns = ['Location', 'Count']

            fig_locations = px.pie(
                location_types,
                values='Count',
                names='Location',
                title='Top 10 Location Types',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )

            fig_locations.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='white', width=2))
            )

            fig_locations.update_layout(
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(size=10)
                )
            )
            st.plotly_chart(fig_locations, use_container_width=True)
        else:
            st.info("No location data available.")

    st.markdown("---")

    # Row 3: Arrest Analysis and Time Pattern
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("👮 Arrest Analysis by Crime Type")

        if total_crimes > 0:
            # Top crime types with arrest rates
            top_crimes = filtered_df['PRIMARY DESCRIPTION'].value_counts().head(8).index
            arrest_analysis = []

            for crime in top_crimes:
                crime_df = filtered_df[filtered_df['PRIMARY DESCRIPTION'] == crime]
                total = len(crime_df)
                arrested = len(crime_df[crime_df['ARREST'] == 'Y'])
                arrest_analysis.append({
                    'Crime Type': crime,
                    'Total': total,
                    'Arrested': arrested,
                    'Arrest Rate': (arrested / total * 100) if total > 0 else 0
                })

            arrest_df = pd.DataFrame(arrest_analysis)

            fig_arrest = go.Figure()

            fig_arrest.add_trace(go.Bar(
                name='Total Crimes',
                y=arrest_df['Crime Type'],
                x=arrest_df['Total'],
                orientation='h',
                marker_color='#002147',
                text=arrest_df['Total'],
                textposition='auto'
            ))

            fig_arrest.add_trace(go.Bar(
                name='Arrests Made',
                y=arrest_df['Crime Type'],
                x=arrest_df['Arrested'],
                orientation='h',
                marker_color='#FFBA00',
                text=arrest_df['Arrested'],
                textposition='auto'
            ))

            fig_arrest.update_layout(
                title='Crimes vs Arrests by Type',
                barmode='overlay',
                height=400,
                xaxis_title='Count',
                yaxis_title='Crime Type',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_arrest, use_container_width=True)
        else:
            st.info("No arrest data available.")

    with col2:
        st.subheader("⏰ Crime Pattern by Hour")

        if total_crimes > 0:
            # Hourly pattern for all data in the period
            hourly_pattern = filtered_df.groupby('hour').size().reset_index(name='count')
            hourly_pattern['hour_label'] = hourly_pattern['hour'].apply(lambda x: f"{x:02d}:00")

            # Categorize hours
            def categorize_hour(hour):
                if 6 <= hour < 12:
                    return 'Morning'
                elif 12 <= hour < 18:
                    return 'Afternoon'
                elif 18 <= hour < 24:
                    return 'Evening'
                else:
                    return 'Night'

            hourly_pattern['period'] = hourly_pattern['hour'].apply(categorize_hour)

            fig_hourly = px.bar(
                hourly_pattern,
                x='hour_label',
                y='count',
                title='24-Hour Crime Pattern',
                labels={'hour_label': 'Hour of Day', 'count': 'Number of Crimes'},
                color='period',
                color_discrete_map={
                    'Morning': '#FFBA00',
                    'Afternoon': '#FFD54F',
                    'Evening': '#003d7a',
                    'Night': '#002147'
                }
            )

            fig_hourly.update_layout(
                height=400,
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig_hourly, use_container_width=True)
        else:
            st.info("No hourly pattern data available.")

    # Data Summary Section
    st.markdown("---")
    st.subheader("📊 Data Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Dataset Overview**")
        st.write(f"- Total Records: {len(df):,}")
        st.write(f"- Date Range: {df['date'].min()} to {df['date'].max()}")
        st.write(f"- Filtered Records: {total_crimes:,}")

    with col2:
        st.markdown("**Crime Categories**")
        st.write(f"- Unique Crime Types: {df['PRIMARY DESCRIPTION'].nunique()}")
        st.write(f"- Unique Location Types: {df['LOCATION DESCRIPTION'].nunique()}")
        st.write(f"- Wards Covered: {df['WARD'].nunique()}")

    with col3:
        st.markdown("**Key Statistics**")
        overall_arrest_rate = (len(df[df['ARREST'] == 'Y']) / len(df) * 100)
        overall_domestic_rate = (len(df[df['DOMESTIC'] == 'Y']) / len(df) * 100)
        st.write(f"- Overall Arrest Rate: {overall_arrest_rate:.1f}%")
        st.write(f"- Overall Domestic Rate: {overall_domestic_rate:.1f}%")
        st.write(f"- Records with GPS: {df['LATITUDE'].notna().sum():,}")

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the Chicago Crimes dataset is available at the specified location.")
