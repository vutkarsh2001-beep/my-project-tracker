import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. SET UP STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Advanced Project Matrix Planner", layout="wide")

# Inject explicit custom style sheets to achieve a frozen left pane and scrollable calendar track
st.markdown('''
<style>
    .gantt-wrapper {
        display: flex;
        flex-direction: column;
        border: 1px solid #333;
        border-radius: 6px;
        background-color: #111;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .gantt-row {
        display: flex;
        border-bottom: 1px solid #222;
        align-items: stretch;
    }
    .gantt-header-row {
        background-color: #1a1a1a;
        font-weight: bold;
        border-bottom: 2px solid #444;
    }
    .fixed-pane {
        width: 550px;
        min-width: 550px;
        display: flex;
        background-color: #161616;
        z-index: 2;
        border-right: 3px solid #444;
    }
    .cell-category { width: 22%; padding: 8px 5px; font-size: 12px; color: #888; overflow: hidden; text-overflow: ellipsis; }
    .cell-project { width: 22%; padding: 8px 5px; font-size: 13px; font-weight: 600; }
    .cell-bucket  { width: 22%; padding: 8px 5px; font-size: 12px; color: #ccc; }
    .cell-task    { width: 24%; padding: 8px 5px; font-size: 12px; font-weight: bold; }
    .cell-priority{ width: 10%; padding: 8px 5px; font-size: 11px; text-align: center; }
    .scrollable-pane {
        display: flex;
        overflow-x: auto;
        flex-grow: 1;
        z-index: 1;
    }
    .month-column-block {
        min-width: 140px;
        width: 140px;
        display: flex;
        flex-direction: column;
        border-right: 1px solid #2a2a2a;
        align-items: center;
    }
    .month-header-title {
        font-size: 11px;
        padding: 4px 0;
        border-bottom: 1px solid #333;
        width: 100%;
        text-align: center;
        background-color: #222;
    }
    .weeks-sub-row {
        display: flex;
        width: 100%;
        justify-content: space-around;
        padding: 2px 0;
    }
    .week-head-number {
        font-size: 9px;
        color: #666;
        width: 25px;
        text-align: center;
    }
    .rectangle-track {
        display: flex;
        width: 100%;
        height: 100%;
        align-items: center;
        justify-content: space-around;
        padding: 6px 0;
    }
    .indicator-rect {
        width: 26px;
        height: 14px;
        border-radius: 2px;
        background-color: transparent;
        transition: transform 0.2s;
    }
    .indicator-rect:hover {
        transform: scale(1.2);
    }
    :target {
        background-color: #223322 !important;
        border: 2px solid #2ca02c !important;
    }
    .matrix-link {
        color: #1f77b4;
        text-decoration: none;
    }
    .matrix-link:hover {
        text-decoration: underline;
        color: #4da3ff;
    }
</style>
''', unsafe_allow_html=True)

DATA_FILE = "planner_matrix_data.csv"

# --- 2. PERSISTENT STORAGE MANAGEMENT ENGINE ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Plan Start"] = pd.to_datetime(df["Plan Start"]).dt.date
        df["Plan End"] = pd.to_datetime(df["Plan End"]).dt.date
        df["Actual End"] = pd.to_datetime(df["Actual End"]).dt.date
        return df.to_dict(orient="records")
    else:
        return [
            {
                "Category": "Digital Strategy", "Project": "Project-1", "Bucket": "Bucket-1", 
                "Task": "Task-1-Name", "Priority": "P1", "Is_Late": False,
                "Plan Start": datetime.date(2026, 4, 1), "Plan End": datetime.date(2026, 7, 15),
                "Actual End": datetime.date(2026, 7, 10)
            },
            {
                "Category": "Operations", "Project": "Project-2", "Bucket": "Bucket-2", 
                "Task": "Task-1-Name", "Priority": "P3", "Is_Late": True,
                "Plan Start": datetime.date(2027, 4, 1), "Plan End": datetime.date(2027, 10, 1),
                "Actual End": datetime.date(2027, 10, 15)
            }
        ]

def save_data(tasks_list):
    df = pd.DataFrame(tasks_list)
    df.to_csv(DATA_FILE, index=False)

# --- 3. DYNAMIC FY BLOCK ENGINE ---
def get_fy_base_year(d):
    return d.year if d.month >= 4 else d.year - 1

def generate_dynamic_fy_blocks(tasks_list):
    if not tasks_list:
        return ["26'27-27'28"]
    found_years = set()
    for task in tasks_list:
        for key in ["Plan Start", "Plan End", "Actual End"]:
            if key in task and isinstance(task[key], datetime.date):
                found_years.add(get_fy_base_year(task[key]))
            elif key in task and isinstance(task[key], str):
                try:
                    d = pd.to_datetime(task[key]).date()
                    found_years.add(get_fy_base_year(d))
                except:
                    pass
    if not found_years:
        return ["26'27-27'28"]
    unique_blocks = set()
    for y in found_years:
        start_y = y - (y % 2)
        next_y = start_y + 1
        label = f"{str(start_y)[2:]}'{str(start_y+1)[2:]}-{str(next_y)[2:]}'{str(next_y+1)[2:]}"
        unique_blocks.add(label)
    sorted_labels = sorted(list(unique_blocks))
    if "26'27-27'28" not in sorted_labels:
        sorted_labels.insert(0, "26'27-27'28")
    return sorted_labels

