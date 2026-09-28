import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. SET UP COMPREHENSIVE STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Advanced Project Matrix Planner", layout="wide")

# Inject explicit custom style sheets to achieve a frozen left pane and scrollable calendar track
st.markdown("""
<style>
    /* Main Layout Grid Setup */
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

    /* Fixed Left Pane Columns (Total 5 frozen fields) */
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

    /* Scrollable Right Pane Calendar Grid Timeline Track */
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

    /* Target Indicator Rectangles */
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
    
    /* Interactive Navigation Anchor Target Highlighting */
    :target {
        background-color: #223322 !important;
        border: 2px solid #2ca02c !important;
    }
    
    /* Link text styling */
    .matrix-link {
        color: #1f77b4;
        text-decoration: none;
    }
    .matrix-link:hover {
        text-decoration: underline;
        color: #4da3ff;
    }
</style>
""", unsafe_allow_html=True)

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
        # Default starter tasks (Baseline 2026/2027)
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

# --- 3. DYNAMIC FY BLOCK ENGINE HELPER FUNCTIONS ---
def get_fy_base_year(d):
    # Standard FY starts April 1st. If month is Jan-Mar, it belongs to the previous calendar year's base.
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
        # Align automatically into 2-year increments starting from even years (2026, 2028, 2030, 2032...)
        start_y = y - (y % 2)
        next_y = start_y + 1
        
        # Format string label layout matching: 26'27-27'28
        label = f"{str(start_y)[2:]}'{str(start_y+1)[2:]}-{str(next_y)[2:]}'{str(next_y+1)[2:]}"
        unique_blocks.add((start_y, label))
        
    # Sort blocks sequentially by their start year value
    sorted_labels = [block[1] for block in sorted(list(unique_blocks))]
    
    if "26'27-27'28" not in sorted_labels:
        sorted_labels.insert(0, "26'27-27'28")
        
    return sorted_labels

def parse_fy_block_dates(label):
    try:
        prefix_year_short = int(label.split("-")[0].split("'")[0])
        full_start_year = 2000 + prefix_year_short
        start_date_bound = datetime.date(full_start_year, 4, 1)
        end_date_bound = datetime.date(full_start_year + 2, 3, 31)
        return start_date_bound, end_date_bound
    except:
        return datetime.date(2026, 4, 1), datetime.date(2028, 3, 31)

# Initialize data footprint state
if "matrix_tasks" not in st.session_state:
    st.session_state.matrix_tasks = load_data()

df = pd.DataFrame(st.session_state.matrix_tasks)

# --- 4. FILTER HEADERS & FLOATING TOP RIGHT LEGEND PANEL ---
st.title("📂 MS Planner Gantt Workspace")

header_col, legend_col = st.columns()

# Compute dynamic horizon selection lists on the fly
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
    st.markdown("""
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 6px; border: 1px solid #333; font-size: 11px; float: right; width: 100%;">
        <div style="font-weight: bold; margin-bottom: 6px; color:#aaa; text-transform: uppercase; font-size:10px;">Gantt Legend Indicator Map</div>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div style="display: flex; align-items: center;"><div style="width: 16px; height: 10px; background-color: #1f77b4; border-radius: 2px; margin-right: 6px;"></div><span>Planned Duration (On-Time)</span></div>
            <div style="display: flex; align-items: center;"><div style="width: 16px; height: 10px; background-color: #2ca02c; border-radius: 2px; margin-right: 6px;"></div><span>Late Target Milestone Breached</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Parse selected 2-FY calendar date boundaries dynamically
start_date, end_date = parse_fy_block_dates(filter_fy)

filtered_df = df.copy()

# Retain tasks whose planned lifespans touch the selected 2-FY window [2]
filtered_df = filtered_df[
    (filtered_df["Plan Start"] <= end_date) & (filtered_df["Plan End"] >= start_date)
]

if filter_cat != "All":
    filtered_df = filtered_df[filtered_df["Category"] == filter_cat]
if filter_priority != "All":
    filtered_df = filtered_df[filtered_df["Priority"] == filter_priority]

# Sort tracking items cleanly by Category -> Project -> Bucket -> Task [2]
if not filtered_df.empty:
    filtered_df = filtered_df.sort_values(by=["Category", "Project", "Bucket", "Task"])

# --- 5. GENERATE CALENDAR TRACK SEQUENCE ---
timeline_months = []
curr_tracker = start_date
while curr_tracker <= end_date:
    timeline_months.append((curr_tracker.year, curr_tracker.month, curr_tracker.strftime("%b'%y")))
    if curr_tracker.month == 12:
        curr_tracker = datetime.date(curr_tracker.year + 1, 1, 1)
    else:
        curr_tracker = datetime.date(curr_tracker.year, curr_tracker.month + 1, 1)

# --- 6. RENDER CONTINUOUS DATA GRID TABLE ---
st.markdown("---")

gantt_html = '<div class="gantt-wrapper">'

# --- HEADER ROW RENDERING ---
gantt_html += '<div class="gantt-row gantt-header-row">'
gantt_html += """
    <div class="fixed-pane">
        <div class="cell-category">Category</div>
        <div class="cell-project">Project</div>
        <div class="cell-bucket">Bucket</div>
