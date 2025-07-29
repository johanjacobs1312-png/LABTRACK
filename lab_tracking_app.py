import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Lab Sample Tracker", layout="centered")

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = []

if "counter" not in st.session_state:
    st.session_state.counter = {}

# Title
st.title("🧪 Laboratory Sample Tracking System")

# Form for new sample entry
with st.form("sample_form"):
    st.subheader("Enter New Sample")

    date_received = st.date_input("Date Received", format="DD/MM/YYYY")
    sample_types = st.text_input("Sample Types (comma-separated, e.g., Water:2, Soil:3)")
    designated_lab = st.text_input("Designated Lab")

    query = st.radio("Is there a query?", ("N", "Y"))
    query_details = ""
    query_resolved = None
    if query == "Y":
        query_details = st.text_area("Query Details")
        query_resolved = st.date_input("Date Resolved")

    analyst_id = st.text_input("Analyst ID (if collected)")
    lab_collect_date = st.date_input("Lab Collect Date")
    report_date = st.date_input("Report Date")

    submitted = st.form_submit_button("Add Sample")

    if submitted:
        # Generate tracking number
        date_key = date_received.strftime("%d/%m")
        if date_key not in st.session_state.counter:
            st.session_state.counter[date_key] = 1
        else:
            st.session_state.counter[date_key] += 1

        tracking_number = f"{date_key.replace('/', '')}-{st.session_state.counter[date_key]:03d}"

        sample_record = {
            "Tracking Number": tracking_number,
            "Date Received": date_received.strftime("%d/%m"),
            "Sample Types": sample_types,
            "Designated Lab": designated_lab,
            "Query": query,
            "Query Details": query_details,
            "Query Resolved": query_resolved.strftime("%d/%m") if query_resolved else "",
            "Analyst ID": analyst_id,
            "Lab Collect Date": lab_collect_date.strftime("%d/%m"),
            "Report Date": report_date.strftime("%d/%m")
        }

        st.session_state.data.append(sample_record)
        st.success(f"Sample added with Tracking Number: {tracking_number}")

# Show data table
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.subheader("📋 Tracked Samples")
    st.dataframe(df, use_container_width=True)

    # Download button
    def to_excel(dataframe):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Samples')
        processed_data = output.getvalue()
        return processed_data

    st.download_button(
        label="📥 Export to Excel",
        data=to_excel(df),
        file_name="lab_samples.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
