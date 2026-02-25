import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="Skylark Executive BI",
    layout="wide"
)

# ===============================
# CUSTOM STYLING
# ===============================

st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight:600;
}
.metric-box {
    background-color: #111827;
    padding: 20px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="big-font">🚀 Skylark Drones Executive BI Dashboard</p>',
    unsafe_allow_html=True
)

API_URL = "https://skylark-bi-agent-ozh9.onrender.com"

# ===============================
# FETCH DATA
# ===============================

@st.cache_data
def fetch_deals():
    response = requests.get(f"{API_URL}/deals")
    return response.json()

@st.cache_data
def fetch_leadership():
    response = requests.get(f"{API_URL}/leadership-update")
    return response.json()

deals_data = fetch_deals()
leadership_data = fetch_leadership()

if not deals_data:
    st.error("Backend not running. Please start FastAPI server.")
    st.stop()

# ===============================
# EXECUTIVE SNAPSHOT
# ===============================

st.subheader("📊 Executive Snapshot")

col1, col2, col3 = st.columns(3)

total_pipeline = deals_data["total_pipeline"]
top_sector = max(
    deals_data["pipeline_by_sector"],
    key=deals_data["pipeline_by_sector"].get
)

col1.metric(
    "Total Pipeline",
    f"₹ {total_pipeline:,.2f}"
)

col2.metric(
    "Top Revenue Sector",
    top_sector
)

col3.metric(
    "Number of Active Sectors",
    len(deals_data["pipeline_by_sector"])
)

st.divider()

# ===============================
# SECTOR FILTER
# ===============================

st.subheader("🔎 Filter by Sector")

selected_sector = st.selectbox(
    "Select Sector",
    ["All"] + list(deals_data["pipeline_by_sector"].keys())
)

if selected_sector != "All":
    st.metric(
        f"Pipeline for {selected_sector}",
        f"₹ {deals_data['pipeline_by_sector'][selected_sector]:,.2f}"
    )

st.divider()

# ===============================
# PIPELINE BY SECTOR
# ===============================

st.subheader("🏭 Pipeline by Sector")

sector_df = pd.DataFrame(
    deals_data["pipeline_by_sector"].items(),
    columns=["Sector", "Pipeline Value"]
)

fig_sector = px.bar(
    sector_df,
    x="Sector",
    y="Pipeline Value",
    color="Pipeline Value",
    height=500,
    title="Revenue Distribution by Sector"
)

st.plotly_chart(fig_sector, use_container_width=True)

# ===============================
# PIPELINE BY STAGE
# ===============================

st.subheader("📈 Pipeline by Deal Stage")

stage_df = pd.DataFrame(
    deals_data["pipeline_by_stage"].items(),
    columns=["Stage", "Pipeline Value"]
)

fig_stage = px.pie(
    stage_df,
    names="Stage",
    values="Pipeline Value",
    hole=0.5,
    title="Pipeline Distribution by Stage"
)

st.plotly_chart(fig_stage, use_container_width=True)

st.divider()

# ===============================
# AI QUERY SECTION
# ===============================

st.subheader("💬 Ask Business Question")

question = st.text_input("Type your question here")

if st.button("Ask"):
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question}
    )

    answer = response.json()["answer"]

    # If answer is dictionary → show formatted table
    if isinstance(answer, dict):
        df_answer = pd.DataFrame(
            answer.items(),
            columns=["Category", "Value"]
        )
        df_answer["Value"] = df_answer["Value"].apply(
            lambda x: f"₹ {x:,.2f}"
        )
        st.dataframe(df_answer, use_container_width=True)

    else:
        st.success(answer)