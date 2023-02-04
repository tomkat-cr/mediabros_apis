# date_utilities.py
import datetime


def get_formatted_date():
    date_format = "%Y-%m-%d %H:%M:%S UTC"
    formatted_date = datetime.date.strftime(
        datetime.datetime.utcnow(), date_format
    )
    return formatted_date
