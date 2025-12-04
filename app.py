import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------- Setup -------------------
st.set_page_config(page_title="Student Expense Tracker", layout="centered")
st.title("Student Expense Tracker")

# ------------------- Ask for username -------------------
username = st.text_input("Enter your username:", value="", key="username_input")

if username:
    # ------------------- Initialize session storage -------------------
    if "expenses" not in st.session_state:
        st.session_state.expenses = []

    # ------------------- Reset/Delete all expenses -------------------
    st.header("Reset all expenses")
    if st.button("Delete all expenses"):
        st.session_state.expenses = []
        st.success("All expenses have been deleted!")

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
            st.session_state.expenses.append({
                "date": date.strftime("%Y-%m-%d"),
                "category": category,
                "description": description,
                "amount": float(amount)
            })
            st.success("Expense added!")

    # ------------------- View + filter expenses -------------------
    st.header("View expenses")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        start = st.date_input("Start date", value=pd.to_datetime(df["date"]).min())
        end = st.date_input("End date", value=pd.to_datetime(df["date"]).max())

        mask = (pd.to_datetime(df["date"]) >= pd.to_datetime(start)) & \
               (pd.to_datetime(df["date"]) <= pd.to_datetime(end))
        filtered = df.loc[mask]

        st.subheader(f"Total: ${filtered['amount'].sum():.2f}")
        st.dataframe(filtered)

        # ------------------- Charts -------------------
        st.header("Charts")
        cat_sum = filtered.groupby("category")["amount"].sum()
        st.bar_chart(cat_sum)

        filtered["month"] = pd.to_datetime(filtered["date"]).dt.to_period("M").astype(str)
        monthly = filtered.groupby("month")["amount"].sum()
        st.line_chart(monthly)

        # ------------------- Download CSV -------------------
        st.download_button(
            "Download filtered data",
            filtered.to_csv(index=False),
            file_name=f"{username}_filtered_expenses.csv"
        )
    else:
        st.info("No expenses added yet.")
