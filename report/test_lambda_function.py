# pylint: skip-file
import pytest
from unittest.mock import Mock, patch, mock_open
import json
from datetime import datetime
from lambda_function import (total_transaction_value,
                             number_of_transactions,
                             total_average_revenue,
                             total_transaction_value_per_truck,
                             number_of_transactions_per_truck,
                             average_revenue_per_truck,
                             write_data_as_json,
                             create_json_file,
                             create_html_file,
                             lambda_handler)

JSON_FILE_NAME = f'report_data_{datetime.today().date()}.json'
HTML_FILE_NAME = f'report_data_{datetime.today().date()}.html'


@pytest.fixture
def sample_data():
    return {
        "total_transaction_value": "2740.12",
        "total_transaction_value_per_truck": [
            {"truck_name": "Burrito Madness", "total_value": "718.6"},
            {"truck_name": "Cupcakes by Michelle", "total_value": "587.01"}
        ],
        "number_of_transactions": 419,
        "number_of_transactions_per_truck": [
            {"truck_name": "Burrito Madness", "transactions": 92},
            {"truck_name": "Cupcakes by Michelle", "transactions": 99}
        ],
        "total_average_revenue": "6.53",
        "average_revenue_per_truck": [
            {"truck_name": "Burrito Madness", "average_revenue": "7.81"},
            {"truck_name": "Cupcakes by Michelle", "average_revenue": "5.92"}
        ]
    }


def test_total_transaction_value():
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [2740.12]

    result = total_transaction_value(mock_cursor)

    assert result == mock_cursor.fetchone.return_value[0]


def test_number_of_transactions():
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [99]

    result = number_of_transactions(mock_cursor)

    assert result == mock_cursor.fetchone.return_value[0]


def test_total_average_revenue():
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [6.50]

    result = total_average_revenue(mock_cursor)

    assert result == mock_cursor.fetchone.return_value[0]


def test_total_transaction_value_per_truck():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("Burrito Madness", 718.60),
        ("Cupcakes by Michelle", 587.01),
        ("Hartmann's Jellied Eels", 124.63),
        ("Kings of Kebabs", 782.40),
        ("SuperSmoothie", 125.78),
        ("Yoghurt Heaven", 401.70)
    ]

    result = total_transaction_value_per_truck(mock_cursor)

    assert result == mock_cursor.fetchall.return_value


def test_number_of_transactions_per_truck():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("Burrito Madness", 3),
        ("Cupcakes by Michelle", 4),
        ("Hartmann's Jellied Eels", 15),
        ("Kings of Kebabs", 2),
        ("SuperSmoothie", 1),
        ("Yoghurt Heaven", 22)
    ]

    result = number_of_transactions_per_truck(mock_cursor)

    assert result == mock_cursor.fetchall.return_value


def test_average_revenue_per_truck():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("Burrito Madness", 1.60),
        ("Cupcakes by Michelle", 5.01),
        ("Hartmann's Jellied Eels", 4.63),
        ("Kings of Kebabs", 2.40),
        ("SuperSmoothie", 1.78),
        ("Yoghurt Heaven", 8.70)
    ]

    result = average_revenue_per_truck(mock_cursor)

    assert result == mock_cursor.fetchall.return_value


