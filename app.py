import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="📊 SLash Report", layout="wide")

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

st.title("📊 Multi-Company Campaign & Process Dashboard")
start_time = time.time()

# === Usage Stats
if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0
if "company_views" not in st.session_state:
    st.session_state.company_views = 0
if "rows_viewed" not in st.session_state:
    st.session_state.rows_viewed = 0

# === Upload Excel File
uploaded_file = st.file_uploader("📤 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    st.session_state.upload_count += 1
    xls = pd.ExcelFile(uploaded_file)
    sheet_options = xls.sheet_names
    selected_sheets = st.multiselect("🏢 Select One or More Companies (Sheets)", sheet_options)

    for sheet in selected_sheets:
        st.markdown(f"---\n### 🏢 {sheet}")
        df = xls.parse(sheet)
        df.ffill(inplace=True)
        df.dropna(how='all', inplace=True)

        df.columns = (
            df.columns.str.strip()
            .str.upper()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        if "CAMPAIGN" in df.columns and "PROCESS" in df.columns:
            df["CAMPAIGN"] = df["CAMPAIGN"].astype(str)
            df["PROCESS"] = df["PROCESS"].astype(str)

            all_campaigns = sorted(df["CAMPAIGN"].unique().tolist())
            selected_campaigns = st.multiselect(f"🎯 Select Campaign(s) - {sheet}", ["All"] + all_campaigns, default="All", key=f"campaigns_{sheet}")

            if "All" in selected_campaigns:
                campaign_filtered_df = df.copy()
            else:
                campaign_filtered_df = df[df["CAMPAIGN"].isin(selected_campaigns)]

            all_processes = sorted(campaign_filtered_df["PROCESS"].unique().tolist())
            selected_processes = st.multiselect(f"⚙ Select Process(es) - {sheet}", ["All"] + all_processes, default="All", key=f"processes_{sheet}")

            if "All" in selected_processes:
                final_df = campaign_filtered_df.copy()
            else:
                final_df = campaign_filtered_df[campaign_filtered_df["PROCESS"].isin(selected_processes)]

            st.session_state.company_views += 1
            st.session_state.rows_viewed += final_df.shape[0]

            # === Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows", final_df.shape[0])
            with col2:
                st.metric("Columns", final_df.shape[1])

            # === Leadset & Calling Mode
            leadset_cols = [col for col in final_df.columns if "LEADSET" in col]
            callingmode_cols = [col for col in final_df.columns if "CALLING" in col and "MODE" in col]
            important_cols = leadset_cols + callingmode_cols
            if important_cols:
                st.subheader("📌 Leadsets & Calling Mode")
                st.dataframe(final_df[important_cols], use_container_width=True)

            # === Data Table
            st.subheader("📋 Full Table")
            st.dataframe(final_df, use_container_width=True)

            # === CSV Export
            export_df = final_df.copy()
            export_df["CAMPAIGN"] = export_df["CAMPAIGN"].mask(export_df["CAMPAIGN"].duplicated(), "")
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, f"{sheet}export.csv", "text/csv", key=f"download{sheet}")

            # === Chart
            numeric_cols = final_df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                st.subheader("📈 Quick Chart")
                selected_col = st.selectbox("Choose numeric column", numeric_cols, key=f"chart_{sheet}")
                st.line_chart(final_df[selected_col])
            else:
                st.info("No numeric columns to visualize.")
        else:
            st.warning(f"❌ 'CAMPAIGN' and 'PROCESS' columns not found in {sheet}")

# === Usage Summary
st.markdown("---")
st.subheader("📊 Usage Summary")

elapsed_time = int(time.time() - start_time)
minutes = elapsed_time // 60
seconds = elapsed_time % 60

st.write(f"🕒 Time on page: *{minutes}m {seconds}s*")
st.write(f"📁 Files uploaded: *{st.session_state.upload_count}*")
st.write(f"🏢 Companies viewed: *{st.session_state.company_views}*")
st.write(f"📊 Total rows viewed: *{st.session_state.rows_viewed}*")
