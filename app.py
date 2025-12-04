import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_PATH = "data/expenses.csv"

st.set_page_config(page_title="Student Expense Tracker", layout="centered")
st.title("Student Expense Tracker")

# ------------------- Ensure data folder exists -------------------
if not os.path.exists("data"):
    os.makedirs("data")

# ------------------- Load data -------------------
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    else:
        df = pd.DataFrame(columns=["date", "category", "description", "amount"])
    return df

df = load_data()

# ------------------- Reset/Delete all expenses -------------------
st.header("Reset all expenses")
if st.button("Delete all expenses"):
    # Clear CSV
    pd.DataFrame(columns=["date", "category", "description", "amount"]).to_csv(DATA_PATH, index=False)
    st.success("All expenses have been deleted!")
    # Reload empty data
    df = pd.DataFrame(columns=["date", "category", "description", "amount"])

# ------------------- Add expense form -------------------
st.header("Add an expense")
with st.form("expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.today())
        category = st.selectbox("Category", ["Food", "Transport", "Rent", "Books", "Other"])
    with col2:
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Add expense")

    if submitted:
        new = {
            "date": pd.to_datetime(date).strftime("%Y-%m-%d"),
            "category": category,
            "description": description,
            "amount": float(amount),
        }

        # If CSV exists, append, else create new
        if os.path.exists(DATA_PATH):
            # If CSV is empty after deletion, write header first
            if os.path.getsize(DATA_PATH) == 0:
                pd.DataFrame([new]).to_csv(DATA_PATH, index=False)
            else:
                pd.DataFrame([new]).to_csv(DATA_PATH, mode="a", header=False, index=False)
        else:
            pd.DataFrame([new]).to_csv(DATA_PATH, index=False)

        st.success("Expense added!")

        # Reload CSV so table updates
        df = pd.read_csv(DATA_PATH, parse_dates=["date"])

# ------------------- View + filter expenses -------------------
st.header("View expenses")

if not df.empty:
    start = st.date_input("Start date", value=df["date"].min())
    end = st.date_input("End date", value=df["date"].max())

    mask = (pd.to_datetime(df["date"]) >= pd.to_datetime(start)) & \
           (pd.to_datetime(df["date"]) <= pd.to_datetime(end))
    filtered = df.loc[mask].copy()
else:
    filtered = pd.DataFrame(columns=["date", "category", "description", "amount"])

st.subheader(f"Total: ${filtered['amount'].sum():.2f}")
st.dataframe(filtered)

# ------------------- Charts -------------------
st.header("Charts")
if not filtered.empty:
    cat_sum = filtered.groupby("category")["amount"].sum()
    st.bar_chart(cat_sum)

    filtered["month"] = pd.to_datetime(filtered["date"]).dt.to_period("M").astype(str)
    monthly = filtered.groupby("month")["amount"].sum()
    st.line_chart(monthly)

# ------------------- Download CSV -------------------
st.download_button(
    "Download filtered data",
    filtered.to_csv(index=False),
    file_name="filtered_expenses.csv"
)
