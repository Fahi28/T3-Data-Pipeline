# pylint: skip-file
"""Script containing SQL queries for Streamlit Application"""
import os
import pandas as pd
import redshift_connector
from redshift_connector import Connection, Cursor


def get_connection() -> Connection:
    """Establish a connection to a redshift database."""
    return redshift_connector.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )


def get_cursor(conn: Connection) -> Cursor:
    """Creates a redshift cursor."""
    return conn.cursor()


def set_schema(db_cursor) -> None:
    """Set search path for Redshift database."""
    db_cursor.execute(f"""SET search_path to {os.getenv("DB_SCHEMA")}""")


def fetch_transaction_data(selected_trucks: list = None) -> pd.DataFrame:
    """Fetch transaction data from the Redshift database.
    Optionally filtered by selected truck IDs."""
    conn = get_connection()
    cursor = get_cursor(conn)

    set_schema(cursor)

    query = "SELECT * FROM fact_transaction"
    if selected_trucks:
        truck_ids = ', '.join(f"'{truck}'" for truck in selected_trucks)
        query += f" WHERE truck_id IN ({truck_ids});"
    else:
        query += ";"

    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    result = cursor.fetchall()

    transaction_data = pd.DataFrame(result, columns=columns)

    return transaction_data


def fetch_transaction_data_pie_chart() -> pd.DataFrame:
    """Fetch transaction data from the Redshift database."""
    conn = get_connection()
    cursor = get_cursor(conn)
    set_schema(cursor)
    query = """
        SELECT 
            ft.transaction_id, 
            ft.at, 
            ft.payment_method_id, 
            ft.total, 
            ft.truck_id,
            dpm.payment_method_type
        FROM 
            fact_transaction ft
        LEFT JOIN 
            dim_payment_method dpm 
        ON 
            ft.payment_method_id = dpm.payment_method_id;
    """

    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    result = cursor.fetchall()

    transaction_data = pd.DataFrame(result, columns=columns)

    return transaction_data


def fetch_truck_card_reader_data() -> pd.DataFrame:
    """Fetches truck names and their card reader status from the database."""

    conn = get_connection()
    cursor = get_cursor(conn)
    set_schema(cursor)
    cursor.execute("SELECT truck_name, has_card_reader FROM dim_truck;")

    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=['truck_name', 'has_card_reader'])
