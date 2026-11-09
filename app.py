import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="India AI Policy Tracker",
    layout="wide"
)

st.title("India AI Policy Tracker")
st.caption(
    "Tracking government AI policy and initiatives across "
    "Karnataka, Tamil Nadu and Maharashtra | 2024–2026"
)

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/ai_policy_final.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Final dataset not found. Run prepare_final_data.py first.")
    st.stop()

if df.empty:
    st.warning("No records available in the final dataset.")
    st.stop()

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

st.sidebar.header("Filter records")

if "state" in df.columns:
    states = sorted(df["state"].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "Select states",
        states,
        default=states
    )
    df = df[df["state"].isin(selected_states)]

if "category" in df.columns:
    categories = sorted(df["category"].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Select categories",
        categories,
        default=categories
    )
    df = df[df["category"].isin(selected_categories)]

if "status" in df.columns:
    statuses = sorted(df["status"].dropna().unique())
    selected_statuses = st.sidebar.multiselect(
        "Select status",
        statuses,
        default=statuses
    )
    df = df[df["status"].isin(selected_statuses)]

st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Verified records", len(df))
col2.metric("States covered", df["state"].nunique() if "state" in df.columns else 0)
col3.metric("Categories covered", df["category"].nunique() if "category" in df.columns else 0)

st.divider()

# Charts
st.subheader("State-wise AI activity")

if "state" in df.columns and not df.empty:
    state_counts = df["state"].value_counts()
    st.bar_chart(state_counts)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Category-wise distribution")
    if "category" in df.columns and not df.empty:
        st.bar_chart(df["category"].value_counts())

with col2:
    st.subheader("Status distribution")
    if "status" in df.columns and not df.empty:
        st.bar_chart(df["status"].value_counts())

st.divider()

# Records table
st.subheader("AI Policy and Initiative Records")

search = st.text_input("Search records by title or description")

if search:
    searchable = df.astype(str).apply(
        lambda col: col.str.contains(search, case=False, na=False)
    ).any(axis=1)
    display_df = df[searchable]
else:
    display_df = df

if "source_url" in display_df.columns:
    display_df = display_df.copy()
    display_df["source_link"] = display_df["source_url"].apply(
        lambda url: f"[Open source]({url})" if pd.notna(url) else ""
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "source_link": st.column_config.LinkColumn("Source")
    }
)


st.caption(
    "Note: This tracker only includes 3 states and is not an exhaustive "
)