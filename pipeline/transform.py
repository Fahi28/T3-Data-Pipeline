"""Takes downloaded data from a S3 bucket and transforms it, making it ready for deployment."""
import os
import logging
import pandas as pd
from dotenv import load_dotenv
from extract import configure_logger
import global_variables as gv


def get_current_directory() -> str:
    """Returns the current directory."""
    return os.path.dirname(os.path.abspath(__file__))


def delete_csv_files(db_logger: logging.Logger) -> None:
    """Deletes individual CSV files."""
    current_directory = get_current_directory()
    db_logger.info('Deleting files!')

    for file in os.listdir(current_directory):
        if file.startswith(gv.PREFIX) and file.endswith(gv.SUFFIX):
            file_path = os.path.join(current_directory, file)
            os.remove(file_path)
    db_logger.info('Files deleted!')


def process_transaction_data_file(file: str, db_logger: logging.Logger) -> pd.DataFrame:
    """Reads a CSV file and appends its contents to the combined DataFrame."""
    db_logger.info(f"Retrieving data from {file}!")

    truck_id = int(file.split('_')[1][1:])

    truck = pd.read_csv(file)
    truck['truck_id'] = truck_id
    db_logger.info(f'File data from {file} copied!')
    return truck


def get_csv_files(current_directory: str) -> list:
    """Returns a list of CSV files in the specified directory that match the criteria."""
    return [f for f in os.listdir(current_directory)
            if f.startswith(gv.PREFIX) and f.endswith(gv.SUFFIX)]


def process_and_combine_files(csv_files: list, db_logger: logging.Logger) -> pd.DataFrame:
    """Processes each CSV file and adds their data to a single DataFrame."""
    combined_trucks = pd.DataFrame()

    for file in csv_files:
        file_path = os.path.join(get_current_directory(), file)
        processed_data = process_transaction_data_file(file_path, db_logger)

        combined_trucks = pd.concat(
            [combined_trucks, processed_data], ignore_index=True)

    return combined_trucks


def combine_transaction_data_files(db_logger: logging.Logger) -> pd.DataFrame:
    """Combines individual CSV files into a single DataFrame."""
    current_directory = get_current_directory()

    csv_files = get_csv_files(current_directory)

    combined_trucks = process_and_combine_files(csv_files, db_logger)

    return combined_trucks


def filter_valid_totals(transactions: pd.DataFrame) -> pd.DataFrame:
    """Filters out invalid total values from the DataFrame."""
    invalid_values = [
        gv.TOTAL_INVALID_BLANK,
        gv.TOTAL_INVALID_ERR,
        gv.TOTAL_INVALID_VOID,
        gv.TOTAL_INVALID_ZERO
    ]

    valid_totals = (
        transactions['total'].notna() &
        ~transactions['total'].isin(invalid_values) &
        (transactions['total'] > 0) &
        (transactions['total'] <= 50)
    )
    return transactions[valid_totals]


def clean_duplicates(transactions: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicate rows from the DataFrame."""
    return transactions.drop_duplicates()


def convert_columns(transactions: pd.DataFrame) -> pd.DataFrame:
    """Converts data types of specified columns."""
    transactions['type'] = transactions['type'].astype(str)
    transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])
    return transactions


def convert_total_to_numeric(transactions: pd.DataFrame) -> pd.DataFrame:
    """Converts the 'total' column to numeric, coercing errors."""
    print(transactions.columns.tolist())
    transactions['total'] = pd.to_numeric(
        transactions['total'], errors='coerce')
    return transactions


def clean_data(db_logger: logging.Logger) -> pd.DataFrame:
    """Cleans the data from the Pandas DataFrame."""
    transactions = combine_transaction_data_files(db_logger)
    transactions = convert_total_to_numeric(transactions)
    transactions = filter_valid_totals(transactions)
    transactions = clean_duplicates(transactions)
    transactions = convert_columns(transactions)

    return transactions


def main() -> None:
    """Main function calling other functions."""
    load_dotenv()

    logger = configure_logger()
    combine_transaction_data_files(logger)
    transactions = clean_data(logger)
    transactions.to_csv(gv.CSV_NAME, index=False)


if __name__ == "__main__":
    main()
