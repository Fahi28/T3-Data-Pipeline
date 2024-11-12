"""Script that will visualise transformed data using Streamlit."""
import streamlit as st
from dotenv import load_dotenv
import database as db
import charts as ch


def home_page() -> None:
    """Home page for the Streamlit application."""
    load_dotenv()

    data = db.fetch_transaction_data()

    st.set_page_config(layout="wide")

    st.markdown("<h1 style='text-align: center;'>Transaction Analysis</h1>",
                unsafe_allow_html=True)

    col_one, col_two = st.columns([0.5, 0.5])

    with col_one:

        ch.line_transactions(data)

    with col_two:

        ch.bar_transactions_per_truck()

    col_three, col_four = st.columns([0.5, 0.5])

    with col_three:

        ch.pie_transactions_per_payment_method_id()

    with col_four:
        ch.display_truck_card_reader_table()

    ch.bar_total_or_average_per_truck(data)


if __name__ == "__main__":
    home_page()
