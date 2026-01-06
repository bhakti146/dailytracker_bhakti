import streamlit as st
import pandas as pd
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="✅ 30-Day Daily Checklist",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📅 30-Day Daily Checklist Tracker")

# ------------------ TASK LIST ------------------
tasks = [
    "Study 📚",
    "Exercise 🏋️",
    "Data Structure 💻",
    "Academic Work 📝",
    "Reading 📖",
    "Screen Time ≤ 1Hour 📱",
    "Sleep ≤ 6 hrs 😴"
]

days = [f"Day {i}" for i in range(1, 31)]
DATA_FILE = "daily_tasks.csv"

# ------------------ LOAD OR INITIALIZE DATA ------------------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, index_col=0)
else:
    df = pd.DataFrame(False, index=days, columns=tasks)
    df.to_csv(DATA_FILE)

# ------------------ SIDEBAR RESET ------------------
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Reset Month"):
        df.iloc[:, :] = False
        df.to_csv(DATA_FILE)
        # Reset session_state keys
        for day in days:
            for task in tasks:
                key = f"{day}_{task}"
                if key in st.session_state:
                    st.session_state[key] = False
        st.experimental_rerun()

# ------------------ FRONTEND: TASK CHECKLIST ------------------
st.subheader("📋 Tick Your Daily Tasks")
st.markdown("💡 Click on each checkbox when you complete a task. Expand each day to see details.")

for day in days:
    with st.expander(f"📅 {day}"):
        cols = st.columns(len(tasks))
        for i, task in enumerate(tasks):
            key = f"{day}_{task}"
            completed = cols[i].checkbox("", value=df.loc[day, task], key=key)
            df.loc[day, task] = completed

# ------------------ SAVE DATA ------------------
df.to_csv(DATA_FILE)

# ------------------ PROGRESS ANALYZER ------------------
st.divider()
st.subheader("📊 Progress Analyzer")

# Overall completion
total_tasks = len(tasks) * 30
completed_tasks = df.values.sum()
progress = (completed_tasks / total_tasks) * 100
st.metric("Overall Consistency", f"{progress:.2f}%")

# Per-task progress with progress bars
st.markdown("### Task-wise Progress")
for task in tasks:
    task_percent = int((df[task].sum() / 30) * 100)
    st.write(f"**{task}**: {task_percent}%")
    st.progress(task_percent)

# Motivation message
st.markdown("### Motivation")
if progress == 100:
    st.balloons()
    st.success("🏆 Incredible! You completed all tasks this month!")
elif progress >= 80:
    st.success("🔥 Excellent consistency! Keep going!")
elif progress >= 50:
    st.info("🙂 Good progress! Try to be more consistent.")
else:
    st.warning("⚠️ Low consistency. Let's improve tomorrow!")

# ------------------ OPTIONAL: DOWNLOAD CSV ------------------
st.divider()
st.subheader("💾 Download Your Checklist")
st.download_button(
    label="📥 Download CSV",
    data=df.to_csv(),
    file_name="daily_tasks.csv",
    mime="text/csv"
)
