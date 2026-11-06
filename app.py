
import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="MineOps | Operations Intelligence",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Industrial Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #101820;
        color: #E8EDF2;
    }

    [data-testid="stSidebar"] {
        background-color: #172631;
        border-right: 1px solid #344754;
    }

    [data-testid="stMetric"] {
        background: #1B2B37;
        border: 1px solid #344754;
        padding: 18px 20px;
        border-radius: 10px;
    }

    [data-testid="stMetricLabel"] {
        color: #AAB8C3;
        font-size: 13px;
    }

    [data-testid="stMetricValue"] {
        color: #F4F6F8;
        font-size: 27px;
        font-weight: 700;
    }

    .main-header {
        background: linear-gradient(110deg, #1B2B37, #243B49);
        padding: 25px 28px;
        border-radius: 12px;
        border-left: 5px solid #E5A23D;
        margin-bottom: 22px;
    }

    .main-header h1 {
        color: #FFFFFF;
        font-size: 29px;
        font-weight: 800;
        margin: 0;
    }

    .main-header p {
        color: #B8C7D1;
        margin: 7px 0 0 0;
        font-size: 13px;
    }

    .section-heading {
        color: #F0B44D;
        font-size: 18px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 12px;
    }

    .status-strip {
        background: #1B2B37;
        border: 1px solid #344754;
        border-radius: 8px;
        padding: 12px 16px;
        color: #C7D2DA;
        font-size: 13px;
        margin-bottom: 18px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #344754;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #C7D2DA;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #F0B44D !important;
    }

    div.stButton > button {
        background-color: #D99A32;
        color: #101820;
        border: none;
        border-radius: 6px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background-color: #F0B44D;
        color: #101820;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Color Palette
COLORS = {
    "Dump Truck": "#E5A23D",
    "Excavator": "#4FA3D1",
    "Dozer": "#65B891",
    "Drilling Machine": "#A88BD5"
}

CHART_TEMPLATE = "plotly_dark"

# Load Dataset
@st.cache_data
def load_data():
    data = pd.read_csv("open_pit_mining_advanced_kpi_dataset.csv")
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    required_columns = [
        "Date", "Equipment_Type", "Equipment_ID", "Pit", "Shift",
        "Production_Tonnes", "Drilling_Meters", "Scheduled_Hours",
        "Operating_Hours", "Available_Hours", "Total_Downtime_Hours",
        "Breakdown_Hours", "Maintenance_Hours", "Fuel_Consumption_L",
        "Target_Production_Tonnes"
    ]

    missing_columns = [
        col for col in required_columns if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return data


try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load dataset: {error}")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("## ⛏️ MINEOPS")
    st.caption("OPERATIONS INTELLIGENCE PLATFORM")
    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Select Dashboard",
        [
            "Executive Overview",
            "Equipment Intelligence",
            "Drilling Operations",
            "Pit & Shift Analysis",
            "Operational Data"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### Operational Filters")

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    date_range = st.date_input(
        "Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    equipment_options = sorted(
        df["Equipment_Type"].dropna().unique().tolist()
    )

    selected_equipment = st.multiselect(
        "Equipment Type",
        equipment_options,
        default=equipment_options
    )

    pit_options = sorted(df["Pit"].dropna().unique().tolist())

    selected_pits = st.multiselect(
        "Mining Pit",
        pit_options,
        default=pit_options
    )

    shift_options = sorted(df["Shift"].dropna().unique().tolist())

    selected_shifts = st.multiselect(
        "Shift",
        shift_options,
        default=shift_options
    )

    st.divider()
    st.caption("MINEOPS | Mining Analytics System")
    st.caption("Data-driven HEMM performance monitoring")

# Apply Filters
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

filtered_df = df[
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date) &
    (df["Equipment_Type"].isin(selected_equipment)) &
    (df["Pit"].isin(selected_pits)) &
    (df["Shift"].isin(selected_shifts))
].copy()

if filtered_df.empty:
    st.warning("No operational records match the selected filters.")
    st.stop()

# Prepare Operational Data
material_df = filtered_df[
    filtered_df["Equipment_Type"] != "Drilling Machine"
].copy()

drilling_df = filtered_df[
    filtered_df["Equipment_Type"] == "Drilling Machine"
].copy()

scheduled_hours = filtered_df["Scheduled_Hours"].sum()
operating_hours = filtered_df["Operating_Hours"].sum()
available_hours = filtered_df["Available_Hours"].sum()
downtime_hours = filtered_df["Total_Downtime_Hours"].sum()

availability = (
    available_hours / scheduled_hours * 100
    if scheduled_hours > 0 else 0
)

utilization = (
    operating_hours / scheduled_hours * 100
    if scheduled_hours > 0 else 0
)

material_handled = material_df["Production_Tonnes"].sum()
fuel_consumption = filtered_df["Fuel_Consumption_L"].sum()

# Header
st.markdown("""
<div class="main-header">
    <h1>⛏️ MINEOPS | Operations Intelligence</h1>
    <p>OPEN-PIT MINE PRODUCTION & HEAVY EARTH MOVING MACHINERY ANALYTICS</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="status-strip">● ANALYTICS ACTIVE &nbsp; | &nbsp; '
    f'PERIOD: {start_date} — {end_date} &nbsp; | &nbsp; '
    f'RECORDS: {len(filtered_df):,} &nbsp; | &nbsp; '
    f'EQUIPMENT TYPES: {filtered_df["Equipment_Type"].nunique()}</div>',
    unsafe_allow_html=True
)

# Chart Layout Helper
def style_chart(fig, height=350):
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        paper_bgcolor="#101820",
        plot_bgcolor="#172631",
        font=dict(
            family="Inter",
            color="#DCE4EA",
            size=12
        ),
        title_font=dict(size=16, color="#F0B44D"),
        margin=dict(l=20, r=20, t=55, b=25),
        legend_title_text="",
        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor="#344754",
            zeroline=False
        )
    )
    return fig


# Executive Overview
if page == "Executive Overview":

    st.markdown(
        '<div class="section-heading">Fleet Performance Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Material Handled",
        f"{material_handled / 1000:,.1f} K tonnes"
    )

    c2.metric(
        "Fleet Availability",
        f"{availability:.1f}%"
    )

    c3.metric(
        "Fleet Utilization",
        f"{utilization:.1f}%"
    )

    c4.metric(
        "Total Downtime",
        f"{downtime_hours:,.1f} hrs"
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Operating Hours", f"{operating_hours:,.0f} hrs")
    c6.metric("Fuel Consumption", f"{fuel_consumption:,.0f} L")
    c7.metric("Equipment Records", f"{len(filtered_df):,}")
    c8.metric("Active Pits", f"{filtered_df['Pit'].nunique()}")

    st.markdown(
        '<div class="section-heading">Production & Fleet Trends</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:
        if not material_df.empty:
            daily_production = (
                material_df.groupby("Date", as_index=False)
                ["Production_Tonnes"].sum()
            )

            fig = px.area(
                daily_production,
                x="Date",
                y="Production_Tonnes",
                title="Daily Material Handled",
                color_discrete_sequence=["#E5A23D"]
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )
        else:
            st.info("No material-handling records for this selection.")

    with right:
        equipment_production = (
            material_df.groupby("Equipment_Type", as_index=False)
            ["Production_Tonnes"].sum()
        )

        fig = px.bar(
            equipment_production,
            x="Equipment_Type",
            y="Production_Tonnes",
            color="Equipment_Type",
            color_discrete_map=COLORS,
            title="Material Handled by Equipment",
            text_auto=".2s"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    st.markdown(
        '<div class="section-heading">Fleet Downtime Composition</div>',
        unsafe_allow_html=True
    )

    downtime_summary = pd.DataFrame({
        "Downtime Type": ["Breakdown", "Maintenance"],
        "Hours": [
            filtered_df["Breakdown_Hours"].sum(),
            filtered_df["Maintenance_Hours"].sum()
        ]
    })

    fig = px.pie(
        downtime_summary,
        names="Downtime Type",
        values="Hours",
        hole=0.58,
        color="Downtime Type",
        color_discrete_map={
            "Breakdown": "#D96C5F",
            "Maintenance": "#E5A23D"
        },
        title="Breakdown vs Maintenance"
    )

    fig.update_traces(
        textinfo="label+percent",
        textfont_size=12
    )

    st.plotly_chart(
        style_chart(fig, 320),
        use_container_width=True
    )

    st.caption(
        "Material handled represents equipment-reported tonnes. "
        "Excavator, dozer and truck estimates may overlap and should "
        "not be interpreted as unique mine production."
    )


# Equipment Intelligence
elif page == "Equipment Intelligence":

    st.markdown(
        '<div class="section-heading">HEMM Performance Monitoring</div>',
        unsafe_allow_html=True
    )

    equipment_df = filtered_df[
        filtered_df["Equipment_Type"] != "Drilling Machine"
    ]

    if equipment_df.empty:
        st.info("No material-handling equipment records available.")
    else:
        equipment_summary = (
            equipment_df.groupby("Equipment_Type", as_index=False)
            .agg(
                Material_Handled_Tonnes=("Production_Tonnes", "sum"),
                Operating_Hours=("Operating_Hours", "sum"),
                Scheduled_Hours=("Scheduled_Hours", "sum"),
                Available_Hours=("Available_Hours", "sum"),
                Breakdown_Hours=("Breakdown_Hours", "sum"),
                Maintenance_Hours=("Maintenance_Hours", "sum"),
                Fuel_Consumption_L=("Fuel_Consumption_L", "sum")
            )
        )

        equipment_summary["Availability_pct"] = (
            equipment_summary["Available_Hours"] /
            equipment_summary["Scheduled_Hours"] * 100
        )

        equipment_summary["Utilization_pct"] = (
            equipment_summary["Operating_Hours"] /
            equipment_summary["Scheduled_Hours"] * 100
        )

        equipment_summary["Productivity_TPH"] = (
            equipment_summary["Material_Handled_Tonnes"] /
            equipment_summary["Operating_Hours"].replace(0, pd.NA)
        )

        st.dataframe(
            equipment_summary.round(2),
            use_container_width=True,
            hide_index=True
        )

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                equipment_summary,
                x="Equipment_Type",
                y="Availability_pct",
                color="Equipment_Type",
                color_discrete_map=COLORS,
                title="Equipment Availability (%)",
                text_auto=".1f"
            )

            fig.update_layout(yaxis_title="Availability (%)")

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with right:
            fig = px.bar(
                equipment_summary,
                x="Equipment_Type",
                y="Utilization_pct",
                color="Equipment_Type",
                color_discrete_map=COLORS,
                title="Equipment Utilization (%)",
                text_auto=".1f"
            )

            fig.update_layout(yaxis_title="Utilization (%)")

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        downtime_equipment = (
            equipment_summary[
                [
                    "Equipment_Type",
                    "Breakdown_Hours",
                    "Maintenance_Hours"
                ]
            ]
            .melt(
                id_vars="Equipment_Type",
                var_name="Downtime_Type",
                value_name="Hours"
            )
        )

        fig = px.bar(
            downtime_equipment,
            x="Equipment_Type",
            y="Hours",
            color="Downtime_Type",
            barmode="stack",
            title="Downtime by Equipment",
            color_discrete_map={
                "Breakdown_Hours": "#D96C5F",
                "Maintenance_Hours": "#E5A23D"
            }
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

        st.markdown("### Equipment Productivity")

        productivity_df = equipment_summary.dropna(
            subset=["Productivity_TPH"]
        )

        fig = px.bar(
            productivity_df,
            x="Equipment_Type",
            y="Productivity_TPH",
            color="Equipment_Type",
            color_discrete_map=COLORS,
            title="Material Handled per Operating Hour",
            text_auto=".2f"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )


# Drilling Operations
elif page == "Drilling Operations":

    st.markdown(
        '<div class="section-heading">Drilling Performance Monitoring</div>',
        unsafe_allow_html=True
    )

    if drilling_df.empty:
        st.info(
            "No drilling machine records match the current filters. "
            "Select Drilling Machine in the equipment filter."
        )
    else:
        total_metres = drilling_df["Drilling_Meters"].sum()
        drilling_hours = drilling_df["Operating_Hours"].sum()

        drilling_rate = (
            total_metres / drilling_hours
            if drilling_hours > 0 else 0
        )

        d1, d2, d3 = st.columns(3)

        d1.metric("Total Drilling", f"{total_metres:,.0f} metres")
        d2.metric("Operating Hours", f"{drilling_hours:,.1f} hrs")
        d3.metric("Drilling Rate", f"{drilling_rate:.2f} m/hr")

        daily_drilling = (
            drilling_df.groupby("Date", as_index=False)
            ["Drilling_Meters"].sum()
        )

        fig = px.line(
            daily_drilling,
            x="Date",
            y="Drilling_Meters",
            markers=True,
            title="Daily Drilling Performance",
            color_discrete_sequence=["#A88BD5"]
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

        machine_summary = (
            drilling_df.groupby("Equipment_ID", as_index=False)
            .agg(
                Drilling_Meters=("Drilling_Meters", "sum"),
                Operating_Hours=("Operating_Hours", "sum")
            )
        )

        machine_summary["Drilling_Rate_M_Hr"] = (
            machine_summary["Drilling_Meters"] /
            machine_summary["Operating_Hours"].replace(0, pd.NA)
        )

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                machine_summary,
                x="Equipment_ID",
                y="Drilling_Meters",
                color_discrete_sequence=["#A88BD5"],
                title="Total Drilling by Machine",
                text_auto=".2s"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with right:
            fig = px.bar(
                machine_summary,
                x="Equipment_ID",
                y="Drilling_Rate_M_Hr",
                color_discrete_sequence=["#4FA3D1"],
                title="Drilling Rate by Machine",
                text_auto=".2f"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        st.dataframe(
            machine_summary.round(2),
            use_container_width=True,
            hide_index=True
        )


# Pit and Shift Analysis
elif page == "Pit & Shift Analysis":

    st.markdown(
        '<div class="section-heading">Production Distribution Analysis</div>',
        unsafe_allow_html=True
    )

    if material_df.empty:
        st.info("No material-handling records available.")
    else:
        left, right = st.columns(2)

        pit_summary = (
            material_df.groupby("Pit", as_index=False)
            ["Production_Tonnes"].sum()
        )

        shift_summary = (
            material_df.groupby("Shift", as_index=False)
            ["Production_Tonnes"].sum()
        )

        with left:
            fig = px.bar(
                pit_summary,
                x="Pit",
                y="Production_Tonnes",
                color="Pit",
                title="Material Handled by Pit",
                text_auto=".2s"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with right:
            fig = px.bar(
                shift_summary,
                x="Shift",
                y="Production_Tonnes",
                color="Shift",
                title="Material Handled by Shift",
                text_auto=".2s"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        st.markdown("### Pit-wise Equipment Distribution")

        pit_equipment = (
            material_df.groupby(
                ["Pit", "Equipment_Type"], as_index=False
            )["Production_Tonnes"].sum()
        )

        fig = px.bar(
            pit_equipment,
            x="Pit",
            y="Production_Tonnes",
            color="Equipment_Type",
            color_discrete_map=COLORS,
            barmode="group",
            title="Equipment Contribution Across Pits"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

        st.markdown("### Shift-wise Fleet Availability")

        shift_availability = (
            filtered_df.groupby("Shift", as_index=False)
            .agg(
                Available_Hours=("Available_Hours", "sum"),
                Scheduled_Hours=("Scheduled_Hours", "sum")
            )
        )

        shift_availability["Availability_pct"] = (
            shift_availability["Available_Hours"] /
            shift_availability["Scheduled_Hours"] * 100
        )

        fig = px.bar(
            shift_availability,
            x="Shift",
            y="Availability_pct",
            title="Fleet Availability by Shift",
            color_discrete_sequence=["#65B891"],
            text_auto=".1f"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )


# Operational Data
elif page == "Operational Data":

    st.markdown(
        '<div class="section-heading">Operational Records Explorer</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Review the filtered equipment-level operational records "
        "and export the selected data."
    )

    st.metric("Filtered Records", f"{len(filtered_df):,}")

    search_equipment = st.text_input(
        "Search Equipment ID",
        placeholder="Example: EQ_001"
    )

    display_df = filtered_df.copy()

    if search_equipment.strip():
        display_df = display_df[
            display_df["Equipment_ID"].astype(str).str.contains(
                search_equipment.strip(),
                case=False,
                na=False
            )
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=480
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Operational Data",
        data=csv_data,
        file_name="mining_operational_data.csv",
        mime="text/csv"
    )

# Footer
st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#82939F; font-size:12px;">
        MINEOPS | OPEN-PIT MINE PRODUCTION & HEMM OPERATIONS ANALYTICS
        <br>
        Mining Operations Intelligence Platform
    </div>
    """,
    unsafe_allow_html=True
)
