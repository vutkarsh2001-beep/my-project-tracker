import streamlit as st
import pandas as pd
import datetime
import os

# Name of our local file database
DATA_FILE = "tasks.csv"

# --- FUNCTION: LOAD DATA ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Convert text dates back into proper date objects
        df["Start"] = pd.to_datetime(df["Start"]).dt.date
        df["End"] = pd.to_datetime(df["End"]).dt.date
        return df.to_dict(orient="records")
    else:
        # Default starter tasks if file doesn't exist yet
        return [
            {"Bucket": "Design", "Task": "Create Wireframes", "Status": "Completed", "Start": datetime.date(2026, 9, 20), "End": datetime.date(2026, 9, 25)},
            {"Bucket": "Development", "Task": "Setup Streamlit App", "Status": "In Progress", "Start": datetime.date(2026, 9, 26), "End": datetime.date(2026, 10, 5)}
        ]

# --- FUNCTION: SAVE DATA ---
def save_data(tasks_list):
    df = pd.DataFrame(tasks_list)
    df.to_csv(DATA_FILE, index=False)

# --- 1. SET UP PAGE ---
st.set_page_config(page_title="Project Tracker", layout="wide")
st.title("📂 Permanent Project Progress Tracker")

# Initialize and load data permanently from file
if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()

df = pd.DataFrame(st.session_state.tasks)

# --- 2. SIDEBAR INTERFACE ---
st.sidebar.header("✨ App Controls")

# FORM A: ADD TASK
with st.sidebar.expander("➕ Add New Task", expanded=True):
    new_bucket = st.selectbox("Select Bucket", ["Design", "Development", "Testing", "Deployment", "Marketing"])
    new_task = st.text_input("Task Name", placeholder="e.g., Design database schema")
    new_status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
    new_start = st.date_input("Start Date", datetime.date.today())
    new_end = st.date_input("Target End Date", datetime.date.today() + datetime.timedelta(days=7))

    if st.button("Add Task"):
        if new_task.strip() == "":
            st.error("Please enter a task name!")
        elif new_end < new_start:
            st.error("End Date cannot be before Start Date.")
        else:
            st.session_state.tasks.append({
                "Bucket": new_bucket,
                "Task": new_task,
                "Status": new_status,
                "Start": new_start,
                "End": new_end
            })
            save_data(st.session_state.tasks) # Write to disk immediately
            st.rerun()

# FORM B: UPDATE TASK
with st.sidebar.expander("✏️ Update Progress", expanded=True):
    if not df.empty:
        task_list = df["Task"].tolist()
        selected_task_name = st.selectbox("Choose Task to Update", task_list)
        task_row = df[df["Task"] == selected_task_name].iloc[0]
        
        updated_status = st.selectbox("Current Status", ["Not Started", "In Progress", "Completed"], index=["Not Started", "In Progress", "Completed"].index(task_row["Status"]))
        updated_end = st.date_input("Revise Target End Date", task_row["End"])
        
        if st.button("Save Update"):
            for task in st.session_state.tasks:
                if task["Task"] == selected_task_name:
                    task["Status"] = updated_status
                    task["End"] = updated_end
            save_data(st.session_state.tasks) # Write to disk immediately
            st.success("Progress Saved!")
            st.rerun()
    else:
        st.write("No tasks available to update.")

# --- 3. METRICS ---
st.subheader("📊 Project Dashboard Metrics")
col1, col2, col3, col4 = st.columns(4)
total_tasks = len(df)
completed_tasks = len(df[df["Status"] == "Completed"]) if total_tasks > 0 else 0
in_progress = len(df[df["Status"] == "In Progress"]) if total_tasks > 0 else 0
progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

with col1: st.metric("Total Tasks", total_tasks)
with col2: st.metric("Completed ✅", completed_tasks)
with col3: st.metric("In Progress ⏳", in_progress)
with col4: st.metric("Project Progress", f"{progress_percent}%")
st.progress(progress_percent / 100)
st.markdown("---")

# --- 4. GANTT CHART TIMELINE ---
st.subheader("📅 Project Gantt Chart (Timeline)")
if not df.empty:
    df_sorted = df.sort_values(by="Start")
    min_date = df_sorted["Start"].min()
    max_date = df_sorted["End"].max()
    total_days = (max_date - min_date).days + 1
    if total_days <= 0: total_days = 1

    for index, row in df_sorted.iterrows():
        task_days = (row["End"] - row["Start"]).days + 1
        start_offset = (row["Start"] - min_date).days
        left_pct = (start_offset / total_days) * 100
        width_pct = (task_days / total_days) * 100
        color = "#2efc0f" if row["Status"] == "Completed" else ("#ffaa00" if row["Status"] == "In Progress" else "#ff4b4b")
        
        st.markdown(f"**[{row['Bucket']}]** {row['Task']} *({row['Start'].strftime('%b %d')} to {row['End'].strftime('%b %d')})*")
        st.markdown(
            f'''
            <div style="background-color: #333; width: 100%; border-radius: 5px; margin-bottom: 12px; padding: 2px;">
                <div style="margin-left: {left_pct}%; width: {width_pct}%; background-color: {color}; color: black; font-weight: bold; padding: 4px 8px; border-radius: 4px; font-size: 12px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {row['Status']}
                </div>
            </div>
            ''', unsafe_allow_html=True
        )
else:
    st.info("No tasks to display yet.")

st.markdown("---")
st.subheader("📋 Active Task Overview")
st.dataframe(df[["Bucket", "Task", "Status", "Start", "End"]], use_container_width=True, hide_index=True)
