import streamlit as st
import pandas as pd
import time

# === PAGE CONFIG ===
st.set_page_config(page_title="SLASH Report", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stDownloadButton > button {
        background-color: #2E8B57;
        color: white;
    }
    h1, h2, h3 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.title("📊 SLASH Report")

# === Upload Excel File
uploaded_file = st.file_uploader("📤 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    company_list = xls.sheet_names
    selected_company = st.selectbox("🏢 Select Company Sheet", company_list)

    df = xls.parse(selected_company)
    df.ffill(inplace=True)
    df.dropna(how='all', inplace=True)
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    if "CAMPAIGN" in df.columns and "PROCESS" in df.columns:
        df["CAMPAIGN"] = df["CAMPAIGN"].astype(str)
        df["PROCESS"] = df["PROCESS"].astype(str)

        all_campaigns = sorted(df["CAMPAIGN"].unique().tolist())
        campaign_options = ["All"] + all_campaigns

        col1, col2 = st.columns(2)
        with col1:
            selected_campaigns = st.multiselect("🎯 Select Campaign(s)", campaign_options, default=["All"])

        if "All" in selected_campaigns or not selected_campaigns:
            campaign_filtered_df = df.copy()
        else:
            campaign_filtered_df = df[df["CAMPAIGN"].isin(selected_campaigns)]

        all_processes = sorted(campaign_filtered_df["PROCESS"].unique().tolist())
        process_options = ["All"] + all_processes

        with col2:
            selected_processes = st.multiselect("⚙ Select Process(es)", process_options, default=["All"])

        if "All" in selected_processes or not selected_processes:
            final_df = campaign_filtered_df.copy()
        else:
            final_df = campaign_filtered_df[campaign_filtered_df["PROCESS"].isin(selected_processes)]

        st.markdown(f"### 📁 {selected_company} → {', '.join(selected_processes) if 'All' not in selected_processes else 'All Processes'}")
        st.markdown("---")

        # === Metrics
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Rows", final_df.shape[0])
        with col4:
            st.metric("Columns", final_df.shape[1])

        # === Leadset & Calling Mode
        leadset_cols = [col for col in final_df.columns if "LEADSET" in col]
        callingmode_cols = [col for col in final_df.columns if "CALLING" in col and "MODE" in col]
        important_cols = leadset_cols + callingmode_cols
        if important_cols:
            st.subheader("📌 Leadsets & Calling Mode")
            st.dataframe(final_df[important_cols], use_container_width=True)

        # === Data Table
        st.subheader("📋 Full Data Table")
        st.dataframe(final_df, use_container_width=True)

        # === CSV Export
        export_df = final_df.copy()
        export_df["CAMPAIGN"] = export_df["CAMPAIGN"].mask(export_df["CAMPAIGN"].duplicated(), "")
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, f"{selected_company}_export.csv", "text/csv")

        # === Chart
        numeric_cols = final_df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            st.subheader("📈 Quick Chart")
            selected_col = st.selectbox("📊 Choose numeric column to plot", numeric_cols)
            st.line_chart(final_df[selected_col])
        else:
            st.info("No numeric columns to visualize.")
    else:
        st.warning("🚫 'CAMPAIGN' and 'PROCESS' columns not found in this sheet.")
else:
    st.info("⬆ Please upload an Excel file to get started.")
