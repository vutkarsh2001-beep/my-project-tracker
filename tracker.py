import streamlit as st
import pandas as pd
import datetime
import os

# Set page config to wide mode for the heavy Gantt matrix view
st.set_page_config(page_title="MS Planner Clone", layout="wide")

DATA_FILE = "planner_data.csv"

# --- 1. DATA STORAGE SETUP ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Plan Start"] = pd.to_datetime(df["Plan Start"]).dt.date
        df["Plan End"] = pd.to_datetime(df["Plan End"]).dt.date
        df["Ach Start"] = pd.to_datetime(df["Ach Start"]).dt.date.fillna(datetime.date.today())
        df["Ach End"] = pd.to_datetime(df["Ach End"]).dt.date.fillna(datetime.date.today())
        return df.to_dict(orient="records")
    else:
        # Default starter tasks with the new columns
        return [
            {
                "Project": "Alpha Launch", "Bucket": "Design", "Task": "Wireframe Layout", 
                "Status": "Completed", "Priority": "Important",
                "Plan Start": datetime.date(2026, 4, 15), "Plan End": datetime.date(2026, 6, 20),
                "Ach Start": datetime.date(2026, 4, 15), "Ach End": datetime.date(2026, 6, 18)
            },
            {
                "Project": "Alpha Launch", "Bucket": "Development", "Task": "Database API Setup", 
                "Status": "In Progress", "Priority": "Medium",
                "Plan Start": datetime.date(2026, 7, 1), "Plan End": datetime.date(2026, 11, 30),
                "Ach Start": datetime.date(2026, 7, 5), "Ach End": datetime.date(2026, 9, 27)
            }
        ]

def save_data(tasks_list):
    df = pd.DataFrame(tasks_list)
    df.to_csv(DATA_FILE, index=False)

if "planner_tasks" not in st.session_state:
    st.session_state.planner_tasks = load_data()

df = pd.DataFrame(st.session_state.planner_tasks)

# --- 2. GLOBAL SIDEBAR (ADD NEW TASK) ---
st.sidebar.header("➕ Create New Task")
sb_project = st.sidebar.text_input("Project Name", "Alpha Launch")
sb_bucket = st.sidebar.selectbox("Bucket", ["To Do", "Design", "Development", "Testing", "Deployment"])
sb_task = st.sidebar.text_input("Task Name")
sb_priority = st.sidebar.selectbox("Priority", ["Urgent", "Important", "Medium", "Low"])
sb_status = st.sidebar.selectbox("Status", ["Not Started", "In Progress", "Completed"])

col_p1, col_p2 = st.sidebar.columns(2)
sb_p_start = col_p1.date_input("Plan Start", datetime.date(2026, 4, 1))
sb_p_end = col_p2.date_input("Plan End", datetime.date(2026, 8, 1))

col_a1, col_a2 = st.sidebar.columns(2)
sb_a_start = col_a1.date_input("Achieved Start", datetime.date(2026, 4, 1))
sb_a_end = col_a2.date_input("Achieved End", datetime.date(2026, 4, 1))

if st.sidebar.button("Add Task to Planner"):
    if sb_task.strip() == "":
        st.sidebar.error("Task Name cannot be blank!")
    else:
        st.session_state.planner_tasks.append({
            "Project": sb_project, "Bucket": sb_bucket, "Task": sb_task,
            "Status": sb_status, "Priority": sb_priority,
            "Plan Start": sb_p_start, "Plan End": sb_p_end,
            "Ach Start": sb_a_start, "Ach End": sb_a_end
        })
        save_data(st.session_state.planner_tasks)
        st.success("Task Added!")
        st.rerun()

# --- 3. TOP NAVIGATION TABS ---
st.title("📋 Microsoft Planner Workspace")
view_tab1, view_tab2, view_tab3 = st.tabs(["📊 Kanban Board", "📝 List View", "📅 Advanced Gantt Chart"])

