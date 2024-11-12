"""Script that will load cleaned data to a live redshift database."""

import logging
import os
import redshift_connector
import pandas as pd
from redshift_connector import Connection, Cursor
from dotenv import load_dotenv
from transform import clean_data, delete_csv_files
from extract import configure_logger
import global_variables as gv


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


def get_foreign_key(db_cursor: Cursor, table_name: str,
                    column_name: str, value: str) -> int:
    """Gets foreign keys."""
    db_cursor.execute(
        f"SELECT * FROM {table_name} WHERE {column_name} = %s", (value,))
    result = db_cursor.fetchone()
    if result:
        return result[0]
    raise ValueError('Invalid Data!')


def set_schema(db_cursor: Cursor, db_schema: str) -> None:
    """Sets the search path for the database schema."""
    db_cursor.execute(f"SET search_path TO {db_schema}")


def insert_query(db_cursor: Cursor, table: str, columns: list, values: tuple) -> None:
    """Query for inserting data into a database."""
    query = f"INSERT INTO {
        table} ({', '.join(columns)}) VALUES (%s, %s, %s, %s)"

    db_cursor.execute(query, values)


def get_foreign_keys(db_cursor: Cursor, row: pd.Series) -> tuple:
    """Retrieves foreign keys for the truck and payment method based on the row data."""
    truck_id = get_foreign_key(
        db_cursor, 'dim_truck', 'truck_id', row['truck_id'])
    payment_method_id = get_foreign_key(
        db_cursor, 'dim_payment_method', 'payment_method_type', row['type'])
    return truck_id, payment_method_id


def upload_row_to_database(db_cursor: Cursor, row: pd.Series) -> None:
    """Uploads a single row of transaction data to the database."""
    truck_id, payment_method_id = get_foreign_keys(db_cursor, row)

    values = (row['timestamp'], payment_method_id, row['total'], truck_id)
    insert_query(db_cursor, 'fact_transaction',
                 ['at', 'payment_method_id', 'total', 'truck_id'],
                 values)


def upload_transaction_data(conn: Connection, db_cursor: Cursor, db_logger: logging.Logger) -> None:
    """Uploads transaction data to the database."""
    transactions = clean_data(db_logger)
    set_schema(db_cursor, os.getenv("DB_SCHEMA"))

    for row in transactions.iterrows():
        upload_row_to_database(db_cursor, row[gv.DATA])

    conn.commit()


def delete_all_csv_files(filename: str, logger: logging.Logger) -> None:
    """Deletes all CSV files."""
    delete_csv_files(logger)
    if os.path.isfile(filename):
        os.remove(filename)
        logger.info(f"Successfully deleted the file: {filename}")
    else:
        logger.warning(f"File not found: {filename}. No action taken.")


def main() -> None:
    """Main function calling other functions."""
    load_dotenv()

    logger = configure_logger()

    db_conn = get_connection()
    cursor = get_cursor(db_conn)
    upload_transaction_data(db_conn, cursor, logger)
    delete_all_csv_files(gv.CSV_NAME, logger)


if __name__ == "__main__":

    main()
