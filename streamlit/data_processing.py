# pylint: skip-file
"""Script that preprocess data for Streamlit application."""
import pandas as pd


def get_unique_trucks(transaction_data: pd.DataFrame) -> list:
    """Extract unique truck IDs from the transaction data."""
    return transaction_data['truck_id'].unique().tolist()


def prepare_truck_data(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Group the transaction data by truck ID and count transactions."""
    return transaction_data.groupby('truck_id').size().reset_index(name='count')


def preprocess_transaction_data_line(transaction_data: pd.DataFrame, view: str) -> pd.DataFrame:
    """Preprocess the transaction data to create a time_period column based on the selected view."""
    transaction_data['at'] = pd.to_datetime(
        transaction_data['at'])

    if view == 'Hour':
        transaction_data['time_period'] = transaction_data['at'].dt.strftime(
            '%H:00')
    elif view == 'Day':
        transaction_data['time_period'] = transaction_data['at'].dt.date

    return transaction_data


def calculate_transaction_counts_pie(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the counts and percentages of transactions per payment_method_id."""
    transaction_counts = transaction_data.groupby(
        ['payment_method_id', 'payment_method_type']).size().reset_index(name='count')
    transaction_counts['percentage'] = (
        transaction_counts['count'] / transaction_counts['count'].sum()) * 100
    return transaction_counts


def calculate_earnings_per_truck(transaction_data: pd.DataFrame, aggregation: str) -> pd.DataFrame:
    """Calculate total or average earnings per truck based on the selected aggregation method."""
    if aggregation == "Total Earnings":
        return transaction_data.groupby("truck_id")["total"].sum().reset_index()
    return transaction_data.groupby("truck_id")["total"].mean().reset_index()