# --- TAB 1: KANBAN BOARD VIEW ---
with view_tab1:
    if df.empty:
        st.info("No tasks available.")
    else:
        buckets = ["To Do", "Design", "Development", "Testing", "Deployment"]
        kb_cols = st.columns(len(buckets))
        
        for idx, b_name in enumerate(buckets):
            with kb_cols[idx]:
                st.markdown(f"### {b_name}")
                st.markdown("---")
                b_tasks = df[df["Bucket"] == b_name]
                
                if b_tasks.empty:
                    st.caption("No tasks in this bucket")
                
                for _, row in b_tasks.iterrows():
                    # Render task card styled box
                    with st.container(border=True):
                        st.markdown(f"**{row['Task']}**")
                        st.caption(f"Project: {row['Project']} | ⚖️ {row['Priority']}")
                        
                        # In-card instant edit parameters
                        new_status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"], 
                                                  index=["Not Started", "In Progress", "Completed"].index(row["Status"]),
                                                  key=f"kb_stat_{row['Task']}")
                        
                        if new_status != row["Status"]:
                            for t in st.session_state.planner_tasks:
                                if t["Task"] == row["Task"]:
                                    t["Status"] = new_status
                            save_data(st.session_state.planner_tasks)
                            st.rerun()

# --- TAB 2: LIST VIEW ---
with view_tab2:
    st.subheader("📝 Complete Task Ledger")
    edited_ledger = st.data_editor(df, use_container_width=True, hide_index=True)
    if st.button("Save Grid Updates"):
        st.session_state.planner_tasks = edited_ledger.to_dict(orient="records")
        save_data(st.session_state.planner_tasks)
        st.success("Changes saved!")
        st.rerun()

# --- TAB 3: ADVANCED GANTT CHART (Apr-26 to Mar-31) ---
with view_tab3:
    st.subheader("📅 Comprehensive Timeline Matrix")
    st.markdown("*Rows tracking: **P** = Plan Horizon (Blue) | **A** = Achievement Window (Green)*")

    # Generate complete list of months from Apr 2026 to Mar 2031
    timeline_months = []
    start_year, start_month = 2026, 4
    end_year, end_month = 2031, 3
    
    curr_y, curr_m = start_year, start_month
    while (curr_y < end_year) or (curr_y == end_year and curr_m <= end_month):
        month_date = datetime.date(curr_y, curr_m, 1)
        timeline_months.append((curr_y, curr_m, month_date.strftime("%b-%y")))
        curr_m += 1
        if curr_m > 12:
            curr_m = 1
            curr_y += 1

    if df.empty:
        st.info("Add items to view timeline grid layout.")
    else:
        # Create columns configuration for the custom Gantt table headers
        header_cols = st.columns([1.5, 1.5, 2] + [0.5] * len(timeline_months))
        header_cols[0].markdown("**Project**")
        header_cols[1].markdown("**Bucket**")
        header_cols[2].markdown("**Task**")
        
        for m_idx, (_, _, m_label) in enumerate(timeline_months):
            header_cols[3 + m_idx].markdown(f"<p style='font-size:10px; font-weight:bold; text-align:center;'>{m_label}</p>", unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:4px 0;' />", unsafe_allow_html=True)

        # Plot rows for every unique task entry item
        for _, row in df.iterrows():
            r_cols_p = st.columns([1.5, 1.5, 2] + [0.5] * len(timeline_months))
            r_cols_a = st.columns([1.5, 1.5, 2] + [0.5] * len(timeline_months))
            
            # Left fixed descriptive columns
            r_cols_p.markdown(f"**{row['Project']}**")
            r_cols_p.markdown(row['Bucket'])
            r_cols_p.markdown(f"{row['Task']} `[P]`")
            
            r_cols_a.markdown("<p style='color:gray; font-size:12px; margin:0;'>↳ Achievement `[A]`</p>", unsafe_allow_html=True)
            
            # Check overlap status for each date cell against timeline ranges
            for m_idx, (y, m, _) in enumerate(timeline_months):
                cell_start = datetime.date(y, m, 1)
                if m == 12:
                    cell_end = datetime.date(y + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    cell_end = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
                
                has_plan = not (row["Plan End"] < cell_start or row["Plan Start"] > cell_end)
                has_ach = not (row["Ach End"] < cell_start or row["Ach Start"] > cell_end)
                
                if has_plan:
                    r_cols_p[3 + m_idx].markdown("<div style='background-color:#1f77b4; height:20px; border-radius:2px;'></div>", unsafe_allow_html=True)
                if has_ach:
                    r_cols_a[3 + m_idx].markdown("<div style='background-color:#2ca02c; height:20px; border-radius:2px;'></div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin:2px 0; border-top:1px dashed #444;' />", unsafe_allow_html=True)
