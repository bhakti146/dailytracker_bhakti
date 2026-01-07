import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sqlite3

# Connect to database (only one!)
conn = sqlite3.connect("daily_checklist.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists (must be before SELECT)
cursor.execute("""
CREATE TABLE IF NOT EXISTS checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    day TEXT NOT NULL,
    task TEXT NOT NULL,
    completed INTEGER DEFAULT 0
)
""")
conn.commit()


#------------------Users------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "reset_version" not in st.session_state:
    st.session_state.reset_version = 0

#------------------------------------------------
if "reset_version" not in st.session_state:
    st.session_state.reset_version = 0


# ------------------ PAGE CONFIG ------------------
st.set_page_config(layout="wide")
st.title("✅ Daily Checklist (30 Days)")

#----------------------------------------------

col1, col2 = st.columns([8, 2])
col1.subheader(f"👋 Welcome, {st.session_state.username}")

if col2.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.reset_version += 1
    st.rerun()


# ------------------ UI ENHANCEMENT ------------------
st.markdown("""
<style>
.main { background-color: #f7f9fc; }
h1 { color: #2c3e50; font-weight: 700; }
.row-card {
    background: white;
    padding: 10px 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.today-row {
    background: linear-gradient(90deg, #e3f2fd, #ffffff);
    border-left: 6px solid #2196f3;
}
input[type="checkbox"] {
    transform: scale(1.2);
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

days = [f"Day {i}" for i in range(1, 31)]
# ---------- LOAD USER DATA FROM SQLITE ----------
df = pd.DataFrame(False, index=days, columns=tasks)

cursor.execute(
    "SELECT day, task, completed FROM checklist WHERE username=?",
    (st.session_state.username,)
)

for day, task, completed in cursor.fetchall():
    if day in df.index and task in df.columns:
        df.loc[day, task] = bool(completed)


#---------------------------------------------------------------
#----------------------------------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Enter Username")

    if st.button("Login"):
        if username.strip() == "":
            st.warning("Please enter a username")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username.lower()
            st.rerun()

    st.stop()

#---------------------------------------------------------
conn = sqlite3.connect("daily_checklist.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    day TEXT NOT NULL,
    task TEXT NOT NULL,
    completed INTEGER DEFAULT 0
)
""")
conn.commit()




# ------------------ HEADER ------------------
st.subheader("📋 Tick Your Daily Tasks")
header_cols = st.columns(len(tasks) + 1)
header_cols[0].write("**Day**")
for i, task in enumerate(tasks):
    header_cols[i + 1].write(f"**{task}**")

# ------------------ TODAY ------------------
today_day = f"Day {datetime.now().day}"



# ------------------ CHECKLIST ------------------
data_changed = False

for day in days:
    row_class = "row-card today-row" if day == today_day else "row-card"
    st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
    cols = st.columns(len(tasks) + 1)
    cols[0].write("⭐ " + day if day == today_day else day)

    for i, task in enumerate(tasks):
        key = f"{day}_{task}_{st.session_state.reset_version}"
        new_value = cols[i + 1].checkbox(
            "",
            value=bool(df.loc[day, task]),
            key=key
        )

        if new_value != df.loc[day, task]:
            df.loc[day, task] = new_value

            cursor.execute("""
                INSERT OR REPLACE INTO checklist
                (username, day, task, completed)
                VALUES (?, ?, ?, ?)
            """, (
                st.session_state.username,
                day,
                task,
                int(new_value)
            ))
            conn.commit()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SAVE ONLY IF CHANGED ------------------


# ------------------ ANALYTICS ------------------
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

# ------------------ WEEKLY ANALYTICS ------------------
st.divider()
st.subheader("📅 Weekly Analytics")

df["Date"] = pd.date_range(start=datetime.now().replace(day=1), periods=30)
df["Weekday"] = pd.to_datetime(df["Date"]).dt.day_name()


weekly_progress = df[tasks].groupby(df["Weekday"]).mean().mean(axis=1) * 100
st.bar_chart(weekly_progress)

# ------------------ MONTHLY ANALYTICS ------------------
st.divider()
st.subheader("🗓️ Monthly Analytics")

df["Daily %"] = (df[tasks].sum(axis=1) / len(tasks)) * 100
perfect_days = (df["Daily %"] == 100).sum()
average_daily = df["Daily %"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Days", len(df))
col2.metric("Perfect Days 🔥", perfect_days)
col3.metric("Avg Daily Consistency", f"{average_daily:.2f}%")

# ------------------ BEST & BAD DAY ------------------
best_day = df["Daily %"].idxmax()
bad_day = df["Daily %"].idxmin()
st.write(f"⭐ **Best Day:** {best_day}")
st.write(f"⚠️ **Bad Day:** {bad_day}")

# ------------------ RESET MONTH ------------------
if st.button("🗑️ Reset Month"):
    cursor.execute(
        "DELETE FROM checklist WHERE username=?",
        (st.session_state.username,)
    )
    conn.commit()

    st.session_state.reset_version += 1
    st.rerun()
