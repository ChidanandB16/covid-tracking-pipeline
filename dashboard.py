import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="COVID Tracking Dashboard",
    page_icon="🦠",
    layout="wide"
)

st.title("🦠 COVID-19 Tracking Dashboard")
st.caption("Cloud-based COVID data pipeline using Python, Pandas and AWS S3")

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/covid_processed.csv")
    df["Day"] = pd.to_datetime(df["Day"])
    return df

df = load_data()

# Sidebar
st.sidebar.header("Filters")

countries = sorted(df["Entity"].dropna().unique())

country = st.sidebar.selectbox(
    "Select Country",
    countries,
    index=countries.index("India") if "India" in countries else 0
)

country_df = df[df["Entity"] == country].copy()

# Metrics
latest_date = country_df["Day"].max()
latest_cases = country_df.loc[
    country_df["Day"] == latest_date, "Weekly cases"
].sum()

total_cases = country_df["Weekly cases"].sum()
peak_cases = country_df["Weekly cases"].max()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Country", country)
col2.metric("Latest Weekly Cases", f"{latest_cases:,.0f}")
col3.metric("Total Reported Cases", f"{total_cases:,.0f}")
col4.metric("Peak Weekly Cases", f"{peak_cases:,.0f}")

st.divider()

# Trend chart
st.subheader(f"📈 Weekly COVID Cases — {country}")

fig = px.line(
    country_df,
    x="Day",
    y="Weekly cases",
    markers=True,
    labels={
        "Day": "Date",
        "Weekly cases": "Weekly Cases"
    }
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Weekly Cases",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Top countries
st.subheader("🌍 Countries by Total Weekly Cases")

top_countries = (
    df.groupby("Entity")["Weekly cases"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.bar(
    top_countries,
    x="Weekly cases",
    y="Entity",
    orientation="h",
    labels={
        "Weekly cases": "Total Weekly Cases",
        "Entity": "Country"
    }
)

fig2.update_layout(yaxis={"categoryorder": "total ascending"})

st.plotly_chart(fig2, use_container_width=True)

# Data preview
with st.expander("🔍 View Processed Data"):
    st.dataframe(
        country_df.sort_values("Day", ascending=False),
        use_container_width=True
    )