def test_write_data_as_json():
    mock_cursor = Mock()

    with patch('lambda_function.total_transaction_value', return_value=2740.12), \
            patch('lambda_function.total_transaction_value_per_truck', return_value=[
                ("Burrito Madness", 718.60),
                ("Cupcakes by Michelle", 587.01),
                ("Hartmann's Jellied Eels", 124.63),
                ("Kings of Kebabs", 782.40),
                ("SuperSmoothie", 125.78),
                ("Yoghurt Heaven", 401.70)
            ]), \
            patch('lambda_function.number_of_transactions', return_value=419), \
            patch('lambda_function.number_of_transactions_per_truck', return_value=[
                ("Burrito Madness", 92),
                ("Cupcakes by Michelle", 99),
                ("Hartmann's Jellied Eels", 37),
                ("Kings of Kebabs", 96),
                ("SuperSmoothie", 22),
                ("Yoghurt Heaven", 73)
            ]), \
            patch('lambda_function.total_average_revenue', return_value=6.53), \
            patch('lambda_function.average_revenue_per_truck', return_value=[
                ("Burrito Madness", 7.81),
                ("Cupcakes by Michelle", 5.92),
                ("Hartmann's Jellied Eels", 3.36),
                ("Kings of Kebabs", 8.15),
                ("SuperSmoothie", 5.71),
                ("Yoghurt Heaven", 5.50)
            ]):

        result = write_data_as_json(mock_cursor)

        expected_result = {
            "total_transaction_value": "2740.12",
            "total_transaction_value_per_truck": [
                {"truck_name": "Burrito Madness", "total_value": "718.6"},
                {"truck_name": "Cupcakes by Michelle", "total_value": "587.01"},
                {"truck_name": "Hartmann's Jellied Eels", "total_value": "124.63"},
                {"truck_name": "Kings of Kebabs", "total_value": "782.4"},
                {"truck_name": "SuperSmoothie", "total_value": "125.78"},
                {"truck_name": "Yoghurt Heaven", "total_value": "401.7"}
            ],
            "number_of_transactions": 419,
            "number_of_transactions_per_truck": [
                {"truck_name": "Burrito Madness", "transactions": 92},
                {"truck_name": "Cupcakes by Michelle", "transactions": 99},
                {"truck_name": "Hartmann's Jellied Eels", "transactions": 37},
                {"truck_name": "Kings of Kebabs", "transactions": 96},
                {"truck_name": "SuperSmoothie", "transactions": 22},
                {"truck_name": "Yoghurt Heaven", "transactions": 73}
            ],
            "total_average_revenue": "6.53",
            "average_revenue_per_truck": [
                {"truck_name": "Burrito Madness", "average_revenue": "7.81"},
                {"truck_name": "Cupcakes by Michelle", "average_revenue": "5.92"},
                {"truck_name": "Hartmann's Jellied Eels", "average_revenue": "3.36"},
                {"truck_name": "Kings of Kebabs", "average_revenue": "8.15"},
                {"truck_name": "SuperSmoothie", "average_revenue": "5.71"},
                {"truck_name": "Yoghurt Heaven", "average_revenue": "5.5"}
            ]
        }

        assert result == expected_result


def test_create_json_file(sample_data):
    mock_cursor = Mock()

    with patch('lambda_function.write_data_as_json', return_value=sample_data), \
            patch("builtins.open", mock_open()) as mocked_file:

        create_json_file(mock_cursor)

        mocked_file.assert_called_once_with(
            JSON_FILE_NAME, mode='w', encoding='utf-8')

        file_handle = mocked_file()

        written_content = ''.join(call[0][0]
                                  for call in file_handle.write.call_args_list)
        expected_file_content = json.dumps(sample_data, indent=4)

        assert written_content == expected_file_content


def test_create_html_file(sample_data):
    rendered_html = "<html><body>Sample Rendered HTML</body></html>"

    with patch('lambda_function.write_data_as_json', return_value=sample_data), \
            patch('lambda_function.Environment') as mock_environment, \
            patch('builtins.open', mock_open()) as mock_file:

        mock_env_instance = mock_environment.return_value
        mock_template = mock_env_instance.get_template.return_value
        mock_template.render.return_value = rendered_html

        mock_cursor = Mock()

        create_html_file(mock_cursor)

        mock_env_instance.get_template.assert_called_once_with('template.html')
        mock_template.render.assert_called_once_with(data=sample_data)

        mock_file.assert_called_once_with(
            HTML_FILE_NAME, mode='w', encoding='utf-8')
        mock_file().write.assert_called_once_with(rendered_html)


def test_lambda_handler(sample_data):
    mock_event = {}
    mock_context = Mock()

    rendered_html = "<html><body>Sample Rendered HTML</body></html>"

    with patch('lambda_function.get_db_cursor') as mock_get_db_cursor, \
            patch('lambda_function.write_data_as_json', return_value=sample_data), \
            patch('lambda_function.Environment') as mock_environment, \
            patch('lambda_function.load_dotenv'):

        mock_cursor = Mock()
        mock_get_db_cursor.return_value = mock_cursor
        mock_env_instance = mock_environment.return_value
        mock_template = mock_env_instance.get_template.return_value
        mock_template.render.return_value = rendered_html

        response = lambda_handler(mock_event, mock_context)

        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'text/html'
        assert response['body'] == rendered_html

        mock_get_db_cursor.assert_called_once()
        mock_env_instance.get_template.assert_called_once_with('template.html')
        mock_template.render.assert_called_once_with(data=sample_data)
