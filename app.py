import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(layout="wide")
st.title("✅ Daily Checklist (30 Days)")

# ------------------ UI ENHANCEMENT (CSS ONLY – SAFE) ------------------
st.markdown("""
<style>

/* Main background */
.main {
    background-color: #f7f9fc;
}

/* Title */
h1 {
    color: #2c3e50;
    font-weight: 700;
}

/* Row card */
.row-card {
    background: white;
    padding: 10px 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Highlight today's row */
.today-row {
    background: linear-gradient(90deg, #e3f2fd, #ffffff);
    border-left: 6px solid #2196f3;
}

/* Checkbox scaling */
input[type="checkbox"] {
    transform: scale(1.2);
    cursor: pointer;
}

/* Buttons */
.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #ff2e2e;
}

/* Progress bar */
div[data-testid="stProgress"] > div {
    height: 16px;
    border-radius: 10px;
}

/* Metric card */
[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

/* Divider */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #4facfe, #00f2fe);
}

</style>
""", unsafe_allow_html=True)

# ------------------ TASK LIST ------------------
tasks = [
    "Study",
    "Exercise",
    "Data Structure",
    "Academic Work",
    "reading",
    "Screen Time ≤ 1Hour",
    "Sleep ≤ 6 hrs"
]

# ------------------ DATA SETUP ------------------
days = [f"Day {i}" for i in range(1, 31)]
DATA_FILE = "daily_tasks.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, index_col=0)
else:
    df = pd.DataFrame(False, index=days, columns=tasks)
    df.to_csv(DATA_FILE)

# ------------------ TABLE HEADER ------------------
st.subheader("📋 Tick Your Daily Tasks")

header_cols = st.columns(len(tasks) + 1)
header_cols[0].write("**Day**")
for i, task in enumerate(tasks):
    header_cols[i + 1].write(f"**{task}**")

# ------------------ TODAY LOGIC ------------------
today_day = f"Day {datetime.now().day}"

# ------------------ CHECKLIST TABLE ------------------
for day in days:
    row_class = "row-card today-row" if day == today_day else "row-card"

    st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)

    row_cols = st.columns(len(tasks) + 1)
    row_cols[0].write("⭐ " + day if day == today_day else day)

    for i, task in enumerate(tasks):
        key = f"{day}_{task}"
        df.loc[day, task] = row_cols[i + 1].checkbox(
            "",
            value=df.loc[day, task],
            key=key
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SAVE DATA ------------------
df.to_csv(DATA_FILE)

# ------------------ ANALYZER ------------------
st.divider()
st.subheader("📊 Progress Analyzer")

total_tasks = len(tasks) * 30
completed_tasks = df.values.sum()
progress = (completed_tasks / total_tasks) * 100

st.metric("Overall Consistency", f"{progress:.2f}%")

task_progress = (df.sum() / 30) * 100
st.bar_chart(task_progress)

if progress >= 80:
    st.success("🔥 Excellent consistency! Keep going!")
elif progress >= 50:
    st.info("🙂 Good progress! Try to be more consistent.")
else:
    st.warning("⚠️ Low consistency. Let's improve tomorrow!")

# ------------------ RESET MONTH ------------------
st.divider()
if st.button("🗑️ Reset Month"):
    # Reset dataframe
    df.iloc[:, :] = False
    df.to_csv(DATA_FILE)

    # Clear all session state safely
    st.session_state.clear()

    st.experimental_rerun()
