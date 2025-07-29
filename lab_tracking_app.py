import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Lab Sample Tracker", layout="centered")

if "data" not in st.session_state:
    st.session_state.data = []

if "counter" not in st.session_state:
    st.session_state.counter = {}

def generate_tracking_number(date_received):
    date_key = date_received.strftime("%d/%m")
    if date_key not in st.session_state.counter:
        st.session_state.counter[date_key] = 1
    else:
        st.session_state.counter[date_key] += 1
    return f"{date_received.strftime('%d%m')}-{st.session_state.counter[date_key]:03d}"

SAMPLE_TYPES = ["Swabs", "Water", "Plates", "Food", "Bulk", "Filters"]
LAB_OPTIONS = ["Micro", "Chem", "Mol"]

st.title("🧪 Laboratory Sample Tracking System")

with st.form("sample_form"):
    st.subheader("Enter New Sample")

    date_received = st.date_input("Date Received", format="DD/MM/YYYY")
    client_details = st.text_input("Client Details")
    tracking_number = generate_tracking_number(date_received)
    st.markdown(f"**Tracking Number:** {tracking_number}")

    st.markdown("### Sample Types and Amounts")
    sample_amounts = {}
    for sample in SAMPLE_TYPES:
        amount = st.number_input(f"{sample} amount", min_value=0, step=1, key=f"amt_{sample}")
        sample_amounts[sample] = amount

    designated_labs = st.multiselect("Designated Lab(s)", LAB_OPTIONS)

    query = st.radio("Is there a query?", ("N", "Y"))
    query_details = ""
    query_resolved = None
    if query == "Y":
        query_details = st.text_area("Query Details")
        query_resolved = st.date_input("Query Resolved Date")

    submitted = st.form_submit_button("Save Sample")

    if submitted:
        filtered_samples = {k: v for k, v in sample_amounts.items() if v > 0}
        record = {
            "Tracking Number": tracking_number,
            "Date Received": date_received.strftime("%d/%m"),
            "Client Details": client_details,
            "Sample Types": ", ".join([f"{k}: {v}" for k, v in filtered_samples.items()]) if filtered_samples else "",
            "Designated Labs": ", ".join(designated_labs),
            "Query": query,
            "Query Details": query_details if query == "Y" else "",
            "Query Resolved": query_resolved.strftime("%d/%m") if (query == "Y" and query_resolved) else "",
            "Analyst ID": "",
            "Date Collected": ""
        }
        st.session_state.data.append(record)
        st.success(f"Sample saved with Tracking Number: {tracking_number}")

if st.session_state.data:
    st.subheader("📋 Tracked Samples")
    df = pd.DataFrame(st.session_state.data)

    for i in range(len(df)):
        with st.expander(f"Lab Collect for {df.at[i, 'Tracking Number']}"):
            analyst_id = st.text_input(f"Analyst ID", value=df.at[i, "Analyst ID"], key=f"analyst_{i}")
            try:
                date_collected_val = datetime.strptime(df.at[i, "Date Collected"], "%d/%m") if df.at[i, "Date Collected"] else datetime.today()
            except:
                date_collected_val = datetime.today()
            date_collected = st.date_input("Date Collected", value=date_collected_val, key=f"date_collected_{i}")

            df.at[i, "Analyst ID"] = analyst_id
            df.at[i, "Date Collected"] = date_collected.strftime("%d/%m")

    st.session_state.data = df.to_dict('records')
    st.dataframe(df, use_container_width=True)

    def to_excel(df):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Samples")
        return output.getvalue()

    st.download_button(
        label="📥 Export Data to Excel",
        data=to_excel(df),
        file_name="lab_samples.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )