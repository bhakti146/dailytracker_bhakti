import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("✅ Daily Checklist (30 Days)")

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

# ------------------ INITIAL DATAFRAME ------------------
days = [f"Day {i}" for i in range(1, 31)]
DATA_FILE = "daily_tasks.csv"

# Load previous data if exists
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, index_col=0)
else:
    df = pd.DataFrame(False, index=days, columns=tasks)
    df.to_csv(DATA_FILE)

# ------------------ FRONTEND TABLE ------------------
st.subheader("📋 Tick Your Daily Tasks")

header_cols = st.columns(len(tasks) + 1)
header_cols[0].write("**Day**")
for i, task in enumerate(tasks):
    header_cols[i + 1].write(f"**{task}**")

for day in days:
    row_cols = st.columns(len(tasks) + 1)
    row_cols[0].write(day)
    for i, task in enumerate(tasks):
        key = f"{day}_{task}"
        df.loc[day, task] = row_cols[i + 1].checkbox(
            "",
            value=df.loc[day, task],
            key=key
        )

# ------------------ SAVE TO CSV ------------------
df.to_csv(DATA_FILE)

# ------------------ ANALYZER ------------------
st.divider()
st.subheader("📊 Progress Analyzer")

total_tasks = len(tasks) * 30
completed_tasks = df.values.sum()
progress = (completed_tasks / total_tasks) * 100

st.metric("Overall Consistency", f"{progress:.2f}%")

# Per-task analysis
task_progress = (df.sum() / 30) * 100
st.bar_chart(task_progress)

# Motivation message
if progress >= 80:
    st.success("🔥 Excellent consistency! Keep going!")
elif progress >= 50:
    st.info("🙂 Good progress! Try to be more consistent.")
else:
    st.warning("⚠️ Low consistency. Let's improve tomorrow!")

# ------------------ MONTHLY RESET ------------------
st.divider()
if st.button("🗑️ Reset Month"):
    df.iloc[:, :] = False
    df.to_csv(DATA_FILE)
    st.experimental_rerun()
