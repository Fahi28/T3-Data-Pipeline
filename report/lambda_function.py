"""Script containing SQL queries to place in daily report."""

import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import redshift_connector
from redshift_connector import Connection, Cursor

JSON_FILE_NAME = f'report_data_{datetime.today().date()}.json'
HTML_FILE_NAME = f'report_data_{datetime.today().date()}.html'


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


def get_db_cursor():
    """Helper function for AWS Lambda."""
    load_dotenv()
    connection = get_connection()
    return get_cursor(connection)


def set_schema(db_cursor) -> None:
    """Set search path for Redshift database."""
    db_cursor.execute(f"""SET search_path to {os.getenv("DB_SCHEMA")}""")


def total_transaction_value(db_cursor: Cursor) -> float:
    """Gets the total transaction value from all trucks."""
    set_schema(db_cursor)

    db_cursor.execute("""
                SELECT SUM(ft.total) FROM fact_transaction AS ft
                WHERE DATE(ft.at) = CURRENT_DATE - INTERVAL '1 day';
                    """)

    result = db_cursor.fetchone()[0]

    return float(result)


def total_transaction_value_per_truck(db_cursor):
    """Gets the total transaction value per truck name."""
    set_schema(db_cursor)

    db_cursor.execute("""
        SELECT dt.truck_name, SUM(ft.total) 
        FROM fact_transaction AS ft
        JOIN dim_truck AS dt ON ft.truck_id = dt.truck_id
        WHERE DATE(ft.at) = CURRENT_DATE - INTERVAL '1 day'
        GROUP BY dt.truck_name
        ORDER BY dt.truck_name;
    """)

    result = db_cursor.fetchall()
    return result


def number_of_transactions(db_cursor: Cursor):
    """Gets the number of transactions per truck."""
    set_schema(db_cursor)

    db_cursor.execute("""
                SELECT COUNT(ft.transaction_id) FROM fact_transaction AS ft
                WHERE DATE(ft.at) = CURRENT_DATE - INTERVAL '1 day';
                   """)

    result = db_cursor.fetchone()[0]
    return result


def number_of_transactions_per_truck(db_cursor):
    """Gets the number of transactions per truck name."""
    set_schema(db_cursor)

    db_cursor.execute("""
        SELECT dt.truck_name, COUNT(ft.transaction_id)
        FROM fact_transaction AS ft
        JOIN dim_truck AS dt ON ft.truck_id = dt.truck_id
        WHERE DATE(ft.at) = CURRENT_DATE - INTERVAL '1 day'
        GROUP BY dt.truck_name
        ORDER BY dt.truck_name;
    """)

    result = db_cursor.fetchall()
    return result


def total_average_revenue(db_cursor: Cursor) -> float:
    """The average revenue from all trucks."""
    set_schema(db_cursor)

    db_cursor.execute("""
                SELECT AVG(ft.total) FROM fact_transaction AS ft
                WHERE DATE(ft.at) = CURRENT_DATE - INTERVAL '1 day';
                   """)
    result = db_cursor.fetchone()[0]
    return float(result)


def average_revenue_per_truck(db_cursor: Cursor):
    """Gets the average revenue per truck name."""
    set_schema(db_cursor)

    db_cursor.execute("""
        SELECT dt.truck_name, AVG(ft.total)
        FROM fact_transaction AS ft
        JOIN dim_truck AS dt ON ft.truck_id = dt.truck_id
        WHERE DATE(ft.at) = CURRENT_DATE - INTERVAL '1 day'
        GROUP BY dt.truck_name
        ORDER BY dt.truck_name;
    """)

    result = db_cursor.fetchall()
    return result


def write_data_as_json(db_cursor: Cursor) -> dict:
    """Prepares the above functions into a readable JSON format."""
    return {
        "total_transaction_value": str(total_transaction_value(db_cursor)),
        "total_transaction_value_per_truck": [
            {"truck_name": truck[0],
             "total_value": str(truck[1])}
            for truck in total_transaction_value_per_truck(db_cursor)
        ],
        "number_of_transactions": number_of_transactions(db_cursor),
        "number_of_transactions_per_truck": [
            {"truck_name": truck[0],
             "transactions": truck[1]}
            for truck in number_of_transactions_per_truck(db_cursor)
        ],
        "total_average_revenue": str(total_average_revenue(db_cursor)),
        "average_revenue_per_truck": [
            {"truck_name": truck[0],
             "average_revenue": str(truck[1])}
            for truck in average_revenue_per_truck(db_cursor)
        ]
    }


def create_json_file(db_cursor: Cursor) -> None:
    """Creates a JSON file displaying key metrics."""
    with open(JSON_FILE_NAME, mode='w', encoding='utf-8') as f:
        json.dump(write_data_as_json(db_cursor), f, indent=4)


def create_html_file(db_cursor: Cursor) -> None:
    """Creates a HTML file displaying the key metrics."""
    data = write_data_as_json(db_cursor)

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')

    rendered_html = template.render(data=data)

    with open(HTML_FILE_NAME, mode='w', encoding='utf-8') as f:
        f.write(rendered_html)


def lambda_handler(event, context):
    db_cursor = get_db_cursor()
    load_dotenv()
    data = write_data_as_json(db_cursor)

    env = Environment(loader=FileSystemLoader('.'))

    template = env.get_template('template.html')

    rendered_html = template.render(data=data)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': rendered_html
    }


if __name__ == "__main__":
    load_dotenv()
    cursor = get_db_cursor()
    response = lambda_handler({}, None)
    print(response['body'])
