import streamlit as st
import pandas as pd

# === Streamlit Page Setup ===
st.set_page_config(page_title="📊 Campaign Dashboard", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stDownloadButton > button {
        background-color: #2E8B57;
        color: white;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Company → Campaign → Process Dashboard")

# === File Upload ===
uploaded_file = st.file_uploader("📤 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    company_list = xls.sheet_names

    selected_company = st.selectbox("🏢 Select Company Sheet", company_list)

    # === Load & Clean Data ===
    df = xls.parse(selected_company)
    df.ffill(inplace=True)  # Fill merged cells
    df.dropna(how='all', inplace=True)

    # ✅ Standardize column names
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

        campaign_list = sorted(df["CAMPAIGN"].unique().tolist())
        campaign_list.insert(0, "All")

        col1, col2 = st.columns([2, 2])
        with col1:
            selected_campaign = st.selectbox("🎯 Select Campaign", campaign_list)

        # 🔄 Filter Processes by Campaign
        if selected_campaign == "All":
            filtered_campaign_df = df.copy()
            process_list = sorted(df["PROCESS"].dropna().unique().tolist())
        else:
            filtered_campaign_df = df[df["CAMPAIGN"] == selected_campaign]
            process_list = sorted(filtered_campaign_df["PROCESS"].dropna().unique().tolist())

        process_list.insert(0, "All")

        with col2:
            selected_process = st.selectbox("⚙ Select Process", process_list)

        # Final filtering
        filtered_df = filtered_campaign_df.copy()
        if selected_process != "All":
            filtered_df = filtered_df[filtered_df["PROCESS"] == selected_process]

        display_process = f"→ {selected_process}" if selected_process != "All" else "→ All Processes"
        st.markdown(f"### 📁 {selected_company} {display_process}")
        st.markdown("---")

        # Metrics
        metric1, metric2 = st.columns(2)
        with metric1:
            st.metric("Total Rows", filtered_df.shape[0])
        with metric2:
            st.metric("Total Columns", filtered_df.shape[1])

        # Leadset and Calling Mode columns
        leadset_cols = [col for col in filtered_df.columns if "LEADSET" in col]
        callingmode_cols = [col for col in filtered_df.columns if "CALLING" in col and "MODE" in col]
        important_cols = leadset_cols + callingmode_cols
        if important_cols:
            st.subheader("📌 Key Info: Leadsets & Calling Mode")
            st.dataframe(filtered_df[important_cols], use_container_width=True)

        # Full table
        st.subheader("📋 Full Data Table")
        st.dataframe(filtered_df, use_container_width=True)

        # Export to CSV with merged-like campaigns
        export_df = filtered_df.copy()
        if "CAMPAIGN" in export_df.columns:
            export_df["CAMPAIGN"] = export_df["CAMPAIGN"].mask(export_df["CAMPAIGN"].duplicated(), "")

        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, f"{selected_company}_export.csv", "text/csv")

        # Chart
        numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            st.subheader("📈 Quick Chart")
            selected_col = st.selectbox("📊 Choose numeric column to plot", numeric_cols)
            st.line_chart(filtered_df[selected_col])
        else:
            st.info("No numeric columns to visualize.")
    else:
        st.warning("🚫 'CAMPAIGN' and 'PROCESS' columns not found in this sheet.")
else:
    st.info("⬆ Please upload an Excel file to get started.")