def parse_fy_block_dates(label):
    try:
        part = label.split("-")
        prefix_year_short = int(part[0].split("'")[0])
        full_start_year = 2000 + prefix_year_short
        start_date_bound = datetime.date(full_start_year, 4, 1)
        end_date_bound = datetime.date(full_start_year + 2, 3, 31)
        return start_date_bound, end_date_bound
    except:
        return datetime.date(2026, 4, 1), datetime.date(2028, 3, 31)

if "matrix_tasks" not in st.session_state:
    st.session_state.matrix_tasks = load_data()

df = pd.DataFrame(st.session_state.matrix_tasks)

# --- 4. FILTER HEADERS & LEGEND ---
st.title("📂 MS Planner Gantt Workspace")

header_col, legend_col = st.columns(2)
available_fy_options = generate_dynamic_fy_blocks(st.session_state.matrix_tasks)

with header_col:
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        filter_fy = st.selectbox("Financial Year Horizon", available_fy_options)
    with f_col2:
        filter_cat = st.selectbox("Category Grouping", ["All", "Digital Strategy", "Operations", "Study & Research", "Administrative"])
    with f_col3:
        filter_priority = st.selectbox("Task Priority View", ["All", "P1", "P2", "P3"])

with legend_col:
    st.markdown('''
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 6px; border: 1px solid #333; font-size: 11px; float: right; width: 100%;">
        <div style="font-weight: bold; margin-bottom: 6px; color:#aaa; text-transform: uppercase; font-size:10px;">Gantt Legend Indicator Map</div>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div style="display: flex; align-items: center;"><div style="width: 16px; height: 10px; background-color: #1f77b4; border-radius: 2px; margin-right: 6px;"></div><span>Planned Duration (On-Time)</span></div>
            <div style="display: flex; align-items: center;"><div style="width: 16px; height: 10px; background-color: #2ca02c; border-radius: 2px; margin-right: 6px;"></div><span>Late Target Milestone Breached</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

start_date, end_date = parse_fy_block_dates(filter_fy)
filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df["Plan Start"] <= end_date) & (filtered_df["Plan End"] >= start_date)
]

if filter_cat != "All":
    filtered_df = filtered_df[filtered_df["Category"] == filter_cat]
if filter_priority != "All":
    filtered_df = filtered_df[filtered_df["Priority"] == filter_priority]

if not filtered_df.empty:
    filtered_df = filtered_df.sort_values(by=["Category", "Project", "Bucket", "Task"])

timeline_months = []
curr_tracker = start_date
while curr_tracker <= end_date:
    timeline_months.append((curr_tracker.year, curr_tracker.month, curr_tracker.strftime("%b'%y")))
    if curr_tracker.month == 12:
        curr_tracker = datetime.date(curr_tracker.year + 1, 1, 1)
    else:
        curr_tracker = datetime.date(curr_tracker.year, curr_tracker.month + 1, 1)

st.markdown("---")
gantt_html = '<div class="gantt-wrapper">'

gantt_html += '<div class="gantt-row gantt-header-row">'
gantt_html += '<div class="fixed-pane">' \
              '<div class="cell-category">Category</div>' \
              '<div class="cell-project">Project</div>' \
              '<div class="cell-bucket">Bucket</div>' \
              '<div class="cell-task">Task Name</div>' \
              '<div class="cell-priority">Priority</div>' \
              '</div>'
gantt_html += '<div class="scrollable-pane">'
for y, m, m_label in timeline_months:
    gantt_html += f'<div class="month-column-block">' \
                  f'<div class="month-header-title">{m_label}</div>' \
                  f'<div class="weeks-sub-row">' \
                  f'<div class="week-head-number">1</div>' \
                  f'<div class="week-head-number">2</div>' \
                  f'<div class="week-head-number">3</div>' \
                  f'<div class="week-head-number">4</div>' \
                  f'</div></div>'
gantt_html += '</div></div>'

if filtered_df.empty:
    gantt_html += '<div style="padding: 20px; text-align: center; color: #666;">No active planner tasks align with your current filtering limits.</div>'
else:
    for idx, row in filtered_df.iterrows():
        p_anchor = f"proj-{str(row['Project']).lower().replace(' ', '-')}"
        b_anchor = f"buck-{str(row['Bucket']).lower().replace(' ', '-')}"
        t_anchor = f"task-{str(row['Task']).lower().replace(' ', '-')}"
        
        gantt_html += '<div class="gantt-row">'
                # --- (This section belongs inside your 'for idx, row in filtered_df.iterrows():' loop) ---
        gantt_html += f'<div class="fixed-pane">' \
                      f'<div class="cell-category">{row["Category"]}</div>' \
                      f'<div class="cell-project"><a class="matrix-link" href="#{p_anchor}" target="_self">📂 {row["Project"]}</a></div>' \
                      f'<div class="cell-bucket"><a class="matrix-link" href="#{b_anchor}" target="_self">📁 {row["Bucket"]}</a></div>' \
                      f'<div class="cell-task"><a class="matrix-link" href="#{t_anchor}" target="_self">📋 {row["Task"]}</a></div>' \
                      f'<div class="cell-priority"><span style="color:#ffaa00; font-weight:bold;">{row["Priority"]}</span></div>' \
                      f'</div>'
        
        gantt_html += '<div class="scrollable-pane">'
        for y, m, _ in timeline_months:
            gantt_html += '<div class="month-column-block"><div class="rectangle-track">'
            for w in range(1, 5):
                day_offset = (w - 1) * 7 + 1
                eval_date = datetime.date(y, m, min(day_offset, 28))
                is_within_plan = row["Plan Start"] <= eval_date <= row["Plan End"]
                is_breached = row["Is_Late"]
                rect_color = "transparent"
                tooltip_title = f"{row['Task']} | {eval_date.strftime('%b %d')}"
                if is_within_plan:
                    rect_color = "#2ca02c" if is_breached else "#1f77b4"
                gantt_html += f'<div class="indicator-rect" style="background-color: {rect_color};" title="{tooltip_title}"></div>'
            gantt_html += '</div></div>'
        gantt_html += '</div></div>'

# --- (This section sits outside the loop, closing the main wrapper elements) ---
gantt_html += '</div>'
st.markdown(gantt_html, unsafe_allow_html=True)

# --- 7. DEEP INTERACTIVE DETAILED ROUTER EDITS ---
st.markdown("---")
st.markdown("### 🔍 Live Focus Detail Router Panel")

with st.expander("➕ Inject New Task Entry Form (Test Auto-Expanding Financial Years)", expanded=False):
    with st.form("new_task_form"):
        ins_cat = st.selectbox("Category Scope", ["Digital Strategy", "Operations", "Study & Research", "Administrative"])
        ins_proj = st.text_input("Project Name", "Project-Future")
        ins_buck = st.text_input("Bucket Target Container", "Bucket-Future")
        ins_task = st.text_input("Unique Task Name")
        ins_priority = st.selectbox("Priority Target", ["P1", "P2", "P3"])
        
        c_d1, c_d2 = st.columns(2)
        ins_p_start = c_d1.date_input("Planned Start Date", datetime.date(2031, 4, 1))
        ins_p_end = c_d2.date_input("Target Planned End Date", datetime.date(2032, 3, 1))
        
        if st.form_submit_button("Commit Task Entry to System"):
            if ins_task.strip() == "":
                st.error("Task description cannot remain blank.")
            else:
                st.session_state.matrix_tasks.append({
                    "Category": ins_cat, 
                    "Project": ins_proj, 
                    "Bucket": ins_buck,
                    "Task": ins_task, 
                    "Priority": ins_priority, 
                    "Is_Late": False,
                    "Plan Start": ins_p_start, 
                    "Plan End": ins_p_end, 
                    "Actual End": ins_p_end
                })
                save_data(st.session_state.matrix_tasks)
                st.success("Committed successfully! Dynamic filter will now list future bounds.")
                st.rerun()

if not filtered_df.empty:
    for idx, row in filtered_df.iterrows():
        p_anchor = f"proj-{str(row['Project']).lower().replace(' ', '-')}"
        b_anchor = f"buck-{str(row['Bucket']).lower().replace(' ', '-')}"
        t_anchor = f"task-{str(row['Task']).lower().replace(' ', '-')}"
        
        st.markdown(f'<div id="{p_anchor}"></div><div id="{b_anchor}"></div><div id="{t_anchor}"></div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            col_x, col_y = st.columns(2)
            with col_x:
                st.subheader(f"✏️ Management Interface: {row['Task']}")
                st.markdown(f"**Project:** {row['Project']} | **Bucket Stack:** {row['Bucket']} | **Stream Category:** {row['Category']}")
                st.markdown(f"🗓️ *Planned Window timeline bounds:* `{row['Plan Start']}` to `{row['Plan End']}`")
            with col_y:
                st.markdown("<br>", unsafe_allow_html=True)
                status_box = st.checkbox("Mark as Target Breached / Late", value=row["Is_Late"], key=f"check_late_{idx}")
                if status_box != row["Is_Late"]:
                    st.session_state.matrix_tasks[idx]["Is_Late"] = status_box
                    save_data(st.session_state.matrix_tasks)
                    st.rerun()
