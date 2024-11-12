"""Script that downloads relevant information from an AWS S3 bucket at regular intevals,
    And formats the data accordingly."""
import os
import logging
from datetime import datetime, timedelta
import pytz
import botocore
from botocore.client import BaseClient
from boto3 import client
from dotenv import load_dotenv
import global_variables as gv


def configure_logger() -> logging.Logger:
    """Sets up and returns a logger instance."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_s_three_client() -> client:
    """Returns an S3 client instance using credentials from env_config."""
    return client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )


def is_valid_hour(hour: int) -> bool:
    """Check if the given hour is valid."""
    return hour in gv.VALID_TIMES


def get_nearest_valid_hour(current_hour: int) -> int:
    """Get the nearest valid hour less than or equal to the current hour."""
    valid_hours = sorted(gv.VALID_TIMES)
    nearest_hour = None
    for hour in reversed(valid_hours):
        if hour <= current_hour:
            nearest_hour = hour
            break
    return nearest_hour


def construct_folder_path(current_time: datetime, hour: int) -> str:
    """Construct the S3 folder path based on the current time and valid hour."""
    return f"trucks/{current_time:%Y-%m}/{current_time.day}/{hour}"


def get_recent_files(bucket_name: str, folder_path: str, current_time: datetime) -> list:
    """Get a list of files uploaded in the last three hours."""
    s_three = get_s_three_client()
    response = s_three.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

    three_hours_ago = current_time.astimezone(pytz.utc) - timedelta(hours=3)

    return [
        obj for obj in response.get('Contents', [])
        if obj['LastModified'] >= three_hours_ago
    ]


def log_invalid_hour(app_logger: logging.Logger, current_hour: int) -> None:
    """Log an error for an invalid hour."""
    app_logger.error(
        f"Current hour ({current_hour}) is not valid. It must be 12, 15, 18, or 21.")
    raise ValueError(
        "Current hour is not valid. It must be 12, 15, 18, or 21.")


def access_correct_folder(app_logger: logging.Logger):
    """Access the correct S3 bucket and folder."""
    bucket_name = os.getenv("BUCKET_NAME")
    current_time = datetime.now(pytz.utc)
    current_hour = current_time.hour

    nearest_hour = get_nearest_valid_hour(current_hour)

    if nearest_hour is None:
        log_invalid_hour(app_logger, current_hour)
        return None

    folder_path = construct_folder_path(current_time, nearest_hour)
    app_logger.info(f"Accessing folder: {folder_path}")

    recent_files = get_recent_files(bucket_name, folder_path, current_time)

    if recent_files:
        app_logger.info(
            f"Found {len(recent_files)} recent files in {folder_path}.")
        return bucket_name, folder_path

    app_logger.warning("No recent files found in the last three hours.")
    raise ValueError("No recent data uploaded in the last three hours.")


def list_s_three_objects(s_three, bucket_name: str, folder_path: str):
    """Lists objects in the specified S3 bucket."""
    response = s_three.list_objects_v2(
        Bucket=(bucket_name), Prefix=folder_path)
    return response.get('Contents', [])


def download_file_if_matching(key: str,
                              s_three: BaseClient,
                              app_logger: logging.Logger) -> None:
    """Downloads the file if it matches the specified prefix and suffix."""
    app_logger.info(f"Checking file: {key}")
    if gv.PREFIX in key and key.endswith(gv.SUFFIX):
        local_path = key.split('/')[-1]
        bucket_name = os.getenv("BUCKET_NAME")
        try:
            app_logger.info(f"Downloading {key} to {local_path}")
            s_three.download_file(bucket_name, key, local_path)
            app_logger.info(f"Successfully downloaded {key} to {local_path}")
        except botocore.exceptions.ClientError as download_error:
            app_logger.error(f"Failed to download {key}: {download_error}")
    else:
        app_logger.info(f"File {key} does not match criteria.")


def download_truck_data_files(app_logger: logging.Logger) -> None:
    """Downloads relevant files from S3 to the current working directory."""
    s_three = get_s_three_client()
    app_logger.info("Starting download process...")
    bucket_name, folder_path = access_correct_folder(app_logger)

    try:
        contents = list_s_three_objects(s_three, bucket_name, folder_path)
        if not contents:
            app_logger.warning("No files found in the bucket.")
            return

        for obj in contents:
            app_logger.info(f"Found object: {obj['Key']}")
            download_file_if_matching(
                obj['Key'], s_three, app_logger)

        app_logger.info("Download Complete!")

    except botocore.exceptions.ClientError as e:
        app_logger.error("Error accessing bucket or listing objects: %s", e)


def main() -> None:
    """Main function calling other functions."""
    load_dotenv()
    logger = configure_logger()
    download_truck_data_files(logger)


if __name__ == "__main__":
    main()
